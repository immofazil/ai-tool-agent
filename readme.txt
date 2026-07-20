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