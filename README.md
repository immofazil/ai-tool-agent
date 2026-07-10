
# Autonomous Single-Tool AI Agent

An intent-driven, autonomous AI agent built with Python and powered by the `gemini-2.5-flash` model. Unlike traditional hardcoded pipelines where software runs in a fixed, predictable sequence, this system demonstrates a true agentic loop. It evaluates user intent dynamically and decides whether to route requests to a specialized local tool or handle the conversation entirely using its internal knowledge.

---

## About the Files

The repository is organized cleanly to separate configuration, dependencies, and core application logic:

* **`src/app.py`**: The heart of the application. It contains the core agent orchestration engine, the explicit manual execution loop, the local mock tool function (`get_current_weather`), error tracking layers, an exponential backoff decorator for handling API transient issues, and the interactive terminal execution context.
* **`.env`**: A protected configuration file that safely isolates sensitive environmental credentials (such as your API key) from your codebase.
* **`.gitignore`**: A vital Git utility instruction file specifying exactly which local files, virtual environments (`.venv`), temporary caches (`__pycache__`), and sensitive configuration parameters (`.env`) must never be tracked or leaked to your public GitHub remote workspace.
* **`requirements.txt`**: A standardized bill of materials listing the exact Python libraries and dependencies required to properly run the agent platform.

---

## Getting Started

### 1. Position Terminal Context
Ensure your active terminal is looking inside the root repository directory where your files are located:
```bash
cd ai-tool-agent

```

### 2. Install Dependencies

Install the required upstream Python packages using `pip`:

```bash
pip install -r requirements.txt

```

### 3. Configure Your Environment Variables

Create a file named `.env` in the root directory (`ai-tool-agent/`) and insert your configuration key variable exactly like this:

```env
# Gemini API Configuration Secrets
GEMINI_API_KEY=your_actual_api_key_here

# Logging Severity Filter Threshold (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO

```

---

## How to Obtain a Gemini API Key

To get your unique API access credential, follow these steps via Google AI Studio:

1. Navigate to the official portal at [Google AI Studio](https://aistudio.google.com/).
2. Sign in using your standard Google account credentials.
3. Locate and click the **"Get API key"** button (typically positioned on the upper left sidebar or main dashboard view).
4. Click on **"Create API key"**. You can choose to generate a key within a default project or link it to an existing Google Cloud project.
5. Copy the long generated alphanumeric string immediately.
6. Paste this string directly into your local `.env` file, replacing the placeholder text `your_actual_api_key_here`.

---

## Running the Agent Runtime

Once your dependencies are fully installed and your `.env` variables are completely loaded, initiate the manual prompt testing environment by running:

```bash
python src/app.py

```

### Observing Intent Decisions

Type different prompts manually into the loop to watch how the agent dynamically chooses its own path through production-ready JSON logs:

* **Tool Execution Path:** Entering `What is the weather in Dubai right now?` prompts the model to return a structured tool request, firing the local backend executor.
* **Direct Path:** Entering `What is SDLC?` causes the model to recognize that the weather tool is irrelevant, prompting it to bypass execution completely and reply directly using its native knowledge.

---

## Running the Multi-Tool Agent (Part 2)

Once your dependencies are fully installed and your `.env` variables are completely loaded, you can run the extended version of the agent. This script (`src/app-2.py`) expands the agent's capabilities to support three distinct tools (`get_weather`, `calculate`, and `search_notes`) running inside a continuous, multi-step execution loop.

To initiate the multi-tool manual testing environment, run:
```bash
python src/app-2.py

```

### Observing Multi-Step Intent Decisions

Type different prompts manually into the loop to watch how the agent autonomously chains multiple actions together or handles errors through production-ready JSON logs:

* **Sequential Multi-Tool Path:** Entering a complex prompt like: *“Check the weather in Dubai, multiply the temperature value by 2, and then search my notes for that specific calculated number.”* Watch the structured JSON logs cycle through three separate tools sequentially (`get_weather` -> `calculate` -> `search_notes`) as it builds its final answer from the previous step's data.
* **Error Handling & Backoff Path:** Try entering inputs with missing or messy arguments. Instead of crashing, the script uses robust error handling paired with an exponential backoff retry mechanism to gracefully catch API drops or bad parameters, safely recording the trace details inside your JSON log objects.

---

## Running the Hardened Multi-Tool Agent (Part 3)

Once your dependencies are fully installed and your `.env` variables are completely loaded, you can run the conversational version of the agent. This script (`src/app-3.py`) builds directly on top of the previous multi-tool agent by introducing a persistent chat loop, structured message history tracking, and an automated history-length guardrail to prevent context explosion.

To initiate the conversational manual testing environment, run:

```bash
python src/app-3.py

```

### Observing Multi-Turn Conversational Memory

Type different prompts manually into the loop to watch how the agent maintains memory across multiple turns, tracks external tool outputs, and utilizes its automated history guard while keeping the structured JSON logging and retry backoffs active:

* **Conversational History & Tool Path:** Try running a multi-turn conversation that requires the agent to remember context from earlier steps. For example, ask for the weather in Dubai, perform a calculation on that data, ask it to check your personal notes for safety thresholds, and then ask it to recall the original temperature from the beginning of the chat. The agent will successfully reference the rolling history script to answer accurately.
* **History Guard & Context Trimming:** As your conversation runs longer, watch the underlying system automatically enforce the history-length guard. Instead of allowing the text history to balloon and blow past the model's hard reading limit, the code will safely slice out the oldest messages to keep token costs low and prevent the application from crashing.

---

## Running the Conversational Multi-Tool Agent (Part 4)

Once your dependencies are fully installed and your `.env` variables are completely loaded, you can run the hardened version of the agent. This script (`src/app-4.py`) builds directly on top of the previous conversational multi-tool agent by introducing strict safety guardrails, pre-execution input validation, and an explicit iteration ceiling to eliminate runaway loops and secure the core application runtime.

To initiate the hardened manual testing environment, run:

```bash
python src/app-4.py

```

### Observing Hardened Safety Guardrails & Failure Paths

Type different prompts manually into the loop to observe how the newly fortified architecture intercepts errors, traces operational sequences, and safely shuts down malicious or broken loops while keeping the structured JSON logging active:

* **Max-Iteration Limit Guardrail:** Try lowering `max_iterations` to 1 in your script and giving the agent a multi-step prompt that requires chaining tools together (e.g., asking to fetch weather, calculate a value, and search notes). You will watch the custom loop limit slam the door shut mid-run, instantly cutting off the agent to protect you from runaway API bills and infinite loops.
* **Pre-Execution Input Validation & Fallbacks:** Try triggering an edge-case error like forcing a division by zero or calling a tool with completely blank parameters. Instead of letting the underlying Python functions crash the entire program, the script will gracefully intercept the bad arguments, document the validation fault in the logs, and return a clean, user-friendly failure message rather than a massive, ugly raw stack trace.
* **Traceable Agent Sequence Logs:** Watch your terminal window closely during a tool run to see a completely clear "flight recorder" trace in action. Every single routing choice, tool call, and back-and-forth decision is tagged with structured sequence steps (e.g., Trace Step 1, Trace Step 2) for bulletproof system observability and easy debugging.
* **Network Resilience & Backoff Recovery:** Try pressing enter on a normal prompt and immediately disconnecting your Wi-Fi for a couple of seconds. The exponential backoff retry mechanism will seamlessly step in, catch the temporary connection drop, print out clear warning traces, and finish the job the exact moment your internet kicks back on without dropping the execution context.

---

## Running the MCP Client (Week 5 — Part 1)

Once your dependencies are fully installed and your `.env` variables are completely loaded, you can run the decoupled, protocol-based version of the agent. This script (`src/mcp_client.py`) implements the **Model Context Protocol (MCP)** to completely separate the main agent orchestration loop from the actual tool execution code.

Instead of hardcoding tools directly inside the script, the application acts as an independent host client that connects to an external, sandboxed server over a secure standard input/output (`stdio`) communication pipe.

### 1. Install Protocol Dependencies

To guarantee stable, bidirectional background communication on Windows without standard stream buffering issues, this project uses the official Python-native fetch server package. Install the protocol SDK extensions using `pip`:

```bash
pip install mcp mcp-server-fetch

```

### 2. Launch the Client Runtime

To initialize the protocol communication loop and trigger the automated discovery pipeline, run:

```bash
python src/mcp_client.py

```

### Observing Decoupled Protocol Cycles

Monitor your terminal window closely to observe how the protocol abstracts capabilities away from the core agent engine through structured JSON logs:

* **Automated Handshake Sequence:** The client uses your local Python interpreter to spin up the external fetch server module as an isolated background subprocess, instantly establishing a bidirectional communication stream.
* **Dynamic Tool Discovery:** The client queries the external server to dynamically inspect its capabilities on the fly. The server responds with its structured JSON schemas, exposing the `["fetch"]` tool definition without it ever being written into your client codebase.
* **Sandboxed Tool Call & Resolution:** The client dispatches a live data extraction request targeting `https://example.com`. The download happens entirely inside the isolated background server process, which safely reads the web content and passes the text payload back across the pipe to the client.
* **Recursive Error Unwrapping:** If a background asynchronous task fails, a custom diagnostic routine automatically intercepts the failure and recursively unwraps Python's nested `ExceptionGroup` layers, forcing the true root-cause error string to print directly into your console logs.

---


## Running the Custom MCP Server (Week 5 — Part 2)

Once your dependencies are fully installed, you can run your own custom Model Context Protocol (MCP) server. This script (`src/mcp_server.py`) implements a standalone tool server using the official Python MCP SDK, turning your core calculation and note-searching logic into standard, shareable infrastructure.

Instead of embedding tools directly inside a specific AI client application, this server sits independently and exposes its functional capabilities over a standard input/output (`stdio`) communication channel to any protocol-compliant host client.

### 1. Install Server Dependencies

To run the custom server host framework, ensure the standard protocol extensions are updated inside your local environment via `pip`:

```bash
pip install mcp

```

### 2. Launch via the MCP Inspector

Because this server relies entirely on standard streams (`stdio`), running it directly in a standard console will simply open an active listening stream. To automatically initialize the proxy environment and boot your python script directly inside the test engine, launch it with this command:

```bash
npx @modelcontextprotocol/inspector python src/mcp_server.py

```

Once the terminal initializes the session proxy, open the printed mnemonic web link (typically `http://localhost:6274`) in your browser. The connection panel will pre-fill, and hitting **Connect** will immediately bridge your live Python process to the visual interface.

---

## Observing Server Lifecycle and Guardrail Events

Monitor the browser dashboard and your terminal engine window to verify how the protocol handles execution routing through your server logic:

* **Automated Blueprint Exposure:** Clicking **List Tools** inside the inspector triggers the protocol to parse your Python docstrings and variable type hints, automatically building strict JSON schemas for `calculate` and `search_notes` without manual boilerplate coding.
* **Absolute File System Resolution:** Running the `search_notes` tool dynamically searches your local `notes.txt` file. The server logic uses an automatic directory look-ahead sequence to resolve the exact absolute file location, ensuring data is found regardless of where the client process is running.
* **Pre-Execution Guardrail Isolation:** Trying to input illegal character streams (like code injection attacks, alphabet letters inside math functions, or malformed formatting text) triggers your internal security checks. The script intercepts the validation failure cleanly and passes back a structured error JSON, blocking the attack vector completely without crashing the server process.
* **Stream-Safe Structured Logging:** Every incoming execution request, functional argument property, and final operational status is serialized into a clean JSON string. Because stdout is reserved for protocol data exchange, all structured logs are safely routed directly to standard error (`sys.stderr`), ensuring total system observability without breaking the communication pipe.

---

Here is the corrected, humanized `README.md` formatted to match your project's layout exactly, with the `.env` section removed and clear instructions on how to run both files simultaneously.

---

# MCP Agent Refactor & Orchestration (Week 5 — Part 3)

## Project Overview

This phase marks the successful refactoring of our Week 4 autonomous AI agent from a monolithic tool setup into a decoupled, client-server architecture powered by the **Model Context Protocol (MCP)**.

Instead of hardcoding functions locally within the core agent code, a brand new standalone tools server—`src/new_server.py`—was implemented to host application capabilities. On startup, the refactored agent (`src/mcp_agent.py`) establishes a network connection via a local Server-Sent Events (SSE) stream, dynamically discovers all available capabilities from the running server, and securely routes execution traffic down the protocol pipe.

---

## Architectural Workflow

```
[ User Prompt ] ──> [ src/mcp_agent.py ] ──( Handshake/Discovery )──> [ src/new_server.py ]
                           │                                                  │
                    ( Passes Schemas )                                  ( Hosts Tools )
                           ▼                                                  ▲
                  [ Gemini 2.5 Flash ] ──( Selection )──> [ Routes Request via RPC ]

```

1. **Discovery:** The agent connects to the live MCP tool server on boot, listing all registered tools dynamically.
2. **Schema Mapping:** Raw JSON-RPC tool declarations are cleanly mapped into schema definitions the model expects (automatically stripping out problematic metadata attributes such as `"title"` keywords).
3. **Execution Loop:** When a tool call is requested by the model, the agent intercepts the payload, translates it into an MCP execution parameter, calls the server, and returns the result to the chat session context.

---

## Technical Enhancements & Guardrails

* **Decoupled Architecture:** Switching from local streams to a local network service (SSE) prevents Windows terminal pipe collisions and keeps background tasks stable.
* **Week 4 Safety Limits:** Built-in loop recursion limits (`max_iterations=5`), robust structural input argument validation, and full JSON-formatted agent log traces remain highly enforced.
* **Resilient Exception Handlers:** Suppresses noisy library deprecation warnings and features an isolated crash-interception layer. If the server is offline or drops connection, the client gracefully falls back to a custom error display rather than leaking raw thread traces.


---

## How To Run the System

To execute the system successfully, you must run both components simultaneously in separate terminal windows:

### Step 1: Start the MCP Server

Open your first terminal window and launch the tool backend:

```bash
python src/new_server.py

```

*Leave this terminal open and running so it can listen for network traffic.*

### Step 2: Start the MCP Agent Client

Open a second terminal window and execute the main agent loop:

```bash
python src/mcp_agent.py

```

---


# MCP Agent Refactor & Orchestration (Week 5 — Part 4)

## Project Overview

This phase marks the successful transition of our autonomous AI agent into a production-ready, cloud-callable service by wrapping our Model Context Protocol (MCP) orchestrator inside a highly stable FastAPI web application.

Instead of trapping the agent inside an isolated terminal loop, it now lives behind a decoupled HTTP API. When a request is made, a custom asynchronous lifecycle application manager seamlessly handles starting the standalone backend tools server (`src/mcp_server.py`) as a sub-process, manages dynamic JSON-RPC schema normalization for the Gemini 2.5 Flash model, and routes execution traffic safely down the line.

---

## Technical Enhancements & Guardrails

* **Exposed Web Service Layer:** Shifting the system from a localized console prompt loop into a callable network endpoint enables language-agnostic integration across web dashboards or secondary microservices.
* **Resilient Data Interception:** Added custom Pydantic models alongside global exception middleware. Input failures are intercepted automatically, returning a standardized JSON body containing error details instead of crashing the process or throwing chaotic terminal tracebacks.
* **API Key Obfuscation:** Configured an asynchronous JSON log formatter to map runtime connection tracking metrics to the system output console while dynamically redacting sensitive environmental variables and authentication tokens.

---

## Endpoint Contract

### POST `/chat`

Submits a user prompt to the agent pipeline along with a tracking identifier to maintain multi-turn context memory.

#### Example Request

```json
{
  "message": "What is 41 * 2?",
  "conversation_id": "user_123"
}

```

#### Example Response (Success Case)

```json
{
  "answer": "41 * 2 is 82.",
  "status": "success",
  "trace": [
    "Invoked tool 'calculate' with args: {'expression': '41 * 2'}"
  ]
}

```

#### Example Response (Handled Error Case)

```json
{
  "error": "Malformed request. 'message' and 'conversation_id' are required strings.",
  "status": "failed"
}

```
---

## How To Run the System

To execute the system successfully, you only need to run a single unified command. The API gateway automatically manages spawning the background MCP tool worker processes for you.

### Step 1: Install Dependencies

Ensure you have the required web routing tools configured in your local environment workspace:

```bash
pip install fastapi uvicorn pydantic

```

### Step 2: Start the Service API Gateway

Launch the application server directly using the Python module executor flag:

```bash
python -m uvicorn src.api:app --host 0.0.0.0 --port 8000

```

Leave this terminal window open. The server will boot the tools backend instantly and begin listening for incoming client requests on port 8000.

---

# API Security and Authentication (Week 6 - Part 1)

## Project Overview

This phase marks the successful hardening of our autonomous AI agent gateway by introducing a robust security layer to our FastAPI web application. Building directly on top of our previous architecture, this upgraded functionality lives inside a brand new file called `src/secure_api.py` to keep our original code perfectly intact.

Instead of leaving our endpoints wide open to the public web where anyone could drain our API budget or sneak a peek at private data, the system now sits behind a strict authentication barrier. Every incoming network request is verified on the fly, ensuring that only authorized callers can interact with the agent pipeline and that user conversation data is completely sandboxed.

---

## Technical Enhancements & Guardrails

* **Token Based Authentication Gatekeeper:** Implemented FastAPI's native HTTPBearer scheme to intercept all incoming traffic, validating bearer tokens against a verified list of user identities before allowing requests to reach the core agent loop.
* **User Scoped Memory Vault:** Completely refactored the conversation dictionary into a deeply nested structure isolated by user ID. This ensures absolute data privacy, making it physically impossible for User A to read or guess the history of User B.
* **PowerShell Error Tamer:** Built a custom exception handler that captures missing or invalid token failures internally. It overrides default error handling to return a clean, structured JSON payload, preventing client terminals from throwing massive blocks of messy red exception text.
* **Secure Telemetry Redaction:** Formatted our structured JSON logs to track authentication milestones smoothly while completely redacting actual secret tokens and environmental variables from the console output.

---

## How To Run the System

To execute the secured system successfully, run the server using our new dedicated security entry point. The gateway will instantly spin up and manage all background protocol processes for you.

### Step 1: Install Dependencies

Ensure you have the required web routing and security tools configured in your local environment workspace:

```bash
pip install fastapi uvicorn pydantic

```

### Step 2: Start the Secure Service API Gateway

Launch the application server directly using the Python module executor flag targeting our new security script:

```bash
python -m uvicorn src.secure_api:app --host 0.0.0.0 --port 8000

```

Leave this terminal window open. The server will boot instantly, activate its custom exception handlers, and begin listening for incoming authorized client requests on port 8000.

### Step 3: Send Requests from a Second Terminal

Because the API server must remain actively running in your first terminal window to listen for incoming traffic, you need to open a brand new, completely separate terminal window to execute your testing or client commands.

Once your second terminal window is open, you can send authorized requests to the running gateway using PowerShell or curl:

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/chat" -Method Post -Headers @{Authorization="Bearer super_secret_token_A"} -ContentType "application/json" -Body '{"message": "Hello agent!", "conversation_id": "test_chat"}' | Format-List

```

---

# API Hardening and Rate Limiting (Week 6 - Part 2)

## Project Overview

This phase upgrades our authenticated API gateway into a resilient, production-ready defense system. Building directly on top of yesterday's authentication layer, this new iteration lives in a dedicated `src/hardened_api.py` file to preserve our previous checkpoints.

Instead of just checking if a user has the right password, the system now actively defends itself against resource exhaustion and malformed payloads. By implementing strict rate limits, rigid input validation, and browser security policies, the API ensures that authorized users cannot accidentally (or intentionally) crash the server, drain the LLM budget, or inject massive text walls.

---

## Technical Enhancements & Guardrails

* **Per-User Rate Limiting:** Engineered a time-based memory store that tracks request velocity mapped specifically to verified user IDs. The system throttles traffic exceeding 5 requests per minute, instantly returning a clean HTTP 429 Too Many Requests error to protect backend compute costs.
* **Strict Input Validation:** Leveraged Pydantic to enforce rigid schema constraints before data ever reaches the agent. The gateway automatically rejects empty payloads and strictly caps message lengths at 500 characters, returning an HTTP 422 Unprocessable Entity error for malformed requests.
* **CORS Configuration (Browser Prep):** Implemented Cross-Origin Resource Sharing (CORS) middleware to explicitly whitelist trusted web frontend origins (like `localhost:3000`). This ensures modern browsers will permit our future web dashboard to communicate with the backend while blocking unknown domains.
* **Graceful Error Telemetry:** Upgraded our global exception handlers so that rate limits and input violations are intercepted internally. The system returns structured JSON errors to the client and logs secure, single-line warnings to the console without ever leaking chaotic Python stack traces.

---

## How To Run the System

To execute the secured system successfully, you must run the server in one terminal and send your commands from another. The gateway will automatically manage the background protocol processes and defensive middleware.

### Step 1: Install Dependencies

Ensure you have the required web routing and security tools configured in your local environment workspace:

```bash
pip install fastapi uvicorn pydantic

```

### Step 2: Start the Hardened Service API Gateway

Launch the application server directly using the Python module executor flag targeting our new hardened script:

```bash
python -m uvicorn src.hardened_api:app --host 0.0.0.0 --port 8000

```

Leave this first terminal window open and running. The server will boot instantly, activate its custom exception handlers and rate limiters, and begin listening for incoming traffic on port 8000.

### Step 3: Send Requests from a Second Terminal

Because the API server must remain actively running in your first terminal window to listen to network traffic, you need to open a brand new, completely separate PowerShell terminal window to execute your client commands.

Once your second terminal window is open, you can send authorized requests to the running gateway using `curl.exe` (to ensure clean JSON error formatting without PowerShell's default red exceptions):

```powershell
curl.exe -X POST http://localhost:8000/chat -H "Authorization: Bearer super_secret_token_A" -H "Content-Type: application/json" -d "{\`"message\`": \`"Hello agent!\`", \`"conversation_id\`": \`"test_chat\`"}"

```

---

# Web Frontend Integration and Multi-Turn Tool Chat (Week 6 - Part 3)

## Project Overview

This phase successfully transitions our secure, hardened backend service into an accessible web product by introducing a dynamic user interface. Building directly on top of our previous architectural checkpoints, this implementation establishes a complete full-stack connection between a web browser client and our secured API gateway.

Instead of hiding our AI agent behind a command-line terminal, the system now features an interactive chat dashboard. Users can easily pass security keys, send prompts, watch the agent trigger math tools dynamically, and track multi-turn conversation memory seamlessly inside a clean, modern visual environment.

---

## Technical Enhancements & Guardrails

* **Browser-to-API Client Pipeline:** Developed an asynchronous communication engine using the native JavaScript `fetch` API. It securely passes headers across local network origins, dispatches user payloads, and paints incoming JSON answers to the browser viewport on the fly.
* **Persistent Conversational Memory State:** Built a frontend memory engine that dynamically tracks a unique `conversation_id`. It continuously appends this identifier to every out-going payload, allowing the backend to review historical message logs and maintain context for follow-up questions.
* **Asynchronous UX Loading Engine:** Engineered an active typing indicator that visually alerts users when the agent is computing logic or triggering tools in the background, locking down input boundaries to ensure users cannot distort request queues.
* **Intelligent Error Mapping:** Wired up status checking logic inside the browser client that intercepts raw HTTP codes (like 401 Unauthorized, 422 Validation Faults, or 429 Throttling). It swaps out confusing network failures for highly readable, friendly alert banners.

---

## How To Run the System

To launch the full-stack product, you must boot up both the backend API server and the frontend web server concurrently across separate terminal sessions. This separation satisfies modern browser security guidelines.

### Step 1: Ensure Backend API Dependencies Are Installed

Confirm your environment has all necessary modules for web routing, schemas, and security processing before running:

```bash
pip install fastapi uvicorn pydantic

```

### Step 2: Boot Up the Secure Backend API Gateway

Open your first terminal window, enter your root project workspace, and start your unified backend server using the module flag:

```bash
python -m uvicorn src.backend_api:app --host 0.0.0.0 --port 8000

```

Keep this terminal window running. The server activates its lifespan protocols, initializes rate limits, configures explicit CORS permissions for `localhost:3000`, and listens for browser calls on port 8000.

### Step 3: Launch the Frontend Web Server

Because modern browsers enforce strict Cross-Origin Resource Sharing (CORS) rules, double-clicking your HTML file locally will cause connection blocks. You must serve your frontend files properly through a dedicated origin web server.

Open a completely new, separate terminal window, navigate into your local frontend development directory, and spin up an independent Python local web instance:

```bash
cd frontend
python -m http.server 3000

```

### Step 4: Open Your Web Browser

With both terminal services running side by side, open any modern web browser and navigate directly to your local web deployment:

```http
http://localhost:3000

```

The graphical client interface will load immediately, letting you interact naturally with your secured agent while background validation, multi-turn tool logic, and defensive rate-limiting mechanisms execute invisibly behind the scenes.

---