# AI Agent Gateway

An enterprise-ready, production-ready AI Agent Gateway built with FastAPI. It connects a web frontend to dynamic Model Context Protocol (MCP) tools through strict security guardrails, including Bearer Token authentication, sliding-window rate limiting, session persistence, and system telemetry observability.

---

## 🌐 Quick Links & Documentation

* **Live Frontend UI (Hugging Face)**: [https://huggingface.co/spaces/immofazil/ai-agent-gateway](https://huggingface.co/spaces/immofazil/ai-agent-gateway)
* **Live Backend API (Render)**: [https://ai-tool-agent.onrender.com](https://ai-tool-agent.onrender.com)
* **Capstone Case Study**: [https://github.com/immofazil/ai-tool-agent/blob/main/docs/capstone/README.md](https://github.com/immofazil/ai-tool-agent/blob/main/docs/capstone/README.md)

---

## 🏗️ System Architecture

The gateway uses a split-architecture design separating UI, API orchestration, tool execution, and storage layers:

```text
[ Frontend UI (Static Space) ] 
              |
              v (HTTP + Bearer Token)
[ API Gateway (FastAPI Guardrails: Auth & Rate Limiter) ]
              |
              v
   [ Agent Orchestrator ]
        /            \
       v              v
[ MCP Tool Suite ]  [ SQLite Persistence ]

```

1. **Frontend Layer**: A lightweight HTML5 and JavaScript web application hosted on Hugging Face Spaces.
2. **API Gateway**: An asynchronous FastAPI service deployed on Render with Bearer Auth (`capstone-secret-token`) and a 5 requests per minute sliding-window rate limiter.
3. **MCP Tool Suite**: Standardized tool registry executing math operations and weather queries.
4. **Storage & Observability**: Local SQLite database for message persistence, plus a `/metrics` telemetry endpoint tracking API traffic and tool calls.

---

## 📁 Repository Structure

```text
AI TOOL AGENT
├── .env.example            # Environment configuration template
├── README.md               # Root repository documentation
└── requirements.txt        # Python dependencies
├── docs/                   # Documentation and resources for learning this project
│   └── capstone/           # Capstone case study materials
│       ├── screenshots/    # Evidence screenshots (Auth, Rate Limit, Tests, UI)
│       └── README.md       # Full 8-Week Capstone Case Study
├── frontend/               # Experimental folder (early learning, sandbox, and frontend testing)
├── mcp/                    # Experimental folder (early learning, sandbox, and MCP protocol testing)
├── server/                 # Experimental folder (early learning, sandbox, and backend testing)
└── src/                    # Primary Production Source Code
    ├── client/             # Production UI web application
    │   ├── app.js          # Web client logic and API requests
    │   └── index.html      # User interface
    └── server/             # Production FastAPI Backend Service
        ├── tests/
        │   └── test_gateway.py  # 7-part Pytest verification suite
        ├── agent_memory.db     # SQLite session database
        ├── database.py         # Database connection & models
        ├── main.py             # FastAPI entry point & guardrail middleware
        └── mcp_tools.py        # MCP tool definitions & execution registry

```

---

## ⚙️ Environment Configuration

Although internal MCP tools do not require external third-party API keys to execute, the server uses standard environment configuration settings.

A template file named `.env.example` is provided at the root:

```env
# Server Configuration
PORT=8000
DATABASE_URL=sqlite:///agent_memory.db

# Guardrail Tokens
API_BEARER_TOKEN=capstone-secret-token

```

---

## 🚀 Local Development & Setup

### Prerequisites

* Python 3.10+
* Virtual Environment (`venv`)

### 1. Install & Run Backend Server

Navigate to the server directory, install dependencies, and run the FastAPI server using Uvicorn:

```bash
# Navigate to server directory
cd src/server

# Install Python packages
pip install -r requirements.txt

# Launch FastAPI backend with Uvicorn
uvicorn main:app --reload --host 127.0.0.1 --port 8000

```

The API will now be accessible at `[http://127.0.0.1:8000](http://127.0.0.1:8000)`. You can test endpoints via the interactive Swagger documentation at `[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)`.

### 2. Run Automated Pytest Suite

To verify authentication, rate limiting, tool execution, session state, and metric logging:

```bash
# Run pytest from src/server directory
pytest tests/test_gateway.py -v

```

### 3. Run Frontend Web Client

Open `src/client/index.html` directly in any web browser, or serve it locally:

```bash
# Navigate to client directory
cd src/client

# Serve statically via Python
python -m http.server 3000

```

Then visit `http://localhost:3000` in your web browser.