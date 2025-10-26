Okay, here's a plan of development moving forward to get from our current state (all 7 backend services running) to a fully functional game application with the features we've discussed.

## Development Plan: AI-TTRPG

**Current Status:** All 7 backend microservices (`rules_engine`, `character_engine`, `world_engine`, `story_engine`, `encounter_generator`, `npc_generator`, `map_generator`) are planned, built with basic functionality, and running locally. Core inter-service communication via the `story_engine` is established.

---

### **Step 1: Backend Refinement & Feature Implementation**

This step focuses on adding the necessary backend logic and endpoints discussed in our "forward-thinking" phase.

1.  **`character_engine` Enhancements:**
    * **Implement Inventory:** Add an `inventory` field (likely a JSON list) to the `character_sheet` in `models.py`.
    * **Add Inventory API:** Create new endpoints in `main.py` (e.g., `POST /v1/characters/{char_id}/inventory/add`, `POST /v1/characters/{char_id}/inventory/remove`) and corresponding `crud.py` functions to manage the player's inventory.
    * **Add Character List API:** Create an endpoint (e.g., `GET /v1/characters/`) to list existing characters for the main menu.
2.  **`world_engine` Enhancements:**
    * **Implement Traps:** Add the `TrapInstance` table to `models.py`, create schemas in `schemas.py`, add CRUD functions, and API endpoints (`POST /v1/traps/spawn`, `PUT /v1/traps/{trap_id}`, `GET /v1/locations/{loc_id}/traps`) in `main.py`.
    * **Implement Puzzle Objects (Optional):** Decide if simple puzzle states (lever position) will be stored in `Location.generated_map_data` or if a dedicated `PuzzleObjectInstance` table is needed. Add necessary models, schemas, CRUD, and API endpoints.
    * **Data Loading:** Implement functions (perhaps called via an API endpoint or on startup) to pre-populate the database with initial Regions, Factions, and key Locations.
    * **AI Annotations Storage:** Ensure the `Location.generated_map_data` field (or a related field) can store the AI's annotations (descriptions, interaction flags, lock states, etc.). Update `crud.py` and `main.py` if needed.
    * **NPC Behavior Storage:** Confirm `NpcInstance` in `models.py` stores `behavior_tags`. Ensure `crud.spawn_npc` handles saving this.
3.  **`story_engine` Enhancements:**
    * **Implement Interaction Logic:** Add internal functions (likely called by API endpoints triggered by the `player_interface`) that handle basic interactions. These functions will fetch annotations/state from `world_engine` (via `services.py`), check conditions, and orchestrate updates to `world_engine` and `character_engine` (e.g., for opening doors, picking up items).
    * **Implement Basic Combat AI Logic:** Create internal functions (likely part of a combat state machine) that fetch NPC `behavior_tags` from `world_engine`, determine basic actions based on simple rules, and orchestrate calls to `rules_engine` (for checks) and `world_engine`/`character_engine` (for updates).
    * **Add Campaign List API:** Create an endpoint (e.g., `GET /v1/campaigns/`) for the main menu.

---

### **Step 2: Implement Generator Algorithms**

Flesh out the core logic within the stateless generators.

1.  **`map_generator`:**
    * **Implement Algorithms:** Replace the placeholder logic in `core.py` with actual procedural generation algorithms (e.g., Cellular Automata, Drunkard's Walk, BSP Trees) based on the definitions in `data/generation_algorithms.json`. Add necessary libraries (`numpy`, `noise`) to `requirements.txt`.
    * **Implement Post-Processing:** Add functions for steps like `add_border_trees`, `clear_center`, `fill_unreachable`.
    * **Refine Spawn Points:** Implement logic to intelligently place player/enemy spawn points on valid tiles.
2.  **`npc_generator`:**
    * **Refine Generation Rules:** Expand `data/generation_rules.json` with more detailed mappings for stats, skills, abilities, and potentially equipment based on input parameters.
    * **Implement Skill/Ability Logic:** Enhance `core.py` to derive relevant skills and select appropriate abilities based on styles and difficulty, possibly calling the `rules_engine` via `httpx` to get valid ability lists or details.

---

### **Step 3: Develop `player_interface`**

Build the client application. This is a significant step.

1.  **Choose Technology:** Decide on the framework (e.g., Web: React, Vue, Svelte; Desktop: Godot, Unity, PySide/Qt).
2.  **Basic Structure:** Set up the main application window/page.
3.  **API Client:** Implement functions to make API calls to the `story_engine`'s orchestration and context endpoints.
4.  **Main Menu:** Implement UI for starting new games, loading saved games (requires save/load logic in `story_engine`), listing characters (calls `character_engine` via `story_engine`).
5.  **Character Sheet Display:** Create a visually appealing display by fetching data from `GET /v1/context/character/{id}`.
6.  **Exploration Mode UI:**
    * Implement map rendering logic that takes the `map_data` array and `tile_definitions.json` (`graphic_ref`) to display the tile map.
    * Handle player movement input (click/keyboard).
    * Implement interaction logic (clicking objects, doors). Send interaction requests to the `story_engine`.
    * Display location descriptions, weather, etc., received from `story_engine`.
7.  **Encounter Mode UI:**
    * Implement UI for turn-based combat (turn order, HP display, action buttons).
    * Handle player combat actions (attack, ability use) - send requests to `story_engine`.
    * Display combat logs/descriptions received from `story_engine`/AI DM.
8.  **Sound/Graphics Integration:** Add logic to load and display graphics based on `graphic_ref` and play sounds/music based on events received from the backend.

---

### **Step 4: Integrate AI DM**

Connect the actual AI "brain" (external language model or logic system).

1.  **AI Wrapper/Interface:** Develop the code that sits between the AI model and your backend. This wrapper will:
    * Receive game state/context from the `story_engine`.
    * Format this context into a suitable prompt for the AI model.
    * Send the prompt to the AI model.
    * Receive the AI's response (narrative text, decisions, commands).
    * Parse the AI's response.
    * Translate AI commands into API calls to the appropriate `story_engine` endpoints (e.g., `POST /v1/quests/`, `POST /v1/flags/`, `POST /v1/actions/spawn_npc`).
    * Send narrative text to the `player_interface` (likely via the `story_engine`).
2.  **Connect AI to `story_engine`:** Hook up this AI wrapper to make calls to the `story_engine`'s API.

---

### **Step 5: Testing, Balancing & Bug Fixing**

The final phase involves extensive end-to-end testing.

1.  **Full Loop Testing:** Play through various scenarios, testing exploration, interaction, map generation, encounter generation, combat (both player and basic NPC AI turns), quest progression, and AI adaptation.
2.  **Identify Bottlenecks:** Look for slow responses or areas where the AI is prompted too frequently.
3.  **Gameplay Balancing:** Adjust rules data (in `rules_engine`), encounter templates (in `encounter_generator`), NPC generation rules (in `npc_generator`), and potentially AI prompting to ensure fair difficulty and engaging gameplay.
4.  **Bug Fixing:** Address errors found in any of the microservices or the interface.

This plan moves step-by-step from refining the backend foundations to implementing the core generation logic, building the user-facing part, integrating the AI brain, and finally polishing the complete system. 🚀