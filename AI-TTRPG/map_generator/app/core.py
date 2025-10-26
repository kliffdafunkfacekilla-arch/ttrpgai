import random
from typing import List, Dict, Optional, Any
from . import models
from .data_loader import GENERATION_ALGORITHMS, TILE_DEFINITIONS

def select_algorithm(tags: List[str]) -> Optional[Dict[str, Any]]:
    """Finds a generation algorithm matching the input tags."""
    tag_set = set(t.lower() for t in tags)
    possible_matches = []
    for algo in GENERATION_ALGORITHMS:
        required_tags = set(t.lower() for t in algo.get("required_tags", []))
        if required_tags.issubset(tag_set):
            possible_matches.append(algo)

    if not possible_matches:
        return None
    # Maybe add logic here to pick the 'best' match if multiple found
    return random.choice(possible_matches)

def run_generation(algorithm: Dict[str, Any], seed: str, width_override: Optional[int], height_override: Optional[int]) -> models.MapGenerationResponse:
    """
    Executes the chosen procedural generation algorithm.
    *** THIS IS A PLACEHOLDER - ACTUAL ALGORITHMS NEED IMPLEMENTATION ***
    """
    random.seed(seed) # Use the seed for reproducibility

    algo_name = algorithm.get("name", "Unknown Algorithm")
    params = algorithm.get("parameters", {})

    width = width_override or params.get("width", 20) # Default size
    height = height_override or params.get("height", 15)

    print(f"Running generation using algorithm: {algo_name} with seed: {seed}")

    # --- Placeholder Generation Logic ---
    # Replace this with actual calls to your chosen algorithms
    # (e.g., cellular automata, drunkard's walk, noise functions)

    map_data = []
    floor_id = params.get("floor_tile_id", 0)
    wall_id = params.get("wall_tile_id", 1)

    for y in range(height):
        row = []
        for x in range(width):
            # Simple random example: place a wall sometimes
            if random.random() < 0.2:
                row.append(wall_id)
            else:
                row.append(floor_id)
        map_data.append(row)

    # --- End Placeholder ---

    # --- Placeholder Spawn Points ---
    # Real logic would find valid floor tiles
    spawn_points = {
        "player": [[height // 2, width // 2]],
        "enemy": [[2, 2], [height - 3, width - 3]]
    }

    return models.MapGenerationResponse(
        width=width,
        height=height,
        map_data=map_data,
        seed_used=seed,
        algorithm_used=algo_name,
        spawn_points=spawn_points
    )