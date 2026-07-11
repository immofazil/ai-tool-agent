# Day 1 - Why MCP? From Local Tools to a Standard Protocol

## Client / Server Architecture

The architecture splits responsibilities into three distinct roles to keep things modular and scalable. First is the **host**, which is the parent application running the main agent orchestration loop. Inside the host lives the **client**, a lightweight connector that opens and manages the connection lifecycle. Finally, the **server** is a separate process entirely that securely houses and exposes the tools.

To talk to each other, they use transport layers like standard input/output (**stdio**) for local communication or HTTP-based streams for remote systems. Tool discovery kicks off with a simple handshake where the client asks the server what capabilities it has. The server then hands back a structured list of names, plain-text descriptions, and JSON schemas, matching the exact format from our Week 4 toolbox.

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