# World Engine Service

## 1. Overview

The World Engine is a stateful FastAPI service responsible for managing the persistent state of the game world. It acts as the single source of truth for the state of all locations, NPCs, items, and other world-level entities.

-   **Stateful:** Manages all world data in its own SQLite database (`world.db`).
-   **Data Source:** Provides detailed information about the game world to the `story_engine` for orchestration purposes.

## 2. Core Responsibilities

-   **Location Management:** Stores and serves data for all game locations, including their procedurally generated maps and any AI-specific metadata (`ai_annotations`).
-   **NPC State:** Manages the state of all non-player characters in the world, including their current health, status effects, and precise coordinates on a map.
-   **Item State:** Tracks the existence and location of all items, whether they are on the ground or in an NPC's inventory.
-   **World Setup:** Includes a `preload_data.py` script to populate the database with initial game data, such as starting regions and factions.

## 3. Key API Endpoints

-   `GET /v1/locations/{location_id}`: Retrieves the complete data for a single location, including its map, all NPC instances, item instances, and trap instances. This is the primary endpoint used by the `story_engine` to get context.

-   `POST /v1/npcs/spawn`: Creates a new `NpcInstance` in the database at a specified location and coordinates. This is called by the `story_engine` at the start of combat.

-   `PUT /v1/npcs/{npc_id}`: Updates the state of an existing NPC. This is used by the `story_engine` to apply damage (by updating `current_hp`), add status effects, or change an NPC's coordinates.

-   `PUT /v1/locations/{location_id}/annotations`: Updates the `ai_annotations` JSON blob for a location. This is used by the `story_engine` to persist changes to interactable objects (e.g., changing a door's status from "locked" to "unlocked").

-   `POST /v1/items/spawn` & `DELETE /v1/items/{item_id}`: Endpoints for creating and deleting item instances in the world.

## 4. Database Schema (`world.db`)

The service uses SQLAlchemy and Alembic to manage its database. The key tables include:

-   `regions` & `factions`: High-level tables for world organization.
-   `locations`: Stores data for each distinct map or area. Contains a `generated_map_data` JSON field for the tile map and an `ai_annotations` JSON field for interactable object states.
-   `npc_instances`: Represents individual NPCs in the world. Includes their `template_id`, `current_hp`, `max_hp`, `status_effects`, and `coordinates`. Linked to a `location`.
-   `item_instances`: Represents individual items. Can be linked to a `location` (on the ground) or an `npc_instance` (in their inventory).
-   `trap_instances`: Represents traps at a location.

## 5. Dependencies

The World Engine is a foundational stateful service and has **no dependencies** on other services. It only responds to requests, typically from the `story_engine`.
