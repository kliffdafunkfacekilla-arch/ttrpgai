# AI-TTRPG System Documentation

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
    *   `POST /v1/combat/{id}/player_action`: Processes a player's action during combat. The core logic is in `combat_handler.py`, which includes the new NPC AI behavior.
    *   `POST /v1/actions/interact`: **(New)** Handles non-combat interactions with world objects. The core logic is in `interaction_handler.py`, which fetches world state from the `world_engine` and character data from the `character_engine`.
*   **Data:** Manages active campaign state, quests, story flags, and the state of ongoing combat encounters in `story.db`.
*   **Dependencies:** Calls all other stateful and stateless services to execute gameplay logic.

### `world_engine` (Stateful)

*   **Purpose:** Manages the persistent state of the game world. It is the source of truth for "what is where."
*   **Core Endpoints:**
    *   `GET /v1/locations/{id}`: Retrieves the full state of a location, including all NPCs, items, and map data.
    *   `POST /v1/npcs/spawn`: Creates a new NPC instance at a specific location.
    *   `PUT /v1/npcs/{id}`: Updates an NPC's state (e.g., `current_hp`, `status_effects`, `coordinates`).
    *   `PUT /v1/locations/{id}/annotations`: **(New)** Allows the `story_engine` to store and update metadata about a location, such as the state of a door or the presence of a key.
*   **Data:** Manages locations, NPCs, items, and their states in `world.db`.

### `character_engine` (Stateful)

*   **Purpose:** The authoritative source for player character data. It manages character sheets, including stats, skills, inventory, and combat-related data.
*   **Core Endpoints:**
    *   `POST /v1/characters/`: Creates a new character.
    *   `GET /v1/characters/{id}`: Retrieves a character's complete sheet.
    *   `PUT /v1/characters/{id}/inventory/add` & `/remove`: Manages a character's inventory.
    *   `PUT /v1/characters/{id}/apply_damage`: Updates a character's `current_hp`.
    *   `PUT /v1/characters/{id}/location`: Updates the player's current location and coordinates.
*   **Data:** Manages character sheets (as a single JSON blob) in `characters.db`. The `character_sheet` JSON blob was recently refactored to include a `combat_stats` dictionary for `max_hp`, `current_hp`, and `status_effects`.

### `rules_engine` (Stateless)

*   **Purpose:** The definitive source for all game mechanics and calculations. It ensures that combat and other actions are resolved consistently according to the game's ruleset.
*   **Core Endpoints:**
    *   `POST /v1/roll/contested_attack`: Performs a complete attack roll, returning the outcome (e.g., "hit", "miss", "critical_hit").
    *   `POST /v1/calculate/damage`: Calculates the final damage dealt after accounting for stats and armor.
    *   `GET /v1/lookup/all_skills`: Provides a list of all skills in the game.
    *   `GET /v1/lookup/npc_template/{template_id}`: **(New)** Returns the generation parameters for a given NPC template ID.
    *   `GET /v1/lookup/item_template/{item_id}`: **(New)** Looks up the definition for a given item ID, returning its type and category.
*   **Data:** Loads all game rules from its `data/` directory of JSON files on startup.

### `npc_generator` (Stateless)

*   **Purpose:** Procedurally generates NPC stat blocks to be used by the `story_engine`.
*   **Core Endpoints:**
    *   `POST /v1/generate`: Creates a new NPC template based on input parameters like kingdom, style, and difficulty. The core logic in `core.py` was recently updated to fetch the skill list dynamically.
*   **Data:** Loads generation rules from `generation_rules.json`.
*   **Dependencies:** Calls the `rules_engine` to get the master list of skills, ensuring generated NPCs are compatible with game rules.

### `map_generator` (Stateless)

*   **Purpose:** Procedurally generates tile-based maps for game locations.
*   **Core Endpoints:**
    *   `POST /v1/generate`: Creates a new tile map using a specified algorithm (e.g., Cellular Automata, Drunkard's Walk). The core logic in `core.py` was recently updated to include the "Drunkard's Walk" algorithm.
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

### Case Study: Spawning an NPC in Combat

The process of spawning an NPC when combat starts is a prime example of the microservice architecture in action, demonstrating the clear separation of concerns.

1.  **Initiation (`story_engine`):** The `story_engine` receives a request to start combat, which includes a list of NPC template IDs (e.g., `["goblin_scout"]`).

2.  **Parameter Lookup (`rules_engine`):** The `story_engine` doesn't know *how* to create a "goblin_scout." It calls the `rules_engine`'s `GET /v1/lookup/npc_template/goblin_scout` endpoint. The `rules_engine` reads from its `npc_templates.json` file and returns the generation parameters: `{ "kingdom": "mammal", "difficulty": "easy", ... }`.

3.  **Procedural Generation (`npc_generator`):** The `story_engine` now knows the recipe. It calls the `npc_generator`'s `POST /v1/generate` endpoint, providing the parameters it just received. The `npc_generator` uses its internal logic to procedurally generate a full NPC template, including stats, skills, and, crucially, a calculated `max_hp`. It returns this full template.

4.  **World State Update (`world_engine`):** The `story_engine` now has a complete, statted NPC. It calls the `world_engine`'s `POST /v1/npcs/spawn` endpoint, providing the full template and the desired coordinates. The `world_engine` creates the NPC instance in its `world.db`, officially placing it in the game world.

5.  **Combat Begins:** The `story_engine` proceeds with the rest of the combat setup, now confident that a fully-formed NPC exists in the world.

This flow ensures that each service is only responsible for its own domain: the `rules_engine` knows the *recipe*, the `npc_generator` knows *how to cook*, and the `world_engine` knows *where to place the dish*. The `story_engine` simply directs the process.

## 4. Current State

The project is currently in a functional, demonstrable state. The core gameplay loop of exploration and combat is implemented, and the foundational architecture is stable.

*   **Implemented Features:**
    *   Full character creation flow.
    *   World exploration with tile-based maps.
    *   Combat initiation and turn-based resolution.
    *   Procedural generation of maps and NPCs.
    *   A comprehensive, data-driven ruleset for combat calculations.

*   **Placeholder Components:**
    *   The `encounter_generator` service is a placeholder and does not yet have a significant role in the system.
    *   NPC AI is basic, with simple "aggressive" or "cowardly" behaviors.
    *   Quest and story progression systems are not yet implemented.

## 5. Intended Final Goal

The intended final goal of the AI-TTRPG project is to create a fully autonomous, endlessly replayable tabletop role-playing experience. The architecture is designed to support a dynamic, procedurally generated world where an AI Dungeon Master (the `story_engine`) can create and manage emergent narratives.

*   **Key Future Features:**
    *   **Dynamic World State:** The world will change in response to player actions, with the `story_engine` and `world_engine` tracking these changes.
    *   **Emergent Storytelling:** The `story_engine` will be expanded to include more sophisticated AI-driven narrative generation, creating quests, and managing story arcs based on player choices.
    *   **Advanced NPC AI:** NPCs will have more complex behaviors, schedules, and relationships, making the world feel more alive.
    *   **Extensibility:** The data-driven nature of the stateless services will allow for easy expansion with new rules, items, and content without requiring code changes.

## 6. Getting Started

-   **Dependencies:** Each service has its own `requirements.txt` file.
-   **Running the System:** The `start_services.bat` and `start_services.sh` scripts in the root directory are configured to launch all seven services, each on its own designated port (8000-8006).
-   **Player Interface:** A React/TypeScript frontend is located in the `player_interface` directory. It must be started separately (`npm run dev`) and connects to the running backend services.
