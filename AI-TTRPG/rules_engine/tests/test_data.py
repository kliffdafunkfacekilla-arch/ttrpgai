# AI-TTRPG/rules_engine/tests/test_data.py
from fastapi.testclient import TestClient
from rules_engine.app.main import app

def test_read_status():
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"
        assert data["stats_loaded_count"] > 0
        assert data["skills_loaded_count"] > 0
        assert data["abilities_loaded_count"] > 0
        assert data["talents_loaded"] is True
        assert data["features_loaded_count"] > 0
        assert data["melee_weapons_loaded_count"] > 0
        assert data["ranged_weapons_loaded_count"] > 0
        assert data["armor_loaded_count"] > 0
        assert data["injury_effects_loaded_count"] > 0
