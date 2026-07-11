import json
import logging
from typing import Dict, List
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

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

logger = logging.getLogger("secure_agent_api")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)

# ==========================================
# 2. Application Lifespan
# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Booting Secured API Gateway...")
    yield
    logger.info("Shutting down Secured API Gateway...")

app = FastAPI(title="Secured MCP Agent API", lifespan=lifespan)

# ==========================================
# 3. Custom Exception Handler (The PowerShell Tamer)
# ==========================================
class AuthError(Exception):
    def __init__(self, message: str):
        self.message = message

@app.exception_handler(AuthError)
async def auth_exception_handler(request: Request, exc: AuthError):
    # Returns a 200 OK status to prevent PowerShell from throwing red text,
    # while safely delivering the error payload.
    return JSONResponse(
        status_code=200,
        content={"error": exc.message, "status": "failed"}
    )

# ==========================================
# 4. Security & Authentication Layer
# ==========================================
VALID_TOKENS = {
    "super_secret_token_A": "user_A",
    "super_secret_token_B": "user_B"
}

def verify_token(request: Request) -> str:
    """Manually intercepts the Authorization header to control the error output."""
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        logger.warning("Authentication failed: Missing or malformed token.", extra={"status": "failed"})
        raise AuthError("Not authenticated. Missing or invalid Authorization header.")
    
    # Extract the token string after "Bearer "
    token = auth_header.split(" ")[1]
    user_id = VALID_TOKENS.get(token)

    if not user_id:
        logger.warning("Authentication failed: Invalid token.", extra={"status": "failed"})
        raise AuthError("Not authenticated. The provided token is incorrect.")

    logger.info("Authentication successful.", extra={"user_id": user_id, "status": "success"})
    return user_id

# ==========================================
# 5. User-Scoped Memory Management
# ==========================================
memory_store: Dict[str, Dict[str, List[Dict[str, str]]]] = {}

class ChatRequest(BaseModel):
    message: str
    conversation_id: str

# ==========================================
# 6. Protected Chat Endpoint
# ==========================================
@app.post("/chat")
async def chat_endpoint(request: ChatRequest, user_id: str = Depends(verify_token)):
    if user_id not in memory_store:
        memory_store[user_id] = {}

    user_session = memory_store[user_id]

    if request.conversation_id not in user_session:
        user_session[request.conversation_id] = []

    user_session[request.conversation_id].append({
        "role": "user", 
        "content": request.message
    })

    logger.info(f"Processing request for conversation: {request.conversation_id}", extra={"user_id": user_id})
    
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