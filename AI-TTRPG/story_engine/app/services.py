# --- ADD OR UPDATE THESE IMPORTS ---
import httpx
from typing import Dict, Any, Optional, List
from fastapi import HTTPException # Import HTTPException for error handling
from . import schemas # Schemas from story_engine
import logging

# --- Ensure these URLs are defined ---
RULES_ENGINE_URL = "http://127.0.0.1:8000"
CHARACTER_ENGINE_URL = "http://127.0.0.1:8001"
WORLD_ENGINE_URL = "http://127.0.0.1:8002"
NPC_GENERATOR_URL = "http://127.0.0.1:8005"
MAP_GENERATOR_URL = "http://127.0.0.1:8006"

logger = logging.getLogger("uvicorn.error")

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

async def get_npc_generation_params(client: httpx.AsyncClient, template_id: str) -> Dict:
    """Calls rules_engine to get generation params for an NPC template ID."""
    url = f"{RULES_ENGINE_URL}/v1/lookup/npc_template/{template_id}"
    return await _call_api(client, "GET", url)

async def get_item_template_params(client: httpx.AsyncClient, item_id: str) -> Dict:
    """Calls rules_engine to get definition for an item template ID."""
    url = f"{RULES_ENGINE_URL}/v1/lookup/item_template/{item_id}"
    return await _call_api(client, "GET", url)

# --- Calls to npc_generator ---
async def generate_npc_template(client: httpx.AsyncClient, generation_request: Dict) -> Dict:
    """Calls npc_generator to generate a full NPC template."""
    url = f"{NPC_GENERATOR_URL}/v1/generate"
    return await _call_api(client, "POST", url, json=generation_request)

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

async def get_world_location_context(client: httpx.AsyncClient, location_id: int) -> Dict:
    """Gets location data (including NPCs, items, region) from world_engine."""
    url = f"{WORLD_ENGINE_URL}/v1/locations/{location_id}"
    location_data = await _call_api(client, "GET", url)

    # --- START OF NEW FIX ---
    # Check if this is the STARTING_ZONE and if its map is the placeholder or just missing (None)
    map_data = location_data.get("generated_map_data")
    placeholder_map = [[1, 1, 1], [1, 0, 1], [1, 1, 1]]

    if location_data.get("name") == "STARTING_ZONE" and (map_data == placeholder_map or map_data is None):
        logger.info(f"First load of STARTING_ZONE (Location {location_id}). Running dynamic setup...")
        try:
            # 1. Generate a new map
            logger.info("Calling Map Generator...")
            map_response = await _call_api(client, "POST", f"{MAP_GENERATOR_URL}/v1/generate", json={"tags": ["forest", "outside", "clearing"]})
            new_map_data = map_response.get("map_data")
            enemy_spawn = map_response.get("spawn_points", {}).get("enemy", [[10, 10]])[0]

            # 2. Spawn a Goblin
            logger.info(f"Spawning Goblin at {enemy_spawn}...")
            template_lookup = await get_npc_generation_params(client, "goblin_scout")
            gen_params = template_lookup.get("generation_params")
            full_template = await generate_npc_template(client, gen_params)
            max_hp = full_template.get("max_hp", 10)
            spawn_npc_data = schemas.OrchestrationSpawnNpc(
                template_id="goblin_scout",
                location_id=location_id,
                coordinates=enemy_spawn,
                name_override=None,
                current_hp=max_hp,
                max_hp=max_hp,
                behavior_tags=full_template.get("behavior_tags", ["aggressive"])
            )
            await spawn_npc_in_world(client, spawn_npc_data)

            # 3. Spawn the Key
            logger.info("Spawning Iron Key at [10, 10]...")
            spawn_item_data = schemas.OrchestrationSpawnItem(
                template_id="item_iron_key",
                location_id=location_id,
                npc_id=None,
                coordinates=[10, 10],
                quantity=1
            )
            await _call_api(client, "POST", f"{WORLD_ENGINE_URL}/v1/items/spawn", json=spawn_item_data.dict())

            # 4. Create Annotations (the locked door)
            logger.info("Creating locked door annotation at [5, 3]...")
            annotations = {
                "door_1": {
                    "type": "door",
                    "status": "locked",
                    "key_id": "item_iron_key",
                    "coordinates": [5, 3]
                }
            }
            await update_location_annotations(client, location_id, annotations)

            # 5. Save the new map to the location
            logger.info("Saving generated map to World Engine...")
            map_update_payload = {
                "generated_map_data": new_map_data,
                "map_seed": map_response.get("seed_used")
            }
            await _call_api(client, "PUT", f"{WORLD_ENGINE_URL}/v1/locations/{location_id}/map", json=map_update_payload)

            # 6. Re-fetch the fully populated location data
            logger.info("Dynamic setup complete. Re-fetching location context.")
            location_data = await _call_api(client, "GET", url)

        except Exception as e:
            logger.exception(f"Failed to dynamically set up STARTING_ZONE: {e}")
            # Don't raise, just return the (mostly empty) location data
    # --- END OF NEW FIX ---

    return location_data # Return raw dict

async def spawn_npc_in_world(client: httpx.AsyncClient, spawn_request: schemas.OrchestrationSpawnNpc) -> Dict:
    """Tells the world_engine to spawn a new NPC."""
    url = f"{WORLD_ENGINE_URL}/v1/npcs/spawn"
    return await _call_api(client, "POST", url, json=spawn_request.dict())

async def spawn_item_in_world(client: httpx.AsyncClient, spawn_request: schemas.OrchestrationSpawnItem) -> Dict:
    """Tells the world_engine to spawn a new item."""
    url = f"{WORLD_ENGINE_URL}/v1/items/spawn"
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
# --- Add this function within the 'Calls to world_engine' section ---
async def update_location_annotations(client: httpx.AsyncClient, location_id: int, annotations: Dict[str, Any]) -> Dict:
    """Calls world_engine to update the AI annotations for a location."""
    url = f"{WORLD_ENGINE_URL}/v1/locations/{location_id}/annotations"
    payload = {"ai_annotations": annotations}
    # Assuming world_engine endpoint expects {"ai_annotations": {...}}
    return await _call_api(client, "PUT", url, json=payload)

# --- Ensure other necessary functions from previous steps are present ---
# (Like get_world_location_context, add_item_to_character (needs adding?), etc.)
# --- Add this function if not present - Needed for interaction results ---
async def add_item_to_character(client: httpx.AsyncClient, char_id: str, item_id: str, quantity: int) -> Dict:
    """Calls character_engine to add an item to a character's inventory."""
    # Ensure char_id is just the number if character_engine expects that
    char_db_id = -1
    try:
        # Assumes format "player_X"
        char_db_id = int(char_id.split('_')[1])
    except (IndexError, ValueError):
        raise HTTPException(status_code=400, detail=f"Invalid character ID format for service call: {char_id}")

    url = f"{CHARACTER_ENGINE_URL}/v1/characters/{char_db_id}/inventory/add"
    payload = {"item_id": item_id, "quantity": quantity}
    return await _call_api(client, "POST", url, json=payload)

async def remove_item_from_character(client: httpx.AsyncClient, char_id: str, item_id: str, quantity: int) -> Dict:
    """Calls character_engine to remove an item from a character's inventory."""
    char_db_id = -1
    try:
        char_db_id = int(char_id.split('_')[1])
    except (IndexError, ValueError):
        raise HTTPException(status_code=400, detail=f"Invalid character ID format for service call: {char_id}")

    url = f"{CHARACTER_ENGINE_URL}/v1/characters/{char_db_id}/inventory/remove" # Uses the existing endpoint
    payload = {"item_id": item_id, "quantity": quantity}
    return await _call_api(client, "POST", url, json=payload) # Assumes POST method matches character_engine
[
  {
    "op": "replace",
    "path": "/get_world_location_context/async_with/if_condition",
    "value": "map_data = location_data.get(\"generated_map_data\")\nplaceholder_map = [[1, 1, 1], [1, 0, 1], [1, 1, 1]]\nif location_data.get(\"name\") == \"STARTING_ZONE\" and (map_data == placeholder_map or map_data is None):"
  }
]