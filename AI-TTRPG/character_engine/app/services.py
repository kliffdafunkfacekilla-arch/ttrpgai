# services.py
import httpx # Use httpx for async requests
from typing import Dict, List, Any
import logging

# --- Configuration ---
RULES_ENGINE_URL = "http://127.0.0.1:8000" # URL of your running Rules Engine
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Helper to Call Rules Engine ---
async def _call_rules_engine(method: str, endpoint: str, params: Dict = None, json_data: Dict = None) -> Any:
    """Generic async helper to call the Rules Engine."""
    url = f"{RULES_ENGINE_URL}{endpoint}"
    try:
        async with httpx.AsyncClient() as client:
            logger.info(f"Calling Rules Engine: {method} {url}")
            if method.upper() == "GET":
                response = await client.get(url, params=params)
            elif method.upper() == "POST":
                response = await client.post(url, json=json_data, params=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status() # Raise exception for 4xx/5xx errors
            logger.info(f"Rules Engine response status: {response.status_code}")
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"Error connecting to Rules Engine at {e.request.url!r}: {e}")
        # Re-raise as an HTTPException for FastAPI to handle
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail=f"Rules Engine service unavailable: {e}")
    except httpx.HTTPStatusError as e:
        logger.error(f"Rules Engine returned error {e.response.status_code}: {e.response.text}")
        from fastapi import HTTPException
        raise HTTPException(status_code=e.response.status_code, detail=f"Rules Engine error: {e.response.text}")

# --- Specific Service Functions ---

async def get_feature_stat_mods(feature_name: str) -> Dict[str, List[str]]:
    """Fetches stat mods for a feature from the Rules Engine."""
    response = await _call_rules_engine(
        "GET",
        "/v1/lookup/kingdom_feature_stats",
        params={"feature_name": feature_name}
    )
    return response.get("mods", {})

async def get_all_skill_names() -> List[str]:
    """Gets the master list of all 72 skill names."""
    response = await _call_rules_engine("GET", "/v1/lookup/all_skills")
    return list(response.keys()) # Expects dict {skill: {category:..., stat:...}}

async def get_all_stats_names() -> List[str]:
    """Gets the list of all 12 stat names."""
    return await _call_rules_engine("GET", "/v1/lookup/all_stats")

async def get_all_ability_schools() -> List[str]:
    """Gets the list of all 12 ability school names."""
    return await _call_rules_engine("GET", "/v1/lookup/all_ability_schools")

async def get_eligible_talents(stats: Dict[str, int], skills: Dict[str, int]) -> List[Dict]:
    """Fetches eligible talents from the Rules Engine."""
    request_data = {"stats": stats, "skills": skills} # Pass skill ranks directly
    return await _call_rules_engine(
        "POST",
        "/v1/lookup/talents",
        json_data=request_data
    )

async def get_base_vitals_from_rules(stats: Dict[str, int]) -> Dict:
    """Fetches calculated Max HP and Resource Pools from the Rules Engine."""
    request_data = {"stats": stats}
    response = await _call_rules_engine(
        "POST",
        "/v1/calculate/base_vitals",
        json_data=request_data
    )
    # response will be {"max_hp": X, "resources": {...}}
    return response

# --- Local Calculation Helpers ---
def calculate_modifier(score: int) -> int:
    """Calculates the attribute modifier based on the score."""
    return (score - 10) // 2