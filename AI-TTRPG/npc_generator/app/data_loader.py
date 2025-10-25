import json
import os
from typing import Dict, Any

# Global variable to hold generation rules
GENERATION_RULES: Dict[str, Any] = {}

def load_rules():
    """Loads the generation_rules.json file."""
    global GENERATION_RULES

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_FILE = os.path.join(BASE_DIR, '..', 'data', 'generation_rules.json')

    print("--- NPC Generator: Loading Rules ---")

    try:
        with open(DATA_FILE, 'r') as f:
            GENERATION_RULES = json.load(f)
        print(f"Loaded NPC generation rules.")
    except FileNotFoundError:
        print(f"FATAL ERROR: Data file not found: {DATA_FILE}")
        raise
    except json.JSONDecodeError as e:
        print(f"FATAL ERROR: Failed to decode JSON from {DATA_FILE}")
        raise

    print("--- NPC Generator: Rules Loaded ---")