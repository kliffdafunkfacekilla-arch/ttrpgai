# AI-TTRPG/rules_engine/tests/test_main.py
from fastapi.testclient import TestClient
from rules_engine.main import app

client = TestClient(app)

def test_get_status():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["stats_loaded_count"] > 0
