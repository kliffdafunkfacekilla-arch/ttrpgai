import httpx
from typing import Dict, Any, Optional
from . import schemas

# These URLs point to our other running services.
# We use the ports we assigned them.
RULES_ENGINE_URL = "http://127.0.0.1:8000"
CHARACTER_ENGINE_URL = "http://127.0.0.1:8001"
WORLD_ENGINE_URL = "http://127.0.0.1:8002"

async def _call_api(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    json: Optional[Dict] = None
) -> Dict:
    """Helper function to make async API calls."""
    try:
        if method.upper() == "GET":
            response = await client.get(url)
        elif method.upper() == "POST":
            response = await client.post(url, json=json)
        elif method.upper() == "PUT":
            response = await client.put(url, json=json)
        else:
            raise ValueError(f"Unsupported method: {method}")

        response.raise_for_status() # Raise exception on 4xx/5xx errors
        return response.json()
    except httpx.RequestError as e:
        # If a service is down, this will be triggered.
        raise Exception(f"API request failed to {e.request.url!r}: {e}")

# --- Orchestration Functions ---

async def get_character_context(
    char_id: int
) -> schemas.OrchestrationCharacterContext:
    """
    Gets the full character sheet from the character_engine.
    """
    url = f"{CHARACTER_ENGINE_URL}/v1/characters/{char_id}"
    async with httpx.AsyncClient() as client:
        data = await _call_api(client, "GET", url)
        return schemas.OrchestrationCharacterContext(**data)

async def get_world_location_context(
    location_id: int
) -> schemas.OrchestrationWorldContext:
    """
    Gets the full location details (map, NPCs, items, region)
    from the world_engine.
    """
    url = f"{WORLD_ENGINE_URL}/v1/locations/{location_id}"
    async with httpx.AsyncClient() as client:
        data = await _call_api(client, "GET", url)
        # Manually construct the response
        return schemas.OrchestrationWorldContext(
            id=data.get('id'),
            name=data.get('name'),
            region=data.get('region', {}),
            generated_map_data=data.get('generated_map_data'),
            npcs=data.get('npc_instances', []),
            items=data.get('item_instances', [])
        )

async def spawn_npc_in_world(spawn_request: schemas.OrchestrationSpawnNpc) -> Dict:
    """
    Tells the world_engine to spawn a new NPC.
    """
    url = f"{WORLD_ENGINE_URL}/v1/npcs/spawn"
    async with httpx.AsyncClient() as client:
        return await _call_api(
            client, "POST", url, json=spawn_request.dict()
        )

async def spawn_item_in_world(spawn_request: schemas.OrchestrationSpawnItem) -> Dict:
    """
    Tells the world_engine to spawn a new Item.
    """
    url = f"{WORLD_ENGINE_URL}/v1/items/spawn"
    async with httpx.AsyncClient() as client:
        return await _call_api(
            client, "POST", url, json=spawn_request.dict()
        )
