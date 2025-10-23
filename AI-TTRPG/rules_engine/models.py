from pydantic import BaseModel
from typing import List, Optional

# API Models
class SkillCheckRequest(BaseModel):
    stat_modifier: int
    skill_rank: int
    dc: int

class SkillCheckResponse(BaseModel):
    success: bool
    roll: int

# Game Data Models

# Ability Schools
class AbilityTier(BaseModel):
    tier: str
    description: str

class AbilityBranch(BaseModel):
    branch: str
    tiers: List[AbilityTier]

class AbilitySchool(BaseModel):
    school: str
    resource: str
    branches: List[AbilityBranch]

# Skills
class CombatSkill(BaseModel):
    stat: str
    armor_skill: str
    melee_skill: str
    ranged_skill: str

class NonCombatSkill(BaseModel):
    stat: str
    conversational_skill: str
    utility_skill: str
    lore_skill: str

class UrbanArchetype(BaseModel):
    stat: str
    urban_archetype: str
    conversational_skill: str
    utility_skill: str
    lore: str

# Crafting
class CraftingDiscipline(BaseModel):
    name: str
    description: str

# Character Creation
class DevotionChoice(BaseModel):
    category: str
    choice_num: int
    name: str
    description: str
    skill_1: str
    skill_2: str

class BirthCircumstance(BaseModel):
    choice_num: int
    skill: str
    name: str
    description: str

class ChildhoodDevelopment(BaseModel):
    choice_num: int
    skill: str
    name: str
    description: str

class ComingOfAgeEvent(BaseModel):
    choice_num: int
    skill: str
    name: str
    description: str

class CharacterCreation(BaseModel):
    devotion: List[DevotionChoice]
    birth_circumstance: List[BirthCircumstance]
    childhood_development: List[ChildhoodDevelopment]
    coming_of_age: List[ComingOfAgeEvent]

# Talents
class SingleStatTalent(BaseModel):
    stat: str
    talent_name: str
    effect: str
    associated_resource_pool: Optional[str] = None


class SingleSkillTalent(BaseModel):
    armor_skill: Optional[str] = None
    skill: Optional[str] = None
    stat_focus: str
    talent_name: str
    prerequisite_mt: str
    focus: str
    effect: str

class DualStatTalent(BaseModel):
    paired_stat: str
    synergy_focus: str
    tier: str
    talent_name: str
    effect: str

class Talents(BaseModel):
    single_stat_mastery: List[SingleStatTalent]
    single_skill_mastery: List[SingleSkillTalent]
    dual_stat_focus: List[DualStatTalent]

class Stat(BaseModel):
    name: str
    description: str

