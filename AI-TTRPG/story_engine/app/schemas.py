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

class OrchestrationSpawnItem(BaseModel):
    template_id: str
    location_id: Optional[int] = None
    npc_id: Optional[int] = None
    quantity: int = 1

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
    npcs: List[Any] = []
    items: List[Any] = []