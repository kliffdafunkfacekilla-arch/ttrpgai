import requests
from typing import Dict, List

RULES_ENGINE_URL = "http://127.0.0.1:8000"

def get_all_ability_schools() -> List[str]:
    response = requests.get(f"{RULES_ENGINE_URL}/v1/lookup/all_ability_schools")
    response.raise_for_status()
    return response.json()

def get_base_resources() -> Dict[str, int]:
    # This is a placeholder. In a real scenario, this might be a more complex rule.
    return {"HP": 100, "MP": 50}
