# Map Generator Service

## 1. Overview

The Map Generator is a stateless FastAPI service that procedurally generates tile-based maps for game locations. It uses a variety of algorithms to create different types of environments based on a set of input tags.

-   **Stateless:** The service does not have a database. It loads its algorithm definitions and tile data from JSON files on startup.
-   **Procedural Generation:** Its purpose is to create map layouts, which are then passed to the `world_engine` to be saved as part of a location's state.

## 2. Core Responsibilities

-   **Algorithm Selection:** Selects an appropriate generation algorithm from `generation_algorithms.json` based on a list of input tags (e.g., `["cave", "small"]`).
-   **Map Generation:** Executes the chosen algorithm to generate a 2D array of tile IDs. Currently implemented algorithms include:
    -   **Cellular Automata:** Creates natural, cave-like structures by simulating cell birth and death based on neighboring tiles.
    -   **Drunkard's Walk:** Creates winding paths and tunnels by simulating a random walk that carves out floor tiles.
-   **Post-Processing:** Applies a series of optional post-processing steps to refine the generated map, such as adding a border or ensuring all areas are reachable.
-   **Spawn Point Placement:** Identifies valid floor tiles on the generated map to be used as spawn points for players and NPCs.

## 3. Key API Endpoints

-   `POST /v1/generate`: The sole endpoint for generating a map.
    -   **Request Body:** `MapGenerationRequest` (a list of `tags`, optional `width`, `height`, and `seed`).
    -   **Process:**
        1.  Selects an algorithm matching the provided tags.
        2.  Executes the generation and post-processing steps.
        3.  Identifies spawn points.
        4.  Returns the complete map data.
    -   **Response Body:** `MapGenerationResponse` (width, height, the `map_data` grid, the seed used, and identified `spawn_points`).

## 4. Data Sources

-   `generation_algorithms.json`: Defines the available generation algorithms, the tags that trigger them, their parameters (e.g., initial density for Cellular Automata), and the post-processing steps to apply.
-   `tile_definitions.json`: Defines the mapping between tile IDs (e.g., `0`, `1`) and their properties (e.g., "Grass", "Wall", "walkable: true").

## 5. Dependencies

The Map Generator is a self-contained service and has **no dependencies** on other services.
