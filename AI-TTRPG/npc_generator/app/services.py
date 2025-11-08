import httpx
import logging
from typing import Dict, Any

logger = logging.getLogger("uvicorn.error")

RULES_ENGINE_URL = "http://127.0.0.1:8000"

async def _call_api(client: httpx.AsyncClient, method: str, url: str, **kwargs) -> Dict[str, Any]:
    """Helper function to call an API and handle responses."""
    try:
        response = await client.request(method, url, **kwargs)
        response.raise_for_status()  # Raise exception on 4xx/5xx errors
        return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"API HTTPStatusError {e.response.status_code} from URL('{e.request.url}'): {e.response.text}")
        raise
    except httpx.RequestError as e:
        logger.error(f"API RequestError calling URL('{e.request.url}'): {e}")
        raise
    except Exception as e:
        logger.exception(f"Unexpected error in _call_api for URL('{url}'): {e}")
        raise

async def fetch_all_rules_data(client: httpx.AsyncClient) -> Dict[str, Any]:
    """
    Fetches all necessary game data from the rules_engine.
    This is a dependency for the generator.
    """
    logger.info("NPC Generator fetching all rules data from Rules Engine...")

    # Define all the endpoints to fetch
    endpoints = {
        "stats_and_skills": "/v1/lookup/stats_and_skills",
        "kingdom_features": "/v1/lookup/creation/kingdom_features",
        "all_skills": "/v1/lookup/all_skills",
    }

    results = {}

    for key, endpoint in endpoints.items():
        try:
            url = f"{RULES_ENGINE_URL}{endpoint}"
            data = await _call_api(client, "GET", url)
            results[key] = data
            logger.info(f"Successfully fetched '{key}' data.")
        except Exception as e:
            logger.error(f"Failed to fetch '{key}' data from {endpoint}: {e}")
            results[key] = {} # Return empty dict on failure for this key

    logger.info("Finished fetching all rules data.")
    return results
