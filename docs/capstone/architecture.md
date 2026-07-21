# System Architecture

This document describes the flow of data through the AI Tool Agent Gateway, detailing how user requests move from the web interface to backend tools and persistent storage.

## End-to-End Data Flow

User Request -> Frontend Interface -> API Gateway (Auth & Rate Limit) -> Agent Orchestrator -> MCP Tool Layer -> SQLite Persistence -> User Response

---

## Project Directory Structure
src/
├── client/
│   ├── index.html
│   └── app.js
└── server/
    ├── database.py
    ├── main.py
    └── mcp_tools.py


## Architectural Layers

### 1. Frontend Interface (`src/client/`)
The frontend provides a web interface using HTML and JavaScript that communicates with the backend asynchronously using fetch requests. It manages UI state, captures user input, and appends unique conversation IDs and Bearer tokens to every request. This ensures that the page updates smoothly without unexpected reloads while providing user feedback for visual tool badges and system errors.

### 2. Secured API Gateway (`src/server/main.py`)
Built with FastAPI, the API gateway serves as the primary entry point and security shield for all incoming traffic. It enforces Bearer token authentication, applies a sliding-window rate limit of 5 requests per minute per IP, and manages CORS settings. The gateway validates request payloads, catches runtime errors safely, and outputs structured JSON telemetry logs for observability.

### 3. Agent Loop and Intent Router
The agent loop processes the incoming prompt and past conversation history to determine the necessary response strategy. Instead of following a rigid script, it dynamically evaluates whether it can answer directly or if it needs to trigger external execution tools. It manages context windows, enforces maximum step ceilings to prevent infinite loops, and formats payloads for tool execution.

### 4. MCP Tool Execution Layer (`src/server/mcp_tools.py`)
This layer houses external capabilities such as weather lookups, calculators, and database queries behind standardized function contracts. By adhering to Model Context Protocol standards, tools are decoupled from the main server logic and exposed using strict schemas. This structure ensures that tool failures or updates remain isolated without crashing the primary server process.

### 5. Persistent Memory Layer (`src/server/database.py`)
Conversation history is saved using a local SQLite database (`agent_memory.db`) to preserve state across multi-turn sessions. Every stored message is linked to a specific user ID and conversation ID to ensure privacy and data isolation. This persistence guarantees that chat context survives server restarts and crashes.

---