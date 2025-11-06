# AI-TTRPG Project Documentation

## 1. High-Level Architecture

The AI-TTRPG system is built on a **microservice architecture**. The project is divided into seven distinct services, each responsible for a specific domain of the game. This design allows for modularity, scalability, and independent development of each component. The services communicate with each other through **REST APIs**, with the `story_engine` acting as the central orchestrator.

The seven services are:
1.  `story_engine`: Manages the narrative, quests, and game state.
2.  `character_engine`: Manages player character data.
3.  `world_engine`: Manages the game world, including locations, NPCs, and items.
4.  `rules_engine`: Provides game rules and calculations.
5.  `npc_generator`: Procedurally generates NPCs.
6.  `map_generator`: Procedurally generates maps.
7.  `encounter_generator`: Generates combat and skill encounters.

## 2. Service Breakdown

### Story Engine
*   **Purpose**: The central orchestrator of the game. It manages the campaign's state, quests, and player actions, and directs the other services.
*   **Key Functions & Endpoints**:
    *   `/v1/actions/interact`: **(New)** Processes player interactions with the game world. The core logic is in `interaction_handler.py`, which fetches world state from the `world_engine` and character data from the `character_engine`.
    *   `/v1/combat/start`: Initiates combat by spawning NPCs and rolling initiative.
    *   `/v1/combat/{combat_id}/player_action`: Processes player actions during combat. The core logic is in `combat_handler.py`, which includes the new NPC AI behavior.
*   **Data Management**: Manages the state of the current campaign, including active quests and story flags, in its own `story.db` database.

### Character Engine
*   **Purpose**: The authoritative source for player character data. It manages character sheets, including stats, skills, inventory, and combat-related data.
*   **Key Functions & Endpoints**:
    *   `/v1/characters/`: Creates a new character.
    *   `/v1/characters/{char_id}`: Retrieves a character's data.
    *   `/v1/characters/{char_id}/inventory/add` & `/remove`: Manages a character's inventory.
    *   `/v1/characters/{char_id}/apply_damage` & `/apply_status`: Modifies a character's combat state. The logic for these functions is in `crud.py`.
*   **Data Management**: Stores all character sheets in its own `characters.db` database. The `character_sheet` JSON blob was recently refactored to include a `combat_stats` dictionary for `max_hp`, `current_hp`, and `status_effects`.

### World Engine
*   **Purpose**: Manages the state of the game world, including locations, NPCs, and items.
*   **Key Functions & Endpoints**:
    *   `/v1/locations/{location_id}`: Retrieves data about a location.
    *   `/v1/locations/{location_id}/annotations`: **(New)** Allows the `story_engine` to store and update metadata about a location, such as the state of a door or the presence of a key.
    *   `/v1/npcs/spawn`: Creates a new NPC instance in the world.
*   **Data Management**: Stores all world data in its own `world.db` database.

### Rules Engine
*   **Purpose**: A stateless calculator for all game mechanics. It provides data on skills, abilities, weapons, and armor, and performs calculations for combat and other actions.
*   **Key Functions & Endpoints**:
    *   `/v1/roll/initiative`: Calculates initiative for combat.
    *   `/v1/roll/contested_attack`: Performs a contested attack roll.
    *   `/v1/calculate/damage`: Calculates damage.
    *   `/v1/lookup/all_skills`: Provides a list of all skills in the game.
    *   `/v1/lookup/npc_template/{template_id}`: **(New)** Returns the generation parameters for a given NPC template ID.
    *   `/v1/lookup/item_template/{item_id}`: **(New)** Looks up the definition for a given item ID, returning its type and category.
*   **Data Management**: Loads all game rules from JSON files in the `data` directory into memory on startup.

### NPC Generator
*   **Purpose**: Procedurally generates NPC templates based on a set of rules.
*   **Key Functions & Endpoints**:
    *   `/v1/generate`: Generates an NPC template based on a request that specifies kingdom, style, difficulty, and other parameters. The core logic in `core.py` was recently updated to fetch the skill list dynamically.
*   **Data Management**: Stateless, but loads generation rules from `generation_rules.json` on startup.

### Map Generator
*   **Purpose**: Procedurally generates tile maps for game locations.
*   **Key Functions & Endpoints**:
    *   `/v1/generate`: Generates a map based on tags and a seed. The core logic in `core.py` was recently updated to include the "Drunkard's Walk" algorithm.
*   **Data Management**: Stateless, but loads generation algorithms from `generation_algorithms.json` and tile definitions from `tile_definitions.json` on startup.

### Encounter Generator
*   **Purpose**: Generates combat and skill encounters based on a set of tags.
*   **Key Functions & Endpoints**:
    *   `/v1/generate`: Generates an encounter based on a request that specifies tags like "forest," "medium," and "combat."
*   **Data Management**: Stateless, but loads encounter data from `combat_encounters.json` and `skill_challenges.json` on startup.

## 3. Development Plan vs. Current State

### Goal: Implement Player Interactions
*   **Current State**: **Complete**.
    *   The `story_engine` now has a `/v1/actions/interact` endpoint that takes an `InteractionRequest` and returns an `InteractionResponse`.
    *   The core logic is implemented in `story_engine/app/interaction_handler.py`.
    *   The system can handle "use" interactions with doors (checking for locked status and keys) and items (adding them to the player's inventory).
    *   This was achieved by adding a new `update_location_annotations` function to the `story_engine`'s `services.py` to communicate with the `world_engine`, and an `add_item_to_character` function to communicate with the `character_engine`.

### Goal: Improve Data Consistency
*   **Current State**: **Complete**.
    *   The `character_engine`'s `character_sheet` data structure has been refactored to include a `combat_stats` dictionary.
    *   The `create_character` function in `character_engine/app/main.py` now initializes this structure, including a placeholder HP calculation.
    *   The `apply_damage_to_character` and `apply_status_to_character` functions in `character_engine/app/crud.py` have been updated to use this new structure.
    *   The `story_engine`'s `combat_handler.py` has been updated to read HP values from the new `combat_stats` structure.

### Goal: Enhance NPC and Map Generation
*   **Current State**: **Complete**.
    *   The `map_generator`'s `core.py` now includes a full implementation of the "Drunkard's Walk" algorithm.
    *   The `story_engine`'s `combat_handler.py` has been updated with a new `determine_npc_action` function that provides basic AI behavior based on "cowardly," "targets_weakest," and "aggressive" tags.

### Goal: Dynamic Data Loading
*   **Current State**: **Complete**.
    *   The `npc_generator`'s `core.py` has been refactored to fetch the master skill list from the `rules_engine`'s `/v1/lookup/all_skills` endpoint, removing the hardcoded list.
    *   **NPC Spawning:** The `story_engine` now orchestrates NPC creation by calling the `rules_engine` to get generation parameters, then the `npc_generator` to create a full template, and finally the `world_engine` to spawn the NPC.
    *   **Item Lookup:** The `story_engine` now determines the category of a player's equipped weapon or armor by calling the `rules_engine`'s `/v1/lookup/item_template/{item_id}` endpoint.
