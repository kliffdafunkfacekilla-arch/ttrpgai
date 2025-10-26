# AI-TTRPG Backend System Documentation

## 1. High-Level Architecture

The AI-TTRPG backend system is designed with a modular microservice architecture. It consists of seven distinct services, each responsible for a specific aspect of the game. This separation of concerns allows for independent development, deployment, and scaling of each component. The services are primarily built with Python and FastAPI.

The services can be categorized as follows:

*   **Stateful Services:** These services manage persistent data and are responsible for the core state of the game. They include:
    *   `character_engine`: Manages character sheets.
    *   `world_engine`: Manages the game world's state, including locations, NPCs, and items.
    *   `story_engine`: Manages campaign progress, quests, and acts as an orchestrator for other services.

*   **Stateless Services:** These services are responsible for generating game content and performing calculations. They do not maintain any persistent state of their own. They include:
    *   `rules_engine`: Provides game rules and performs calculations.
    *   `encounter_generator`: Generates combat and skill encounters.
    *   `npc_generator`: Procedurally generates NPC templates.
    *   `map_generator`: Procedurally generates tile maps.

## 2. Module Breakdown

### `rules_engine`

*   **Primary Purpose:** Acts as a stateless "calculator" and data source for all game mechanics. It loads game rules into memory on startup and provides endpoints for other services to perform rule-based calculations and lookups.
*   **Key Features/API Endpoints:**
    *   `POST /v1/validate/skill_check`: Performs a d20 skill check against a DC.
    *   `POST /v1/validate/ability_check`: Performs a d20 ability check against a tiered DC.
    *   `GET /v1/lookup/kingdom_feature_stats`: Returns the stat modifiers for a given kingdom feature.
    *   `POST /v1/lookup/talents`: Finds eligible talents based on a character's stats and skills.
    *   `GET /v1/lookup/all_stats`: Returns the list of all core stats.
    *   `GET /v1/lookup/all_skills`: Returns the master map of all skills.
    *   `GET /v1/lookup/all_ability_schools`: Returns the list of all ability schools.
*   **Technologies:** FastAPI.
*   **Database:** None. This is a stateless service that loads data from JSON files on startup.
*   **Data Managed:** Game rules, including abilities, kingdom features, stats, skills, and talents, from various JSON files in its `data` directory.

### `character_engine`

*   **Primary Purpose:** A stateful service responsible for creating, managing, and updating persistent character sheets.
*   **Key Features/API Endpoints:**
    *   `POST /v1/characters/`: Creates a new character, calculating their initial stats and skills by calling the `rules_engine`.
    *   `GET /v1/characters/{char_id}`: Retrieves a specific character's full data.
    *   `POST /v1/characters/{char_id}/add_sre`: Adds a Skill Rank Experience (SRE) point to a character's skill and handles skill rank-ups.
*   **Technologies:** FastAPI, SQLAlchemy, Alembic, httpx.
*   **Database:** SQLite (`characters.db`).
*   **Data Managed:** Character sheets, which are stored as JSON blobs in the database.

### `world_engine`

*   **Primary Purpose:** A stateful service that manages the game world's state, including all locations, NPCs, items, and world data.
*   **Key Features/API Endpoints:**
    *   `GET /v1/locations/{location_id}`: Retrieves data for a single location.
    *   `PUT /v1/locations/{location_id}/map`: Updates a location with a procedurally generated map.
    *   `POST /v1/npcs/spawn`: Creates a new NPC instance in the world.
    *   `GET /v1/npcs/{npc_id}`: Retrieves the current status of an NPC.
    *   `PUT /v1/npcs/{npc_id}`: Updates an NPC's state (e.g., health, location).
    *   `DELETE /v1/npcs/{npc_id}`: Removes an NPC from the world.
    *   `POST /v1/items/spawn`: Creates a new item instance in the world.
    *   `DELETE /v1/items/{item_id}`: Removes an item from the world.
*   **Technologies:** FastAPI, SQLAlchemy, Alembic.
*   **Database:** SQLite (presumably `world.db`).
*   **Data Managed:** The state of all entities in the game world, including locations, NPCs, items, regions, and factions.

### `story_engine`

*   **Primary Purpose:** A stateful service that manages campaign state, quests, and orchestrates other services to drive the narrative.
*   **Key Features/API Endpoints:**
    *   Manages campaigns, quests, and story flags.
    *   Provides high-level orchestration endpoints for the AI DM to take actions, such as spawning NPCs and items by calling the `world_engine`.
    *   Retrieves context from other services, such as character sheets from the `character_engine` and location data from the `world_engine`.
*   **Technologies:** FastAPI, SQLAlchemy, Alembic, httpx.
*   **Database:** SQLite (presumably `story.db`).
*   **Data Managed:** Campaign progress, active quests, and story flags.

### `encounter_generator`

*   **Primary Purpose:** A stateless service that generates combat and skill encounters based on a set of tags.
*   **Key Features/API Endpoints:**
    *   `POST /v1/generate`: Generates an encounter based on a list of tags (e.g., "forest", "medium", "combat").
*   **Technologies:** FastAPI.
*   **Database:** None.
*   **Data Managed:** Encounter templates from JSON files.

### `npc_generator`

*   **Primary Purpose:** A stateless service that procedurally generates NPC templates.
*   **Key Features/API Endpoints:**
    *   `POST /v1/generate`: Generates a new NPC template based on parameters like kingdom, styles, and difficulty.
*   **Technologies:** FastAPI.
*   **Database:** None.
*   **Data Managed:** NPC generation rules from JSON files.

### `map_generator`

*   **Primary Purpose:** A stateless service that procedurally generates tile maps.
*   **Key Features/API Endpoints:**
    *   `POST /v1/generate`: Generates a map based on tags, with optional seed and dimensions.
*   **Technologies:** FastAPI.
*   **Database:** None.
*   **Data Managed:** Map generation algorithms and tile definitions from JSON files.

## 3. Inter-Service Communication

The services communicate with each other via synchronous HTTP API calls. The primary interactions observed in the codebase are:

*   **`character_engine` -> `rules_engine`**: The `character_engine` is a client of the `rules_engine`. When creating a character or updating skills, it calls the `rules_engine`'s endpoints to:
    *   Fetch the master lists of stats and skills.
    *   Get stat modifications for kingdom features.
    *   Look up eligible talents based on the character's current stats and skills.

*   **`story_engine` -> `character_engine` & `world_engine`**: The `story_engine` acts as an orchestrator and is a client of both the `character_engine` and `world_engine`. It calls them to:
    *   Get the full context of a character from the `character_engine`.
    *   Get the full context of a location (including NPCs and items) from the `world_engine`.
    *   Send commands to the `world_engine` to spawn new NPCs or items.

The generator services (`encounter_generator`, `npc_generator`, `map_generator`) are designed to be called by a higher-level consumer, presumably the AI Dungeon Master or the `story_engine`, although no direct calls from the `story_engine` to these services are present in the current files.

## 4. Project Goals

Based on the file contents, the main goals of the project are:

*   **Create a Modular AI DM Toolkit:** The microservice architecture is explicitly designed to create a flexible and extensible toolkit for an AI Dungeon Master.
*   **Separation of Concerns:** Each service has a clearly defined responsibility, separating rules from character state, world state, and narrative orchestration.
*   **Procedural Generation:** Several services are dedicated to procedurally generating content (NPCs, encounters, maps), indicating a goal of creating a dynamic and replayable game experience.

## 5. Current Status

*   **`rules_engine`:** Appears to be complete and functional, with a well-defined API for game mechanics.
*   **`character_engine`:** Appears to be largely complete and functional, with core features for character creation and progression implemented.
*   **`world_engine`:** Appears to be well-developed, with a comprehensive API for managing the game world's state.
*   **`story_engine`:** The core functionality of managing campaign state and orchestrating other services is in place.
*   **`encounter_generator`, `npc_generator`, `map_generator`:** These services appear to be complete and functional, each with a clear and simple API for generating its specific type of content.

Overall, the project appears to be in a relatively mature state, with all the core services implemented and functional. The `start_services.bat` script indicates that the project is intended to be run as a complete system with all services active simultaneously.
