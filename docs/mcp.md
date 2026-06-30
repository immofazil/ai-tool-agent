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