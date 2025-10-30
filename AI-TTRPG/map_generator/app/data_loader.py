import json
import os
from typing import Dict, List, Any

# Global variables
TILE_DEFINITIONS: Dict[str, Any] = {}
GENERATION_ALGORITHMS: List[Dict[str, Any]] = []

def load_data():
    """Loads map generation data files."""
    global TILE_DEFINITIONS, GENERATION_ALGORITHMS

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, '..', 'data')

    print("--- Map Generator: Loading Data ---")

    try:
        # Load Tile Definitions
        tile_file = os.path.join(DATA_DIR, 'tile_definitions.json')
        with open(tile_file, 'r') as f:
            TILE_DEFINITIONS.clear()
            TILE_DEFINITIONS.update(json.load(f))
        print(f"Loaded {len(TILE_DEFINITIONS)} tile definitions.")

        # Load Generation Algorithms
        algo_file = os.path.join(DATA_DIR, 'generation_algorithms.json')
        with open(algo_file, 'r') as f:
            GENERATION_ALGORITHMS.clear()
            GENERATION_ALGORITHMS.extend(json.load(f).get("algorithms", []))
        print(f"Loaded {len(GENERATION_ALGORITHMS)} generation algorithms.")

    except FileNotFoundError as e:
        print(f"FATAL ERROR: Data file not found: {e.filename}")
        raise
    except json.JSONDecodeError as e:
        print(f"FATAL ERROR: Failed to decode JSON from {e.doc}")
        raise

    print("--- Map Generator: Data Loaded ---")