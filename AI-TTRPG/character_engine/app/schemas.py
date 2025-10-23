from pydantic import BaseModel
from typing import Dict, List, Any

class CharacterCreateRequest(BaseModel):
    name: str
    kingdom: str
    f_stats: Dict[str, str]
    capstone_stat: str
    background_skills: List[str]

class CharacterResponse(BaseModel):
    id: int
    name: str
    kingdom: str
    character_sheet: Dict[str, Any]

    class Config:
        orm_mode = True
