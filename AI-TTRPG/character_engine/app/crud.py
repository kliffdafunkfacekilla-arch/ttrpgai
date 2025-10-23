from sqlalchemy.orm import Session
from . import models, schemas

def get_character(db: Session, char_id: int):
    return db.query(models.Character).filter(models.Character.id == char_id).first()

def create_character(db: Session, character_data: dict):
    new_character = models.Character(
        name=character_data['name'],
        kingdom=character_data['kingdom'],
        character_sheet=character_data['character_sheet']
    )
    db.add(new_character)
    db.commit()
    db.refresh(new_character)
    return new_character

def update_character_sheet(db: Session, char_id: int, sheet_update: dict):
    character = get_character(db, char_id)
    if character:
        character.character_sheet.update(sheet_update)
        db.commit()
        db.refresh(character)
    return character
