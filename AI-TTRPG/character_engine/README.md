# Character Engine Service

## 1. Overview

The Character Engine is a stateful FastAPI service that manages the creation, persistence, and modification of player character sheets. It is the sole authority on player character data.

-   **Stateful:** Manages character data in its own SQLite database (`characters.db`).
-   **Data-Focused:** Its primary role is to serve and update character data upon request from the `story_engine` or `player_interface`.

## 2. Core Responsibilities

-   **Character Creation:** Handles the complex process of creating a new character, including calculating initial stats, skills, and talents by making calls to the `rules_engine`.
-   **Data Persistence:** Stores character data in a flat schema managed via SQLAlchemy and Alembic, with dedicated columns for stats, skills, inventory, etc.
-   **State Modification:** Provides a suite of endpoints for modifying a character's state, such as applying damage, adding status effects, managing inventory, and updating their location.
-   **Progression:** Manages character progression by tracking Skill Rank Experience (SRE) and unlocking new talents when milestones are reached.

## 3. Key API Endpoints

-   `POST /v1/characters/`: Creates a new character.
    -   **Process:** This is an orchestrated endpoint that calls the `rules_engine` multiple times to fetch master stat/skill lists, get stat modifications from features, and determine base vitals (HP/resources).

-   `GET /v1/characters/{char_id}`: Retrieves the full character context for a given character.

-   `PUT /v1/characters/{char_id}/apply_damage`: Applies HP damage to a character.
    -   **Request Body:** `ApplyDamageRequest` (damage amount).
    -   **Process:** Modifies the `current_hp` column for the character.

-   `PUT /v1/characters/{char_id}/apply_status`: Applies a status effect to a character.
    -   **Request Body:** `ApplyStatusRequest` (status ID).
    -   **Process:** Appends the status ID to the `status_effects` JSON array in the character's row.

-   `PUT /v1/characters/{char_id}/location`: Updates the character's current position.
    -   **Request Body:** `LocationUpdateRequest` (new location ID and coordinates).
    -   **Process:** Modifies the `current_location_id`, `position_x`, and `position_y` columns for the character.

-   `POST /v1/characters/{char_id}/inventory/add` & `/remove`: Adds or removes items from the character's inventory.

## 4. Database Schema (`characters.db`)

The `characters` table uses a flat model with individual columns for each data attribute, managed by SQLAlchemy. Key columns include:

-   `id` (String, UUID) - Primary Key
-   `name` (String)
-   `kingdom` (String)
-   `level` (Integer)
-   `stats` (JSON)
-   `skills` (JSON)
-   `max_hp` (Integer)
-   `current_hp` (Integer)
-   `resource_pools` (JSON)
-   `talents` (JSON)
-   `abilities` (JSON)
-   `inventory` (JSON)
-   `equipment` (JSON)
-   `status_effects` (JSON)
-   `injuries` (JSON)
-   `position_x` (Integer)
-   `position_y` (Integer)
-   `current_location_id` (Integer)

## 5. Dependencies

-   **`rules_engine`:** The Character Engine depends heavily on the `rules_engine` during character creation and progression to ensure all stats and abilities conform to the game's ruleset. It makes no calls to other services.
