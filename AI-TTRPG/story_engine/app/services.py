# AI-TTRPG/story_engine/app/services.py
import httpx
from typing import Dict, Any, Optional, List
from fastapi import HTTPException
from . import schemas
import logging
import json
import asyncio
import random

RULES_ENGINE_URL = "http://127.0.0.1:8000"
CHARACTER_ENGINE_URL = "http://127.0.0.1:8001"
WORLD_ENGINE_URL = "http://127.0.0.1:8002"
# NPC_GENERATOR_URL REMOVED
MAP_GENERATOR_URL = "http://127.0.0.1:8006"

logger = logging.getLogger("uvicorn.error")

MAX_RETRIES = 5
RETRY_INITIAL_DELAY = 1.0

async def _call_api(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    json: Optional[Dict] = None,
    params: Optional[Dict] = None) -> Dict:
    log_url = url
    if params:
        log_url += "?" + "&".join(f"{k}={v}" for k, v in params.items())
    for attempt in range(MAX_RETRIES):
        try:
            print(f"Calling {method.upper()} {log_url} (Attempt {attempt + 1}/{MAX_RETRIES})")
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
            response.raise_for_status()
            if response.status_code == 204:
                 return {"success": True}
            return response.json()
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            is_unavailable = False
            if isinstance(e, httpx.RequestError):
                 error_msg = f"API RequestError to {e.request.url!r}: {e}"
                 is_unavailable = True
            elif isinstance(e, httpx.HTTPStatusError) and e.response.status_code in [500, 503]:
                 error_msg = f"API HTTPStatusError {e.response.status_code} from {e.request.url!r}: {e.response.text}"
                 is_unavailable = True
            else:
                 error_msg = f"Non-retryable API HTTPStatusError {e.response.status_code} from {e.request.url!r}: {e.response.text}"
                 print(f"ERROR: {error_msg}")
                 raise HTTPException(status_code=e.response.status_code, detail=f"Error from {e.request.url!r}: {e.response.text}")
            if is_unavailable and attempt < MAX_RETRIES - 1:
                delay = RETRY_INITIAL_DELAY * (2 ** attempt) + random.uniform(0, 0.5)
                print(f"WARNING: {error_msg}. Retrying in {delay:.2f}s...")
                await asyncio.sleep(delay)
                continue
            else:
                print(f"FATAL ERROR: {error_msg}")
                raise HTTPException(status_code=503, detail=f"Service unavailable/Max retries reached: {e.request.url!r}. Details: {e}")
        except Exception as e:
            error_msg = f"Unexpected error calling {url}: {e}"
            print(f"FATAL ERROR: {error_msg}")
            raise HTTPException(status_code=500, detail=error_msg)
    raise HTTPException(status_code=500, detail="Internal API Call logic failed before returning.")

async def roll_initiative(client: httpx.AsyncClient, endurance: int, reflexes: int, fortitude: int, logic: int, intuition: int, willpower: int) -> Dict:
    url = f"{RULES_ENGINE_URL}/v1/roll/initiative"
    request_data = {
        "endurance": endurance, "reflexes": reflexes, "fortitude": fortitude,
        "logic": logic, "intuition": intuition, "willpower": willpower
    }
    return await _call_api(client, "POST", url, json=request_data)

async def get_npc_generation_params(client: httpx.AsyncClient, template_id: str) -> Dict:
    url = f"{RULES_ENGINE_URL}/v1/lookup/npc_template/{template_id}"
    return await _call_api(client, "GET", url)

async def get_item_template_params(client: httpx.AsyncClient, item_id: str) -> Dict:
    """Calls rules_engine to get definition for an item template ID."""
    url = f"{RULES_ENGINE_URL}/v1/lookup/item_template/{item_id}"
    return await _call_api(client, "GET", url)

# --- MODIFIED: Consolidated NPC Generation Call to Rules Engine ---
async def generate_npc_template(client: httpx.AsyncClient, generation_request: Dict) -> Dict:
    """Calls the Rules Engine (now the single source) to generate a full NPC template."""
    url = f"{RULES_ENGINE_URL}/v1/generate/npc_template"
    return await _call_api(client, "POST", url, json=generation_request)

async def spawn_npc_in_world(client: httpx.AsyncClient, spawn_request: schemas.OrchestrationSpawnNpc) -> Dict:
    url = f"{WORLD_ENGINE_URL}/v1/npcs/spawn"
    return await _call_api(client, "POST", url, json=spawn_request.dict())

async def update_location_annotations(client: httpx.AsyncClient, location_id: int, annotations: Dict[str, Any]) -> Dict:
    url = f"{WORLD_ENGINE_URL}/v1/locations/{location_id}/annotations"
    payload = {"ai_annotations": annotations}
    return await _call_api(client, "PUT", url, json=payload)

async def get_world_location_context(client: httpx.AsyncClient, location_id: int) -> Dict:
    url = f"{WORLD_ENGINE_URL}/v1/locations/{location_id}"
    location_data = await _call_api(client, "GET", url)
    map_data = location_data.get("generated_map_data")
    if isinstance(map_data, str):
        try:
            map_data = json.loads(map_data)
        except json.JSONDecodeError:
            logger.error("Failed to decode map data string as JSON. Treating as None.")
            map_data = None
    location_data["generated_map_data"] = map_data
    is_placeholder_map = map_data and len(map_data) == 3 and len(map_data[0]) == 3
    if location_data.get("name") == "STARTING_ZONE" and (map_data is None or is_placeholder_map):
        logger.info(f"First load of STARTING_ZONE (Location {location_id}). Running dynamic setup...")
        try:
            map_response = await _call_api(client, "POST", f"{MAP_GENERATOR_URL}/v1/generate", json={"tags": ["forest", "outside", "clearing"]})
            new_map_data = map_response.get("map_data")
            enemy_spawn = map_response.get("spawn_points", {}).get("enemy", [[10, 10]])[0]
            template_lookup = await get_npc_generation_params(client, "goblin_scout")
            generation_params = template_lookup.get("generation_params")
            if not generation_params:
                raise Exception("Missing NPC generation params.")
            full_npc_template = await generate_npc_template(client, generation_params)
            npc_max_hp = full_npc_template.get("max_hp", 10)
            spawn_npc_data = schemas.OrchestrationSpawnNpc(
                template_id="goblin_scout",
                location_id=location_id,
                coordinates=enemy_spawn,
                name_override=None,
                current_hp=npc_max_hp,
                max_hp=npc_max_hp,
                behavior_tags=full_npc_template.get("behavior_tags", ["aggressive"])
            )
            await spawn_npc_in_world(client, spawn_npc_data)
            spawn_item_data = schemas.OrchestrationSpawnItem(
                template_id="item_iron_key",
                location_id=location_id,
                npc_id=None,
                coordinates=[10, 10],
                quantity=1
            )
            await _call_api(client, "POST", f"{WORLD_ENGINE_URL}/v1/items/spawn", json=spawn_item_data.dict())
            annotations = {
                "door_1": {
                    "type": "door", "status": "locked", "key_id": "item_iron_key", "coordinates": [5, 3]
                }
            }
            await update_location_annotations(client, location_id, annotations)
            map_update_payload = {
                "generated_map_data": new_map_data,
                "map_seed": map_response.get("seed_used"),
                "spawn_points": map_response.get("spawn_points")
            }
            await _call_api(client, "PUT", f"{WORLD_ENGINE_URL}/v1/locations/{location_id}/map", json=map_update_payload)
            location_data = await _call_api(client, "GET", url)
        except Exception as e:
            logger.exception(f"FATAL: Failed to dynamically set up STARTING_ZONE: {e}. Returning possibly empty data.")
    return location_data
