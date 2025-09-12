# Study Mode MCP Server

A Model Context Protocol (MCP) server that provides document-based knowledge retrieval and web search capabilities for AI tutoring systems. This server enables agents to search through uploaded documents and the web while maintaining a guided learning approach.

## 🌟 Features

- **Document Knowledge Search**: Retrieves relevant information from uploaded documents using vector search
- **Web Search Integration**: Searches the web for current information via DuckDuckGo
- **Study Mode System Prompt**: Provides educational guidance system prompt for AI agents
- **Easy Document Upload**: Add any `.txt` file to knowledge base and rebuild vectors

## 📚 Current Knowledge Base

The server includes 3 educational documents:
- `context_engineering_tutorial.txt` - AI agent context engineering guide
- `prompt_engineering_tutorial.txt` - Comprehensive prompt engineering tutorial 

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- Google Gemini API key
- Internet connection (for DuckDuckGo web search)
- [uv](https://github.com/astral-sh/uv) package manager installed
```bash
  pip install uv
```

### Setup

1. **Install dependencies**:
```bash
uv sync
```

2. **Configure environment**:
```bash
# Create .env file with your API key
GEMINI_API_KEY=your_gemini_api_key_here
```

3. **Build vector store** (required first time and after adding documents):
```bash
uv run build_vector_store.py
```

4. **Start MCP server**:
```bash
uv run server.py
```

Server runs on `http://localhost:8000`

## 📄 Adding Documents

To add new documents to the knowledge base:

1. **Create a `.txt` file** in the `knowledge-base/` folder
2. **Paste your content** into the file
3. **Rebuild the vector store**:
```bash
uv run build_vector_store.py
```
4. **Restart the server**

> **Note**: For CLI version, document upload can be integrated into the frontend. Currently using manual file addition for simplicity.

## 🛠️ MCP Tools & Prompts

### Tools Available
1. **`doc_search_tool(query: str)`**
   - Searches uploaded documents using vector similarity
   - Returns relevant chunks with source metadata
   - Uses Google Gemini embeddings

2. **`web_search_tool(query: str)`**
   - Searches the web via DuckDuckGo (free, no API key needed)
   - Provides current information beyond knowledge base

### System Prompt
- **`prompt-v1`**: Study Mode system prompt for AI agents
  - Implements Socratic teaching methodology
  - Guides learning instead of providing direct answers
  - Used by agent-core as system prompt

### Technical Details
- **Vector Store**: ChromaDB with Gemini embeddings
- **Chunking**: 900 chars with 100 char overlap
- **Storage**: Local `vector_store/` directory

## 🔄 Development

### File Structure
```
mcp-server/
├── server.py                 # Main MCP server
├── build_vector_store.py     # Vector store builder
├── knowledge-base/           # Document storage
│   ├── context_engineering_tutorial.txt
│   ├── prompt_engineering_tutorial.txt
│   └── six_part_prompting_framework.txt
├── vector_store/             # ChromaDB storage (auto-generated)
```

### Workflow
1. Add documents → `knowledge-base/` folder
2. Build vectors → `uv run build_vector_store.py`
3. Start server → `uv run server.py`
4. Use tools in your AI agent via MCP protocol



## 🔑 API Keys

### Google Gemini API
- Visit [Google AI Studio](https://aistudio.google.com/apikey)
- Create API key → Add to `.env`

---

**Built with**: FastMCP, ChromaDB, LangChain, Google Gemini AI, DuckDuckGo Search
