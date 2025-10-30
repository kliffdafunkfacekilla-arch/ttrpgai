from fastapi.testclient import TestClient
from map_generator.app.main import app

def test_generate_map():
    with TestClient(app) as client:
        response = client.post(
            "/v1/generate",
            json={
                "tags": ["cave", "inside", "dungeon"],
                "seed": "12345",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "map_data" in data
        assert len(data["map_data"]) > 0
