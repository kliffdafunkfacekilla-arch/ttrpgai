# app/schemas.py
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

# --- NEW SCHEMAS ---
class FeatureChoice(BaseModel):
    """Represents a single feature choice made by the user."""
    feature_id: str # e.g., "F1", "F9"
    choice_name: str # e.g., "Predator's Gaze", "Capstone: +2 Might"

class CharacterCreate(BaseModel):
    """
    This is the new complex object sent from the frontend
    to create a new character.
    """
    name: str
    kingdom: str
    # This list should contain all 9 feature choices (F1-F8 + F9)
    feature_choices: List[FeatureChoice]
    background_talent: str
    ability_school: str
    ability_talent: str

# --- UNCHANGED SCHEMAS ---
class CharacterBase(BaseModel):
    name: str
    kingdom: Optional[str] = None
    level: int = 1

class Character(CharacterBase):
    id: str
    class Config:
        from_attributes = True

class CharacterContextResponse(CharacterBase):
    """
    This is the full character sheet/context object returned
    to the frontend. It is UNCHANGED.
    """
    id: str
    stats: Dict[str, int]
    skills: Dict[str, int]
    max_hp: int
    current_hp: int
    resource_pools: Dict[str, Any] # e.g., {"Stamina": {"current": 10, "max": 10}, ...}
    talents: List[str]
    abilities: List[str]
    inventory: Dict[str, Any]
    equipment: Dict[str, Any]
    status_effects: List[str]
    injuries: List[Dict[str, Any]]
    position_x: int
    position_y: int

    class Config:
        from_attributes = True

class InventoryItem(BaseModel):
    item_id: str
    quantity: int

class InventoryUpdateRequest(BaseModel):
    item_id: str
    quantity: int

class ApplyDamageRequest(BaseModel):
    damage_amount: int
    damage_type: Optional[str] = None

class ApplyStatusRequest(BaseModel):
    status_id: str

class LocationUpdateRequest(BaseModel):
    location_id: int
    coordinates: List[int]
    duration: Optional[int] = None
