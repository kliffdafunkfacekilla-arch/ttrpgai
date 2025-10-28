# AI-TTRPG Backend System Documentation

## 1. High-Level Architecture

The AI-TTRPG backend system is designed with a modular microservice architecture. It consists of seven distinct services, each responsible for a specific aspect of the game. This separation of concerns allows for independent development, deployment, and scaling of each component. The services are primarily built with Python and FastAPI.

The services can be categorized as follows:

* **Stateful Services:** These services manage persistent data and are responsible for the core state of the game. They use SQLite databases managed via SQLAlchemy and Alembic. They include:
    * `character_engine`: Manages persistent character sheets (`characters.db`).
    * `world_engine`: Manages the game world's state, including locations, NPCs, items, traps, regions, and factions (`world.db`).
    * `story_engine`: Manages campaign progress, quests, story flags, and active combat state (`story.db`). Acts as an orchestrator for other services.

* **Stateless Services:** These services are responsible for generating game content and performing calculations based on data loaded from JSON files at startup. They do not maintain any persistent state of their own. They include:
    * `rules_engine`: Provides game rules and performs calculations (skill checks, combat rolls, damage, etc.).
    * `encounter_generator`: Generates combat and skill encounters based on tags.
    * `npc_generator`: Procedurally generates NPC templates based on parameters.
    * `map_generator`: Procedurally generates tile maps based on tags (currently uses placeholder logic).

## 2. Module Breakdown

### `rules_engine`

* **Primary Purpose:** Acts as a stateless "calculator" and data source for all game mechanics. It loads extensive game rules (stats, skills, abilities, items, armor, talents, injuries, statuses) into memory on startup and provides endpoints for calculations and lookups.
* **Key Features/API Endpoints:**
    * **Validation:**
        * `POST /v1/validate/skill_check`: Performs a d20 skill check.
        * `POST /v1/validate/ability_check`: Performs a d20 ability check.
    * **Combat Rolls & Calculations:**
        * `POST /v1/roll/initiative`: Rolls initiative based on 6 core stats.
        * `POST /v1/roll/contested_attack`: Performs a contested attack roll, determining outcome (hit, miss, crit, etc.).
        * `POST /v1/calculate/damage`: Calculates final damage after dice rolls, mods, and DR.
    * **Lookups:**
        * `GET /v1/lookup/kingdom_feature_stats`: Returns stat mods for kingdom features.
        * `POST /v1/lookup/talents`: Finds eligible talents.
        * `GET /v1/lookup/all_stats`, `/all_skills`, `/all_ability_schools`: Return master lists.
        * `GET /v1/lookup/melee_weapon/{category_name}`, `/ranged_weapon/{category_name}`, `/armor/{category_name}`: Returns stats for specific item categories.
        * `POST /v1/lookup/injury_effects`: Returns mechanical effects for injuries.
        * `GET /v1/lookup/status_effect/{status_name}`: Returns definition for status effects.
* **Technologies:** FastAPI.
* **Database:** None. Loads data from JSON files in its `data` directory on startup.
* **Data Managed:** Game rules loaded from JSON.

### `character_engine`

* **Primary Purpose:** A stateful service responsible for creating, managing, and updating persistent character sheets.
* **Key Features/API Endpoints:**
    * `POST /v1/characters/`: Creates a new character, calculating initial stats/skills/talents by calling the `rules_engine`.
    * `GET /v1/characters/{char_id}`: Retrieves a specific character's full data.
    * `GET /v1/characters/`: Lists existing characters.
    * `POST /v1/characters/{char_id}/add_sre`: Adds SRE, handles rank-ups, and checks for new talents via `rules_engine`.
    * `POST /v1/characters/{char_id}/inventory/add`, `/remove`: Manages items in the character's inventory (stored in the character sheet JSON).
    * `PUT /v1/characters/{char_id}/apply_damage`: Applies HP damage to the character sheet.
    * `PUT /v1/characters/{char_id}/apply_status`: Adds a status effect to the character sheet.
* **Technologies:** FastAPI, SQLAlchemy, Alembic, httpx.
* **Database:** SQLite (`characters.db`).
* **Data Managed:** Character sheets stored as JSON blobs.

### `world_engine`

* **Primary Purpose:** A stateful service that manages the game world's state, including all locations, NPCs, items, traps, regions, and factions.
* **Key Features/API Endpoints:**
    * **Locations:**
        * `POST /v1/locations/`: Creates a new location.
        * `GET /v1/locations/{location_id}`: Retrieves data for a location (including NPCs, items, traps).
        * `PUT /v1/locations/{location_id}/map`: Updates a location with a procedurally generated map and seed.
        * `PUT /v1/locations/{location_id}/annotations`: Updates AI-specific notes/flags for a location.
    * **NPCs:**
        * `POST /v1/npcs/spawn`: Creates a new NPC instance with HP, status effects, and behavior tags.
        * `GET /v1/npcs/{npc_id}`: Retrieves the current status of an NPC.
        * `PUT /v1/npcs/{npc_id}`: Updates an NPC's state (HP, status effects, location).
        * `DELETE /v1/npcs/{npc_id}`: Removes an NPC (e.g., on death).
    * **Items:**
        * `POST /v1/items/spawn`: Creates a new item instance (on ground or in NPC inventory).
        * `DELETE /v1/items/{item_id}`: Removes an item (e.g., when picked up).
    * **Traps:**
        * `POST /v1/traps/spawn`: Creates a new trap instance at a location.
        * `PUT /v1/traps/{trap_id}`: Updates a trap's status (armed, disarmed, triggered).
        * `GET /v1/locations/{loc_id}/traps`: Retrieves all traps for a location.
    * **Regions/Factions:**
        * Endpoints exist to create and read regions and factions (primarily for setup via `preload_data.py`).
* **Technologies:** FastAPI, SQLAlchemy, Alembic.
* **Database:** SQLite (`world.db`).
* **Data Managed:** State of all world entities. Includes `preload_data.py` script for initial population.

### `story_engine`

* **Primary Purpose:** A stateful service that manages campaign state, quests, story flags, active combat encounters, and orchestrates other services.
* **Key Features/API Endpoints:**
    * **Campaign/Quest/Flag Management:**
        * CRUD endpoints for `Campaigns`, `ActiveQuests`, and `StoryFlags`.
    * **Orchestration & Context:**
        * `POST /v1/actions/spawn_npc`, `/spawn_item`: High-level commands calling `world_engine`.
        * `GET /v1/context/character/{char_id}`: Fetches full character context from `character_engine`.
        * `GET /v1/context/location/{location_id}`: Fetches full location context from `world_engine`.
    * **Combat Orchestration:**
        * `POST /v1/combat/start`: Initiates combat: spawns NPCs via `world_engine`, gets player/NPC stats, rolls initiative via `rules_engine`, creates `CombatEncounter` and `CombatParticipant` records in its database.
        * `POST /v1/combat/{combat_id}/player_action`: Processes player actions (currently 'attack'), orchestrating calls to `rules_engine` (contested roll, damage calc), `character_engine` (apply damage/status to player), and `world_engine` (apply damage/status to NPC).
* **Technologies:** FastAPI, SQLAlchemy, Alembic, httpx.
* **Database:** SQLite (`story.db`).
* **Data Managed:** Campaign progress, quests, flags, active combat state (turn order, participants).

### `encounter_generator`

* **Primary Purpose:** A stateless service that generates combat and skill encounters based on tags.
* **Key Features/API Endpoints:**
    * `POST /v1/generate`: Takes a list of tags (e.g., ["forest", "medium", "combat"]) and returns a matching encounter structure (combat or skill challenge).
* **Technologies:** FastAPI.
* **Database:** None. Loads encounter templates from JSON files.
* **Data Managed:** Encounter templates.

### `npc_generator`

* **Primary Purpose:** A stateless service that procedurally generates NPC templates.
* **Key Features/API Endpoints:**
    * `POST /v1/generate`: Generates an NPC template (stats, HP, basic abilities/skills, behavior tags) based on input parameters (kingdom, styles, difficulty, etc.) using rules from `generation_rules.json`.
* **Technologies:** FastAPI, httpx (potentially for future calls to `rules_engine` for advanced generation).
* **Database:** None. Loads generation rules from JSON files.
* **Data Managed:** NPC generation rules.

### `map_generator`

* **Primary Purpose:** A stateless service intended to procedurally generate tile maps.
* **Key Features/API Endpoints:**
    * `POST /v1/generate`: Generates a map based on tags, seed, and dimensions. **Currently uses placeholder random generation logic.**
* **Technologies:** FastAPI.
* **Database:** None. Loads algorithm definitions and tile definitions from JSON files.
* **Data Managed:** Map generation algorithms (definitions, not implementations yet) and tile data.

## 3. Inter-Service Communication

Services communicate via synchronous HTTP API calls using `httpx`. Key interactions:

* **`character_engine` -> `rules_engine`**: Fetches rules (stats, skills, features, talents) needed for character creation and SRE updates.
* **`story_engine` -> `rules_engine`**: Calls for initiative rolls, contested attacks, damage calculations, injury/status lookups, and item data during combat orchestration.
* **`story_engine` -> `character_engine`**: Fetches character context; applies damage and status effects to characters during combat.
* **`story_engine` -> `world_engine`**: Fetches location/NPC context; spawns NPCs/items; applies damage and status effects to NPCs during combat; potentially updates trap status or AI annotations based on game events.
* **Potential Future:** `story_engine` or AI DM likely calls generator services (`encounter_generator`, `npc_generator`, `map_generator`) as needed, though direct calls are not explicitly shown in current `story_engine` code. `npc_generator` might call `rules_engine` for advanced generation.

## 4. Project Goals

* **Create a Modular AI DM Toolkit:** Build a flexible backend for an AI Dungeon Master.
* **Separation of Concerns:** Clearly define responsibilities for rules, state management, orchestration, and generation.
* **Procedural Generation:** Enable dynamic content creation for NPCs, encounters, and maps.
* **Implement Core TTRPG Mechanics:** Provide robust support for character progression, combat, and world interaction based on the defined ruleset.

## 5. Current Status

The project is functional, with all seven microservices running and core communication established. Significant progress has been made on implementing core gameplay features beyond the initial service setup.

* **`rules_engine`:** Functionally rich, providing calculations and lookups for core stats, skills, talents, items, and detailed combat mechanics (initiative, attack, damage, injuries, statuses).
* **`character_engine`:** Supports character creation, SRE progression (including talent checks), inventory management, and receiving combat effects (damage, status). Character listing is available.
* **`world_engine`:** Manages world state effectively, including locations, NPCs (with behavior tags), items, and newly added traps. Supports map/annotation updates and data preloading.
* **`story_engine`:** Core campaign/quest/flag management is functional. **Crucially, it now orchestrates turn-based combat**, initiating encounters and resolving player attack actions by coordinating calls across other services.
* **`encounter_generator`:** Functionally complete for its defined scope (selecting encounters based on tags).
* **`npc_generator`:** Core procedural generation logic is implemented based on defined rules, producing basic NPC templates.
* **`map_generator`:** Service is running, but **core procedural generation algorithms are not yet implemented** (uses placeholder logic).

**Overall:** The backend foundation is solid, and key gameplay systems, particularly combat, are integrated across the relevant services. The primary remaining backend tasks involve implementing the actual map generation algorithms and potentially adding more complex interaction logic and basic NPC AI behavior within the `story_engine`. The next major development phase focuses on building the `player_interface` and integrating the AI DM. The `start_services.bat` script allows running the entire system.