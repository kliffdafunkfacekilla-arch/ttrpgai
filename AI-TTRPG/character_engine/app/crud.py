# crud.py
from sqlalchemy.orm import Session
from . import models
from typing import Dict, Any, List
from sqlalchemy.orm.attributes import flag_modified

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

def add_item_to_inventory(db: Session, character: models.Character, item_id: str, quantity: int) -> models.Character:
    sheet = dict(character.character_sheet)
    inventory = sheet.get("inventory", [])
    found = False
    for item in inventory:
        if item.get("item_id") == item_id:
            item["quantity"] = item.get("quantity", 0) + quantity
            found = True
            break
    if not found:
        inventory.append({"item_id": item_id, "quantity": quantity})

    sheet["inventory"] = inventory
    character.character_sheet = sheet
    flag_modified(character, "character_sheet")
    db.commit()
    db.refresh(character)
    return character

def remove_item_from_inventory(db: Session, character: models.Character, item_id: str, quantity: int) -> models.Character:
    sheet = dict(character.character_sheet)
    inventory = sheet.get("inventory", [])
    new_inventory = []
    for item in inventory:
        if item.get("item_id") == item_id:
            item["quantity"] = item.get("quantity", 0) - quantity
            if item["quantity"] > 0:
                new_inventory.append(item)
        # If quantity is 0 or less, don't add it back
        else:
            new_inventory.append(item)

    sheet["inventory"] = new_inventory
    character.character_sheet = sheet
    flag_modified(character, "character_sheet")
    db.commit()
    db.refresh(character)
    return character

def list_characters(db: Session, skip: int = 0, limit: int = 100) -> List[models.Character]:
    """Retrieves a list of characters."""
    return db.query(models.Character).offset(skip).limit(limit).all()