from pydantic import BaseModel
from enum import Enum

class Stat(str, Enum):
    STRENGTH = "Strength"
    DEXTERITY = "Dexterity"
    CONSTITUTION = "Constitution"
    INTELLIGENCE = "Intelligence"
    WISDOM = "Wisdom"
    CHARISMA = "Charisma"

class Skill(str, Enum):
    ACROBATICS = "Acrobatics"
    # ... other skills

class SkillCheckRequest(BaseModel):
    stat_modifier: int
    skill_rank: int
    dc: int

class SkillCheckResponse(BaseModel):
    success: bool
    roll: int

class BackgroundChoice(BaseModel):
    name: str
    description: str
    features: list[str]

class KingdomFeature(BaseModel):
    name: str
    description: str

class TalentDefinition(BaseModel):
    name: str
    description: str

class Ability(BaseModel):
    name: str
    description: str

class SkillDefinition(BaseModel):
    name: str
    description: str
    ability: str
