from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_character_success():
    response = client.post(
        "/v1/characters/",
        json={
            "name": "Jules",
            "kingdom": "Engineer",
            "f_stats": {"F1": "Predator's Gaze"},
            "capstone_stat": "Might",
            "background_skills": ["Great Weapons", "Plate Armor", "Intimidation", "Athletics", "Endurance", "History", "Logic", "Investigation", "Awareness", "Intuition", "Charm", "Willpower"],
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Jules"
    assert data["kingdom"] == "Engineer"
    assert "stats" in data["character_sheet"]
