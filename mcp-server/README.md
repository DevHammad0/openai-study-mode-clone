# StudyMode MCP Server

A **Model Context Protocol (MCP) server** for intelligent tutoring with knowledge base search and web search capabilities. Features a Socratic teaching approach that guides learners through discovery rather than providing direct answers.

## Tools

- **`doc_search_tool(query)`** - Search local knowledge base using semantic similarity
- **`web_search_tool(query)`** - Live DuckDuckGo search with content extraction

## Prompt

- **`prompt-v1`** - Study Mode tutoring system that adapts to learning levels, asks guiding questions, and provides step-by-step educational support

## Setup

1. **Install dependencies**:
```bash
uv sync
```

2. **Configure environment**:
```bash
# Create .env file with your API key
GEMINI_API_KEY=your_gemini_api_key_here
```

3. **Start server**:
```bash
uv run server.py
```

Server runs on `http://127.0.0.1:8000`

## Knowledge Base

Documents are automatically added to the vector store via the Chainlit frontend application. Users can upload files through the web interface, which handles document processing and vector store updates automatically.

