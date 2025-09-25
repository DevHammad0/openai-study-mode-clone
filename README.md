# OpenAI Study Mode Clone

> An intelligent AI tutoring system using Socratic teaching methods to guide students through personalized learning experiences.

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![OpenAI Agents SDK](https://img.shields.io/badge/OpenAI-Agents%20SDK-green.svg)](https://github.com/openai/agents-sdk)
[![MCP Protocol](https://img.shields.io/badge/MCP-Protocol-orange.svg)](https://modelcontextprotocol.io/)
[![Google Gemini](https://img.shields.io/badge/Google-Gemini-red.svg)](https://ai.google.dev/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

## Features

- **Socratic Teaching**: Guides learning through questions, not direct answers
- **Document Knowledge Base**: Vector-based semantic search through uploaded materials
- **Web Search Integration**: Real-time information retrieval for current topics
- **Interactive Web Interface**: Drag-and-drop file upload with real-time tool visualization
- **Docker Ready**: Complete containerization with development and production configurations

## Architecture

Two-container system with shared vector store:

```
├── frontend/          # Chainlit web app (Port 8001)
├── mcp-server/        # FastMCP server (Port 8000)
└── vector_store/      # Shared ChromaDB volume
```

## Quick Start

### Prerequisites
- [Docker](https://www.docker.com/get-started) and Docker Compose
- [Google Gemini API key](https://aistudio.google.com/apikey)

### Setup

1. **Clone and configure**:
   ```bash
   git clone https://github.com/DevHammad0/openai-study-mode-clone.git
   cd openai-study-mode-clone
   
   # Create environment files
   echo "GEMINI_API_KEY=your_api_key_here" > mcp-server/.env
   echo "GEMINI_API_KEY=your_api_key_here" > frontend/.env
   echo "MCP_SERVER_URL=http://mcp-server:8000/mcp" >> frontend/.env
   ```

2. **Start the application**:
   ```bash
   # Production
   docker-compose up -d
   
   # Development (with hot reload)
   docker-compose -f docker-compose.yml -f docker-compose.override.yml up
   ```

3. **Access**: `http://localhost:8001`

## Usage

1. **Upload documents**: Drag and drop `.txt` or `.md` files
2. **Start learning**: AI tutor will introduce itself and assess your level
3. **Ask questions**: Receive guided responses with real-time tool visualization

### Source Control

- **Document-only**: `"Explain X, answer only from document"`
- **Web search**: `"What are the latest developments in AI?"`
- **Mixed (default)**: `"Help me understand machine learning"`

## Docker Management

```bash
# Start/stop services
docker-compose up -d
docker-compose down

# View logs
docker-compose logs -f

# Rebuild containers
docker-compose build --no-cache

# Check status
docker-compose ps
```

## Development

### Docker Development (Recommended)
```bash
# Start with hot reload
docker-compose -f docker-compose.yml -f docker-compose.override.yml up

# View logs
docker-compose logs -f
```

### Local Development
```bash
# MCP Server
cd mcp-server && uv sync && uv run server.py

# Frontend (new terminal)
cd frontend && uv sync && uv run chainlit_app.py
```

## Troubleshooting

### Common Issues

**Container fails to start**
- Check Docker daemon: `docker info`
- View logs: `docker-compose logs [service-name]`

**Port already in use**
- Stop services: `docker-compose down`
- Check ports: `netstat -tulpn | grep :8000`

**API key not working**
- Verify key at [Google AI Studio](https://aistudio.google.com/apikey)
- Restart containers: `docker-compose restart`

**Document upload fails**
- Check internet connection (needed for embeddings)
- Verify API quota limits
- Only `.txt` and `.md` files supported

## Resources

- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Google Gemini](https://ai.google.dev/)
- [Docker](https://www.docker.com/)
- [Chainlit](https://chainlit.io/)

---

**Built with ❤️ for better learning experiences**

[LinkedIn](https://linkedin.com/in/devhammad0/)