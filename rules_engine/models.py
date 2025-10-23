# models.py
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Union

# --- API Request Models ---

class SkillCheckRequest(BaseModel):
    stat_modifier: int
    skill_rank: int
    dc: int = Field(default=15, description="Difficulty Class")

class AbilityCheckRequest(BaseModel):
    ability_school_rank: int
    associated_stat_modifier: int
    ability_tier: int = Field(gt=0, le=10, description="Tier 1-10")

class TalentLookupRequest(BaseModel):
    stats: Dict[str, int] = Field(description="Dictionary of all 12 stats and their scores")
    skills: Dict[str, int] = Field(description="Dictionary of all 72 skills and their ranks")

# --- API Response Models ---

class RollResult(BaseModel):
    roll_value: int
    total_value: int
    dc: int
    is_success: bool
    is_critical_success: bool = False
    is_critical_failure: bool = False
    sre_triggered: bool = False

class TalentInfo(BaseModel):
    name: str
    source: str
    effect: str

class FeatureStatsResponse(BaseModel):
    name: str
    mods: Dict[str, List[str]]

class SkillCategoryResponse(BaseModel):
    categories: Dict[str, List[str]]

class AbilitySchoolResponse(BaseModel):
    school: str
    resource_pool: str
    associated_stat: str
    tiers: List[Dict[str, Any]]
