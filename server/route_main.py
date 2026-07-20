import time
import asyncio
from fastapi import FastAPI, Request, Header, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from server.routes import router as observability_router, metrics_store

app = FastAPI(title="AI Agent API")

app.include_router(observability_router)

# FIX 1: Strict Input Validation Guards
class ChatRequest(BaseModel):
    conversation_id: str = Field(..., min_length=1, max_length=100)
    message: str = Field(..., min_length=1, max_length=500)

@app.middleware("http")
async def observe_metrics(request: Request, call_next):
    if request.url.path == "/chat":
        start_time = time.time()
        metrics_store["total_requests"] += 1
        
        response = await call_next(request)
        
        if response.status_code >= 400:
            metrics_store["total_errors"] += 1
            
        process_time_ms = (time.time() - start_time) * 1000
        metrics_store["total_response_time_ms"] += process_time_ms
        return response
        
    return await call_next(request)

# FIX 2: Retry Logic with Exponential Backoff
async def call_agent_with_retry(message: str, max_retries: int = 3) -> str:
    """Simulates an external call with automatic retries on network drops."""
    base_delay = 1
    for attempt in range(max_retries):
        try:
            # Simulate a transient network failure on the first attempt
            if message == "trigger_network_drop" and attempt == 0:
                raise ConnectionError("Transient network failure.")
            # Simulate a hard crash
            if message == "trigger_error":
                raise ValueError("Simulated unexpected backend failure.")
                
            return f"Processed message: {message}"
            
        except Exception as err:
            # Do not retry on intentional ValueError crashes or on the final attempt
            if attempt == max_retries - 1 or isinstance(err, ValueError):
                raise err
            # Exponential backoff: 1s, 2s, 4s...
            await asyncio.sleep(base_delay * (2 ** attempt))
    return ""

@app.post("/chat")
async def chat_endpoint(payload: ChatRequest, authorization: str = Header(None)):
    try:
        # Check authentication header (Fixed to return 401 instead of 400)
        if not authorization or not authorization.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "status": "error",
                    "error_code": "MISSING_AUTH_TOKEN",
                    "message": "Authorization header is missing or malformed."
                }
            )

        # Execute the request through the retry wrapper
        agent_response = await call_agent_with_retry(payload.message)

        return {
            "status": "success",
            "conversation_id": payload.conversation_id,
            "answer": agent_response
        }

    except Exception as err:
        # Code-level try-except block handling runtime errors cleanly
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "status": "error",
                "error_code": type(err).__name__,
                "message": str(err)
            }
        )