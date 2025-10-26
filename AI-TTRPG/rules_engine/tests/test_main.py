# AI-TTRPG/rules_engine/tests/test_main.py
from fastapi.testclient import TestClient
from rules_engine.main import app

def test_get_status():
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"
        assert data["stats_loaded_count"] > 0
        assert "melee_weapons_loaded_count" in data
        assert data["melee_weapons_loaded_count"] > 0
