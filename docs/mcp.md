# Day 1 - Why MCP? From Local Tools to a Standard Protocol

## What MCP Is and Why It Exists

Before the Model Context Protocol (MCP) came along, building AI capabilities felt like reinventing the wheel every single time. Every agent had hardcoded tools stuck inside its own code, meaning there was absolutely no reuse or shared standards between different projects. If you wrote a great custom feature for one app, you had to manually copy, paste, and rewrite it for the next.

MCP completely changes this by standardizing exactly how an agent discovers and calls tools exposed by an external server. It gives us a universal protocol so any agent host can seamlessly query a server to see what it can do and then run those functions safely. The framework relies on three core primitives: prompts as text templates, resources as static background context, and tools as dynamic functions. Tools are the real muscle here, giving the agent a clean, uniform way to interact with the outside world.

## Client / Server Architecture

The architecture splits responsibilities into three distinct roles to keep things modular and scalable. First is the **host**, which is the parent application running the main agent orchestration loop. Inside the host lives the **client**, a lightweight connector that opens and manages the connection lifecycle. Finally, the **server** is a separate process entirely that securely houses and exposes the tools.

To talk to each other, they use transport layers like standard input/output (**stdio**) for local communication or HTTP-based streams for remote systems. Tool discovery kicks off with a simple handshake where the client asks the server what capabilities it has. The server then hands back a structured list of names, plain-text descriptions, and JSON schemas, matching the exact format from our Week 4 toolbox.

## Connecting It Back to Week 4

Transitioning to MCP doesn’t change the fundamental agent loop built last week, but it completely shifts where the execution happens. What stays exactly the same is the core communication contract. The model still reads clear tool descriptions, determines the correct pathing, halts text generation to request a function call, and expects a raw text payload to return to its history log.

The massive shift is that the tool code no longer runs inside our local application process. In Week 4, a buggy tool could instantly crash the entire agent script. With MCP, the tool is safely sandboxed in an external server, meaning our main agent stays perfectly stable while speaking a universal language.

---

# Day 2 - Build Your Own MCP Server

Building a Model Context Protocol (MCP) server means moving from using tools to making them. Instead of just connecting to external services, existing Python code is turned into a standard package that any AI agent can plug into and use.

## The Server Author's Responsibilities

As a server creator, there are two main responsibilities: declaring the tools and writing the handlers. Declaring a tool means making a clear blueprint. The tool must have a unique name, a simple description, and a strict input schema listing the exact data types required. The handler contains the actual Python code that performs the task and sends back the result.

## How the SDK Bridges the Gap

The MCP SDK acts like a translator for the code. There is no need to completely rewrite functions. Instead, the SDK uses simple wrappers to listen for requests from the AI. When a request arrives, the SDK checks the data against the blueprint, runs the normal Python function, and converts the output into a clean format the AI understands.

## The Stdio Transport Layer

For local setups, the client and server communicate using standard input and output (stdio). This functions like a direct text message chain between two programs on a computer. The client launches the server in the background and sends text commands to its input stream, and the server replies instantly through the output stream. This method skips messy network setups.

## Why Precision Matters

Clear descriptions and strict schemas matter because a developer will never meet the external users or AI models connecting to the server. The AI relies entirely on the written definitions to figure out when to use a tool. If the guidelines are confusing or loose, the AI makes bad guesses, sends broken data, and crashes the pipeline. Clear rules ensure everything works perfectly.

---

# Day 3 - Connect Your Agent to Your MCP Server

Connecting an autonomous agent to a standalone MCP server completely changes how we think about building AI applications. Instead of building a bloated program where the AI's "brain" and its actual tools are tangled up in the same codebase, this setup splits them into two independent layers talking over a standard protocol.

The end-to-end flow becomes a dynamic loop happening entirely on the fly: user prompt ➔ agent engine (LLM) ➔ agent asks MCP client for available tools ➔ client fetches blueprints from server ➔ client injects definitions into model ➔ model picks tool ➔ client calls server ➔ server executes logic ➔ result returns to model ➔ final answer.

The core engineering shift here is that tool definitions aren't hardcoded into the agent anymore; they are fetched at runtime. This gives you massive wins: you can tweak a tool's internal logic or add a brand-new feature on the server, and the agent instantly gets those capabilities without you touching a single line of client code. Plus, it lets multiple completely different agents plug into and share the exact same tool server simultaneously.

However, separating the brain from the hands introduces real-world trade-offs like added execution latency and the risk of a broken connection. If the server crashes or the process drops, a fragile agent loop will freeze or blow up. This is where reliability work becomes essential. To make this robust, you must build in smart retry loops with exponential backoff and structured failure messages, ensuring that if the server goes down, the system handles it cleanly instead of crashing.