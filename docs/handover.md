# Handover Note

## Current System State

The AI Agent Gateway is fully deployed, tested, and operational. The backend runs on Render with Bearer token authentication, sliding-window rate limiting (5 req/min), MCP tools, and SQLite database persistence. The static frontend is live on Hugging Face Spaces. All 7 automated unit tests are passing.

## Where Everything Lives

* **Production Application**: Inside `src/` (`src/server/` contains `main.py`, `mcp_tools.py`, and `database.py`; `src/client/` contains `index.html` and `app.js`).
* **Documentation & Case Study**: Located in `docs/capstone/README.md`.
* **Sandbox Folders**: Root-level `frontend/`, `mcp/`, and `server/` directories were used for early experimental testing and learning.

## Immediate Next Steps

If you are picking up this project on Monday, start with these top priorities:

1. **Database Migration**: Move from the local SQLite file (`agent_memory.db`) to PostgreSQL or Supabase to prevent file-locking during concurrent traffic.
2. **Containerization**: Create a Dockerfile and deploy to Fly.io or AWS ECS to eliminate free-tier Render cold starts.
3. **Semantic RAG Memory**: Add a vector database such as ChromaDB or Pinecone to allow semantic retrieval across past chat sessions.