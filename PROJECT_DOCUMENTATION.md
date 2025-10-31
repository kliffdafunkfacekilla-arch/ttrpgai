# AI-TTRPG Backend System Documentation

## 1. High-Level Architecture

The AI-TTRPG system is a Python-based backend built on a **microservice architecture**. It consists of seven distinct FastAPI services, each handling a specific domain of the game. This design promotes modularity, independent development, and scalability.

The services are divided into two primary categories:

*   **Stateful Services:** These three services manage persistent game data using individual SQLite databases, with schemas and migrations handled by SQLAlchemy and Alembic.
    *   `character_engine`: Manages the creation, state, and progression of player characters.
    *   `world_engine`: Manages the state of the game world, including locations, NPCs, and items.
    *   `story_engine`: Manages campaign state and acts as the central orchestrator for complex actions.

*   **Stateless Services:** These four services act as data providers and calculators. They load their necessary data from local JSON files upon startup and do not maintain any persistent state of their own.
    *   `rules_engine`: The single source of truth for all game rules and combat calculations.
    *   `npc_generator`: Procedurally generates NPC templates based on a set of rules.
    *   `map_generator`: Procedurally generates tile-based maps using various algorithms.
    *   `encounter_generator`: (Placeholder) Intended to generate pre-defined encounters.

### Inter-Service Communication Flow

Services communicate via synchronous REST API calls, primarily orchestrated by the `story_engine`.

```
+------------------+      +-----------------+      +-----------------+
| player_interface |----->|  story_engine   |----->| character_engine|
+------------------+      +-------+---------+      +-----------------+
                              ^   |                (Player State)
                              |   |
                              |   v
                              |   +---------------->+-----------------+
                              |                    |   world_engine  |
                              |                    +-----------------+
                              |                    (World State)
                              v
                      +-------+---------+
                      |   rules_engine  |
                      +-----------------+
                      (Rules & Calculations)
```

## 2. Service Breakdown

### `story_engine` (Orchestrator)

*   **Purpose:** Acts as the central nervous system of the application. It directs the flow of gameplay by receiving high-level requests (e.g., "start combat," "move player") and orchestrating the necessary calls to other services.
*   **Core Endpoints:**
    *   `POST /v1/combat/start`: Initiates a combat encounter.
    *   `POST /v1/combat/{id}/player_action`: Processes a player's action during combat.
    *   `POST /v1/actions/interact`: Handles non-combat interactions with world objects.
*   **Data:** Manages active campaign state, quests, story flags, and the state of ongoing combat encounters in `story.db`.
*   **Dependencies:** Calls all other stateful and stateless services to execute gameplay logic.

### `world_engine` (Stateful)

*   **Purpose:** Manages the persistent state of the game world. It is the source of truth for "what is where."
*   **Core Endpoints:**
    *   `GET /v1/locations/{id}`: Retrieves the full state of a location, including all NPCs, items, and map data.
    *   `POST /v1/npcs/spawn`: Creates a new NPC instance at a specific location.
    *   `PUT /v1/npcs/{id}`: Updates an NPC's state (e.g., `current_hp`, `status_effects`, `coordinates`).
    *   `PUT /v1/locations/{id}/annotations`: Updates the metadata for interactable objects.
*   **Data:** Manages locations, NPCs, items, and their states in `world.db`.

### `character_engine` (Stateful)

*   **Purpose:** Manages the persistent state of all player characters.
*   **Core Endpoints:**
    *   `POST /v1/characters/`: Creates a new character.
    *   `GET /v1/characters/{id}`: Retrieves a character's complete sheet.
    *   `PUT /v1/characters/{id}/apply_damage`: Updates a character's `current_hp`.
    *   `PUT /v1/characters/{id}/location`: Updates the player's current location and coordinates.
*   **Data:** Manages character sheets (as a single JSON blob) in `characters.db`.

### `rules_engine` (Stateless)

*   **Purpose:** The definitive source for all game mechanics and calculations. It ensures that combat and other actions are resolved consistently according to the game's ruleset.
*   **Core Endpoints:**
    *   `POST /v1/roll/contested_attack`: Performs a complete attack roll, returning the outcome (e.g., "hit", "miss", "critical_hit").
    *   `POST /v1/calculate/damage`: Calculates the final damage dealt after accounting for stats and armor.
    *   `GET /v1/lookup/...`: A wide variety of endpoints to look up data for skills, items, statuses, etc.
*   **Data:** Loads all game rules from its `data/` directory of JSON files on startup.

### `npc_generator` (Stateless)

*   **Purpose:** Procedurally generates NPC stat blocks to be used by the `story_engine`.
*   **Core Endpoints:**
    *   `POST /v1/generate`: Creates a new NPC template based on input parameters like kingdom, style, and difficulty.
*   **Data:** Loads generation rules from `generation_rules.json`.
*   **Dependencies:** Calls the `rules_engine` to get the master list of skills, ensuring generated NPCs are compatible with game rules.

### `map_generator` (Stateless)

*   **Purpose:** Procedurally generates tile-based maps for game locations.
*   **Core Endpoints:**
    *   `POST /v1/generate`: Creates a new tile map using a specified algorithm (e.g., Cellular Automata, Drunkard's Walk).
*   **Data:** Loads algorithm parameters and tile definitions from JSON files.

### `encounter_generator` (Stateless)

*   **Purpose:** A placeholder service intended to provide pre-defined combat or skill-based encounters.
*   **Core Endpoints:**
    *   `POST /v1/generate`: (Not fully utilized) Returns an encounter structure from a JSON file.

## 3. Core Gameplay Loops

### Exploration and Movement

1.  The `player_interface` renders the current location by fetching data from the `story_engine`, which in turn gets the complete location context (map, NPCs, items) from the `world_engine`.
2.  The player presses a movement key (e.g., 'W').
3.  The `player_interface` sends the new coordinates to the `character_engine`'s `PUT /v1/characters/{id}/location` endpoint, persisting the player's new position.
4.  The interface re-renders the scene.

### Turn-Based Combat

This is the most complex interaction, showcasing the full orchestration pattern.

1.  **Initiation:** The player moves into a tile occupied by an "aggressive" NPC. The `player_interface` detects this and calls the `story_engine`'s `POST /v1/combat/start` endpoint.
2.  **Setup:** The `story_engine` orchestrates the entire combat setup:
    *   It fetches map data from the `world_engine` to determine valid spawn points for NPCs.
    *   It calls the `world_engine` to officially spawn the NPC instances into the world state with coordinates.
    *   It retrieves the full context for all participants (player data from `character_engine`, NPC data from `world_engine`).
    *   It calls the `rules_engine`'s `/v1/roll/initiative` endpoint for every participant.
    *   It saves the full encounter state, including the initiative-sorted turn order, to its own `story.db`.
3.  **Player Turn:** The `player_interface` switches to a combat view. The player clicks an "Attack" button, targeting an NPC.
    *   The interface calls the `story_engine`'s `POST /v1/combat/{id}/player_action` endpoint with the action details.
4.  **Action Resolution:** The `story_engine` resolves the attack:
    *   It fetches the player's equipped weapon and the target's armor from the `character_engine` and `world_engine`.
    *   It retrieves the detailed stats for that weapon and armor from the `rules_engine`.
    *   It sends all relevant stats (attacker's skill, defender's armor stat, etc.) to the `rules_engine`'s `/v1/roll/contested_attack` endpoint.
    *   If the attack is a hit, it calls the `rules_engine`'s `/v1/calculate/damage` endpoint.
    *   Finally, it applies the damage by calling the appropriate service (`world_engine` for NPCs, `character_engine` for players).
5.  **Turn Advancement:** The `story_engine` records the results in a combat log, advances the turn index, and returns the log to the `player_interface`.
6.  **NPC Turn:** If the new turn belongs to an NPC, the `story_engine` runs a simple AI (`determine_npc_action`) and executes the NPC's turn by following the same action resolution steps.
7.  **Conclusion:** The loop continues until one side is defeated. The `story_engine` marks the combat as "finished," and the `player_interface` returns to the exploration screen.

## 4. Getting Started

-   **Dependencies:** Each service has its own `requirements.txt` file.
-   **Running the System:** The `start_services.bat` script in the root directory is configured to launch all seven services, each on its own designated port (8000-8006).
-   **Player Interface:** A React/TypeScript frontend is located in the `player_interface` directory. It must be started separately (`npm run dev`) and connects to the running backend services.
