# crud.py
from sqlalchemy.orm import Session
from . import models
from typing import Dict, Any, List
from sqlalchemy.orm.attributes import flag_modified


def get_character(db: Session, char_id: int) -> models.Character | None:
    """Retrieves a single character by ID."""
    return db.query(models.Character).filter(models.Character.id == char_id).first()


def create_character(
    db: Session, name: str, kingdom: str, character_sheet: Dict[str, Any]
) -> models.Character:
    """Creates and saves a new character with the fully calculated sheet."""
    db_character = models.Character(
        name=name, kingdom=kingdom, character_sheet=character_sheet
    )
    db.add(db_character)
    db.commit()
    db.refresh(db_character)
    return db_character


def update_character_sheet(
    db: Session, character: models.Character, full_sheet_update: Dict[str, Any]
) -> models.Character:
    """
    Updates the character sheet JSON for an *existing* character object.
    This function NO LONGER re-fetches the character.
    """
    # Directly reassign the entire updated sheet dictionary
    character.character_sheet = full_sheet_update
    db.commit()
    db.refresh(character)
    return character


def apply_damage_to_character(
    db: Session, character: models.Character, damage_amount: int
) -> models.Character:
    """Subtracts damage from current_hp within character_sheet['combat_stats']."""
    if damage_amount <= 0:
        return character  # No damage

    sheet = dict(character.character_sheet)  # Get a mutable copy
    combat_stats = sheet.get("combat_stats", {})  # Get combat_stats dict

    current_hp = combat_stats.get("current_hp", combat_stats.get("max_hp", 0))  # Get HP
    new_hp = current_hp - damage_amount
    # Add logic here: Clamp HP to 0 minimum? Check for Downed/Dying state?
    new_hp = max(0, new_hp)  # Clamp HP at 0

    print(
        f"Applying {damage_amount} damage to {character.name}. HP: {current_hp} -> {new_hp}"
    )
    combat_stats["current_hp"] = new_hp  # Update HP in the combat_stats dict

    sheet["combat_stats"] = (
        combat_stats  # Put the updated combat_stats back into the sheet
    )
    character.character_sheet = sheet  # Assign the modified sheet back
    flag_modified(character, "character_sheet")  # Mark as modified
    db.commit()
    db.refresh(character)
    return character


def apply_status_to_character(
    db: Session, character: models.Character, status_id: str
) -> models.Character:
    """Adds a status effect ID to character_sheet['combat_stats']['status_effects']."""
    sheet = dict(character.character_sheet)
    combat_stats = sheet.get("combat_stats", {})
    status_effects = combat_stats.get("status_effects", [])

    # Avoid duplicate statuses? Or allow stacking? Rule dependent. Assume no duplicates for now.
    if status_id not in status_effects:
        status_effects.append(status_id)
        print(f"Applying status '{status_id}' to {character.name}")

    combat_stats["status_effects"] = (
        status_effects  # Update status list in combat_stats
    )
    sheet["combat_stats"] = combat_stats  # Put combat_stats back into the sheet
    character.character_sheet = sheet  # Assign modified sheet back
    flag_modified(character, "character_sheet")  # Mark as modified
    db.commit()
    db.refresh(character)
    return character


# --- ADD THIS NEW FUNCTION ---
def update_character_location_and_coords(
    db: Session,
    character: models.Character,
    new_location_id: int,
    new_coordinates: List[int],
) -> models.Character:
    """Updates the 'location' object within the character_sheet JSON."""
    sheet = dict(character.character_sheet)  # Get a mutable copy

    # Get the location object, or create it if it's the old string format
    location_data = sheet.get("location", {})
    if not isinstance(location_data, dict):
        location_data = {}  # Overwrite old string format

    location_data["current_location_id"] = new_location_id
    location_data["coordinates"] = new_coordinates

    sheet["location"] = location_data  # Put the updated location object back

    character.character_sheet = sheet  # Assign the modified sheet back
    flag_modified(character, "character_sheet")  # Mark as modified
    db.commit()
    db.refresh(character)
    return character


# --- ---


def add_item_to_inventory(
    db: Session, character: models.Character, item_id: str, quantity: int
) -> models.Character:
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


def remove_item_from_inventory(
    db: Session, character: models.Character, item_id: str, quantity: int
) -> models.Character:
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


def list_characters(
    db: Session, skip: int = 0, limit: int = 100
) -> List[models.Character]:
    """Retrieves a list of characters."""
    return db.query(models.Character).offset(skip).limit(limit).all()


def apply_damage_to_character(
    db: Session, character: models.Character, damage_amount: int
) -> models.Character:
    """Subtracts damage from current_hp within character_sheet['combat_stats']."""
    if damage_amount <= 0:
        return character  # No damage

    sheet = dict(character.character_sheet)  # Get a mutable copy
    combat_stats = sheet.get("combat_stats", {})  # Get combat_stats dict

    current_hp = combat_stats.get("current_hp", combat_stats.get("max_hp", 0))  # Get HP
    new_hp = current_hp - damage_amount
    # Add logic here: Clamp HP to 0 minimum? Check for Downed/Dying state?
    new_hp = max(0, new_hp)  # Clamp HP at 0

    print(
        f"Applying {damage_amount} damage to {character.name}. HP: {current_hp} -> {new_hp}"
    )
    combat_stats["current_hp"] = new_hp  # Update HP in the combat_stats dict

    sheet["combat_stats"] = (
        combat_stats  # Put the updated combat_stats back into the sheet
    )
    character.character_sheet = sheet  # Assign the modified sheet back
    flag_modified(character, "character_sheet")  # Mark as modified
    db.commit()
    db.refresh(character)
    return character


def apply_status_to_character(
    db: Session, character: models.Character, status_id: str
) -> models.Character:
    """Adds a status effect ID to character_sheet['combat_stats']['status_effects']."""
    sheet = dict(character.character_sheet)
    combat_stats = sheet.get("combat_stats", {})
    status_effects = combat_stats.get("status_effects", [])

    # Avoid duplicate statuses? Or allow stacking? Rule dependent. Assume no duplicates for now.
    if status_id not in status_effects:
        status_effects.append(status_id)
        print(f"Applying status '{status_id}' to {character.name}")

    combat_stats["status_effects"] = (
        status_effects  # Update status list in combat_stats
    )
    sheet["combat_stats"] = combat_stats  # Put combat_stats back into the sheet
    character.character_sheet = sheet  # Assign modified sheet back
    flag_modified(character, "character_sheet")  # Mark as modified
    db.commit()
    db.refresh(character)
    return character
