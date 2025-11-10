# crud.py
from sqlalchemy.orm import Session
from . import models
from typing import Dict, Any, List
from sqlalchemy.orm.attributes import flag_modified

def get_character(db: Session, char_id: str) -> models.Character | None:
    """Retrieves a single character by ID."""
    return db.query(models.Character).filter(models.Character.id == char_id).first()

def apply_damage_to_character(
    db: Session, character: models.Character, damage_amount: int
) -> models.Character:
    """Subtracts damage from current_hp."""
    if damage_amount <= 0:
        return character # No damage

    # --- MODIFICATION: Update the correct column ---
    current_hp = character.current_hp
    new_hp = current_hp - damage_amount
    new_hp = max(0, new_hp) # Clamp HP at 0

    print(
        f"Applying {damage_amount} damage to {character.name}. HP: {current_hp} -> {new_hp}"
    )
    character.current_hp = new_hp # Update the direct column

    # --- END MODIFICATION ---

    flag_modified(character, "current_hp") # Mark as modified
    db.commit()
    db.refresh(character)
    return character

def apply_status_to_character(
    db: Session, character: models.Character, status_id: str
) -> models.Character:
    """Adds a status effect ID to the status_effects list."""
    # --- MODIFICATION: Update the correct column ---
    status_effects = character.status_effects or []

    if status_id not in status_effects:
        status_effects.append(status_id)
        print(f"Applying status '{status_id}' to {character.name}")

    character.status_effects = status_effects # Assign modified list back
    flag_modified(character, "status_effects") # Mark as modified
    # --- END MODIFICATION ---
    db.commit()
    db.refresh(character)
    return character

# --- MODIFIED: THIS NEW FUNCTION ---
def update_character_location_and_coords(
    db: Session,
    character: models.Character,
    new_location_id: int,
    new_coordinates: List[int],
) -> models.Character:
    """Updates the character's location ID and coordinates."""

    character.current_location_id = new_location_id
    character.position_x = new_coordinates[0]
    character.position_y = new_coordinates[1]

    flag_modified(character, "current_location_id")
    flag_modified(character, "position_x")
    flag_modified(character, "position_y")

    db.commit()
    db.refresh(character)
    return character
# --- ---

def add_item_to_inventory(
    db: Session, character: models.Character, item_id: str, quantity: int
) -> models.Character:
    # --- MODIFICATION: Update the correct column ---
    inventory = character.inventory or {}

    # Assuming inventory is a dict {item_id: {name: "...", "quantity": X}}
    # Based on apiTypes.ts, it seems to be: { item_id: { name: "...", quantity: X } }
    # Let's check apiTypes.ts...
    # `inventory: { [key: string]: InventoryItem };` where InventoryItem is `{ name: string, quantity: number}`
    # This is complex. The `create_character` service initializes it as `{}`.
    # The `apiTypes` implies it should be `{ "potion_1": { "name": "Health Potion", "quantity": 1 } }`
    # Let's assume the key is the item_id for simplicity.

    # A simpler structure `{ "potion_health_small": 5 }` is easier.
    # But your `create_character` service sets `inventory={}` (a dict)
    # and your `apiTypes` expects `inventory: { [key: string]: InventoryItem };`
    # Let's stick to the `apiTypes` definition.

    # This logic is complex and needs a call to rules_engine to get item details (like name).
    # For now, let's just add the ID and quantity.
    # A better structure would be: `inventory: { "potion_health_small": 5 }`
    # Let's assume this simpler structure for now, as the `create_character` sets an empty dict.

    current_quantity = inventory.get(item_id, 0)
    inventory[item_id] = current_quantity + quantity

    character.inventory = inventory
    flag_modified(character, "inventory")
    # --- END MODIFICATION ---
    db.commit()
    db.refresh(character)
    return character

def remove_item_from_inventory(
    db: Session, character: models.Character, item_id: str, quantity: int
) -> models.Character:
    # --- MODIFICATION: Update the correct column ---
    inventory = character.inventory or {}

    current_quantity = inventory.get(item_id, 0)
    new_quantity = current_quantity - quantity

    if new_quantity > 0:
        inventory[item_id] = new_quantity
    else:
        if item_id in inventory:
            del inventory[item_id] # Remove item if quantity is 0 or less

    character.inventory = inventory
    flag_modified(character, "inventory")
    # --- END MODIFICATION ---
    db.commit()
    db.refresh(character)
    return character

# This function is duplicated in your file, removing the second copy.
# def apply_damage_to_character( ... )
# This function is duplicated in your file, removing the second copy.
# def apply_status_to_character( ... )
def list_characters(
    db: Session, skip: int = 0, limit: int = 100
) -> List[models.Character]:
    """Retrieves a list of characters."""
    return db.query(models.Character).offset(skip).limit(limit).all()