# main.py
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import logging
from typing import List
from pydantic import BaseModel
from sqlalchemy.orm.attributes import flag_modified

# Import local modules using relative paths
from . import crud, models, schemas, services
from .database import SessionLocal, engine, Base # Import Base if needed here

# Create tables if they don't exist (useful for simple setups, Alembic is better for prod)
# Base.metadata.create_all(bind=engine)

app = FastAPI(title="Character Engine")
logger = logging.getLogger("uvicorn.error")

# --- Dependency ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- API Endpoints ---

@app.post("/v1/characters/", response_model=schemas.CharacterResponse, status_code=201)
async def create_character( # Make endpoint async
    character_request: schemas.CharacterCreateRequest,
    db: Session = Depends(get_db)
):
    """Creates a new character, calculating stats and fetching rules."""
    logger.info(f"Received request to create character: {character_request.name}")
    try:
        # --- 1. Calculate Stats ---
        logger.info("Calculating stats...")
        stats_list = await services.get_all_stats_names()
        final_stats = {stat: 8 for stat in stats_list}

        for feature_key, feature_name in character_request.f_stats.items():
            mods = await services.get_feature_stat_mods(feature_name)
            for stat in mods.get("+2", []): final_stats[stat] = final_stats.get(stat, 8) + 2
            for stat in mods.get("+1", []): final_stats[stat] = final_stats.get(stat, 8) + 1
            for stat in mods.get("-1", []): final_stats[stat] = final_stats.get(stat, 8) - 1

        cap_stat = character_request.capstone_stat
        if cap_stat in final_stats:
            final_stats[cap_stat] += 1
        logger.info("Stats calculation complete.")

        # --- 2. Initialize Skills & Apply Background ---
        logger.info("Initializing skills...")
        all_skill_names = await services.get_all_skill_names()
        final_skills = {skill: {"rank": 0, "sre": 0} for skill in all_skill_names}

        if len(character_request.background_skills) != 12:
             # This check should ideally happen during Pydantic validation if model enforces length
             logger.warning("Incorrect number of background skills provided.")
             # Raise error or handle default skills? We'll proceed but log warning.
             # raise HTTPException(status_code=400, detail="Must provide exactly 12 background skills.")

        for skill_name in character_request.background_skills:
            if skill_name in final_skills:
                final_skills[skill_name]["rank"] = 1
            else:
                logger.warning(f"Background skill '{skill_name}' not found in master list.")
        logger.info("Skills initialized.")

        # --- 3. Initialize Abilities ---
        logger.info("Initializing abilities...")
        ability_school_names = await services.get_all_ability_schools()
        final_abilities = {school: 0 for school in ability_school_names} # Store rank as int
        logger.info("Abilities initialized.")

        # --- 4. Initialize Resources ---
        logger.info("Initializing resources...")
        # Call the new rules_engine endpoint to get HP and Resources
        vitals_data = await services.get_base_vitals_from_rules(final_stats)
        final_resources = vitals_data.get("resources")
        max_hp = vitals_data.get("max_hp")
        logger.info("Resources initialized.")

        # --- 5. Get Initial Talents ---
        logger.info("Fetching initial talents...")
        skill_ranks_for_talents = {name: data["rank"] for name, data in final_skills.items()}
        initial_talents = await services.get_eligible_talents(final_stats, skill_ranks_for_talents)
        logger.info(f"Found {len(initial_talents)} starting talents.")

        # --- 6. Construct Character Sheet ---
        logger.info("Constructing character sheet...")
        # HP is now fetched from get_base_vitals_from_rules

        character_sheet_data = {
            "stats": final_stats,
            "skills": final_skills,
            "abilities": final_abilities,
            "resources": final_resources, # Fetched from rules_engine
            "combat_stats": {
                "max_hp": max_hp, # Fetched from rules_engine
                "current_hp": max_hp, # Start at full health
                "status_effects": []
            },
            "inventory": [],
            "equipment": {},
            "choices": {
                "features": character_request.f_stats,
                "capstone": character_request.capstone_stat,
                "background_skills": character_request.background_skills
            },
            "unlocked_talents": initial_talents,
            "location": "STARTING_ZONE",
        }
        logger.info("Character sheet constructed.")

        # --- 7. Save to Database via CRUD ---
        logger.info("Saving character to database...")
        db_character = crud.create_character(
            db=db,
            name=character_request.name,
            kingdom=character_request.kingdom,
            character_sheet=character_sheet_data # Pass the calculated sheet
        )
        logger.info(f"Character '{db_character.name}' saved with ID {db_character.id}.")

        # --- 8. Return Response ---
        # Construct the response according to schemas.CharacterResponse
        return schemas.CharacterResponse(
            id=db_character.id,
            name=db_character.name,
            kingdom=db_character.kingdom,
            character_sheet=db_character.character_sheet # Return the saved sheet
        )

    # Keep existing exception handlers for ConnectionError etc.
    except HTTPException as e:
        logger.error(f"HTTP Exception during character creation: {e.detail}")
        raise e
    except Exception as e:
        logger.exception(f"Unexpected error during character creation for {character_request.name}") # Log full traceback
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


@app.get("/v1/characters/{char_id}", response_model=schemas.CharacterResponse)
async def read_character(char_id: int, db: Session = Depends(get_db)): # Make async
    """Retrieves a character by ID."""
    logger.info(f"Fetching character ID: {char_id}")
    db_character = crud.get_character(db, char_id=char_id)
    if db_character is None:
        logger.warning(f"Character ID {char_id} not found.")
        raise HTTPException(status_code=404, detail="Character not found")
    logger.info(f"Character '{db_character.name}' found.")
    # Response model automatically handles conversion if orm_mode=True
    return db_character


# --- Simplified SRE Logic (Placeholder) ---
# Define a Pydantic model for the request body
class SreRequest(BaseModel):
    skill_name: str

@app.post("/v1/characters/{char_id}/add_sre")
async def add_sre_to_character(char_id: int, sre_request: SreRequest, db: Session = Depends(get_db)):
    """Adds SRE to a skill and handles rank-up logic."""
    logger.info(f"Adding SRE to skill '{sre_request.skill_name}' for char ID: {char_id}")
    character = crud.get_character(db, char_id=char_id)
    if not character:
        logger.warning(f"Add SRE failed: Character ID {char_id} not found.")
        raise HTTPException(status_code=404, detail="Character not found")

    # Get a mutable copy of the entire sheet
    sheet = dict(character.character_sheet)
    skills = sheet.get("skills", {})
    skill_data = skills.get(sre_request.skill_name)

    if skill_data is None:
        logger.warning(f"Skill '{sre_request.skill_name}' not found in character sheet.")
        raise HTTPException(status_code=400, detail=f"Skill '{sre_request.skill_name}' not found for character.")

    # Increment SRE
    skill_data["sre"] = skill_data.get("sre", 0) + 1
    new_sre = skill_data["sre"]
    new_rank = skill_data.get("rank", 0)
    message = f"Added 1 SRE to {sre_request.skill_name}. Current SRE: {new_sre}."
    newly_unlocked_talents = [] # This will hold the talent dictionaries

    if new_sre >= 5: # Rule: 5 SRE per rank
        skill_data["sre"] = 0
        skill_data["rank"] += 1
        new_rank = skill_data["rank"]
        new_sre = 0
        message = f"Ranked up {sre_request.skill_name} to Rank {new_rank}!"
        logger.info(message)

        # Check for new talents
        try:
            logger.info("Checking for newly unlocked talents...")
            char_stats = sheet.get("stats", {})
            skill_ranks_now = {name: data.get("rank", 0) for name, data in skills.items()}

            # This returns a list of dictionaries, e.g., [{"name": "...", "source": "...", "effect": "..."}]
            all_eligible_talents_raw = await services.get_eligible_talents(char_stats, skill_ranks_now)

            current_talent_dicts = sheet.get("unlocked_talents", [])
            current_talents_set = {t['name'] for t in current_talent_dicts if isinstance(t, dict) and 'name' in t}

            new_talents_found_dicts = []
            for talent_dict in all_eligible_talents_raw:
                if talent_dict.get('name') not in current_talents_set:
                    new_talents_found_dicts.append(talent_dict)
                    newly_unlocked_talents.append(talent_dict) # Add the raw dict to our response list
                    logger.info(f"New talent unlocked: {talent_dict.get('name')}")

            if new_talents_found_dicts:
                 sheet["unlocked_talents"] = current_talent_dicts + new_talents_found_dicts

        except Exception as e:
             logger.error(f"Error checking/updating talents for char {char_id}: {e}")
             # Log the error but don't crash the SRE add

    # Explicitly flag the JSON column as modified
    flag_modified(character, "character_sheet")

    # Pass the ENTIRE modified sheet dictionary to the update function
    updated_char = crud.update_character_sheet(db, character, sheet)

    if not updated_char:
         raise HTTPException(status_code=500, detail="Failed to update character sheet after adding SRE.")

    return {
        "character_id": char_id,
        "skill_name": sre_request.skill_name,
        "new_rank": new_rank,
        "new_sre": new_sre,
        "sre_update_message": message,
        "newly_unlocked_talents": newly_unlocked_talents # Return the list of dictionaries
    }

    # Update the sheet in the DB
    updated_char = crud.update_character_sheet(db, char_id, {"skills": skills})
    # --- ---

    if not updated_char: # Should not happen if character was found initially
         raise HTTPException(status_code=500, detail="Failed to update character sheet after adding SRE.")

    return {"message": message, "new_rank": new_rank, "new_sre": new_sre}

# Add endpoint to list characters
@app.get("/v1/characters/", response_model=List[schemas.CharacterResponse])
async def list_all_characters(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    characters = crud.list_characters(db, skip=skip, limit=limit)
    return characters

# Add endpoint to add item
@app.post("/v1/characters/{char_id}/inventory/add", response_model=schemas.CharacterResponse)
async def add_inventory_item(char_id: int, item_update: schemas.InventoryUpdateRequest, db: Session = Depends(get_db)):
    db_character = crud.get_character(db, char_id=char_id)
    if db_character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    return crud.add_item_to_inventory(db, db_character, item_update.item_id, item_update.quantity)

# Add endpoint to remove item
@app.post("/v1/characters/{char_id}/inventory/remove", response_model=schemas.CharacterResponse)
async def remove_inventory_item(char_id: int, item_update: schemas.InventoryUpdateRequest, db: Session = Depends(get_db)):
    db_character = crud.get_character(db, char_id=char_id)
    if db_character is None:
        raise HTTPException(status_code=404, detail="Character not found")

    sheet = dict(db_character.character_sheet)
    inventory = sheet.get("inventory", [])

    item_found = False
    for item in inventory:
        if item.get("item_id") == item_update.item_id:
            item_found = True
            if item.get("quantity", 0) < item_update.quantity:
                raise HTTPException(status_code=400, detail=f"Not enough {item_update.item_id} in inventory.")
            break

    if not item_found:
        raise HTTPException(status_code=400, detail=f"{item_update.item_id} not found in inventory.")

    return crud.remove_item_from_inventory(db, db_character, item_update.item_id, item_update.quantity)


@app.put("/v1/characters/{char_id}/apply_damage", response_model=schemas.CharacterResponse, tags=["Combat Integration"])
async def apply_damage(char_id: int, damage_request: schemas.ApplyDamageRequest, db: Session = Depends(get_db)):
     """Applies HP damage to a character."""
     db_character = crud.get_character(db, char_id=char_id)
     if not db_character: raise HTTPException(404, "Character not found")
     # Add validation: Ensure damage_amount is non-negative
     if damage_request.damage_amount < 0:
         raise HTTPException(status_code=400, detail="Damage amount cannot be negative.")

     return crud.apply_damage_to_character(db, db_character, damage_request.damage_amount)

@app.put("/v1/characters/{char_id}/apply_status", response_model=schemas.CharacterResponse, tags=["Combat Integration"])
async def apply_status(char_id: int, status_request: schemas.ApplyStatusRequest, db: Session = Depends(get_db)):
     """Applies a status effect to a character."""
     db_character = crud.get_character(db, char_id=char_id)
     if not db_character: raise HTTPException(404, "Character not found")
     # Add validation: Ensure status_id is valid?
     if not status_request.status_id:
          raise HTTPException(status_code=400, detail="Status ID cannot be empty.")

     return crud.apply_status_to_character(db, db_character, status_request.status_id)
