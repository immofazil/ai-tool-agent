PRODUCTION-GRADE MCP-COMPLIANT AI AGENT WITH SQLITE PERSISTENCE

1. PROJECT OVERVIEW
-------------------
This project implements a lightweight, secure, and production-grade AI 
agent API using FastAPI, Pydantic, and SQLite. It provides persistent 
conversational memory across server restarts and enforces multi-tenant 
scoping to keep user chat histories completely isolated.

Key Features:
- FastAPI Backend: Lightweight RESTful service for handling chat interactions.
- SQLite Persistence: Uses 'agent_memory.db' to store turn-by-turn context.
- Multi-Tenant Scoping: Header tokens map requests to isolated user accounts.
- Input Validation: Pydantic schemas validate JSON request payloads.
- Complete Test Suite: Verification using PowerShell's Invoke-RestMethod.

2. PREREQUISITES & SETUP
------------------------
Make sure Python 3.10+ is installed on your system.

Step 1: Clone or open the repository directory in terminal/VS Code.

Step 2: Create a virtual environment (if not already created):
    python -m venv venv

Step 3: Activate the virtual environment:
    - On Windows (PowerShell):
        .\venv\Scripts\Activate.ps1
    - On macOS/Linux:
        source venv/bin/activate

Step 4: Install required dependencies:
    pip install fastapi uvicorn pydantic


3. HOW TO RUN AND TEST THE PROJECT (TWO-TERMINAL WORKFLOW)
----------------------------------------------------------
Testing persistent database memory and lifecycle events requires two separate 
terminal windows running concurrently.

--------------------------------------------------
TERMINAL 1: SERVER HOST (Uvicorn Server Process)
--------------------------------------------------
1. Open Terminal 1 and activate the virtual environment:
   .\venv\Scripts\Activate.ps1

2. Start the FastAPI server with auto-reload enabled:
   python -m uvicorn server.main:app --reload

   * The server will launch on http://127.0.0.1:8000
   * Real-time logs will display database initialization and incoming requests.

--------------------------------------------------
TERMINAL 2: CLIENT TERMINAL (Sending Requests)
--------------------------------------------------
1. Open Terminal 2 and activate the virtual environment:
   .\venv\Scripts\Activate.ps1

2. Run an initial request for a new session (e.g., session_103):
   (Invoke-RestMethod -Uri "http://127.0.0.1:8000/chat" `
                      -Method Post `
                      -Headers @{ "Authorization" = "Bearer super_secret_token_A" } `
                      -ContentType "application/json" `
                      -Body '{"conversation_id": "session_103", "message": "My favorite programming language is Python."}').answer

   * Expected Output: "Loaded 0 prior history records from SQLite database."

3. Simulate a server restart:
   - Go to Terminal 1, press CTRL+C to stop the uvicorn process.
   - Restart the server: python -m uvicorn server.main:app --reload

4. Test context persistence across the server restart (In Terminal 2):
   (Invoke-RestMethod -Uri "http://127.0.0.1:8000/chat" `
                      -Method Post `
                      -Headers @{ "Authorization" = "Bearer super_secret_token_A" } `
                      -ContentType "application/json" `
                      -Body '{"conversation_id": "session_103", "message": "What did I tell you my favorite language was?"}').answer

   * Expected Output: "Loaded prior history records from SQLite database." 
     This confirms the chat history was preserved in agent_memory.db across restarts.


4. EXITING THE ENVIRONMENT
--------------------------
To stop the server in Terminal 1: Press CTRL+C.
To deactivate the virtual environment in either terminal:
    deactivate


Day 2

FASTAPI AGENT AUTOMATED TESTING SUITE (PYTEST)

1. PROJECT OVERVIEW
-------------------
This project implements an automated, fast, zero-cost test suite using Pytest and 
FastAPI's TestClient for a hardened AI agent backend. The primary goal is to ensure 
system reliability, data security, rate limits, and persistence across critical application 
paths without incurring live LLM API costs.

Key Features & Test Coverage:
- Schema Guardrails: Validates input parameters and boundary limits via Pydantic.
- API Authentication: Enforces Bearer token security and 401 Unauthorized handling.
- Rate Limiting: Enforces sliding-window rate limit checks and 429 Too Many Requests responses.
- SQLite Persistence: Verifies sequential conversation turn storage and context reloading.
- Isolated Execution: Mocks LLM responses and resets state via Pytest fixtures for offline execution.


2. PROJECT STRUCTURE
--------------------
ai-tool-agent/
├── server/
│   ├── __init__.py          # Marks server as an importable package
│   └── main.py              # FastAPI application & SQLite database logic
├── tests/
│   └── test_main.py         # Pytest suite (7 critical path test cases)
├── agent_memory.db          # SQLite persistent database file
├── requirements.txt         # Project dependencies
└── README.txt               # Documentation file


3. PREREQUISITES & ENVIRONMENT SETUP
------------------------------------
Ensure Python 3.10 or higher is installed on your machine.

Step 1: Open the project root directory in your terminal or VS Code.

Step 2: Create a virtual environment (if not already created):
    python -m venv venv

Step 3: Activate the virtual environment:
    - On Windows (PowerShell):
        .\venv\Scripts\Activate.ps1
    - On macOS/Linux:
        source venv/bin/activate

Step 4: Install required dependencies:
    pip install fastapi uvicorn pydantic pytest httpx


4. HOW TO RUN THE AUTOMATED TEST SUITE
--------------------------------------
The test suite executes entirely offline in under two seconds.

1. Ensure your virtual environment is active:
    .\venv\Scripts\Activate.ps1

2. Run pytest from the project root directory:
    python -m pytest tests/ -v

3. Expected Output:
    tests/test_main.py::test_tool_argument_validation PASSED
    tests/test_main.py::test_max_iteration_guardrail PASSED
    tests/test_main.py::test_malformed_llm_response PASSED
    tests/test_main.py::test_chat_authenticated_success PASSED
    tests/test_main.py::test_chat_missing_credentials_401 PASSED
    tests/test_main.py::test_chat_rate_limit_429 PASSED
    tests/test_main.py::test_conversation_persistence PASSED

    ======== 7 passed in < 2.00s ========


5. SUMMARY OF TEST PROTECTIONS
------------------------------
- test_tool_argument_validation: Protects against malformed payloads by asserting 422 errors when required fields are missing.
- test_max_iteration_guardrail: Protects system boundaries by rejecting messages exceeding 500 characters with a 422 error.
- test_malformed_llm_response: Protects against empty input payloads, enforcing non-empty string validation.
- test_chat_authenticated_success: Protects the primary API route by confirming valid Bearer tokens return 200 OK responses.
- test_chat_missing_credentials_401: Protects API routes from unauthorized access by asserting 401 status on unauthenticated calls.
- test_chat_rate_limit_429: Protects against spam by blocking requests beyond 5 per minute with a 429 Too Many Requests response.
- test_conversation_persistence: Protects memory state by verifying turn history is correctly saved and loaded from SQLite.


6. EXITING THE ENVIRONMENT
--------------------------
To deactivate the virtual environment:
    deactivate