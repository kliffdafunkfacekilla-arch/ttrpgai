from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_character_success():
    response = client.post(
        "/v1/characters/",
        json={
            "name": "Jules",
            "kingdom": "Engineer",
            "f_stats": {"F1": "Strength"},
            "capstone_stat": "Strength",
            "background_skills": ["Coding", "Debugging"],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Jules"
    assert data["kingdom"] == "Engineer"
    assert "valid_ability_schools" in data["character_sheet"]
