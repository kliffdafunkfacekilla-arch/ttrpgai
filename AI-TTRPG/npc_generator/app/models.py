from pydantic import BaseModel, Field
from typing import List, Dict, Optional

# --- API Request Model ---
class NpcGenerationRequest(BaseModel):
    """
    Inputs from the AI DM to generate an NPC template.
    """
    biome: Optional[str] = None
    kingdom: str = "mammal" # Default kingdom
    offense_style: str
    defense_style: str
    ability_focus: Optional[str] = None
    behavior: str = "aggressive"
    difficulty: str = "medium" # easy, medium, hard, boss
    custom_name: Optional[str] = None # Allow AI to name it

# --- API Response Model ---
class NpcTemplateResponse(BaseModel):
    """
    The generated NPC template/stat block.
    """
    generated_id: str # Unique ID based on inputs, e.g., procgen_forest_mammal_melee_hard_01
    name: str
    description: str
    stats: Dict[str, int]
    skills: Dict[str, int] # We'll need rules to derive these
    abilities: List[str] # List of ability names/IDs
    max_hp: int
    behavior_tags: List[str]
    loot_table_ref: Optional[str] = None # Suggests a loot table for world_engine