import json
import logging
import time
import re
import asyncio
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "https://ai-agent-chat-tfvj.onrender.com" # Replace with your real frontend URL
    ], 
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
# 8. Context-Aware Mock Agent Pipeline Logic
# ==========================================
async def my_real_agent_function(message: str, history: List[Dict[str, str]]) -> str:
    """A mock agent that uses conversation history to maintain context for tools."""
    await asyncio.sleep(1) 
    msg_clean = message.lower()
    
    # Check if the user is asking to continue a calculation from a previous turn
    if "that answer" in msg_clean or "previous answer" in msg_clean:
        # Step 1: Scan backwards through history to find the last bot answer containing a number
        last_number = None
        for turn in reversed(history):
            if turn["role"] == "model" and "is " in turn["content"]:
                # Pull the number right after the word 'is'
                match = re.search(r'is\s+(\d+)', turn["content"])
                if match:
                    last_number = int(match.group(1))
                    break
        
        if last_number is not None:
            # Step 2: Figure out what math operations to perform on that old number
            match_ops = re.search(r'(multiply|add|subtract|divide)\s*(\d+)', msg_clean)
            if match_ops:
                operation, value_str = match_ops.groups()
                val = int(value_str)
                
                if "multiply" in operation: result = last_number * val; op_symbol = "*"
                elif "add" in operation: result = last_number + val; op_symbol = "+"
                elif "subtract" in operation: result = last_number - val; op_symbol = "-"
                elif "divide" in operation: result = int(last_number / val); op_symbol = "/"
                
                return f"I remembered our context! Taking the previous answer ({last_number}) and running the tool: {last_number} {op_symbol} {val} is {result}."
    
    # Standard direct calculation trigger
    if "calculate" in msg_clean:
        match = re.search(r'(\d+)\s*([\+\-\*\/])\s*(\d+)', message)
        if match:
            num1, operator, num2 = match.groups()
            num1, num2 = int(num1), int(num2)
            
            if operator == '*': result = num1 * num2
            elif operator == '+': result = num1 + num2
            elif operator == '-': result = num1 - num2
            elif operator == '/': result = num1 / num2
            
            return f"I triggered my calculator tool! The answer to {num1} {operator} {num2} is {result}."
            
    return f"I securely received your message: {message}"

# ==========================================
# 9. Protected Chat Endpoint
# ==========================================
memory_store: Dict[str, Dict[str, List[Dict[str, str]]]] = {}

@app.post("/chat")
async def chat_endpoint(request: ChatRequest, user_id: str = Depends(check_rate_limit)):
    if user_id not in memory_store:
        memory_store[user_id] = {}

    user_session = memory_store[user_id]

    if request.conversation_id not in user_session:
        user_session[request.conversation_id] = []

    # Note: We pass the existing history list BEFORE appending the current message, 
    # so the agent can inspect the true historical log.
    current_history = list(user_session[request.conversation_id])

    user_session[request.conversation_id].append({
        "role": "user", 
        "content": request.message
    })

    logger.info(f"Processing request for conversation: {request.conversation_id}", extra={"user_id": user_id, "status": "success"})
    
    # We change this line to pass the actual full history array!
    final_answer = await my_real_agent_function(request.message, current_history)
    
    user_session[request.conversation_id].append({
        "role": "model", 
        "content": final_answer
    })

    return {
        "answer": final_answer,
        "status": "success",
        "trace": ["Invoked secure agent pipeline"]
    }