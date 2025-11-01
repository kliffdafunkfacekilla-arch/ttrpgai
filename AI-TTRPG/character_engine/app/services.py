# app/services.py
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import uuid
import httpx  # Import httpx
import os  # Import os
from . import models, schemas

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


# --- UNCHANGED: get_character_context ---
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
        position_x=db_character.position_x,
        position_y=db_character.position_y,
    )


# --- ADDED: Helper functions for new creation logic ---
async def _call_rules_engine(
    method: str, endpoint: str, params: Dict = None, json_data: Dict = None
) -> Any:
    """Generic async helper to call the Rules Engine."""
    url = f"{RULES_ENGINE_URL}{endpoint}"
    try:
        async with httpx.AsyncClient() as client:
            logger.info(f"Calling Rules Engine: {method} {url}")
            if method.upper() == "GET":
                response = await client.get(url, params=params)
            elif method.upper() == "POST":
                response = await client.post(url, json=json_data, params=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()  # Raise exception for 4xx/5xx errors
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
    request_data = {"stats": stats, "skills": skills}  # Pass skill ranks directly
    return await _call_rules_engine(
        "POST", "/v1/lookup/talents", json_data=request_data
    )


def _get_rules_engine_data() -> Dict[str, Any]:
    """
    Fetches all necessary data from the rules_engine service.
    """
    print("Fetching all creation data from Rules Engine...")
    endpoints = {
        "kingdom_features": "/lookup/creation/kingdom_features",
        "background_talents_list": "/lookup/creation/background_talents",
        "ability_talents_list": "/lookup/creation/ability_talents",
        "ability_schools": "/lookup/all_ability_schools",  # Returns a list of names
        "stats_list": "/lookup/all_stats",
        "all_skills": "/lookup/all_skills",
        "all_talents": "/v1/lookup/talents",  # POST, needs empty body to get all
        "all_abilities_full": "/lookup/all_ability_schools",  # Re-using, need to get full data
    }

    rules_data = {}
    client = httpx.Client(base_url=RULES_ENGINE_URL, timeout=CLIENT_TIMEOUT)

    try:
        # GET requests
        for key, endpoint in endpoints.items():
            if key in ["all_talents"]:
                continue  # Skip POST
            if key in ["all_abilities_full"]:
                continue  # Handled below
            print(f"Fetching {key} from {endpoint}...")
            response = client.get(endpoint)
            response.raise_for_status()
            rules_data[key] = response.json()

        # Fetch full talent data
        response = client.post("/lookup/talents", json={"stats": {}, "skills": {}})
        response.raise_for_status()
        # This returns a list. Let's convert to a dict for easy lookup.
        all_talents_list = response.json()
        rules_data["all_talents_map"] = {t["name"]: t for t in all_talents_list}
        print(f"all_talents_map: {rules_data['all_talents_map']}")

        # Fetch full ability school data
        school_details = {}
        for school_name in rules_data["ability_schools"]:
            response = client.get(f"/lookup/ability_school/{school_name}")
            response.raise_for_status()
            school_details[school_name] = response.json()
        rules_data["all_abilities_map"] = school_details

        print("Successfully fetched all creation data.")
        return rules_data

    except httpx.RequestError as e:
        print(f"FATAL: HTTP request failed: {e}")
        raise Exception(f"Rules Engine connection failed: {e}")
    except httpx.HTTPStatusError as e:
        print(f"FATAL: HTTP status error: {e.response.status_code} - {e.response.text}")
        raise Exception(f"Rules Engine error: {e.response.status_code}")
    finally:
        client.close()


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


# --- MODIFIED: create_character ---
def create_character(
    db: Session, character: schemas.CharacterCreate
) -> schemas.CharacterContextResponse:
    """
    Creates a new character in the database after calculating all
    stats and vitals based on user choices.
    """
    print(f"Starting creation for character: {character.name}")

    # 1. Get all rules data from Rules Engine
    try:
        rules = _get_rules_engine_data()
    except Exception as e:
        print(f"Failed to fetch rules data from rules_engine: {e}")
        # Re-raise as a more specific HTTP-style exception if desired
        raise Exception(f"Failed to fetch rules data: {e}")

    # 2. Initialize base stats and skills
    base_stats = {stat: 8 for stat in rules["stats_list"]}
    base_skills = {skill: 0 for skill in rules["all_skills"]}
    print(f"Initialized stats (all 8s) and skills (all 0s).")

    # 3. Apply Feature mods
    print("Applying feature mods...")
    all_features_data = rules.get("kingdom_features", {})
    for choice in character.feature_choices:
        # F9 uses 'All' key, others use kingdom name
        kingdom_key = "All" if choice.feature_id == "F9" else character.kingdom

        try:
            # Find the specific choice from the rules data
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

    # 4. Apply Background Talent mods
    print(f"Applying Background Talent mods for: {character.background_talent}")
    bg_talent_data = rules.get("all_talents_map", {}).get(character.background_talent)
    if bg_talent_data and "mods" in bg_talent_data:
        _apply_mods(base_stats, bg_talent_data["mods"])
    else:
        print(
            f"Warning: No mod data found for background talent {character.background_talent}"
        )

    # 5. Apply Ability Talent mods
    print(f"Applying Ability Talent mods for: {character.ability_talent}")
    ab_talent_data = rules.get("all_talents_map", {}).get(character.ability_talent)
    if ab_talent_data and "mods" in ab_talent_data:
        _apply_mods(base_stats, ab_talent_data["mods"])
    else:
        print(
            f"Warning: No mod data found for ability talent {character.ability_talent}"
        )

    print(f"Final calculated stats: {base_stats}")

    # 6. Get Vitals from Rules Engine
    print("Calculating vitals...")
    try:
        response = httpx.post(
            f"{RULES_ENGINE_URL}/calculate/base_vitals",
            json={"stats": base_stats},
            timeout=CLIENT_TIMEOUT,
        )
        response.raise_for_status()
        vitals_data = response.json()
        max_hp = vitals_data.get("max_hp", 1)  # Default to 1 to avoid DB constraints
        resource_pools = vitals_data.get("resources", {})
        print(f"Vitals calculated: MaxHP={max_hp}")
    except Exception as e:
        print(f"FATAL: Failed to calculate vitals from rules_engine: {e}")
        raise Exception(f"Failed to calculate vitals: {e}")

    # 7. Get base abilities
    base_abilities = []
    school_data = rules.get("all_abilities_map", {}).get(character.ability_school)
    if school_data and "tiers" in school_data and len(school_data["tiers"]) > 0:
        # Add Tier 0 ability
        base_abilities.append(school_data["tiers"][0].get("name", "Unknown Ability"))
        print(f"Added Tier 0 ability: {base_abilities[0]}")

    # 8. Create DB model
    print("Creating database entry...")
    db_character = models.Character(
        id=str(uuid.uuid4()),
        name=character.name,
        kingdom=character.kingdom,
        level=1,
        stats=base_stats,
        skills=base_skills,
        max_hp=max_hp,
        current_hp=max_hp,  # Start at full health
        resource_pools=resource_pools,
        talents=[character.background_talent, character.ability_talent],
        abilities=base_abilities,
        # Set defaults for the rest
        inventory={},
        equipment={},
        status_effects=[],
        injuries=[],
        position_x=0,  # TODO: Get start position from world_engine
        position_y=0,
    )

    # 9. Save and return
    try:
        db.add(db_character)
        db.commit()
        db.refresh(db_character)
        print(f"Successfully created character {db_character.id} in database.")
        return get_character_context(db_character)
    except Exception as e:
        db.rollback()
        print(f"Database error on character save: {e}")
        raise Exception(f"Database error: {e}")


# --- UNCHANGED: update_character_context ---
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
