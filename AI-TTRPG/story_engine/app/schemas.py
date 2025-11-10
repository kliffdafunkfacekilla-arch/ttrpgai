from pydantic import BaseModel
from typing import List, Optional, Any, Dict

# --- StoryFlag ---
class StoryFlagBase(BaseModel):
    flag_name: str
    value: str

class StoryFlag(StoryFlagBase):
    id: int
    class Config:
        orm_mode = True

# --- ActiveQuest ---
class ActiveQuestBase(BaseModel):
    title: str
    description: Optional[str] = None
    steps: List[str]
    current_step: int = 1
    status: str = "active"
    campaign_id: int

class ActiveQuestCreate(ActiveQuestBase):
    pass

class ActiveQuest(ActiveQuestBase):
    id: int
    class Config:
        orm_mode = True

class ActiveQuestUpdate(BaseModel):
    # Only these fields can be updated
    current_step: Optional[int] = None
    status: Optional[str] = None
    description: Optional[str] = None
    steps: Optional[List[str]] = None

# --- Campaign ---
class CampaignBase(BaseModel):
    name: str
    main_plot_summary: Optional[str] = None

class CampaignCreate(CampaignBase):
    pass

class Campaign(CampaignBase):
    id: int
    # This will automatically include the quests
    active_quests: List[ActiveQuest] = []
    class Config:
        orm_mode = True

# --- Orchestration Schemas (for talking to other services) ---

class OrchestrationSpawnNpc(BaseModel):
    template_id: str
    location_id: int
    name_override: Optional[str] = None
    # --- ADD THIS LINE ---
    coordinates: Optional[Any] = None # e.g., [x, y]

class OrchestrationSpawnItem(BaseModel):
    template_id: str
    location_id: Optional[int] = None
    npc_id: Optional[int] = None
    quantity: int = 1
    # --- ADD THIS LINE ---
    coordinates: Optional[Any] = None # e.g., [x, y]

class OrchestrationCharacterContext(BaseModel):
    # This is a schema for the *response* from character_engine
    id: int
    name: str
    kingdom: str
    character_sheet: Dict[str, Any]

class OrchestrationWorldContext(BaseModel):
    # This is a schema for the *response* from world_engine
    id: int
    name: str
    region: Any # We can just grab the whole sub-object
    generated_map_data: Optional[Any] = None
    # --- ADDED/FIXED FIELDS ---
    ai_annotations: Optional[Dict[str, Any]] = None  # Ensure annotations pass through
    spawn_points: Optional[Dict[str, Any]] = None    # Ensure spawn points pass through
    # --- END ADDED/FIXED FIELDS ---
    npcs: List[Any] = []
    items: List[Any] = []

# --- ADD THESE SCHEMAS FOR INTERACTIONS ---
class InteractionRequest(BaseModel):
    """
    Request sent from player interface to interact with something.
    """
    actor_id: str # e.g., "player_1"
    location_id: int
    target_object_id: str # The key within ai_annotations, e.g., "door_1", "lever_A"
    interaction_type: str = "use" # e.g., "use", "examine", "talk" (expand later)

class InteractionResponse(BaseModel):
    """
    Response summarizing the outcome of an interaction.
    """
    success: bool
    message: str # Narrative description of what happened
    updated_annotations: Optional[Dict[str, Any]] = None # The new state if changed
    items_added: Optional[List[Dict]] = None # Items added to player inventory
    items_removed: Optional[List[Dict]] = None # Items removed from player inventory
    # Add other potential outcomes like quests updated, flags set, etc. later

# --- Ensure Combat Schemas are also present if not already added ---
# (Add these if they are missing from your schemas.py)
class CombatStartRequest(BaseModel):
    location_id: int
    player_ids: List[str] # e.g., ["player_1"]
    npc_template_ids: List[str] # e.g., ["goblin_scout", "goblin_scout"]

class CombatParticipantResponse(BaseModel):
    actor_id: str
    actor_type: str
    initiative_roll: int
    class Config:
        from_attributes = True # or orm_mode = True

class CombatEncounter(BaseModel):
    id: int
    location_id: int
    status: str # active, players_win, npcs_win, etc.
    turn_order: List[str]
    current_turn_index: int
    participants: List[CombatParticipantResponse] = []
    class Config:
        from_attributes = True # or orm_mode = True

class PlayerActionRequest(BaseModel):
    action: str # e.g., "attack", "move", "use_ability", "wait"
    target_id: Optional[str] = None # e.g., "npc_12", "player_2"
    ability_id: Optional[str] = None
    item_id: Optional[str] = None
    # Add other fields like ability_id, position, etc. as needed

class PlayerActionResponse(BaseModel):
    success: bool
    message: str
    log: list[str]
    new_turn_index: int
    combat_over: bool = False
