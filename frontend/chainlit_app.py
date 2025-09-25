import atexit
import os
import glob
import shutil
import time
from typing import cast, List
from datetime import datetime

from openai import AsyncOpenAI
from openai.types.responses import ResponseTextDeltaEvent, ResponseFunctionToolCall
from dotenv import load_dotenv
from chromadb.config import Settings
from langchain_community.document_loaders import TextLoader, UnstructuredMarkdownLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain.schema import Document
from pydantic import SecretStr
import hashlib
import uuid

import chainlit as cl
from agents.mcp import MCPServerStreamableHttp
from agents import Agent, OpenAIChatCompletionsModel, Runner, SQLiteSession, gen_trace_id, trace

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")
mcp_server_url = os.getenv("MCP_SERVER_URL")

if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set")
if not mcp_server_url:
    raise ValueError("MCP_SERVER_URL is not set")

client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# Global embeddings instance to reuse
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=SecretStr(gemini_api_key)
)

def reset_vector_store():
    """Reset the Chroma vector store collection instead of deleting files."""
    ds_name = os.path.join("..", "vector_store")
    print(f"[INFO] Resetting vector store at {ds_name}")

    try:
        vector_store = Chroma(
            persist_directory=ds_name,
            embedding_function=embeddings,
            collection_name="study_documents"
        )
        vector_store.reset_collection()   # Clears all documents
        print(f"[INFO] Successfully reset vector store at {ds_name}")
    except Exception as e:
        print(f"[WARNING] Could not reset vector store: {e}")

# --- Delete vector store each run ---
# reset_vector_store()              # Run at startup - commented out to preserve documents
# atexit.register(reset_vector_store)  # Run again on shutdown




@cl.on_chat_start
async def start():
    """Initialize the chat session with agent and MCP server."""
    
    # Create MCP server instance that will persist throughout the session
    mcp_server_instance = MCPServerStreamableHttp(
        name="StudyMode StreamableHttp Server",
        params={"url": f"{mcp_server_url}"},
        cache_tools_list=True,
        client_session_timeout_seconds=30
    )

    # Connect to the MCP server
    await mcp_server_instance.__aenter__()

    # Store the MCP server in the user session
    cl.user_session.set("mcp_server", mcp_server_instance)

    prompt_result = await mcp_server_instance.get_prompt("prompt-v1")
    # Extract the actual prompt text from the GetPromptResult object
    if prompt_result.messages and len(prompt_result.messages) > 0:
        first_message = prompt_result.messages[0]
        if hasattr(first_message.content, 'text'):
            instruction_text = first_message.content.text
        elif isinstance(first_message.content, str):
            instruction_text = first_message.content
        else:
            instruction_text = str(first_message.content)
    else:
        instruction_text = "No prompt text found"

    agent = Agent(
        name="Assistant",
        instructions=instruction_text,
        model=OpenAIChatCompletionsModel(
            model="gemini-2.5-flash",
            openai_client=client,
        ),
        mcp_servers=[mcp_server_instance]
    )

    session = SQLiteSession("session_1")
    trace_id = gen_trace_id()
    print(f"\nView trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\n")

    with trace("StudyMode Clone Workflow", trace_id=trace_id):
        result = await Runner.run(agent, "Hello", session=session)

    cl.user_session.set("agent", agent)
    cl.user_session.set("session", session)

    await cl.Message(content=result.final_output).send()

@cl.on_message
async def main(message: cl.Message):
    """Process incoming messages and handle file uploads."""
    agent: Agent = cl.user_session.get("agent")
    session: SQLiteSession = cl.user_session.get("session")

    # Use a session-based dictionary to track tool calls for UI updates
    cl.user_session.set("tool_steps", {})

    # Handle file uploads
    if message.elements:
        await handle_file_uploads(message.elements)
    
    # Process incoming message with the agent
    response_msg = cl.Message(content="", author=agent.name)
    await response_msg.send()

    try:
        result = Runner.run_streamed(
            starting_agent=agent, input=message.content, session=session)

        async for event in result.stream_events():
            if event.type == "raw_response_event" and isinstance(
                event.data, ResponseTextDeltaEvent
            ):
                # Stream the raw LLM tokens to the UI
                await response_msg.stream_token(event.data.delta or "")

            elif event.type == "run_item_stream_event":
                item = event.item
                tool_steps = cl.user_session.get("tool_steps")

                if item.type == "tool_call_item":
                    tool_call = cast(ResponseFunctionToolCall, item.raw_item)
                    step = cl.Step(
                        name=tool_call.name,
                        type="tool",
                        parent_id=response_msg.id,
                    )
                    step.input = tool_call.arguments
                    await step.send()
                    tool_steps[tool_call.id] = step

                elif item.type == "tool_call_output_item":
                    tool_call_id = getattr(item.raw_item, 'call_id', None) or getattr(
                        item, 'tool_call_id', None)
                    output_value = getattr(item.raw_item, 'output', None) or getattr(
                        item, 'output', str(item.raw_item))

                    if tool_call_id and tool_call_id in tool_steps:
                        step = tool_steps.pop(tool_call_id)
                        step.output = str(output_value)
                        await step.update()
                    else:
                        step = cl.Step(
                            name="Tool Output",
                            type="tool",
                            parent_id=response_msg.id,
                        )
                        step.output = str(output_value)
                        await step.send()

        # Update the UI with the final message
        final_text = result.final_output if result.final_output else "No final output."
        response_msg.content = final_text
        await response_msg.update()

    except Exception as e:
        response_msg.content = f"An unexpected error occurred: {str(e)}"
        await response_msg.update()
        print(f"Error: {str(e)}")

async def handle_file_uploads(elements):
    """Handle multiple file uploads efficiently."""
    processed_files = []
    failed_files = []
    
    for element in elements:
        try:
            if element.mime in ["text/plain"]:
                # Handle text files
                loader = TextLoader(element.path, encoding="utf-8")
                document = loader.load()[0]
                
                # Add metadata
                document.metadata.update({
                    "filename": element.name,
                    "file_type": "text",
                    "upload_date": datetime.now().isoformat(),
                    "file_size": os.path.getsize(element.path),
                    "source": f"uploaded/{element.name}"
                })
                
                await add_document_to_vector_store(document)
                processed_files.append(element.name)
            
            elif element.name.endswith('.md') or element.mime == "text/markdown":
                # Handle Markdown files with UnstructuredMarkdownLoader
                loader = UnstructuredMarkdownLoader(
                    element.path,
                    mode="single",
                    strategy="fast",
                )
                document = loader.load()[0]
                
                # Add metadata
                document.metadata.update({
                    "filename": element.name,
                    "file_type": "markdown",
                    "upload_date": datetime.now().isoformat(),
                    "file_size": os.path.getsize(element.path),
                    "source": f"uploaded/{element.name}"
                })
                
                await add_document_to_vector_store(document)
                processed_files.append(element.name)
                
                
            else:
                failed_files.append(f"{element.name} (unsupported type: {element.mime}). Supported: .txt and .md files only")
                
        except Exception as e:
            failed_files.append(f"{element.name} (error: {str(e)})")
    
    # Send feedback to user
    if processed_files:
        await cl.Message(
            content=f"✅ Successfully processed: {', '.join(processed_files)}"
        ).send()
    
    if failed_files:
        await cl.Message(
            content=f"❌ Failed to process: {', '.join(failed_files)}"
        ).send()

async def add_document_to_vector_store(document: Document):
    """Add a single document to the existing vector store."""
    await add_documents_to_vector_store([document])

async def add_documents_to_vector_store(documents: List[Document]):
    """Add multiple documents to the existing vector store without replacing it."""
    try:
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = text_splitter.split_documents(documents)
        
        # Add unique IDs to prevent duplicates
        for chunk in chunks:
            # Create a hash of the content for deduplication
            content_hash = hashlib.md5(chunk.page_content.encode()).hexdigest()[:8]
            chunk.metadata["chunk_id"] = f"{chunk.metadata.get('filename', 'unknown')}_{content_hash}"
        
        ds_name = os.path.join("..", "vector_store")
        
        # Create directory if it doesn't exist
        # os.makedirs(os.path.dirname(ds_name), exist_ok=True)
       
        
        # Load existing vector store or create new one
        try:
            vector_store = Chroma(
                persist_directory=ds_name,
                embedding_function=embeddings,
                collection_name="study_documents"
            )
            
            # Add new documents to existing store
            await vector_store.aadd_documents(chunks)
            print(f"[INFO] Added {len(chunks)} chunks to existing vector store")
            
        except Exception as e:
            # If loading fails, create a new vector store
            print(f"[INFO] Creating new vector store: {str(e)}")
            vector_store = await Chroma.afrom_documents(
                documents=chunks,
                embedding=embeddings,
                persist_directory=ds_name,
                collection_name="study_documents"
            )
            print(f"[INFO] Created new vector store with {len(chunks)} chunks")
        
        # Get total count
        total_chunks = vector_store._collection.count()
        print(f"[INFO] Vector store now contains {total_chunks} total chunks")
        
    except Exception as e:
        print(f"[ERROR] Failed to add documents to vector store: {str(e)}")
        raise

@cl.on_chat_end
async def end():
    """Clean up MCP server connection when chat session ends."""
    mcp_server_instance = cl.user_session.get("mcp_server")
    if mcp_server_instance:
        try:
            await mcp_server_instance.__aexit__(None, None, None)
            print("[INFO] MCP server connection closed successfully")
        except Exception as e:
            print(f"[WARNING] Error closing MCP server (this is usually harmless): {e}")
            pass
        finally:
            cl.user_session.set("mcp_server", None)




if __name__ == "__main__":
    import subprocess

    # Run Chainlit app on port 8001 with watch mode
    subprocess.run([
        "uv", "run", "python", "-m", "chainlit", "run", "chainlit_app.py",
        "--port", "8001", "-w"
    ])