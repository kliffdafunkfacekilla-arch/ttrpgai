# Character Engine Service

## 1. Overview

The Character Engine is a stateful FastAPI service that manages the creation, persistence, and modification of player character sheets. It is the sole authority on player character data.

-   **Stateful:** Manages character data in its own SQLite database (`characters.db`).
-   **Data-Focused:** Its primary role is to serve and update character data upon request from the `story_engine` or `player_interface`.

## 2. Core Responsibilities

-   **Character Creation:** Handles the complex process of creating a new character, including calculating initial stats, skills, and talents by making calls to the `rules_engine`.
-   **Data Persistence:** Stores the entire character sheet as a single JSON blob in the database, which is managed via SQLAlchemy and Alembic.
-   **State Modification:** Provides a suite of endpoints for modifying a character's state, such as applying damage, adding status effects, managing inventory, and updating their location.
-   **Progression:** Manages character progression by tracking Skill Rank Experience (SRE) and unlocking new talents when milestones are reached.

## 3. Key API Endpoints

-   `POST /v1/characters/`: Creates a new character.
    -   **Process:** This is an orchestrated endpoint that calls the `rules_engine` multiple times to fetch master stat/skill lists, get stat modifications from features, and determine base vitals (HP/resources).

-   `GET /v1/characters/{char_id}`: Retrieves the full `character_sheet` for a given character.

-   `PUT /v1/characters/{char_id}/apply_damage`: Applies HP damage to a character.
    -   **Request Body:** `ApplyDamageRequest` (damage amount).
    -   **Process:** Modifies the `current_hp` field within the `combat_stats` section of the character's JSON sheet.

-   `PUT /v1/characters/{char_id}/apply_status`: Applies a status effect to a character.
    -   **Request Body:** `ApplyStatusRequest` (status ID).
    -   **Process:** Appends the status ID to the `status_effects` list in the character's JSON sheet.

-   `PUT /v1/characters/{char_id}/location`: Updates the character's current position.
    -   **Request Body:** `LocationUpdateRequest` (new location ID and coordinates).
    -   **Process:** Modifies the `location` object within the character's JSON sheet.

-   `POST /v1/characters/{char_id}/inventory/add` & `/remove`: Adds or removes items from the character's inventory list within the JSON sheet.

## 4. Database Schema (`characters.db`)

-   `characters`: The primary table, containing basic info (`id`, `name`, `kingdom`) and a `character_sheet` column.
    -   `character_sheet`: A `JSON` field that stores the entire character data structure, including stats, skills, inventory, equipment, combat stats, location, and more. All modifications to a character are performed on this JSON object.

## 5. Dependencies

-   **`rules_engine`:** The Character Engine depends heavily on the `rules_engine` during character creation and progression to ensure all stats and abilities conform to the game's ruleset. It makes no calls to other services.
