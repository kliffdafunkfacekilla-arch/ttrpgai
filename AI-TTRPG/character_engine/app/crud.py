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


def apply_damage_to_character(db: Session, character: models.Character, damage_amount: int) -> models.Character:
    """Subtracts damage from HP, stored in character_sheet."""
    if damage_amount <= 0: return character # No damage

    sheet = dict(character.character_sheet)
    stats = sheet.get("stats", {}) # Assuming HP stored under stats for now
    current_hp = stats.get("current_hp", stats.get("max_hp", 0)) # Need clear HP structure

    # --- Placeholder HP structure ---
    # TODO: Define where current_hp and max_hp are stored in character_sheet
    # Example assumes {"stats": {"current_hp": X, "max_hp": Y, ...}}
    new_hp = current_hp - damage_amount
    print(f"Applying {damage_amount} damage to {character.name}. HP: {current_hp} -> {new_hp}")
    stats["current_hp"] = new_hp
    # Add logic here to check for Downed/Dying state if new_hp <= 0

    sheet["stats"] = stats
    character.character_sheet = sheet
    flag_modified(character, "character_sheet")
    db.commit()
    db.refresh(character)
    return character

def apply_status_to_character(db: Session, character: models.Character, status_id: str) -> models.Character:
    """Adds a status effect to the character_sheet."""
    sheet = dict(character.character_sheet)
    status_effects = sheet.get("status_effects", [])

    # Avoid duplicate statuses? Or allow stacking? Rule dependent.
    if status_id not in status_effects:
         status_effects.append(status_id)
         print(f"Applying status '{status_id}' to {character.name}")

    sheet["status_effects"] = status_effects # Need defined place in sheet
    character.character_sheet = sheet
    flag_modified(character, "character_sheet")
    db.commit()
    db.refresh(character)
    return character