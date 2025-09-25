# StudyMode Frontend

A **Chainlit web application** that provides an interactive tutoring interface with document upload capabilities and real-time chat with AI agents. Connects to the StudyMode MCP server for enhanced learning experiences.

## Features

- **Interactive Chat Interface** - Real-time conversation with AI tutor
- **Document Upload** - Drag-and-drop file upload with automatic vector store integration
- **Tool Call Visualization** - Real-time display of agent tool usage
- **Session Persistence** - Conversation history maintained across interactions

## Setup

1. **Install dependencies**:
```bash
uv sync
```

2. **Configure environment**:
```bash
# Create .env file with your API keys and MCP server URL
GEMINI_API_KEY=your_gemini_api_key_here
MCP_SERVER_URL=http://localhost:8000/mcp
```

3. **Start application**:
```bash
uv run chainlit_app.py
```

Application runs on `http://localhost:8001`

## File Upload

Users can upload documents through the web interface for automatic processing and knowledge base integration.

**Supported file types**: `.txt` and `.md` files only.
