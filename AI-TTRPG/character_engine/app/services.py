# app/services.py
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import uuid
import httpx # Import httpx
import os # Import os
from . import models, schemas
import logging # --- ADD LOGGING ---
# --- ADDED: Logger ---
logger = logging.getLogger("uvicorn.error")
# --- ADDED: Rules Engine Configuration ---
RULES_ENGINE_URL = os.getenv("RULES_ENGINE_URL", "http://127.0.0.1:8000/v1")
CLIENT_TIMEOUT = 10.0
print(f"Character Engine configured to use Rules Engine at: {RULES_ENGINE_URL}")
# --- UNCHANGED: get_character, get_characters ---
def get_character(db: Session, character_id: str) -> Optional[models.Character]:
    """Fetches a single character by its UUID."""
    return (
        db.query(models.Character).filter(models.Character.id == character_id).first()
    )
def get_characters(
    db: Session, skip: int = 0, limit: int = 100
) -> List[models.Character]:
    """Fetches a list of all characters."""
    return db.query(models.Character).offset(skip).limit(limit).all()
# --- MODIFIED: get_character_context ---
def get_character_context(
    db_character: models.Character,
) -> schemas.CharacterContextResponse:
    """
    Maps the SQLAlchemy model (with JSON fields) to the Pydantic
    response model. THIS FUNCTION IS REUSED.
    """
    if not db_character:
        return None

    # Ensure JSON fields are dictionaries, not strings
    # (FastAPI's JSON type usually handles this, but good to be safe)
    def_stats = {}
    def_skills = {}
    def_pools = {}
    def_talents = []
    def_abilities = []
    def_inv = {}
    def_equip = {}
    def_status = []
    def_injuries = []

    return schemas.CharacterContextResponse(
        id=db_character.id,
        name=db_character.name,
        kingdom=db_character.kingdom or "Unknown",
        level=db_character.level,
        stats=db_character.stats if isinstance(db_character.stats, dict) else def_stats,
        skills=(
            db_character.skills if isinstance(db_character.skills, dict) else def_skills
        ),
        max_hp=db_character.max_hp,
        current_hp=db_character.current_hp,
        resource_pools=(
            db_character.resource_pools
            if isinstance(db_character.resource_pools, dict)
            else def_pools
        ),
        talents=(
            db_character.talents
            if isinstance(db_character.talents, list)
            else def_talents
        ),
        abilities=(
            db_character.abilities
            if isinstance(db_character.abilities, list)
            else def_abilities
        ),
        inventory=(
            db_character.inventory
            if isinstance(db_character.inventory, dict)
            else def_inv
        ),
        equipment=(
            db_character.equipment
            if isinstance(db_character.equipment, dict)
            else def_equip
        ),
        status_effects=(
            db_character.status_effects
            if isinstance(db_character.status_effects, list)
            else def_status
        ),
        injuries=(
            db_character.injuries
            if isinstance(db_character.injuries, list)
            else def_injuries
        ),
        # --- ADD THIS LINE ---
        current_location_id=db_character.current_location_id,
        # --- END ADD ---
        position_x=db_character.position_x,
        position_y=db_character.position_y,
    )
# --- MODIFIED: Helper functions for new creation logic ---
async def _call_rules_engine(
    method: str, endpoint: str, params: Dict = None, json_data: Dict = None
) -> Any:
    """Generic async helper to call the Rules Engine."""
    url = f"{RULES_ENGINE_URL}{endpoint}"
    try:
        async with httpx.AsyncClient() as client:
            logger.info(f"Calling Rules Engine: {method} {url}")
            if method.upper() == "GET":
                response = await client.get(url, params=params, timeout=CLIENT_TIMEOUT)
            elif method.upper() == "POST":
                response = await client.post(
                    url, json=json_data, params=params, timeout=CLIENT_TIMEOUT
                )
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status() # Raise exception for 4xx/5xx errors
            logger.info(f"Rules Engine response status: {response.status_code}")
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"Error connecting to Rules Engine at {e.request.url!r}: {e}")
        # Re-raise as an HTTPException for FastAPI to handle
        from fastapi import HTTPException

        raise HTTPException(
            status_code=503, detail=f"Rules Engine service unavailable: {e}"
        )
    except httpx.HTTPStatusError as e:
        logger.error(
            f"Rules Engine returned error {e.response.status_code}: {e.response.text}"
        )
        from fastapi import HTTPException

        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Rules Engine error: {e.response.text}",
        )
async def get_eligible_talents(
    stats: Dict[str, int], skills: Dict[str, int]
) -> List[Dict]:
    """Fetches eligible talents from the Rules Engine."""
    request_data = {"stats": stats, "skills": skills} # Pass skill ranks directly
    return await _call_rules_engine(
        "POST", "/lookup/talents", json_data=request_data
    )
async def _get_rules_engine_data() -> Dict[str, Any]:
    """
    Fetches all necessary data from the rules_engine service asynchronously.
    """
    print("Fetching all creation data from Rules Engine...")
    endpoints = {
        "kingdom_features": "/lookup/creation/kingdom_features",
        "ability_talents_list": "/lookup/creation/ability_talents",
        "ability_schools": "/lookup/all_ability_schools",
        "stats_list": "/lookup/all_stats",
        "all_skills": "/lookup/all_skills",
        "origin_choices": "/lookup/creation/origin_choices",
        "childhood_choices": "/lookup/creation/childhood_choices",
        "coming_of_age_choices": "/lookup/creation/coming_of_age_choices",
        "training_choices": "/lookup/creation/training_choices",
        "devotion_choices": "/lookup/creation/devotion_choices",
    }

    rules_data = {}

    try:
        # GET requests
        for key, endpoint in endpoints.items():
            print(f"Fetching {key} from {endpoint}...")
            rules_data[key] = await _call_rules_engine("GET", endpoint)

        # Fetch full talent data (POST)
        response = await _call_rules_engine(
            "POST", "/lookup/talents", json_data={"stats": {}, "skills": {}}
        )
        all_talents_list = response
        rules_data["all_talents_map"] = {t["name"]: t for t in all_talents_list}
        print(f"Loaded {len(rules_data['all_talents_map'])} talents into map.")

        # Fetch full ability school data (Series of GETs)
        school_details = {}
        for school_name in rules_data["ability_schools"]:
            school_details[school_name] = await _call_rules_engine(
                "GET", f"/lookup/ability_school/{school_name}"
            )
        rules_data["all_abilities_map"] = school_details

        print("Successfully fetched all creation data.")
        return rules_data

    except Exception as e:
        # Errors will be raised as HTTPErrors from the helper
        print(f"FATAL: Error in _get_rules_engine_data: {e}")
        raise e
def _apply_mods(stats: Dict[str, int], mods: Dict[str, List[str]]):
    """
    Helper to apply a standard 'mods' block to a stats dictionary.
    Modifies the stats dictionary in-place.
    """
    if not isinstance(mods, dict):
        print(f"Warning: Invalid mods format, expected dict, got {type(mods)}")
        return

    for key, stat_list in mods.items():
        if not isinstance(stat_list, list):
            continue

        value = 0
        if key == "+2":
            value = 2
        elif key == "+1":
            value = 1
        elif key == "-1":
            value = -1

        if value == 0:
            continue

        for stat_name in stat_list:
            if stat_name in stats:
                stats[stat_name] += value
                print(f"Applied {key} to {stat_name}. New value: {stats[stat_name]}")
            else:
                print(f"Warning: Stat '{stat_name}' in mods not found in base stats.")
async def create_character(
    db: Session, character: schemas.CharacterCreate
) -> schemas.CharacterContextResponse:
    """
    Creates a new character in the database after calculating all
    stats and vitals based on user choices.
    """
    logger.info(f"--- Starting character creation for: {character.name} ---")
    logger.debug(f"Received character creation payload: {character.model_dump_json(indent=2)}")

    # 1. Get all rules data from Rules Engine
    try:
        rules = await _get_rules_engine_data()
    except Exception as e:
        print(f"Failed to fetch rules data from rules_engine: {e}")
        raise e # Re-raise the HTTPException from the helper

    # 2. Initialize base stats and skills
    base_stats = {stat: 8 for stat in rules.get("stats_list", [])}
    base_skills = {}
    for skill_name in rules.get("all_skills", {}):
        base_skills[skill_name] = {"rank": 0, "sre": 0}

    if not base_stats or not base_skills:
        logger.error("Failed to initialize stats/skills. Rules data for 'stats_list' or 'all_skills' was empty.")
        raise HTTPException(status_code=500, detail="Character creation failed: Missing core rules data.")

    print(f"Initialized stats (all 8s) and skills (all 0s).")

    # 3. Apply Feature mods
    print("Applying feature mods...")
    all_features_data = rules.get("kingdom_features", {})
    for choice in character.feature_choices:
        kingdom_key = "All" if choice.feature_id == "F9" else character.kingdom
        try:
            feature_set = all_features_data.get(choice.feature_id, {}).get(
                kingdom_key, []
            )
            mod_data = next(
                (item for item in feature_set if item["name"] == choice.choice_name),
                None,
            )
            if mod_data and "mods" in mod_data:
                print(f"Applying mods for: {choice.choice_name}")
                _apply_mods(base_stats, mod_data["mods"])
            else:
                print(
                    f"Warning: Could not find mod data for {choice.feature_id} -> {choice.choice_name}"
                )
        except Exception as e:
            print(
                f"Error applying feature {choice.feature_id} ({choice.choice_name}): {e}"
            )

    # 4. Apply Background Skills
    print("Applying background skills...")
    background_choices_map = {
        "origin": {item["name"]: item for item in rules.get("origin_choices", [])},
        "childhood": {
            item["name"]: item for item in rules.get("childhood_choices", [])
        },
        "coming_of_age": {
            item["name"]: item for item in rules.get("coming_of_age_choices", [])
        },
        "training": {item["name"]: item for item in rules.get("training_choices", [])},
        "devotion": {item["name"]: item for item in rules.get("devotion_choices", [])},
    }
    origin_skills = (
        background_choices_map["origin"]
        .get(character.origin_choice, {})
        .get("skills", [])
    )
    childhood_skills = (
        background_choices_map["childhood"]
        .get(character.childhood_choice, {})
        .get("skills", [])
    )
    coming_of_age_skills = (
        background_choices_map["coming_of_age"]
        .get(character.coming_of_age_choice, {})
        .get("skills", [])
    )
    training_skills = (
        background_choices_map["training"]
        .get(character.training_choice, {})
        .get("skills", [])
    )
    devotion_skills = (
        background_choices_map["devotion"]
        .get(character.devotion_choice, {})
        .get("skills", [])
    )
    all_background_skills = (
        origin_skills
        + childhood_skills
        + coming_of_age_skills
        + training_skills
        + devotion_skills
    )
    for skill_name in all_background_skills:
        if skill_name in base_skills:
            base_skills[skill_name]["rank"] = 1
            print(f"Granted Rank 1 in skill: {skill_name}")
        else:
            print(f"Warning: Background choice granted unknown skill '{skill_name}'")

    # 5. Apply Ability Talent mods
    print(f"Applying Ability Talent mods for: {character.ability_talent}")
    ab_talent_data = rules.get("all_talents_map", {}).get(character.ability_talent)
    if ab_talent_data and "mods" in ab_talent_data:
        _apply_mods(base_stats, ab_talent_data["mods"])

    print(f"Final calculated stats: {base_stats}")

    # 6. Get Vitals from Rules Engine
    print("Calculating vitals...")
    try:
        vitals_data = await _call_rules_engine(
            "POST",
            "/calculate/base_vitals",
            json_data={"stats": base_stats}
        )
        max_hp = vitals_data.get("max_hp", 1)
        resource_pools = vitals_data.get("resources", {})
        print(f"Vitals calculated: MaxHP={max_hp}")
    except Exception as e:
        print(f"FATAL: Failed to calculate vitals from rules_engine: {e}")
        raise e # Re-raise the HTTPException from the helper

    # 7. Get base abilities
    base_abilities = []
    school_data = rules.get("all_abilities_map", {}).get(character.ability_school)
    if school_data and "tiers" in school_data and len(school_data["tiers"]) > 0:
        base_abilities.append(school_data["tiers"][0].get("name", "Unknown Ability"))
        print(f"Added Tier 0 ability: {base_abilities[0]}")

    # 8. Create DB model (saving to separate columns)
    print("Creating database entry...")
    db_character = models.Character(
        id=str(uuid.uuid4()),
        name=character.name,
        kingdom=character.kingdom,
        level=1,
        stats=base_stats,
        skills=base_skills,
        max_hp=max_hp,
        current_hp=max_hp,
        resource_pools=resource_pools,
        talents=[character.ability_talent],
        abilities=base_abilities,
        inventory={"item_iron_sword": 1, "item_leather_jerkin": 1},
        equipment={"weapon": "item_iron_sword", "armor": "item_leather_jerkin"},
        status_effects=[],
        injuries=[],
        # --- ADD THIS LINE ---
        current_location_id=1, # Default to STARTING_ZONE
        position_x=5, # Default start position
        position_y=5 # Default start position
    )

    logger.debug(f"Constructed DB character model: {db_character.__dict__}")

    # 9. Save and return
    try:
        logger.info("Adding character to DB session...")
        db.add(db_character)
        logger.info("Committing transaction...")
        db.commit()
        logger.info("Transaction committed.")
        db.refresh(db_character)
        logger.info(f"Successfully refreshed character from DB: {db_character.id}")

        # This function will now work, as db_character has the separate fields
        response = get_character_context(db_character)
        logger.debug(f"Returning character context response: {response.model_dump_json(indent=2)}")
        logger.info("--- Character creation successful ---")
        return response
    except Exception as e:
        db.rollback()
        logger.error(f"Database error on character save: {e}", exc_info=True)
        raise Exception(f"Database error: {e}")
# --- MODIFIED: update_character_context ---
def update_character_context(
    db: Session, character_id: str, updates: schemas.CharacterContextResponse
) -> Optional[models.Character]:
    """
    Updates a character in the database from a full context object.
    """
    db_character = get_character(db, character_id)
    if db_character:
        print(f"Updating character: {character_id}")
        # Update all fields from the 'updates' Pydantic model
        db_character.name = updates.name
        db_character.kingdom = updates.kingdom
        db_character.level = updates.level
        db_character.stats = updates.stats
        db_character.skills = updates.skills
        db_character.max_hp = updates.max_hp
        db_character.current_hp = updates.current_hp
        db_character.resource_pools = updates.resource_pools
        db_character.talents = updates.talents
        db_character.abilities = updates.abilities
        db_character.inventory = updates.inventory
        db_character.equipment = updates.equipment
        db_character.status_effects = updates.status_effects
        db_character.injuries = updates.injuries
        # --- ADD THIS LINE ---
        db_character.current_location_id = updates.current_location_id
        # --- END ADD ---
        db_character.position_x = updates.position_x
        db_character.position_y = updates.position_y

        try:
            db.commit()
            db.refresh(db_character)
            print(f"Successfully updated character {character_id}.")
            return db_character
        except Exception as e:
            db.rollback()
            print(f"Database error on character update: {e}")
            raise Exception(f"Database error: {e}")
    else:
        print(f"Update failed: Character {character_id} not found.")
        return None


async def create_default_test_character(db: Session, rules_data: dict):
    """Creates a hardcoded default character for testing by calling the main creation service."""
    logger.info("--- Creating Default Test Character ---")

    # 1. Define the default choices using the correct schemas.CharacterCreate payload
    # This payload mirrors what a user would select in the frontend for a quick start.
    creation_request = schemas.CharacterCreate(
        name="Tester",
        kingdom="kingdom_automata",
        feature_choices=[
            schemas.FeatureChoice(feature_id="F1", choice_name="Automata Optics"),
            schemas.FeatureChoice(feature_id="F2", choice_name="Automata Plating"),
            schemas.FeatureChoice(feature_id="F3", choice_name="Automata Scent Sensors"),
            schemas.FeatureChoice(feature_id="F4", choice_name="Automata Vocalizer"),
            schemas.FeatureChoice(feature_id="F5", choice_name="Automata Auditory Sensors"),
            schemas.FeatureChoice(feature_id="F6", choice_name="Automata Stabilizer"),
            schemas.FeatureChoice(feature_id="F7", choice_name="Automata Chassis"),
            schemas.FeatureChoice(feature_id="F8", choice_name="Automata Power Core"),
            schemas.FeatureChoice(feature_id="F9", choice_name="Capstone: +2 Cunning"),
        ],
        origin_choice="Origin: Scribe",
        childhood_choice="Childhood: Street Urchin",
        coming_of_age_choice="Coming of Age: Scout",
        training_choice="Training: Self-Taught",
        devotion_choice="Devotion: The People",
        ability_school="Force",
        ability_talent="Mind over Matter"
    )

    logger.info(f"Default character payload created for '{creation_request.name}'. Passing to main creation service.")

    # 2. Call the robust, existing create_character service with the payload
    # This avoids duplicating logic and ensures the test character is always created
    # with the same rules and calculations as a player character.
    try:
        # Note: We don't need to pass 'rules_data' here because create_character fetches it internally.
        new_character = await create_character(db=db, character=creation_request)
        logger.info("--- Default test character creation successful ---")
        return new_character
    except Exception as e:
        logger.exception("An error occurred in the main creation service while creating the default character.")
        # Re-raise the exception to be handled by the endpoint.
        raise e
