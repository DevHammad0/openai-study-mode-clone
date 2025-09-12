# Agent-Core Study Mode Agent

An intelligent tutoring agent that uses Socratic teaching methods. Built with OpenAI Agents SDK, connects to MCP servers, and powered by Google Gemini.

## Project Structure
```
parent-folder/
├── agent-core/          # This project
└── mcp-server/          # Your MCP server project
```

## Setup

### Prerequisites
- Python 3.13+
- UV package manager
- Google Gemini API key
- Running MCP server

### Installation

1. **Navigate to agent-core**:
   ```bash
   cd agent-core
   ```

2. **Install dependencies**:
   ```bash
   uv sync
   ```

3. **Environment variables**:
   Create `.env` file:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   MCP_SERVER_URL=your_mcp_server_url_here
   ```

## Usage

**Run the agent**:
```bash
uv run main.py
```

**Interactive commands**:
- Ask any question to start learning
- Type `exit` or `quit` to end session

## Configuration

**Session Storage**:
- Default: In-memory (lost on exit)
- Persistent: Uncomment line 32 in `main.py`

