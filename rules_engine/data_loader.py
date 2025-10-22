import json
from pathlib import Path
from typing import List
from .models import BackgroundChoice, KingdomFeature, TalentDefinition, Ability, SkillDefinition

def load_data():
    data_dir = Path(__file__).parent / "data"

    with open(data_dir / "backgrounds.json") as f:
        backgrounds: List[BackgroundChoice] = [BackgroundChoice(**item) for item in json.load(f)]

    with open(data_dir / "kingdom_feats.json") as f:
        kingdom_feats: List[KingdomFeature] = [KingdomFeature(**item) for item in json.load(f)]

    with open(data_dir / "talents.json") as f:
        talents: List[TalentDefinition] = [TalentDefinition(**item) for item in json.load(f)]

    with open(data_dir / "abilities.json") as f:
        abilities: List[Ability] = [Ability(**item) for item in json.load(f)]

    with open(data_dir / "skills.json") as f:
        skills: List[SkillDefinition] = [SkillDefinition(**item) for item in json.load(f)]

    return {
        "backgrounds": backgrounds,
        "kingdom_feats": kingdom_feats,
        "talents": talents,
        "abilities": abilities,
        "skills": skills,
    }

game_data = load_data()
