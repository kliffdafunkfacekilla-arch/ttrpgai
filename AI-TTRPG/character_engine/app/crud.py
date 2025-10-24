# crud.py
from sqlalchemy.orm import Session
from . import models, schemas # Keep schemas import if needed elsewhere, but not used here directly
from typing import Dict, Any

def get_character(db: Session, char_id: int) -> models.Character | None:
    """Retrieves a single character by ID."""
    return db.query(models.Character).filter(models.Character.id == char_id).first()

def create_character(db: Session, name: str, kingdom: str, character_sheet: Dict[str, Any]) -> models.Character:
    """Creates and saves a new character with the fully calculated sheet."""
    # Create the SQLAlchemy model instance
    db_character = models.Character(
        name=name,
        kingdom=kingdom,
        character_sheet=character_sheet # Save the calculated sheet directly
    )
    db.add(db_character)
    db.commit()
    db.refresh(db_character)
    return db_character

def update_character_sheet(db: Session, char_id: int, sheet_update: Dict[str, Any]) -> models.Character | None:
    """Updates parts of the character sheet JSON."""
    character = get_character(db, char_id)
    if character:
        # For JSON columns, ensure mutability or reassign
        current_sheet = dict(character.character_sheet) # Get a mutable copy
        current_sheet.update(sheet_update)
        character.character_sheet = current_sheet # Reassign the updated dict
        db.commit()
        db.refresh(character)
    return character

# Add other CRUD functions as needed (get_all_characters, delete_character, etc.)