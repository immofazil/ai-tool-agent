# Secure AI Tool Agent: Full-Stack MCP Architecture

### 🌐 Live Deployment
**Live Demo:** 

## 🚀 What It Is
This project is a production-ready, full-stack AI agent application. It connects a responsive web frontend to a secure, rate-limited FastAPI backend gateway. 

Instead of hardcoding functions directly into the agent, the backend orchestrates an external **Model Context Protocol (MCP)** tool server. This architecture allows the LLM to dynamically discover, select, and execute external Python operations (like complex math calculations) safely inside a sandboxed environment while maintaining multi-turn conversational memory.

## 🏗️ Architecture Diagram

graph TD
    A[Web Browser / Frontend] -->|HTTPS POST + Auth Token| B[FastAPI Gateway]
    B -->|Rate Limit & Validation| C[Agent Orchestrator]
    C -->|Context & Prompts| D[LLM Brain]
    C -->|MCP Client Handshake| E[MCP Tool Server]
    E -->|Executes Python Tools| F[Local Compute]
    F -->|Results| E
    E -->|JSON Response| C
    C -->|Final Answer| B
    B -->|JSON Payload| A

---

## 📁 Repository Structure

AI-TOOL-AGENT/
├── docs/                   # System Documentation
│   ├── deployment.md       # Cloud deployment instructions
│   ├── mcp-client.md       # Agent orchestration logic
│   ├── mcp-server.md       # Tool creation and exposure
│   └── security.md         # Rate limiting and auth breakdown
├── frontend/               # User Interface Layer
│   └── index.html          # Chat UI and asynchronous fetch logic
├── mcp/                    # Core Protocol & Tool Logic
│   ├── mcp_agent.py        
│   ├── mcp_client.py       
│   └── mcp_server.py       
└── server/                 # FastAPI Gateway Architecture
    └── backend_api.py      # Main unified gateway server


## 💻 How to Run Locally

To run this full-stack application on your own machine, you must boot the backend and frontend concurrently in two separate terminal windows.

### 1. Install Dependencies

Ensure you have the required Python packages installed:

```bash
pip install fastapi uvicorn pydantic

```

### 2. Start the Backend API Gateway (Terminal 1)

Boot the Uvicorn server, which automatically initializes rate limiters, CORS middleware, and custom exception handlers.

```bash
python -m uvicorn server.backend_api:app --host 0.0.0.0 --port 8000

```

### 3. Start the Frontend Server (Terminal 2)

Open a new terminal window to serve the static frontend assets.

```bash
cd frontend
python -m http.server 3000

```

Access the application dashboard by opening your web browser to `http://localhost:3000`.

## 🔒 Authentication

The API is secured behind a Bearer Token authorization layer. Any request missing a valid token, or providing an incorrect one, will be immediately rejected with an HTTP `401 Unauthorized` status.

* **Valid Test Tokens:** `super_secret_token_A` or `super_secret_token_B`
* **Header Format:** `Authorization: Bearer <token>`

## 📡 Protected API Endpoints

### `POST /chat`

The primary gateway for interacting with the MCP agent.

* **Rate Limits:** Enforces a maximum velocity of 5 requests per minute per user. Exceeding this limit returns a `429 Too Many Requests` error.
* **Input Constraints:** Enforces strict strict schema validation. Messages must be strings between 1 and 500 characters. Violations return a `422 Unprocessable Entity` error.

**Example Request Payload:**

```json
{
  "message": "calculate 95-20",
  "conversation_id": "session_xyz_123"
}

```

**Example Response Payload:**

```json
{
  "answer": "I triggered my calculator tool! The answer to 95 - 20 is 75.",
  "status": "success",
  "trace": ["Invoked secure agent pipeline"]
}
