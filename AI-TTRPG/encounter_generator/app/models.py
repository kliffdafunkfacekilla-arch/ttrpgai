from pydantic import BaseModel
from typing import List, Dict, Any, Optional

# --- API Request Model ---
class EncounterRequest(BaseModel):
    """
    This is what the AI DM sends to us.
    It provides a list of tags to filter by.
    """
    # e.g., ["forest", "medium", "combat"]
    tags: List[str]

# --- API Response Models ---
# These are the structured objects we send back.

class CombatEncounterResponse(BaseModel):
    type: str = "combat"
    id: str
    description: str
    npcs_to_spawn: List[str]

class SkillChallengeStage(BaseModel):
    description: str
    skill: str
    dc: int

class SkillEncounterResponse(BaseModel):
    type: str = "skill"
    id: str
    title: str
    description: str
    success_threshold: int
    stages: List[SkillChallengeStage]

# We can add SocialEncounterResponse later