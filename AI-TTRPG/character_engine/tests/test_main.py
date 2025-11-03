from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app, get_db
from app.database import Base
from unittest.mock import patch, MagicMock

# In-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    Base.metadata.create_all(bind=engine)  # Create tables on the in-memory engine
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)  # Drop tables after the test


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@patch("app.services.httpx.post")
@patch("app.services._get_rules_engine_data")
def test_create_character_success(mock_get_rules, mock_httpx_post):
    # Mock the return value of the rules engine call
    mock_get_rules.return_value = {
        "stats_list": [
            "Might",
            "Endurance",
            "Finesse",
            "Reflexes",
            "Vitality",
            "Fortitude",
            "Knowledge",
            "Logic",
            "Awareness",
            "Intuition",
            "Charm",
            "Willpower",
        ],
        "all_skills": {
            "Survival": {"category": "Utility", "stat": "Awareness"},
            "Intimidation": {"category": "Conversational", "stat": "Willpower"},
            "Lore: Agricul. & Wilds": {"category": "Lore", "stat": "Knowledge"},
            "Slight of Hand": {"category": "Utility", "stat": "Finesse"},
            "Precision Blades": {"category": "Combat", "stat": "Finesse"},
            "Resilience": {"category": "Non-Combat", "stat": "Fortitude"},
            "Polearms & Shields": {"category": "Combat", "stat": "Might"},
            "Plate Armor": {"category": "Armor", "stat": "Might"},
            "Lore: Royalty/Political": {"category": "Lore", "stat": "Knowledge"},
            "Reinforced": {"category": "Armor", "stat": "Fortitude"},
        },
        "kingdom_features": {
            "F1": {
                "Mammal": [
                    {"name": "Predator's Gaze", "mods": {"+1": ["Awareness", "Intuition"]}}
                ]
            },
            "F9": {"All": [{"name": "Capstone: +2 Might", "mods": {"+2": ["Might"]}}]},
        },
        "origin_choices": [
            {
                "name": "Forested Highlands",
                "description": "Raised in the high-altitude forests, you are a natural survivalist and tracker.",
                "skills": ["Survival", "Lore: Agricul. & Wilds"],
            }
        ],
        "childhood_choices": [
            {
                "name": "Street Urchin",
                "description": "You grew up fending for yourself, learning to be quick with your hands and your words.",
                "skills": ["Slight of Hand", "Intimidation"],
            }
        ],
        "coming_of_age_choices": [
            {
                "name": "The Grand Tournament",
                "description": "You proved your mettle in single combat with a blade.",
                "skills": ["Precision Blades", "Resilience"],
            }
        ],
        "training_choices": [
            {
                "name": "Soldier's Discipline",
                "description": "You were trained in the regimented arts of the shield and polearm.",
                "skills": ["Polearms & Shields", "Plate Armor"],
            }
        ],
        "devotion_choices": [
            {
                "name": "Devotion to the State",
                "description": "You are a patriot, dedicated to the laws and history of your kingdom.",
                "skills": ["Lore: Royalty/Political", "Reinforced"],
            }
        ],
        "all_talents_map": {
            "Ability Talent": {"name": "Ability Talent", "mods": {"+1": ["Finesse"]}},
        },
        "all_abilities_map": {"Force": {"tiers": [{"name": "Force Push"}]}},
    }
    # Mock the vitals calculation call
    mock_vitals_response = MagicMock()
    mock_vitals_response.status_code = 200
    mock_vitals_response.json.return_value = {
        "max_hp": 15,
        "resources": {"Stamina": {"current": 10, "max": 10}},
    }
    mock_httpx_post.return_value = mock_vitals_response

    response = client.post(
        "/v1/characters/",
        json={
            "name": "Jules",
            "kingdom": "Mammal",
            "feature_choices": [
                {"feature_id": "F1", "choice_name": "Predator's Gaze"},
                {"feature_id": "F9", "choice_name": "Capstone: +2 Might"},
            ],
            "origin_choice": "Forested Highlands",
            "childhood_choice": "Street Urchin",
            "coming_of_age_choice": "The Grand Tournament",
            "training_choice": "Soldier's Discipline",
            "devotion_choice": "Devotion to the State",
            "ability_school": "Force",
            "ability_talent": "Ability Talent",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Jules"
    assert data["kingdom"] == "Mammal"
    assert "stats" in data
    assert data["stats"]["Might"] == 10
    assert data["stats"]["Awareness"] == 9
    assert data["stats"]["Intuition"] == 9
    assert data["stats"]["Finesse"] == 9
    assert data["skills"]["Survival"] == 1
    assert data["skills"]["Intimidation"] == 1
    assert "Ability Talent" in data["talents"]
    assert "background_talent" not in data["talents"]
