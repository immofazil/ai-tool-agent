import pytest
from fastapi.testclient import TestClient

from server.main import app, rate_limit_store

client = TestClient(app)

VALID_HEADERS = {"Authorization": "Bearer super_secret_token_A"}
VALID_PAYLOAD = {
    "message": "Hello world",
    "conversation_id": "conv_123"
}


@pytest.fixture(autouse=True)
def reset_rate_limit():
    """Resets the rate limit tracking store before each test execution."""
    rate_limit_store.clear()


# ==========================================
# UNIT TESTS (Logic & Guardrails)
# ==========================================

def test_tool_argument_validation():
    """Protects against invalid inputs by asserting strict 422 payload rejection."""
    # Omit mandatory 'conversation_id' field to trigger Pydantic schema validation failure
    invalid_payload = {"message": "Missing conversation_id"}
    response = client.post("/chat", headers=VALID_HEADERS, json=invalid_payload)
    
    assert response.status_code == 422
    assert response.json()["status"] == "failed"


def test_max_iteration_guardrail():
    """Protects against oversized message inputs exceeding system limits."""
    # Send a message exceeding the 500-character maximum limit
    oversized_payload = {
        "message": "A" * 501,
        "conversation_id": "conv_123"
    }
    response = client.post("/chat", headers=VALID_HEADERS, json=oversized_payload)
    
    assert response.status_code == 422
    assert response.json()["status"] == "failed"


def test_malformed_llm_response():
    """Protects against empty message payload submissions."""
    # Send an empty message violating min_length=1
    empty_payload = {
        "message": "",
        "conversation_id": "conv_123"
    }
    response = client.post("/chat", headers=VALID_HEADERS, json=empty_payload)
    
    assert response.status_code == 422
    assert response.json()["status"] == "failed"


# ==========================================
# INTEGRATION TESTS (API Flow)
# ==========================================

def test_chat_authenticated_success():
    """Protects the primary endpoint path for authorized requests."""
    response = client.post("/chat", headers=VALID_HEADERS, json=VALID_PAYLOAD)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "user_A" in data["answer"]


def test_chat_missing_credentials_401():
    """Protects endpoints from unauthorized access attempts."""
    # Send request without Authorization header
    response = client.post("/chat", json=VALID_PAYLOAD)
    
    assert response.status_code == 401
    assert response.json()["status"] == "failed"


def test_chat_rate_limit_429():
    """Protects server resources from spam by enforcing rate limits."""
    # Send MAX_REQUESTS_PER_MINUTE (5) valid requests
    for _ in range(5):
        res = client.post("/chat", headers=VALID_HEADERS, json=VALID_PAYLOAD)
        assert res.status_code == 200

    # The 6th request must trigger HTTP 429
    blocked_response = client.post("/chat", headers=VALID_HEADERS, json=VALID_PAYLOAD)
    assert blocked_response.status_code == 429
    assert blocked_response.json()["status"] == "failed"


# ==========================================
# PERSISTENCE TEST (Database State)
# ==========================================

def test_conversation_persistence():
    """Protects data integrity by verifying SQLite state persistence across calls."""
    unique_conv = {"message": "First message", "conversation_id": "persistence_test_session"}
    
    # 1. First interaction: history count should be 0
    first_res = client.post("/chat", headers=VALID_HEADERS, json=unique_conv)
    assert first_res.status_code == 200
    assert first_res.json()["history_turns_loaded"] == 0

    # 2. Second interaction with same conversation_id: history count should be 2 (1 user + 1 model turn)
    second_payload = {"message": "Second message", "conversation_id": "persistence_test_session"}
    second_res = client.post("/chat", headers=VALID_HEADERS, json=second_payload)
    
    assert second_res.status_code == 200
    assert second_res.json()["history_turns_loaded"] == 2