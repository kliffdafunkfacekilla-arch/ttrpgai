# main.py
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import logging
from typing import List
from pydantic import BaseModel
from sqlalchemy.orm.attributes import flag_modified

# Import local modules using relative paths
from . import crud, models, schemas, services
from .database import SessionLocal, engine, Base

# Create tables if they don't exist (useful for simple setups, Alembic is better for prod)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Character Engine")
logger = logging.getLogger("uvicorn.error")

# Add CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # The origin of the frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Dependency ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- API Endpoints ---


@app.post(
    "/v1/characters/", response_model=schemas.CharacterContextResponse, status_code=201
)
async def create_character_endpoint(
    character: schemas.CharacterCreate, db: Session = Depends(get_db)
):
    """
    Creates a new character.
    """
    return await services.create_character(db=db, character=character)


@app.get("/v1/characters/{char_id}", response_model=schemas.CharacterContextResponse)
def read_character(char_id: str, db: Session = Depends(get_db)):
    """
    Retrieves a character by its UUID.
    """
    db_character = services.get_character(db, character_id=char_id)
    if db_character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    return services.get_character_context(db_character)


class SreRequest(BaseModel):
    skill_name: str


@app.post("/v1/characters/{char_id}/add_sre")
async def add_sre_to_character(
    char_id: int, sre_request: SreRequest, db: Session = Depends(get_db)
):
    """Adds SRE to a skill and handles rank-up logic."""
    logger.info(
        f"Adding SRE to skill '{sre_request.skill_name}' for char ID: {char_id}"
    )
    character = crud.get_character(db, char_id=char_id)
    if not character:
        logger.warning(f"Add SRE failed: Character ID {char_id} not found.")
        raise HTTPException(status_code=404, detail="Character not found")

    # Get a mutable copy of the entire sheet
    sheet = dict(character.character_sheet)
    skills = sheet.get("skills", {})
    skill_data = skills.get(sre_request.skill_name)

    if skill_data is None:
        logger.warning(
            f"Skill '{sre_request.skill_name}' not found in character sheet."
        )
        raise HTTPException(
            status_code=400,
            detail=f"Skill '{sre_request.skill_name}' not found for character.",
        )

    # Increment SRE
    skill_data["sre"] = skill_data.get("sre", 0) + 1
    new_sre = skill_data["sre"]
    new_rank = skill_data.get("rank", 0)
    message = f"Added 1 SRE to {sre_request.skill_name}. Current SRE: {new_sre}."
    newly_unlocked_talents = []  # This will hold the talent dictionaries

    if new_sre >= 5:  # Rule: 5 SRE per rank
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
            skill_ranks_now = {
                name: data.get("rank", 0) for name, data in skills.items()
            }

            # This returns a list of dictionaries, e.g., [{"name": "...", "source": "...", "effect": "..."}]
            all_eligible_talents_raw = await services.get_eligible_talents(
                char_stats, skill_ranks_now
            )

            current_talent_dicts = sheet.get("unlocked_talents", [])
            current_talents_set = {
                t["name"]
                for t in current_talent_dicts
                if isinstance(t, dict) and "name" in t
            }

            new_talents_found_dicts = []
            for talent_dict in all_eligible_talents_raw:
                if talent_dict.get("name") not in current_talents_set:
                    new_talents_found_dicts.append(talent_dict)
                    newly_unlocked_talents.append(
                        talent_dict
                    )  # Add the raw dict to our response list
                    logger.info(f"New talent unlocked: {talent_dict.get('name')}")

            if new_talents_found_dicts:
                sheet["unlocked_talents"] = (
                    current_talent_dicts + new_talents_found_dicts
                )

        except Exception as e:
            logger.error(f"Error checking/updating talents for char {char_id}: {e}")
            # Log the error but don't crash the SRE add

    # Explicitly flag the JSON column as modified
    flag_modified(character, "character_sheet")

    # Pass the ENTIRE modified sheet dictionary to the update function
    updated_char = crud.update_character_sheet(db, character, sheet)

    if not updated_char:
        raise HTTPException(
            status_code=500, detail="Failed to update character sheet after adding SRE."
        )

    return {
        "character_id": char_id,
        "skill_name": sre_request.skill_name,
        "new_rank": new_rank,
        "new_sre": new_sre,
        "sre_update_message": message,
        "newly_unlocked_talents": newly_unlocked_talents,  # Return the list of dictionaries
    }


@app.put(
    "/v1/characters/{char_id}/apply_damage",
    response_model=schemas.CharacterContextResponse,
    tags=["Combat Integration"],
)
async def apply_damage(
    char_id: int,
    damage_request: schemas.ApplyDamageRequest,
    db: Session = Depends(get_db),
):
    """Applies HP damage to a character."""
    db_character = crud.get_character(db, char_id=char_id)
    if not db_character:
        raise HTTPException(404, "Character not found")
    # Add validation: Ensure damage_amount is non-negative
    if damage_request.damage_amount < 0:
        raise HTTPException(status_code=400, detail="Damage amount cannot be negative.")

    return crud.apply_damage_to_character(
        db, db_character, damage_request.damage_amount
    )


@app.put(
    "/v1/characters/{char_id}/apply_status",
    response_model=schemas.CharacterContextResponse,
    tags=["Combat Integration"],
)
async def apply_status(
    char_id: int,
    status_request: schemas.ApplyStatusRequest,
    db: Session = Depends(get_db),
):
    """Applies a status effect to a character."""
    db_character = crud.get_character(db, char_id=char_id)
    if not db_character:
        raise HTTPException(404, "Character not found")
    # Add validation: Ensure status_id is valid?
    if not status_request.status_id:
        raise HTTPException(status_code=400, detail="Status ID cannot be empty.")

    return crud.apply_status_to_character(db, db_character, status_request.status_id)


@app.put(
    "/v1/characters/{char_id}/location",
    response_model=schemas.CharacterContextResponse,
    tags=["Location"],
)
async def update_character_location(
    char_id: int,
    location_update: schemas.LocationUpdateRequest,
    db: Session = Depends(get_db),
):
    """Updates the character's current location ID and coordinates."""
    db_character = crud.get_character(db, char_id=char_id)
    if not db_character:
        raise HTTPException(status_code=404, detail="Character not found")

    return crud.update_character_location_and_coords(
        db, db_character, location_update.location_id, location_update.coordinates
    )


@app.get("/v1/characters/", response_model=List[schemas.CharacterContextResponse])
def read_characters(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieves a list of all characters.
    """
    characters = services.get_characters(db, skip=skip, limit=limit)
    return [services.get_character_context(c) for c in characters]


@app.put("/v1/characters/{char_id}", response_model=schemas.CharacterContextResponse)
def update_character(
    char_id: str,
    character_update: schemas.CharacterContextResponse,
    db: Session = Depends(get_db),
):
    """
    Updates a character's full context.
    """
    db_character = services.update_character_context(db, char_id, character_update)
    if db_character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    return services.get_character_context(db_character)
