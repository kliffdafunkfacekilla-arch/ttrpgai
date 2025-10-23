import json
from pathlib import Path
from typing import List, Dict, Any
from .models import (
    AbilitySchool,
    CharacterCreation,
    CombatSkill,
    NonCombatSkill,
    UrbanArchetype,
    CraftingDiscipline,
    Talents,
    Stat,
    DevotionChoice,
    BirthCircumstance,
    ChildhoodDevelopment,
    ComingOfAgeEvent,
    SingleStatTalent,
    SingleSkillTalent,
    DualStatTalent
)

def load_data() -> Dict[str, Any]:
    data_dir = Path(__file__).parent / "data"

    with open(data_dir / "abilities.json") as f:
        ability_data = json.load(f)
        ability_schools: List[AbilitySchool] = [AbilitySchool(**item) for item in ability_data]

    with open(data_dir / "character_creation.json") as f:
        char_data = json.load(f)
        character_creation = CharacterCreation(
            devotion=[DevotionChoice(**item) for item in char_data["devotion"]],
            birth_circumstance=[BirthCircumstance(**item) for item in char_data["birth_circumstance"]],
            childhood_development=[ChildhoodDevelopment(**item) for item in char_data["childhood_development"]],
            coming_of_age=[ComingOfAgeEvent(**item) for item in char_data["coming_of_age"]],
        )

    with open(data_dir / "crafting.json") as f:
        crafting_data = json.load(f)
        crafting: List[CraftingDiscipline] = [CraftingDiscipline(**item) for item in crafting_data]

    with open(data_dir / "skills.json") as f:
        skills_data = json.load(f)
        skills = {
            "combat_skills": [CombatSkill(**item) for item in skills_data["combat_skills"]],
            "non_combat_skills": [NonCombatSkill(**item) for item in skills_data["non_combat_skills"]],
            "urban_archetypes": [UrbanArchetype(**item) for item in skills_data["urban_archetypes"]],
        }

    with open(data_dir / "stats.json") as f:
        stats_data = json.load(f)
        stats: List[Stat] = [Stat(**item) for item in stats_data]

    with open(data_dir / "talents.json") as f:
        talents_data = json.load(f)
        talents = Talents(
            single_stat_mastery=[SingleStatTalent(**item) for item in talents_data["single_stat_mastery"]],
            single_skill_mastery=[SingleSkillTalent(**item) for item in talents_data["single_skill_mastery"]],
            dual_stat_focus=[DualStatTalent(**item) for item in talents_data["dual_stat_focus"]],
        )

    return {
        "ability_schools": ability_schools,
        "character_creation": character_creation,
        "crafting": crafting,
        "skills": skills,
        "stats": stats,
        "talents": talents,
    }

game_data = load_data()
