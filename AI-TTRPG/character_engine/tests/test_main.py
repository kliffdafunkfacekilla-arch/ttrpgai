from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app, get_db
from app.database import Base
import pytest
from unittest.mock import patch, AsyncMock

from sqlalchemy.pool import StaticPool

# In-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.mark.asyncio
@patch("app.services._call_rules_engine", new_callable=AsyncMock)
async def test_create_character_success(mock_call_rules, client):
    # Configure the mock to return different values based on the endpoint
    async def side_effect(method, endpoint, json_data=None, params=None):
        if endpoint == "/lookup/creation/kingdom_features":
            return {
                "F1": {"Mammal": [{"name": "Predator's Gaze", "mods": {"+1": ["Awareness", "Intuition"]}}]},
                "F9": {"All": [{"name": "Capstone: +2 Might", "mods": {"+2": ["Might"]}}]},
            }
        if endpoint == "/lookup/creation/origin_choices":
            return [{"name": "Forested Highlands", "skills": ["Survival", "Lore: Agricul. & Wilds"]}]
        if endpoint == "/lookup/creation/childhood_choices":
            return [{"name": "Street Urchin", "skills": ["Slight of Hand", "Intimidation"]}]
        if endpoint == "/lookup/creation/coming_of_age_choices":
            return [{"name": "The Grand Tournament", "skills": ["Precision Blades", "Resilience"]}]
        if endpoint == "/lookup/creation/training_choices":
            return [{"name": "Soldier's Discipline", "skills": ["Polearms & Shields", "Plate Armor"]}]
        if endpoint == "/lookup/creation/devotion_choices":
            return [{"name": "Devotion to the State", "skills": ["Lore: Royalty/Political", "Reinforced"]}]
        if endpoint == "/lookup/talents" and method.upper() == "POST":
            return [{"name": "Ability Talent", "mods": {"+1": ["Finesse"]}}]
        if endpoint == "/lookup/all_ability_schools":
            return ["Force"]
        if endpoint == "/lookup/all_stats":
            return ["Might", "Endurance", "Finesse", "Reflexes", "Vitality", "Fortitude", "Knowledge", "Logic", "Awareness", "Intuition", "Charm", "Willpower"]
        if endpoint == "/lookup/all_skills":
            return ["Survival", "Intimidation", "Lore: Agricul. & Wilds", "Slight of Hand", "Precision Blades", "Resilience", "Polearms & Shields", "Plate Armor", "Lore: Royalty/Political", "Reinforced"]
        if endpoint.startswith("/lookup/ability_school/"):
            return {"tiers": [{"name": "Force Push"}]}
        if endpoint == "/calculate/base_vitals" and method.upper() == "POST":
            return {"max_hp": 15, "resources": {"Stamina": {"current": 10, "max": 10}}}
        # Default mock values for other GET calls
        return {}

    mock_call_rules.side_effect = side_effect

    # The client call is now synchronous because TestClient handles the event loop
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
    assert data["skills"]["Survival"]["rank"] == 1
    assert data["skills"]["Intimidation"]["rank"] == 1
    assert "Ability Talent" in data["talents"]
    assert "background_talent" not in data["talents"]
