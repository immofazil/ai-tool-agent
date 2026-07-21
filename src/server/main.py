from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import time
import json
import logging
from src.server.database import init_db, save_message, get_history
from src.server.mcp_tools import execute_mcp_tool

# Setup Structured JSON Logging
logging.basicConfig(level=logging.INFO)

def log_json(level: str, event: str, **kwargs):
    log_entry = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "level": level,
        "event": event,
        **kwargs
    }
    print(json.dumps(log_entry))

# Initialize database tables
init_db()

app = FastAPI(
    title="Cumulative Production AI Agent Gateway",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_TOKEN = "capstone-secret-token"
security_scheme = HTTPBearer()

RATE_LIMIT_REQUESTS = 5
RATE_LIMIT_WINDOW_SECONDS = 60
request_history = {}

metrics = {
    "total_requests": 0,
    "total_errors": 0,
    "tools_executed": 0
}

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)):
    """Security Hardening: Bearer Token Auth Guardrail."""
    if credentials.credentials != SECRET_TOKEN:
        metrics["total_errors"] += 1
        log_json("WARNING", "auth_failed", detail="Invalid Bearer Token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Invalid Bearer Token"
        )
    return credentials.credentials

@app.middleware("http")
async def rate_limit_and_telemetry_middleware(request: Request, call_next):
    """Middleware: Handles rate limiting cleanly with JSON logs instead of raw exceptions."""
    client_ip = request.client.host
    now = time.time()

    if request.url.path == "/chat":
        metrics["total_requests"] += 1
        
        user_requests = request_history.get(client_ip, [])
        valid_requests = [t for t in user_requests if now - t < RATE_LIMIT_WINDOW_SECONDS]
        
        if len(valid_requests) >= RATE_LIMIT_REQUESTS:
            metrics["total_errors"] += 1
            log_json("ERROR", "rate_limit_exceeded", client_ip=client_ip, path=request.url.path)
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Rate limit exceeded. Maximum 5 requests per minute allowed."}
            )
        
        valid_requests.append(now)
        request_history[client_ip] = valid_requests

    try:
        response = await call_next(request)
        log_json("INFO", "http_request", path=request.url.path, status_code=response.status_code)
        return response
    except Exception as exc:
        metrics["total_errors"] += 1
        log_json("CRITICAL", "unhandled_exception", error=str(exc), path=request.url.path)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error", "error": str(exc)}
        )

class ChatRequest(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=50)
    message: str = Field(..., min_length=1, max_length=500)

@app.post("/chat")
async def agent_chat_endpoint(req: ChatRequest, token: str = Depends(verify_token)):
    """Secure Agent Chat Route with Persistent Memory and MCP Tool Routing."""
    save_message(req.session_id, "user", req.message)
    history = get_history(req.session_id)
    
    msg_lower = req.message.lower()
    tool_used = None
    
    if "weather" in msg_lower:
        tool_used = "get_weather"
        query_location = req.message.replace("weather", "").strip() or "Dubai"
        tool_output = execute_mcp_tool(tool_used, query_location)
        metrics["tools_executed"] += 1
        agent_response = f"I invoked the MCP Weather Tool. {tool_output}"
        
    elif "calc" in msg_lower or "math" in msg_lower or any(op in msg_lower for op in ["+", "*", "/"]):
        tool_used = "calculator"
        expr = "".join([c for c in req.message if c in "0123456789+-*/.()"])
        tool_output = execute_mcp_tool(tool_used, expr)
        metrics["tools_executed"] += 1
        agent_response = f"I invoked the MCP Calculator Tool. {tool_output}"
        
    else:
        agent_response = f"Processed query: '{req.message}'. Total active history depth: {len(history)} messages."

    save_message(req.session_id, "assistant", agent_response)
    log_json("INFO", "chat_processed", session_id=req.session_id, tool_executed=tool_used)
    
    return {
        "status": "success",
        "session_id": req.session_id,
        "response": agent_response,
        "tool_executed": tool_used,
        "history_count": len(history)
    }

@app.get("/health")
def health_endpoint():
    return {"status": "healthy", "database": "connected", "service": "FastAPI AI Agent Gateway"}

@app.get("/metrics")
def metrics_endpoint(token: str = Depends(verify_token)):
    return {
        "telemetry": metrics,
        "active_rate_limit_ips": len(request_history)
    }