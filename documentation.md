# Project Documentation

This document outlines the broken and unfinished sections of the AI-TTRPG project, as well as the purpose of each service.

## Services

### Character Engine

The `character_engine` is a stateful FastAPI application that serves as a persistent database for character sheets, using SQLAlchemy for ORM and Alembic for migrations.

### Encounter Generator

The `encounter_generator` is a stateless FastAPI service that generates encounters from JSON data (`combat_encounters.json`, `skill_challenges.json`) based on tags.

### Map Generator

The `map_generator` is a stateless FastAPI service that procedurally generates tile maps from rules in `generation_algorithms.json` and `tile_definitions.json`.

### NPC Generator

The `npc_generator` is a stateless FastAPI service that procedurally generates NPC templates from rules defined in `generation_rules.json`.

**Issues:**

*   `core.py` contains a hardcoded URL for the `rules_engine`, which could make testing and deployment difficult.
*   `data_loader.py` does not handle cases where the `generation_rules.json` file is missing or invalid, which could cause the service to crash.

### Rules Engine

The `rules_engine` is a stateless FastAPI application that provides game rules and data to the other services.

**Issues:**

*   `core.py` contains a hardcoded `EQUIPMENT_CATEGORY_TO_SKILL_MAP` dictionary that should be moved to a JSON file.
*   `data_loader.py` could benefit from more robust error handling.

### Story Engine

The `story_engine` is a FastAPI application that manages campaign state, quests, and orchestrates other services.

**Issues:**

*   `combat_handler.py` contains significant placeholder logic, especially in the `get_equipped_weapon` and `get_equipped_armor` functions.
*   The skill mapping in `combat_handler.py` is simplified and marked with a `FIXME` comment.
*   `interaction_handler.py` only handles doors and item pickups, and the logic for removing keys from inventory is not yet implemented.

### World Engine

The `world_engine` is a FastAPI application using SQLAlchemy, Alembic, and Pydantic to manage game world state (locations, NPCs, items).

**Issues:**

*   The `spawn_npc` function in `crud.py` uses placeholder logic to assign default `current_hp` and `max_hp` values instead of fetching them from a data source.
