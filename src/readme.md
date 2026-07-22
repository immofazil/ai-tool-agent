Here is a clean, production-ready `README.md` file tailored specifically for your unified project structure. You can save this at the root of your repository (`ai-tool-agent/README.md`).

---

# AI Tool Agent Gateway & Client

A production-grade AI Agent Gateway built with **FastAPI** and a decoupled web interface. This architecture incorporates Bearer Token security, sliding-window rate limiting, persistent multi-turn SQLite conversation memory, Model Context Protocol (MCP) tool execution, and structured JSON telemetry logging.

---

## 📁 Repository Structure

```text
ai-tool-agent/
├── src/
│   ├── server/
│   │   ├── database.py       # SQLite persistence (session memory & history)
│   │   ├── mcp_tools.py      # Tool execution router (Weather, Calculator, DB Lookup)
│   │   └── main.py           # FastAPI entrypoint, middleware, security, & routes
│   ├── tests/
│   │   ├── test_gateway.py   # Tests the gateway
│   └── client/
│       ├── index.html        # Clean HTML5 chat client interface
│       └── app.js            # Frontend logic (Fetch API, DOM rendering, state handling)
├── docs/
│   └── capstone/
│       └── overview.md       # Architectural overview & project submission docs
└── README.md                 # Project documentation

```

---

## ✨ Features & Components

### 1. Server Capabilities (`src/server/`)

* **Security Guardrails:** Enforces Bearer Token authentication (`capstone-secret-token`) on protected routes.
* **Sliding-Window Rate Limiting:** Enforces a maximum of **5 requests per minute per IP** with clear HTTP 429 guardrail responses.
* **Persistent Memory:** Uses SQLite (`agent_memory.db`) to store multi-turn chat sessions and reconstruct conversation context.
* **MCP Tool Integration:** Automatically detects intent and executes external tool logic (`get_weather`, `calculator`, `database_lookup`).
* **Structured Observability:** Emits structured JSON logs for all request lifecycles, authentication attempts, and internal errors.
* **Telemetry Endpoints:** Exposes live operational metrics at `/metrics` and service status at `/health`.

### 2. Client Capabilities (`src/client/`)

* **Asynchronous Fetch Messaging:** Decoupled HTML/JS interface for real-time interactions without full page reloads.
* **Visual Tool Execution Badges:** Highlights when an external tool is invoked by the backend.
* **Guardrail Feedback:** Displays styled UI error states for 401 Unauthorized, 429 Rate Limit Exceeded, or network connectivity failures.

---

## 🚀 How to Run the Project

### Prerequisites

Make sure you have Python installed, then install the required dependencies:

```bash
pip install fastapi uvicorn pydantic

```

---

### Step 1: Start the FastAPI Backend Server

Run Uvicorn from the root directory using the module flag:

```bash
python -m uvicorn src.server.main:app --reload

```

* **Server URL:** `http://localhost:8000`
* **Health Check:** `http://localhost:8000/health`
* **Interactive API Docs:** `http://localhost:8000/docs`

---

### Step 2: Start the Frontend Client

Open a second terminal window, navigate to the `src/client` directory, and serve it via Python's HTTP server:

```bash
cd src/client
python -m http.server 3000

```

Open your browser and navigate to:
👉 **`http://localhost:3000`**

---

## 🧪 Testing the Integration

1. **Test Persistent Memory:**
* Type `Hello, my name is Alex`.
* Ask `What was my name?` to verify that the backend retrieves session history from SQLite.


2. **Test MCP Tool Execution:**
* Type `What is the weather in Dubai?` -> Triggers `get_weather` tool badge.
* Type `calc 45 * 2` -> Triggers `calculator` tool badge.


3. **Test Security Guardrails:**
* Modify the Bearer Token input field in the UI to an invalid string and click Send -> Triggers a **401 Unauthorized** error badge.
* Send more than 5 messages within 60 seconds -> Triggers a **429 Rate Limit Exceeded** guardrail message.