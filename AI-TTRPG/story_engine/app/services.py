# --- ADD OR UPDATE THESE IMPORTS ---
import httpx
from typing import Dict, Any, Optional, List
from fastapi import HTTPException # Import HTTPException for error handling
from . import schemas # Schemas from story_engine

# --- Ensure these URLs are defined ---
RULES_ENGINE_URL = "http://127.0.0.1:8000"
CHARACTER_ENGINE_URL = "http://127.0.0.1:8001"
WORLD_ENGINE_URL = "http://127.0.0.1:8002"

# --- Ensure the _call_api helper function exists ---
async def _call_api(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    json: Optional[Dict] = None,
    params: Optional[Dict] = None # Added params for GET requests
) -> Dict:
    """Helper function to make async API calls with error handling."""
    log_url = url
    if params:
        log_url += "?" + "&".join(f"{k}={v}" for k, v in params.items())

    print(f"Calling {method.upper()} {log_url}") # Basic logging
    try:
        if method.upper() == "GET":
            response = await client.get(url, params=params)
        elif method.upper() == "POST":
            response = await client.post(url, json=json)
        elif method.upper() == "PUT":
            response = await client.put(url, json=json)
        elif method.upper() == "DELETE":
             response = await client.delete(url)
        else:
            raise ValueError(f"Unsupported method: {method}")

        response.raise_for_status() # Raise exception on 4xx/5xx errors

        # Handle cases where response might be empty (like DELETE 204 No Content)
        if response.status_code == 204:
             return {"success": True}

        return response.json()
    except httpx.RequestError as e:
        error_msg = f"API RequestError to {e.request.url!r}: {e}"
        print(f"ERROR: {error_msg}")
        raise HTTPException(status_code=503, detail=f"Service unavailable: {e.request.url!r}. Details: {e}")
    except httpx.HTTPStatusError as e:
        error_msg = f"API HTTPStatusError {e.response.status_code} from {e.request.url!r}: {e.response.text}"
        print(f"ERROR: {error_msg}")
        # Forward the status code and detail from the downstream service
        raise HTTPException(status_code=e.response.status_code, detail=f"Error from {e.request.url!r}: {e.response.text}")
    except Exception as e:
        error_msg = f"Unexpected error calling {url}: {e}"
        print(f"ERROR: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)

# --- ADD THE FOLLOWING NEW FUNCTIONS ---
# --- Calls to rules_engine ---
async def roll_initiative(client: httpx.AsyncClient, endurance: int, agility: int, fortitude: int, logic: int, intuition: int, willpower: int) -> Dict:
    """Calls rules_engine to roll initiative."""
    url = f"{RULES_ENGINE_URL}/v1/roll/initiative"
    request_data = {
        "endurance": endurance, "agility": agility, "fortitude": fortitude,
        "logic": logic, "intuition": intuition, "willpower": willpower
    }
    return await _call_api(client, "POST", url, json=request_data)

async def roll_contested_attack(client: httpx.AsyncClient, attack_params: Dict) -> Dict:
    """Calls rules_engine for a contested attack roll."""
    url = f"{RULES_ENGINE_URL}/v1/roll/contested_attack"
    # Ensure attack_params matches the ContestedAttackRequest schema in rules_engine
    return await _call_api(client, "POST", url, json=attack_params)

async def calculate_damage(client: httpx.AsyncClient, damage_params: Dict) -> Dict:
    """Calls rules_engine to calculate damage."""
    url = f"{RULES_ENGINE_URL}/v1/calculate/damage"
    # Ensure damage_params matches the DamageRequest schema in rules_engine
    return await _call_api(client, "POST", url, json=damage_params)

async def get_injury_effects(client: httpx.AsyncClient, location: str, sub_location: str, severity: int) -> Dict:
    """Calls rules_engine to get injury effects."""
    url = f"{RULES_ENGINE_URL}/v1/lookup/injury_effects"
    request_data = {"location": location, "sub_location": sub_location, "severity": severity}
    return await _call_api(client, "POST", url, json=request_data)

async def get_weapon_data(client: httpx.AsyncClient, category_name: str, weapon_type: str) -> Dict:
     """Calls rules_engine to get weapon data (melee or ranged)."""
     if weapon_type not in ["melee", "ranged"]:
         raise ValueError("Invalid weapon_type specified. Use 'melee' or 'ranged'.")
     url = f"{RULES_ENGINE_URL}/v1/lookup/{weapon_type}_weapon/{category_name}"
     return await _call_api(client, "GET", url)

async def get_armor_data(client: httpx.AsyncClient, category_name: str) -> Dict:
     """Calls rules_engine to get armor data."""
     url = f"{RULES_ENGINE_URL}/v1/lookup/armor/{category_name}"
     return await _call_api(client, "GET", url)

# --- Calls to character_engine ---
async def get_character_context(client: httpx.AsyncClient, char_id: str) -> Dict: # Changed char_id type hint
    """Gets the full character sheet from the character_engine."""
    char_db_id = int(char_id.split('_')[1])
    url = f"{CHARACTER_ENGINE_URL}/v1/characters/{char_db_id}"
    data = await _call_api(client, "GET", url)
    # No need to wrap in schemas.OrchestrationCharacterContext here, return raw dict
    return data

async def apply_damage_to_character(client: httpx.AsyncClient, char_id: str, damage_amount: int, damage_type: Optional[str] = None) -> Dict:
    """Calls character_engine to apply damage. (Endpoint needs creation)"""
    char_db_id = int(char_id.split('_')[1])
    url = f"{CHARACTER_ENGINE_URL}/v1/characters/{char_db_id}/apply_damage" # Assumed endpoint
    payload = {"damage_amount": damage_amount, "damage_type": damage_type}
    return await _call_api(client, "PUT", url, json=payload)

async def apply_status_to_character(client: httpx.AsyncClient, char_id: str, status_id: str, duration: Optional[int] = None) -> Dict:
    """Calls character_engine to apply a status effect. (Endpoint needs creation)"""
    char_db_id = int(char_id.split('_')[1])
    url = f"{CHARACTER_ENGINE_URL}/v1/characters/{char_db_id}/apply_status" # Assumed endpoint
    payload = {"status_id": status_id, "duration": duration}
    return await _call_api(client, "PUT", url, json=payload)

# --- Calls to world_engine ---
async def get_npc_context(client: httpx.AsyncClient, npc_id: int) -> Dict:
    """Gets NPC instance data from the world_engine."""
    url = f"{WORLD_ENGINE_URL}/v1/npcs/{npc_id}"
    return await _call_api(client, "GET", url)

async def get_world_location_context(client: httpx.AsyncClient, location_id: int) -> Dict: # Return raw Dict
    """Gets location data (including NPCs, items, region) from world_engine."""
    url = f"{WORLD_ENGINE_URL}/v1/locations/{location_id}"
    return await _call_api(client, "GET", url) # Return raw dict

async def spawn_npc_in_world(client: httpx.AsyncClient, spawn_request: schemas.OrchestrationSpawnNpc) -> Dict:
    """Tells the world_engine to spawn a new NPC."""
    url = f"{WORLD_ENGINE_URL}/v1/npcs/spawn"
    return await _call_api(client, "POST", url, json=spawn_request.dict())

async def apply_damage_to_npc(client: httpx.AsyncClient, npc_id: int, new_hp: int) -> Dict:
    """Calls world_engine to update NPC HP."""
    url = f"{WORLD_ENGINE_URL}/v1/npcs/{npc_id}"
    return await _call_api(client, "PUT", url, json={"current_hp": new_hp})

async def apply_status_to_npc(client: httpx.AsyncClient, npc_id: int, status_list: List[str]) -> Dict:
    """Calls world_engine to update NPC status effects list."""
    url = f"{WORLD_ENGINE_URL}/v1/npcs/{npc_id}"
    return await _call_api(client, "PUT", url, json={"status_effects": status_list})

    # --- Add other needed service calls (e.g., delete_item_in_world, add_item_to_character) ---
