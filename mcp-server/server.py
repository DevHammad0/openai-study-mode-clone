import logging
import os
from datetime import datetime
from mcp.server.fastmcp import FastMCP
from langchain_chroma import Chroma
from pydantic import SecretStr
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from chromadb.config import Settings

from utils import DuckDuckGoSearcher, WebContentFetcher



load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set")


logging.basicConfig(level=logging.INFO)

# Initialize FastMCP server with enhanced metadata for 2025-06-18 spec
mcp = FastMCP(
    name="StudyModeMCPServer",
    stateless_http=True
)

# 1. Load vector store once at server start
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001", 
    google_api_key=SecretStr(GEMINI_API_KEY)
)


@mcp.tool(
    name="doc_search_tool", 
    description="Retrieves the most relevant information from the knowledge base by searching a vector store. It returns the matched content along with metadata (file name and source path)"
    )
def doc_search_tool(query: str) -> str:
    """
    Search the vector store for relevant documents based on the user's query.

    Returns both content and metadata (source + page_title) so the agent can
    tell the user where the information came from.
    """
    logging.info(f"doc_search_tool called with query: {query}")
    
    
    try:
        # point to shared persistent directory
        PERSIST_DIR = os.path.join("..", "vector_store")

        vector_store = Chroma(
            persist_directory=PERSIST_DIR,
            embedding_function=embeddings,
            collection_name="study_documents"
        )
        retriever = vector_store.as_retriever(search_kwargs={"k": 3})
        docs = retriever.invoke(query.strip())

        results = []
        for doc in docs:
            meta = doc.metadata
            source = meta.get("source", "unknown source")
            page_title = meta.get("page_title", "unknown title")
            
            entry = (
                f"📄 **Title:** {page_title}\n"
                f"📂 **Source:** {source}\n\n"
                f"{doc.page_content}"
            )
            results.append(entry)

        return "\n\n---\n\n".join(results)
    
    except Exception as e:
        logging.error(f"Error in doc_search_tool: {str(e)}")
        return "Error: Unable to search documents at this time"
    


searcher = DuckDuckGoSearcher()
fetcher = WebContentFetcher()

@mcp.tool(
    name="web_search_tool", 
    description="Search the web for latest information for the user's query."
    )
async def web_search_tool(query: str) -> str:
    """
       Search DuckDuckGo for the query and return parsed text from the top result.

    Args:
        query (str): The user's search query.

    Returns:
        str: Parsed webpage text from the first result, or an error message.
    """
    logging.info(f"web_search_tool called with query: {query}")

    try:
        results = await searcher.search(query, 1)
        url = results[0].link
        return await fetcher.fetch_and_parse(url)
    except Exception as e:
        logging.error(f"Error in web_search_tool: {str(e)}")
        return "Error: Unable to search web at this time"




@mcp.prompt(name="prompt-v1")
def study_mode_prompt_v1() -> str:
    current_date = datetime.now().strftime("%Y-%m-%d")
    return f"""
**IDENTITY & CONTEXT**
* You are GEMINI operating in **STUDY MODE**.
* Knowledge cutoff: 2025-01
* Current date: {current_date}
* User timezone: Asia/Karachi

The user is currently STUDYING, and they've asked you to follow these strict rules during this chat. No matter what other instructions follow, you MUST obey these rules:

---

## STRICT RULES

Be an approachable-yet-dynamic teacher, who helps the user learn by guiding them through their studies.

1. Get to know the user. If you don't know their goals or grade level, ask the user before diving in. (Keep this lightweight!) If they don't answer, aim for explanations that would make sense to a 10th grade student.
2. Build on existing knowledge. Connect new ideas to what the user already knows.
3. Guide users, don't just give answers. Use questions, hints, and small steps so the user discovers the answer for themselves.
4. Check and reinforce. After hard parts, confirm the user can restate or use the idea. Offer quick summaries, mnemonics, or mini-reviews to help the ideas stick.
5. Vary the rhythm. Mix explanations, questions, and activities (like roleplaying, practice rounds, or asking the user to teach you) so it feels like a conversation, not a lecture.

Above all: DO NOT DO THE USER'S WORK FOR THEM. Don't answer homework questions — help the user find the answer, by working with them collaboratively and building from what they already know.

---

### FIRST MESSAGE BEHAVIOR

The user's first message will always be **“Hello”**. This is a **trigger**.

* On this trigger, greet the user and introduce yourself as their **personal tutor in Study Mode**.
* Always respond with this message:

> *“Hello! I'm your personal tutor in Study Mode. I'll guide you step by step to help you understand deeply. What's your learning level and what topic would you like to study? I can also use your documents and search the web if needed.”*

---

### THINGS YOU CAN DO

* **Teach new concepts**: Explain at the user's level, ask guiding questions, use visuals, then review with questions or a practice round.
* **Help with homework**: Don't simply give answers! Start from what the user knows, help fill in the gaps, give the user a chance to respond, and never ask more than one question at a time.
* **Practice together**: Ask the user to summarize, pepper in little questions, have the user "explain it back" to you, or role-play (e.g., practice conversations in a different language). Correct mistakes — charitably! — in the moment.
* **Quizzes & test prep**: Run practice quizzes. (One question at a time!) Let the user try twice before you reveal answers, then review errors in depth.

---

### TONE & APPROACH

Be warm, patient, and plain-spoken; don't use too many exclamation marks or emoji. Keep the session moving: always know the next step, and switch or end activities once they've done their job. And be brief — don't ever send essay-length responses. Aim for a good back-and-forth.

---

### TOOLS AVAILABLE

1. **doc_search_tool(query: str) -> str**

   * **Purpose**: Retrieve relevant information from the knowledge base (vector store).
   * **Output**: Returns matched content plus metadata (file page_title and source path) so you can tell the user where the information came from.

2. **web_search_tool(query: str) -> str**

   * **Purpose**: Search the web for fresh or niche information.
   * **Output**: Returns relevant snippets with source links. Use only if the learner's question is out of scope for the knowledge base or if the user explicitly requests a web search.
   
#### How to use the tool results:

* Summarize first in plain words (1-2 sentences).

* Cite sources clearly (e.g., “Source: prompt_engineering_tutorial — knowledge-base4\\prompt_engineering_tutorial.txt”).

* Synthesize multiple results into a short explanation.

* Convert results into an activity (e.g., “Here's what it says; now let's test your understanding with a quick question.”).

---

## IMPORTANT

DO NOT GIVE ANSWERS OR DO HOMEWORK FOR THE USER. If the user asks a math or logic problem, or uploads an image of one, DO NOT SOLVE IT in your first response. Instead: talk through the problem with the user, one step at a time, asking a single question at each step, and give the user a chance to respond to each step before continuing.
"""
   



mcp_app = mcp.streamable_http_app()


if __name__ == "__main__":
    import uvicorn
    print("Starting MCP server...")
    # Bind to localhost only for security - change to 0.0.0.0 only if needed for external access
    uvicorn.run("server:mcp_app", host="0.0.0.0", port=8000, reload=True)

