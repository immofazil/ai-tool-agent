# Key Engineering Decisions

This document details the core architectural choices made during the development of the AI Tool Agent Gateway, outlining the rationale and trade-offs behind each decision.

---

### 1. Autonomous Agent Loop vs. Fixed Workflow

* **Decision**: Built an autonomous agent loop that chooses tools dynamically instead of using a hardcoded, step-by-step pipeline.
* **Why**: A fixed workflow executes the same sequence of actions regardless of the prompt. An agent reads the input, evaluates its options, and decides whether to answer directly, run a single tool, or chain multiple tools together.
* **Trade-off**: Gives up strict deterministic control over execution paths and increases latency because the model must make multiple evaluation passes.

---

### 2. Model Context Protocol (MCP) vs. Hardcoded Tools

* **Decision**: Adopted the Model Context Protocol pattern to expose tools using standardized schemas rather than embedding function logic directly inside the main application loop.
* **Why**: MCP decouples tool implementation from agent orchestration. Tools can be modified, expanded, or hosted on separate servers without editing or risking the core agent code.
* **Trade-off**: Adds slight structural complexity and small JSON serialization overhead compared to invoking local Python functions directly.

---

### 3. Bearer Token Auth & Rate Limiting vs. Open API

* **Decision**: Implemented Bearer token authentication alongside a 5 request per minute sliding-window rate limiter at the gateway level.
* **Why**: Unprotected LLM endpoints are vulnerable to unauthorized access, accidental client loops, and automated spam that can quickly drain API budgets.
* **Trade-off**: Adds per-request validation processing and requires frontend clients to store access passes and handle HTTP 429 rate limit responses gracefully.

---

### 4. SQLite Persistence vs. In-Memory Storage

* **Decision**: Used a file-based SQLite database (`agent_memory.db`) for conversation history instead of in-memory Python dictionaries.
* **Why**: In-memory storage is volatile and loses all active conversation states whenever the server reboots. SQLite keeps message histories safe across server restarts while maintaining multi-tenant separation using session keys.
* **Trade-off**: SQLite locks the database file during write actions, which can cause performance bottlenecks under heavy concurrent traffic. When high concurrent write usage is reached, the database should be upgraded to PostgreSQL or Redis.

---

### 5. Automated Testing with LLM Mocking vs. Manual Testing

* **Decision**: Created an automated Pytest suite that mocks external LLM calls and uses temporary database fixtures.
* **Why**: Manual terminal testing is slow and unreliable. Mocking LLM responses allows the test suite to execute in milliseconds, verifying system routing, security guardrails, and database interactions without spending real API funds or dealing with unpredictable model outputs.
* **Trade-off**: Mocked tests confirm that internal code and logic work, but they do not test real model reasoning variations or live external network failures.

---