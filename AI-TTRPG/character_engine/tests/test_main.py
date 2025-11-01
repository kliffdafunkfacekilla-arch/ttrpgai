from fastapi.testclient import TestClient
from app.main import app
from app.database import engine, Base
from unittest.mock import patch, ANY

# Create the database tables
Base.metadata.create_all(bind=engine)

client = TestClient(app)

@patch('app.services._get_rules_engine_data')
def test_create_character_success(mock_get_rules):
    # Mock the return value of the rules engine call
    mock_get_rules.return_value = {
        'stats_list': ['Strength', 'Dexterity', 'Constitution', 'Intelligence', 'Wisdom', 'Charisma', 'Might', 'Agility', 'Vitality', 'Insight', 'Reasoning', 'Presence'],
        'all_skills': {'Unarmed': {'category': 'Combat', 'stat': 'Strength'}},
        'kingdom_features': {
            "F1": {
                "Mammal": [
                    {
                        "name": "Predator's Gaze",
                        "mods": {
                            "+1": ["Presence", "Insight"]
                        }
                    }
                ]
            },
            "F9": {
                "All": [
                    {
                        "name": "Capstone: +2 Might",
                        "mods": {
                            "+2": ["Might"]
                        }
                    }
                ]
            }
        },
        'all_talents_map': {
            'Background Talent': {'name': 'Background Talent', 'mods': {'+1': ['Strength']}},
            'Ability Talent': {'name': 'Ability Talent', 'mods': {'+1': ['Dexterity']}}
        },
        'all_abilities_map': {
            'Force': {
                'tiers': [
                    {'name': 'Force Push'}
                ]
            }
        }
    }


    response = client.post(
        "/v1/characters/",
        json={
            "name": "Jules",
            "kingdom": "Mammal",
            "feature_choices": [{"feature_id": "F1", "choice_name": "Predator's Gaze"}, {"feature_id": "F9", "choice_name": "Capstone: +2 Might"}],
            "background_talent": "Background Talent",
            "ability_school": "Force",
            "ability_talent": "Ability Talent"
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Jules"
    assert data["kingdom"] == "Mammal"
    assert "stats" in data
