
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