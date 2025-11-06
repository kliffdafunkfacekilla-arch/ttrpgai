# Story Engine Service

## 1. Overview

The Story Engine is a stateful FastAPI service that acts as the central orchestrator for the AI-TTRPG system. It is responsible for managing high-level game state, directing gameplay loops, and coordinating actions across all other microservices.

-   **Stateful:** Manages campaign progress, quests, story flags, and active combat encounters in its own SQLite database (`story.db`).
-   **Orchestrator:** It is the only service that communicates with all other services, acting as a central hub for game logic.

## 2. Core Responsibilities

-   **Campaign and Quest Management:** Provides endpoints for creating, updating, and querying campaigns and active quests.
-   **Combat Orchestration:** Manages the entire lifecycle of a combat encounter, from initiation and setup to turn-by-turn action resolution and conclusion.
-   **Interaction Handling:** Processes player interactions with the game world, such as using an item on an object, by fetching world state and coordinating updates.
-   **Context Aggregation:** Provides endpoints to get a complete, aggregated context for a character or a location by fetching and combining data from the `character_engine` and `world_engine`.

## 3. Key API Endpoints

### Combat Orchestration

-   `POST /v1/combat/start`: Initiates a new combat encounter.
    -   **Request Body:** `CombatStartRequest` (location ID, list of player IDs, list of NPC template IDs).
    -   **Process:** For each NPC template ID, it first calls the `rules_engine` to get generation parameters. It then calls the `npc_generator` to create a full NPC template with stats and HP. Finally, it tells the `world_engine` to spawn the NPC with the correct data, rolls initiative for all participants, and creates the combat encounter state in its own database.
    -   **Response Body:** `CombatEncounter` (the initial state of the combat, including turn order).

-   `POST /v1/combat/{combat_id}/player_action`: Processes an action taken by a player.
    -   **Request Body:** `PlayerActionRequest` (action type, target ID).
    -   **Process:** When a player attacks, it determines their equipped weapon by calling the `rules_engine`'s item lookup endpoint. It then orchestrates calls to the `rules_engine` for attack rolls and damage calculation, and finally calls `character_engine` or `world_engine` to apply the results.
    -   **Response Body:** A dictionary containing a detailed log of the action's resolution.

### Interaction Handling

-   `POST /v1/actions/interact`: Processes a non-combat player interaction.
    -   **Request Body:** `InteractionRequest` (actor ID, target object ID, location ID).
    -   **Process:** Fetches world annotations from `world_engine`, checks for conditions (e.g., player has a key via `character_engine`), and sends updates back to the `world_engine`.
    -   **Response Body:** `InteractionResponse` (success status, message, and any updated world state).

## 4. Database Schema (`story.db`)

The service uses SQLAlchemy and Alembic to manage its database.

-   `combat_encounters`: Stores the state of all combat encounters, including the current turn index and status (active, players_win, etc.).
-   `combat_participants`: A linking table that stores the participants for each encounter, their actor ID (e.g., `player_1`, `npc_123`), and their initiative roll.
-   `campaigns`, `active_quests`, `story_flags`: Tables for managing the narrative state of the game.

## 5. Dependencies

The Story Engine is the most interconnected service and depends on:

-   **`rules_engine`:** For all combat calculations, initiative rolls, and data lookups (including NPC generation parameters and item details).
-   **`character_engine`:** To get player character state and apply damage/status effects.
-   **`world_engine`:** To get world/NPC state, spawn NPCs, and apply damage/status effects to them.
-   **`npc_generator`:** To generate full NPC templates with stats and HP before they are spawned.
