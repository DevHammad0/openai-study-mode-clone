from agents import Agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI, trace, SQLiteSession, gen_trace_id, set_tracing_disabled, run_demo_loop
import agents
from agents.mcp import MCPServer, MCPServerStreamableHttp
from agents.items import TResponseInputItem, TResponseOutputItem
from dotenv import load_dotenv
import asyncio
import os

# set_tracing_disabled(True)

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


# Create a session instance with a session ID
# In-memory database (lost when process ends)
session = SQLiteSession("session_1")

## Persistent file-based database
# session = SQLiteSession("session_1", "conversations.db")


async def run_agent(mcp_server: MCPServer, instructions: str, session: SQLiteSession | None = None):
    agent = Agent(
            name="Assistant", 
            instructions=instructions,
            model=OpenAIChatCompletionsModel(
                model="gemini-2.5-flash",
                openai_client=client,
            ),
            mcp_servers=[mcp_server]
        )
    trace_id = gen_trace_id()
    print(f"\nView trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\n")
    
    with trace("StudyMode Clone Workflow", trace_id=trace_id): 
        result = await Runner.run(agent, "Hello", session= session)
        print(f"[AGENT]: {result.final_output}\n\n")

        while True:
            user_input = input("[USER MESSAGE]: ")
            if user_input in ["exit", "quit"]:
                break
            result = await Runner.run(agent, user_input,session= session)
            print(f"\n\n[AGENT]: {result.final_output}")
        



async def main():
    async with MCPServerStreamableHttp(
        name="StudyMode StreamableHttp Server", 
        params={"url":f"{mcp_server_url}"},
        cache_tools_list=True
        ) as mcp_server:
        
        prompt_result = await mcp_server.get_prompt("prompt-v1")
        # Extract the actual prompt text from the GetPromptResult object
        if prompt_result.messages and len(prompt_result.messages) > 0:
            # Get the first message's content
            first_message = prompt_result.messages[0]
            if hasattr(first_message.content, 'text'):
                instruction_text = first_message.content.text
            elif isinstance(first_message.content, str):
                instruction_text = first_message.content
            else:
                instruction_text = str(first_message.content)
        else:
            instruction_text = "No prompt text found"
        
        # print(instruction_text)
        await run_agent(mcp_server, instructions=instruction_text, session=session)
        
        
        
if __name__ == "__main__":
    asyncio.run(main())
        
    
        