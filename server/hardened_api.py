import json
import logging
import time
from typing import Dict, List
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field

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
    logger.info("Booting Hardened API Gateway...")
    yield
    logger.info("Shutting down Hardened API Gateway...")

app = FastAPI(title="Hardened MCP Agent API", lifespan=lifespan)

# ==========================================
# 3. CORS Configuration (Prep for Frontend)
# ==========================================
# This tells the server to only accept web browser requests from localhost:3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 4. Custom Exception Handlers (Clean JSON Errors)
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
    # Catches empty or oversized inputs and returns a clean 422 without a messy stack trace
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
    """Ensures a user does not exceed the allowed requests per minute."""
    now = time.time()
    if user_id not in rate_limit_store:
        rate_limit_store[user_id] = []

    # Filter out timestamps older than 60 seconds
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
    # Pydantic will automatically reject empty strings (min_length=1) and huge essays (max_length=500)
    message: str = Field(..., min_length=1, max_length=500)
    conversation_id: str = Field(..., min_length=1, max_length=100)

# ==========================================
# 8. Protected Chat Endpoint
# ==========================================
memory_store: Dict[str, Dict[str, List[Dict[str, str]]]] = {}

@app.post("/chat")
async def chat_endpoint(request: ChatRequest, user_id: str = Depends(check_rate_limit)):
    if user_id not in memory_store:
        memory_store[user_id] = {}

    user_session = memory_store[user_id]

    if request.conversation_id not in user_session:
        user_session[request.conversation_id] = []

    user_session[request.conversation_id].append({
        "role": "user", 
        "content": request.message
    })

    logger.info(f"Processing request for conversation: {request.conversation_id}", extra={"user_id": user_id, "status": "success"})
    
    final_answer = f"Hello {user_id}, I securely received your message: {request.message}"
    
    user_session[request.conversation_id].append({
        "role": "model", 
        "content": final_answer
    })

    return {
        "answer": final_answer,
        "status": "success",
        "trace": ["Invoked secure agent pipeline"]
    }