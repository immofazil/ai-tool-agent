import json
import logging
import sqlite3
import time
from contextlib import asynccontextmanager
from typing import Dict, List
from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# ==========================================
# 0. SQLite Database Initialization
# ==========================================
DB_FILE = "agent_memory.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Create persistent messages table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            role TEXT NOT NULL CHECK (role IN ('user', 'model', 'assistant', 'tool', 'system')),
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Index to speed up user and conversation scoped history lookups
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_user_conv 
        ON messages (user_id, conversation_id, id ASC)
    """)
    conn.commit()
    conn.close()

# Initialize DB table on startup
init_db()


# ==========================================
# 1. Structured JSON Logging Setup
# ==========================================
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "level": record.levelname,
            "message": record.getMessage()
        }
        if hasattr(record, "user_id"):
            log_record["user_id"] = record.user_id
        if hasattr(record, "status"):
            log_record["status"] = record.status
            
        return json.dumps(log_record)

logger = logging.getLogger("hardened_agent_api")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)


# ==========================================
# 2. Application Lifespan
# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Booting Hardened API Gateway with SQLite Persistence...")
    yield
    logger.info("Shutting down Hardened API Gateway...")

app = FastAPI(title="Hardened MCP Agent API", lifespan=lifespan)


# ==========================================
# 3. CORS Configuration
# ==========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# 4. Custom Exception Handlers
# ==========================================
class AuthError(Exception):
    def __init__(self, message: str):
        self.message = message

class RateLimitError(Exception):
    def __init__(self, message: str):
        self.message = message

@app.exception_handler(AuthError)
async def auth_exception_handler(request: Request, exc: AuthError):
    return JSONResponse(status_code=401, content={"error": exc.message, "status": "failed"})

@app.exception_handler(RateLimitError)
async def rate_limit_exception_handler(request: Request, exc: RateLimitError):
    return JSONResponse(status_code=429, content={"error": exc.message, "status": "failed"})

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning("Input validation failed.", extra={"status": "failed"})
    return JSONResponse(
        status_code=422, 
        content={"error": "Invalid input. Messages must be between 1 and 500 characters.", "status": "failed"}
    )


# ==========================================
# 5. Security & Authentication Layer
# ==========================================
VALID_TOKENS = {
    "super_secret_token_A": "user_A",
    "super_secret_token_B": "user_B"
}

def verify_token(request: Request) -> str:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        logger.warning("Authentication failed: Missing or malformed token.", extra={"status": "failed"})
        raise AuthError("Not authenticated. Missing or invalid Authorization header.")
    
    token = auth_header.split(" ")[1]
    user_id = VALID_TOKENS.get(token)

    if not user_id:
        logger.warning("Authentication failed: Invalid token.", extra={"status": "failed"})
        raise AuthError("Not authenticated. The provided token is incorrect.")

    return user_id


# ==========================================
# 6. Rate Limiting Logic
# ==========================================
MAX_REQUESTS_PER_MINUTE = 5
rate_limit_store: Dict[str, List[float]] = {}

def check_rate_limit(user_id: str = Depends(verify_token)):
    now = time.time()
    if user_id not in rate_limit_store:
        rate_limit_store[user_id] = []

    rate_limit_store[user_id] = [t for t in rate_limit_store[user_id] if now - t < 60]

    if len(rate_limit_store[user_id]) >= MAX_REQUESTS_PER_MINUTE:
        logger.warning("Rate limit exceeded.", extra={"user_id": user_id, "status": "failed"})
        raise RateLimitError("Rate limit exceeded. Please wait a minute before sending more messages.")

    rate_limit_store[user_id].append(now)
    return user_id


# ==========================================
# 7. Input Validation Models
# ==========================================
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=500)
    conversation_id: str = Field(..., min_length=1, max_length=100)


# ==========================================
# 8. Persistent Protected Chat Endpoint
# ==========================================
@app.post("/chat")
async def chat_endpoint(request: ChatRequest, user_id: str = Depends(check_rate_limit)):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Load prior conversation history scoped strictly by user_id and conversation_id
    cursor.execute(
        "SELECT role, content FROM messages WHERE user_id = ? AND conversation_id = ? ORDER BY id ASC",
        (user_id, request.conversation_id)
    )
    prior_turns = cursor.fetchall()
    history_count = len(prior_turns)

    # Simulated agent processing using loaded context
    final_answer = (
        f"Hello {user_id}, I securely received your message: '{request.message}'. "
        f"Loaded {history_count} prior history records from SQLite database."
    )

    # Persist current user message turn
    cursor.execute(
        "INSERT INTO messages (conversation_id, user_id, role, content) VALUES (?, ?, ?, ?)",
        (request.conversation_id, user_id, "user", request.message)
    )

    # Persist model response turn
    cursor.execute(
        "INSERT INTO messages (conversation_id, user_id, role, content) VALUES (?, ?, ?, ?)",
        (request.conversation_id, user_id, "model", final_answer)
    )

    conn.commit()
    conn.close()

    # Structured logging strictly excluding raw message payload (PII protection)
    logger.info(
        f"Processed chat request. Session: {request.conversation_id}, Prior turns loaded: {history_count}", 
        extra={"user_id": user_id, "status": "success"}
    )

    return {
        "answer": final_answer,
        "status": "success",
        "history_turns_loaded": history_count,
        "trace": ["Invoked secure agent pipeline with SQLite persistence"]
    }