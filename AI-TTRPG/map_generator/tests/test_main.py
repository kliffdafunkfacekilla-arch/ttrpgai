from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_generate_map():
    response = client.post(
        "/v1/generate",
        json={
            "tags": ["cave", "small"],
            "seed": "12345",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "map_data" in data
    assert len(data["map_data"]) > 0
