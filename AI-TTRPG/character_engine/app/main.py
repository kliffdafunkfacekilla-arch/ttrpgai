from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
import requests

from . import crud, models, schemas, services
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/v1/characters/", response_model=schemas.CharacterResponse)
def create_character(character_request: schemas.CharacterCreateRequest, db: Session = Depends(get_db)):
    try:
        ability_schools = services.get_all_ability_schools()
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail="Rules Engine is unavailable.")

    # A more robust implementation would validate character_request against ability_schools

    base_resources = services.get_base_resources()

    character_sheet = {
        "stats": character_request.f_stats,
        "capstone": character_request.capstone_stat,
        "background_skills": character_request.background_skills,
        "resources": base_resources,
        "sre": {},
        "valid_ability_schools": ability_schools
    }

    character_data = {
        "name": character_request.name,
        "kingdom": character_request.kingdom,
        "character_sheet": character_sheet
    }

    return crud.create_character(db=db, character_data=character_data)

@app.get("/v1/characters/{char_id}", response_model=schemas.CharacterResponse)
def read_character(char_id: int, db: Session = Depends(get_db)):
    db_character = crud.get_character(db, char_id=char_id)
    if db_character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    return db_character

@app.post("/v1/characters/{char_id}/add_sre")
def add_sre_to_character(char_id: int, sre_request: dict, db: Session = Depends(get_db)):
    skill_name = sre_request.get("skill_name")
    if not skill_name:
        raise HTTPException(status_code=400, detail="skill_name not provided")

    character = crud.get_character(db, char_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    # This is a simplified SRE addition logic. A real implementation would
    # call the Rules Engine to get the SRE progression rules.
    current_sre = character.character_sheet.get("sre", {})
    current_rank = current_sre.get(skill_name, 0)

    # In this example, we'll just increment the rank.
    new_rank = current_rank + 1
    current_sre[skill_name] = new_rank

    crud.update_character_sheet(db, char_id, {"sre": current_sre})

    return {"message": f"SRE for {skill_name} added/updated.", "new_rank": new_rank}
