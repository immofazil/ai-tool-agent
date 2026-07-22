import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
TOKEN = "capstone-secret-token"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

def test_1_health_check():
    """1. Public Health Check Endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_2_auth_guardrail_unauthorized():
    """2. Security: Block missing or invalid bearer token."""
    response = client.post("/chat", json={"session_id": "test", "message": "hello"})
    assert response.status_code in [401, 403]

def test_3_single_tool_execution_weather():
    """3. MCP Tool Routing: Single tool (Weather)."""
    payload = {"session_id": "s_weather", "message": "What is the weather in Tokyo?"}
    response = client.post("/chat", json=payload, headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert "get_weather" in data["tool_executed"]

def test_4_single_tool_execution_calculator():
    """4. MCP Tool Routing: Single tool (Calculator)."""
    payload = {"session_id": "s_calc", "message": "calculate 25*5"}
    response = client.post("/chat", json=payload, headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert "calculator" in data["tool_executed"]

def test_5_multi_tool_execution():
    """5. MCP Tool Routing: Multi-tool orchestration in a single query."""
    payload = {"session_id": "s_multi", "message": "weather in Tokyo and calculate 125-8"}
    response = client.post("/chat", json=payload, headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert "get_weather" in data["tool_executed"]
    assert "calculator" in data["tool_executed"]

def test_6_telemetry_metrics_endpoint():
    """6. Observability: Authenticated access to gateway metrics."""
    response = client.get("/metrics", headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert "telemetry" in data
    assert data["telemetry"]["total_requests"] > 0

def test_7_rate_limit_enforcement():
    """7. Gateway Guardrails: Middleware rate limiting enforcement."""
    session_payload = {"session_id": "s_rate", "message": "ping"}
    
    # Send requests to reach the 5 req/min threshold
    for _ in range(5):
        client.post("/chat", json=session_payload, headers=HEADERS)
        
    # The 6th request should return 429 Too Many Requests
    exceeded_response = client.post("/chat", json=session_payload, headers=HEADERS)
    assert exceeded_response.status_code == 429
    assert "Rate limit exceeded" in exceeded_response.json()["detail"]