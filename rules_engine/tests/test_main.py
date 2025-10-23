from fastapi.testclient import TestClient
from rules_engine.main import app

client = TestClient(app)

def test_get_status():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["stats_loaded"] > 0
    assert data["skills_loaded"] > 0
    assert data["abilities_loaded"] > 0
    assert data["talents_loaded"] > 0
    assert data["features_loaded"] > 0

def test_get_kingdom_feature_stats():
    response = client.get("/v1/lookup/kingdom_feature_stats?feature_name=Predator's Gaze")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Predator's Gaze"
    assert "+2" in data["mods"]
    assert "Might" in data["mods"]["+2"]
