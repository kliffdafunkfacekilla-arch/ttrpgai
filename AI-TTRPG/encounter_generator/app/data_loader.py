import json
import os
from typing import List, Dict, Any

# Global variables to hold our loaded data
COMBAT_ENCOUNTERS: List[Dict[str, Any]] = []
SKILL_ENCOUNTERS: List[Dict[str, Any]] = []

def load_all_data():
    """
    Loads all encounter JSON files from the 'data' directory
    into the global variables.
    """
    global COMBAT_ENCOUNTERS, SKILL_ENCOUNTERS

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, '..', 'data')

    print("--- Encounter Generator: Loading Data ---")

    try:
        # Load Combat Encounters
        combat_file = os.path.join(DATA_DIR, 'combat_encounters.json')
        with open(combat_file, 'r') as f:
            COMBAT_ENCOUNTERS = json.load(f)
        print(f"Loaded {len(COMBAT_ENCOUNTERS)} combat encounters.")

        # Load Skill Encounters
        skill_file = os.path.join(DATA_DIR, 'skill_challenges.json')
        with open(skill_file, 'r') as f:
            SKILL_ENCOUNTERS = json.load(f)
        print(f"Loaded {len(SKILL_ENCOUNTERS)} skill challenges.")

    except FileNotFoundError as e:
        print(f"FATAL ERROR: Data file not found: {e.filename}")
        raise
    except json.JSONDecodeError as e:
        print(f"FATAL ERROR: Failed to decode JSON from {e.doc}")
        raise

    print("--- Encounter Generator: Data Loaded ---")