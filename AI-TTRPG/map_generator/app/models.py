from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# --- API Request Model ---
class MapGenerationRequest(BaseModel):
    """
    Inputs from the AI DM or story_engine.
    """
    tags: List[str] # e.g., ["forest", "outside", "ruins"]
    seed: Optional[str] = None # For reproducible generation
    width: Optional[int] = None # Optional override
    height: Optional[int] = None # Optional override

# --- API Response Model ---
class MapGenerationResponse(BaseModel):
    """
    The generated map data.
    """
    width: int
    height: int
    map_data: List[List[int]] # The 2D array of tile IDs
    seed_used: str # The actual seed used (generated if none provided)
    algorithm_used: str # Name of the algorithm from the rules file
    spawn_points: Optional[Dict[str, List[List[int]]]] = None # e.g., {"player": [[5,5]], "enemy": [[10,10],[12,8]]}