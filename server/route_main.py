import time
from fastapi import FastAPI, Request, Header, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from server.routes import router as observability_router, metrics_store

app = FastAPI(title="AI Agent API")

app.include_router(observability_router)

class ChatRequest(BaseModel):
    conversation_id: str
    message: str

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


@app.post("/chat")
async def chat_endpoint(payload: ChatRequest, authorization: str = Header(None)):
    try:
        # Check authentication header
        if not authorization or not authorization.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "status": "error",
                    "error_code": "MISSING_AUTH_TOKEN",
                    "message": "Authorization header is missing or malformed."
                }
            )

        # Handle message content
        if payload.message == "trigger_error":
            raise ValueError("Simulated unexpected backend failure.")

        return {
            "status": "success",
            "conversation_id": payload.conversation_id,
            "answer": f"Processed message: {payload.message}"
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