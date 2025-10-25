# crud.py
from sqlalchemy.orm import Session
from . import models
from typing import Dict, Any

def get_character(db: Session, char_id: int) -> models.Character | None:
    """Retrieves a single character by ID."""
    return db.query(models.Character).filter(models.Character.id == char_id).first()

def create_character(db: Session, name: str, kingdom: str, character_sheet: Dict[str, Any]) -> models.Character:
    """Creates and saves a new character with the fully calculated sheet."""
    db_character = models.Character(
        name=name,
        kingdom=kingdom,
        character_sheet=character_sheet
    )
    db.add(db_character)
    db.commit()
    db.refresh(db_character)
    return db_character

# --- MODIFIED FUNCTION ---
def update_character_sheet(db: Session, character: models.Character, full_sheet_update: Dict[str, Any]) -> models.Character:
    """
    Updates the character sheet JSON for an *existing* character object.
    This function NO LONGER re-fetches the character.
    """
    # Directly reassign the entire updated sheet dictionary
    character.character_sheet = full_sheet_update
    db.commit()
    db.refresh(character)
    return character
# --- ---