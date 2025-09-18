# OpenAI Study Mode Clone

> An intelligent AI tutoring system that uses Socratic teaching methods to guide students through personalized learning experiences.

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![OpenAI Agents SDK](https://img.shields.io/badge/OpenAI-Agents%20SDK-green.svg)](https://github.com/openai/agents-sdk)
[![MCP Protocol](https://img.shields.io/badge/MCP-Protocol-orange.svg)](https://modelcontextprotocol.io/)
[![Google Gemini](https://img.shields.io/badge/Google-Gemini-red.svg)](https://ai.google.dev/)

## 🎯 Overview

This project implements an AI-powered study assistant that follows Socratic teaching principles. Instead of providing direct answers, it guides students through questions and hints to help them discover solutions themselves. The system combines document-based knowledge retrieval with real-time web search capabilities.

### Key Features

- **Socratic Teaching Method**: Guides learning through questions rather than providing direct answers
- **Document Knowledge Base**: Vector-based semantic search through uploaded materials
- **Web Search Integration**: Real-time information retrieval for current topics
- **Source Control**: Specify document-only or web search for targeted responses
- **Interactive Web Interface**: Drag-and-drop file upload with real-time tool visualization
- **MCP Architecture**: Modular design using Model Context Protocol
- **Google Gemini Powered**: Advanced language understanding and embeddings

## 🏗️ Architecture

The system consists of two main components:

```
openai-study-mode-clone/
├── frontend/           # Interactive web interface (Chainlit + OpenAI Agents)
│   ├── chainlit_app.py # Main web application with AI agent
│   └── pyproject.toml  # Dependencies and configuration
└── mcp-server/         # Knowledge and search server (FastMCP)
    ├── server.py       # MCP server with tools and prompts
    ├── utils.py        # Web search and content fetching utilities
    └── pyproject.toml  # Dependencies and configuration
```

### Component Details

**Frontend (Web Interface)**
- Built with Chainlit + OpenAI Agents SDK
- Interactive web application with AI tutoring agent
- Document upload with drag-and-drop support (`.txt` and `.md` files)
- Real-time tool call visualization and session persistence
- Automatic vector store management

**MCP Server**
- FastMCP-based server providing tools and prompts
- Connects to shared vector store for document search
- DuckDuckGo web search integration with rate limiting
- System prompt management for Socratic teaching mode
- Stateless design - no local document storage

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- [uv package manager](https://github.com/astral-sh/uv)
- Google Gemini API key

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/DevHammad0/openai-study-mode-clone.git
   cd openai-study-mode-clone
   ```

2. **Set up MCP Server**:
   ```bash
   cd mcp-server
   uv sync
   
   # Create .env file
   echo "GEMINI_API_KEY=your_gemini_api_key_here" > .env
   
   # Start MCP server
   uv run server.py
   ```

3. **Set up Frontend** (in a new terminal):
   ```bash
   cd frontend
   uv sync
   
   # Create .env file
   echo "GEMINI_API_KEY=your_gemini_api_key_here" > .env
   echo "MCP_SERVER_URL=http://localhost:8000/mcp" >> .env
   
   # Run the web application
   uv run chainlit_app.py
   ```
   Access at `http://localhost:8001`

### Getting Your Google Gemini API Key

1. Visit [Google AI Studio](https://aistudio.google.com/apikey)
2. Create a new API key
3. Add it to your `.env` files in both directories

## 💡 Usage

1. **Access the application**: Open `http://localhost:8001` in your browser
2. **Upload documents**: Drag and drop `.txt` or `.md` files to add to knowledge base
3. **Start learning**: The AI tutor will introduce itself and ask about your learning level
4. **Interactive sessions**: Ask questions and receive guided responses
5. **Real-time feedback**: Watch tool calls and document searches in real-time

### Source Control

Control which information sources the agent uses:

**Document-Only Responses:**
```
"Explain prompt engineering, answer only from document"
```

**Web Search for Current Information:**
```
"What are the latest developments in AI?"
```

**Mixed Sources (Default):**
```
"Help me understand machine learning"
```

> **Note**: Use "answer only from document" to restrict responses only from uploaded files only.

## 📚 Knowledge Base

The system uses a shared vector store that's managed entirely through the frontend interface.

### Adding Documents

**Web Interface:**
- Drag and drop `.txt` or `.md` files into the Chainlit web interface
- Documents are automatically processed and added to the shared vector store
- The MCP server will immediately have access to new documents
- No manual rebuilding or server restart required

## 🚨 Troubleshooting

### Common Issues

**"No such file or directory: vector_store"**
- The vector store is created automatically when you upload your first document
- Simply upload a `.txt` or `.md` file through the web interface

**"GEMINI_API_KEY is not set"**
- Ensure your `.env` file exists in the correct directory
- Verify your API key is valid at [Google AI Studio](https://aistudio.google.com/apikey)

**"Connection refused" when running agent**
- Ensure MCP server is running on `http://localhost:8000`
- Check that both components have the correct environment variables

**Document upload fails**
- Verify internet connection (needed for Gemini API embeddings)
- Ensure sufficient disk space for ChromaDB
- **Check API quota limits** if using Gemini free tier (visit [Google AI Studio](https://aistudio.google.com/apikey) to check usage)
- Only `.txt` and `.md` files are supported

## 🛠️ Configuration

### MCP Server Settings

- **Host**: `127.0.0.1` (localhost only)
- **Port**: `8000`
- **Vector Store**: ChromaDB with Gemini embeddings
- **Chunk Size**: 900 characters with 100 character overlap

## 🔧 Development

### Project Structure

```
openai-study-mode-clone/
├── frontend/
│   ├── chainlit_app.py         # Main web application
│   ├── public/                 # Static assets (logos, themes)
│   ├── pyproject.toml          # Python dependencies
│   └── README.md               # Component documentation
├── mcp-server/
│   ├── server.py               # FastMCP server
│   ├── utils.py                # Web search utilities
│   ├── pyproject.toml          # Python dependencies
│   └── README.md               # Component documentation
├── vector_store/               # ChromaDB files (auto-generated)
└── README.md                   # This file
```


## 📖 Resources

- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) - Agent framework
- [Model Context Protocol](https://modelcontextprotocol.io/) - Server architecture
- [Google Gemini](https://ai.google.dev/) - Language model and embeddings
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [LangChain](https://langchain.com/) - LLM application framework

---

**Built with ❤️ for better learning experiences**

Connect with me: [LinkedIn](https://linkedin.com/in/devhammad0/)
