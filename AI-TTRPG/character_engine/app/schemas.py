from pydantic import BaseModel
from typing import Dict, List, Any

class CharacterCreateRequest(BaseModel):
    name: str
    kingdom: str
    f_stats: Dict[str, str]
    capstone_stat: str
    background_skills: List[str]

class InventoryItem(BaseModel):
    item_id: str # Corresponds to template_id in world_engine/item_templates.json
    quantity: int

class InventoryUpdateRequest(BaseModel):
    item_id: str
    quantity: int

class CharacterResponse(BaseModel):
    id: int
    name: str
    kingdom: str
    character_sheet: Dict[str, Any]

    class Config:
        from_attributes = True


class ApplyDamageRequest(BaseModel):
    damage_amount: int
    damage_type: str | None = None

class ApplyStatusRequest(BaseModel):
    status_id: str

# --- ADD THIS NEW SCHEMA ---
class LocationUpdateRequest(BaseModel):
    location_id: int
    coordinates: List[int] # [x, y]
    duration: int | None = None # Or maybe specific end condition
