from rules_engine.data_loader import game_data
from rules_engine.models import (
    AbilitySchool,
    CharacterCreation,
    CraftingDiscipline,
    Talents,
    Stat,
    Kingdom
)

def test_data_loading():
    assert "ability_schools" in game_data
    assert "character_creation" in game_data
    assert "crafting" in game_data
    assert "skills" in game_data
    assert "stats" in game_data
    assert "talents" in game_data
    assert "kingdom_features" in game_data

    assert isinstance(game_data["ability_schools"][0], AbilitySchool)
    assert isinstance(game_data["character_creation"], CharacterCreation)
    assert isinstance(game_data["crafting"][0], CraftingDiscipline)
    assert isinstance(game_data["talents"], Talents)
    assert isinstance(game_data["stats"][0], Stat)
    assert isinstance(game_data["kingdom_features"][0], Kingdom)

    assert len(game_data["ability_schools"]) == 12
    assert len(game_data["crafting"]) == 6
    assert len(game_data["stats"]) > 0
    assert len(game_data["kingdom_features"]) == 6

    # Check for a specific, deeply nested value
    assert game_data["ability_schools"][0].branches[0].tiers[0].description == "Minor Shove (Push 1 target 2m)"
    assert game_data["kingdom_features"][0].features[0].choices[0].choice_name == "Predator's Gaze"
