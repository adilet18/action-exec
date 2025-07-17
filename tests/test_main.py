from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_simulated_restart_service():
    response = client.post("/action/execute", json={
        "action_type": "restart_service",
        "parameters": {"service_name": "my-service", "namespace": "default"},
        "simulate": True
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "simulated"
    assert data["action"] == "restart"
    assert data["service"] == "my-service"

def test_simulated_call_webhook():
    response = client.post("/action/execute", json={
        "action_type": "call_webhook",
        "parameters": {"url": "http://example.com", "payload": {"foo": "bar"}},
        "simulate": True
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "simulated"
    assert data["action"] == "webhook"
    assert data["url"] == "http://example.com"

def test_unknown_action_type():
    response = client.post("/action/execute", json={
        "action_type": "unknown_action",
        "parameters": {},
        "simulate": True
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Unknown action type" 