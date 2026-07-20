import sqlite3
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

router = APIRouter()

# Global metrics storage
metrics_store = {
    "total_requests": 0,
    "total_errors": 0,
    "total_tool_calls": 0,
    "total_response_time_ms": 0.0
}

def record_tool_call():
    """Helper function to increment tool calls during agent processing."""
    metrics_store["total_tool_calls"] += 1

@router.get("/health", tags=["Observability"])
async def get_health():
    db_reachable = False
    try:
        conn = sqlite3.connect("agent_memory.db")
        conn.execute("SELECT 1")
        conn.close()
        db_reachable = True
    except sqlite3.Error:
        db_reachable = False

    if db_reachable:
        return {"status": "up", "database": "reachable"}
    else:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "degraded", "database": "unreachable"}
        )

@router.get("/metrics", tags=["Observability"])
async def get_metrics():
    avg_latency = 0.0
    req_count = metrics_store["total_requests"]
    
    if req_count > 0:
        avg_latency = metrics_store["total_response_time_ms"] / req_count
        
    return {
        "total_requests": req_count,
        "total_errors": metrics_store["total_errors"],
        "total_tool_calls": metrics_store["total_tool_calls"],
        "average_response_time_ms": round(avg_latency, 2)
    }