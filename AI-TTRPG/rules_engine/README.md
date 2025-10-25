AI-TTRPG Project
This project provides a comprehensive backend system for a tabletop role-playing game (TTRPG), built using a microservice architecture. It is composed of two primary services: the Rules Engine and the Character Engine.

Architecture Overview
The system is split into two distinct FastAPI applications that communicate with each other:

Rules Engine (/AI-TTRPG/rules_engine/): A stateless service that acts as a "calculator" and data source for all game mechanics. It loads all game data (stats, skills, abilities, talents) into memory on startup.

Character Engine (/AI-TTRPG/character_engine/): A stateful service responsible for creating, managing, and updating persistent character sheets. It uses a SQLite database (characters.db) for storage and calls the Rules Engine to get the necessary data for calculations.

1. Rules Engine
Path: AI-TTRPG/rules_engine/

This module is the stateless "calculator" for the Fulcrum System. It knows all the rules and performs all calculations.

Key Features
Data Loading: Loads all game rules from JSON files (abilities.json, kingdom_features.json, stats_and_skills.json, talents.json) into memory on startup.

Validation Endpoints:

/v1/validate/skill_check: Performs a d20 skill check against a DC.

/v1/validate/ability_check: Performs a d20 ability check against a tiered DC.

Lookup Endpoints:

/v1/lookup/kingdom_feature_stats: Returns the stat modifiers for a given feature name.

/v1/lookup/talents: Finds eligible talents based on a character's stats and skill ranks.

/v1/lookup/all_stats: Returns the list of all 12 core stats.

/v1/lookup/all_skills: Returns the master map of all 72 skills.

/v1/lookup/all_ability_schools: Returns the list of all 12 ability schools.

Setup and Run
(Instructions from AI-TTRPG/rules_engine/README.md)

Navigate to the AI-TTRPG/rules_engine/ directory.

Install dependencies: pip install -r requirements.txt

Run the server: uvicorn main:app --reload --port 8000

Test the API at http://127.0.0.1:8000/docs.

2. Character Engine
Path: AI-TTRPG/character_engine/

This module is responsible for managing character sheets. It handles the creation, storage, and modification of player characters.

Key Features
Database: Uses SQLAlchemy and Alembic to manage a SQLite database (characters.db). The characters table stores the character's name, kingdom, and the entire character sheet as a JSON blob.

Rules Engine Integration: This service is dependent on the Rules Engine. It makes httpx calls to the Rules Engine (assumed to be running on http://127.0.0.1:8000) to fetch rules data needed for character creation.

API Endpoints:

POST /v1/characters/: Creates a new character. This endpoint receives the player's choices (name, kingdom, features, skills), calls the Rules Engine to get stat mods and skill lists, calculates the final character sheet, and saves it to the database.

GET /v1/characters/{char_id}: Retrieves a specific character's full data from the database.

POST /v1/characters/{char_id}/add_sre: Adds a Skill Rank Experience (SRE) point to a character's skill, handles skill rank-ups, and checks for newly unlocked talents by calling the Rules Engine.

Setup and Run
(Instructions from AI-TTRPG/character_engine/README.md)

Note: The Rules Engine must be running on port 8000 for this service to function.

Navigate to the AI-TTRPG/character_engine/ directory.

Install dependencies: pip install -r requirements.txt

Initialize the database: alembic upgrade head

Run the server: uvicorn app.main:app --host 127.0.0.1 --port 8001

Test the API at http://127.0.0.1:8001/docs.