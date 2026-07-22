
# AI Agent Gateway - Capstone Project (Part 2)

An end-to-end, production-ready **AI Agent Gateway** built with FastAPI, implementing dynamic MCP tool execution, strict guardrails (Bearer Authentication & Rate Limiting), telemetry observability, and a modern web interface.

---

## 🌐 Live Deployment Links

* **Frontend UI (Hugging Face Static Space)**: [https://huggingface.co/spaces/immofazil/ai-agent-gateway](https://huggingface.co/spaces/immofazil/ai-agent-gateway)
* **Backend API (Render Web Service)**: [https://ai-tool-agent.onrender.com](https://ai-tool-agent.onrender.com)
* **Interactive API Documentation**: [https://ai-tool-agent.onrender.com/docs](https://ai-tool-agent.onrender.com/docs)

---

## 🏗️ Architecture & Component Breakdown

The project follows a decoupled, split-architecture model:

1. **Frontend Layer (`src/client/`)**:
   * Pure HTML5/JavaScript static client hosted on Hugging Face Spaces.
   * Handles user interaction, pre-filled Bearer token pass-through (`capstone-secret-token`), error/guardrail UI feedback, and execution badge rendering.

2. **Backend API Gateway (`src/server/`)**:
   * Asynchronous **FastAPI** service deployed on Render.

3. **Guardrail Engine**:
   * **Authentication**: Enforces Bearer Token HTTP Authorization headers (`HTTP_401_UNAUTHORIZED`).
   * **Rate Limiter**: Sliding-window rate limiting allowing a maximum of 5 requests per minute (`HTTP_429_TOO_MANY_REQUESTS`).
   * **Input Sanitization**: Rejects invalid payloads or empty messages (`HTTP_422_UNPROCESSABLE_ENTITY`).

4. **MCP Tool Suite (`mcp_tools.py`)**:
   * Modular Tool Registry featuring automated routing for mathematical operations, weather queries, and multi-tool orchestration.

5. **Observability & Health Telemetry**:
   * Real-time metrics endpoint (`/metrics`) tracking total incoming requests, rate-limit triggers, tool execution counts, and uptime latency.

6. **Automated Testing Suite (`tests/test_gateway.py`)**:
   * 7-part comprehensive `pytest` suite ensuring full coverage across authentication, guardrails, tool routing, session memory, and metrics logging.

---

## 📂 Project Structure

```text
AI TOOL AGENT
├── docs/
├── frontend/
├── mcp/
├── server/
└── src/
    ├── client/
    │   ├── app.js
    │   └── index.html
    └── server/
        ├── tests/
        │   └── test_gateway.py
        ├── agent_memory.db
        ├── database.py
        ├── main.py
        ├── mcp_tools.py
        └── requirements.txt

```

---

## 📸 Evidence & Validation Pack

All visual evidence proving full system functionality is embedded below and stored in the root repository:

### 1. Authentication Guardrail Test
Visual proof of HTTP 401 Unauthorized rejection when an invalid Bearer token is provided.
![Auth Rejection](auth_rejection.png)

### 2. Rate Limiting Guardrail Test
Demonstration of the 5 req/min rate limiter triggering an HTTP 429 response upon excess requests.
![Rate Limit 429](rate_limit_429.png)

### 3. Dynamic Multi-Tool Execution
Multi-tool query execution showing visual tool execution badges (`🛠️ Tool Executed`).
![Multi-Tool Run](multitool_run.png)

### 4. Full Frontend Chat Integration
Full live chat UI operating seamlessly on Hugging Face and connected to the Render backend.
![Frontend Chat](frontend_chat.png)

### 5. Telemetry & Health Endpoint
Raw JSON output from the `/metrics` endpoint showing real-time health telemetry.
![Health Metrics](health_metrics.png)

### 6. Automated Test Suite Verification
Terminal output displaying `7 passed` across all `pytest` validation cases.
![Test Suite Green](test_suite_green.png)


---

## 🚀 Local Development Setup

### 1. Requirements

* Python 3.10+
* Virtual Environment (`venv`)

### 2. Installation & Run Backend

```bash
# Navigate to server directory
cd src/server

# Install dependencies
pip install -r requirements.txt

# Launch FastAPI backend with Uvicorn
uvicorn main:app --reload --host 127.0.0.1 --port 8000

```

### 3. Running the Test Suite

```bash
# Run pytest from src/server directory
pytest tests/test_gateway.py -v

---