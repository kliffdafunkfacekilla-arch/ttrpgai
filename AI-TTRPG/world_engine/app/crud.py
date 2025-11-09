from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from . import models, schemas
from typing import List, Optional
from fastapi import HTTPException
import logging

logger = logging.getLogger("uvicorn.error")

# --- Faction ---
def get_faction(db: Session, faction_id: int) -> Optional[models.Faction]:
    return db.query(models.Faction).filter(models.Faction.id == faction_id).first()

def create_faction(db: Session, faction: schemas.FactionCreate) -> models.Faction:
    db_faction = models.Faction(**faction.dict())
    db.add(db_faction)
    db.commit()
    db.refresh(db_faction)
    return db_faction

# --- Region ---
def get_region(db: Session, region_id: int) -> Optional[models.Region]:
    return db.query(models.Region).filter(models.Region.id == region_id).first()

def create_region(db: Session, region: schemas.RegionCreate) -> models.Region:
    db_region = models.Region(name=region.name)
    db.add(db_region)
    db.commit()
    db.refresh(db_region)
    return db_region

# --- Location ---
def get_location(db: Session, location_id: int) -> Optional[models.Location]:
    """
    Gets a single location by ID.
    The 'relationships' in models.py will auto-load its
    region, NPCs, and items.
    """
    return db.query(models.Location).filter(models.Location.id == location_id).first()

def create_location(db: Session, loc: schemas.LocationCreate) -> models.Location:
    db_loc = models.Location(
        name=loc.name,
        region_id=loc.region_id,
        tags=loc.tags,
        exits=loc.exits
    )
    db.add(db_loc)
    db.commit()
    db.refresh(db_loc)
    return db_loc

def update_location_map(db: Session, location_id: int, map_update: schemas.LocationMapUpdate) -> Optional[models.Location]:
    """
    This is how the story_engine saves a persistent map.
    """
    db_loc = get_location(db, location_id)
    if db_loc:
        db_loc.generated_map_data = map_update.generated_map_data
        db_loc.map_seed = map_update.map_seed
        db_loc.spawn_points = map_update.spawn_points # <-- ADD THIS

        # This line is important for JSON fields
        flag_modified(db_loc, "generated_map_data")
        flag_modified(db_loc, "spawn_points") # <-- ADD THIS

        db.commit()
        db.refresh(db_loc)
    return db_loc

def update_location_annotations(db: Session, location_id: int, annotations: dict) -> Optional[models.Location]:
    db_loc = get_location(db, location_id)
    if db_loc:
        db_loc.ai_annotations = annotations
        flag_modified(db_loc, "ai_annotations")
        db.commit()
        db.refresh(db_loc)
    return db_loc

# --- NPC Instance ---
def get_npc(db: Session, npc_id: int) -> Optional[models.NpcInstance]:
    return db.query(models.NpcInstance).filter(models.NpcInstance.id == npc_id).first()

def spawn_npc(db: Session, npc: schemas.NpcSpawnRequest) -> models.NpcInstance:
    # --- THIS FUNCTION IS NOW FIXED ---
    # It now prioritizes the HP values from the request schema.
    # The 'or 10' is just a final fallback if None is passed.
    db_npc = models.NpcInstance(
        template_id=npc.template_id,
        location_id=npc.location_id,
        name_override=npc.name_override,
        current_hp=npc.current_hp if npc.current_hp is not None else 10,
        max_hp=npc.max_hp if npc.max_hp is not None else 10,
        behavior_tags=npc.behavior_tags,
        coordinates=npc.coordinates # Save the coordinates
    )
    # --- END FIX ---
    db.add(db_npc)
    db.commit()
    db.refresh(db_npc)
    return db_npc

def update_npc(db: Session, npc_id: int, updates: schemas.NpcUpdate) -> Optional[models.NpcInstance]:
    """
    This is how we deal damage, apply status, or move an NPC.
    """
    db_npc = get_npc(db, npc_id)
    if db_npc:
        # 'exclude_unset=True' means we only get the fields
        # that were actually sent in the request.
        update_data = updates.dict(exclude_unset=True)

        for key, value in update_data.items():
            setattr(db_npc, key, value)

        if "status_effects" in update_data:
            flag_modified(db_npc, "status_effects")

        if "coordinates" in update_data:
            flag_modified(db_npc, "coordinates")

        db.commit()
        db.refresh(db_npc)
    return db_npc

def delete_npc(db: Session, npc_id: int) -> bool:
    """This is how we remove a dead NPC from the world."""
    db_npc = get_npc(db, npc_id)
    if db_npc:
        # Also delete all items in their inventory
        db.query(models.ItemInstance).filter(models.ItemInstance.npc_id == npc_id).delete()

        db.delete(db_npc)
        db.commit()
        return True
    return False

# --- Trap Instance ---
def create_trap(db: Session, trap: schemas.TrapInstanceCreate) -> models.TrapInstance:
    db_trap = models.TrapInstance(**trap.dict())
    db.add(db_trap)
    db.commit()
    db.refresh(db_trap)
    return db_trap

def get_trap(db: Session, trap_id: int) -> Optional[models.TrapInstance]:
    return db.query(models.TrapInstance).filter(models.TrapInstance.id == trap_id).first()

def get_traps_for_location(db: Session, location_id: int) -> List[models.TrapInstance]:
    return db.query(models.TrapInstance).filter(models.TrapInstance.location_id == location_id).all()

def update_trap_status(db: Session, trap_id: int, status: str) -> Optional[models.TrapInstance]:
    db_trap = get_trap(db, trap_id)
    if db_trap:
        db_trap.status = status
        db.commit()
        db.refresh(db_trap)
    return db_trap

# --- Item Instance ---
def spawn_item(db: Session, item: schemas.ItemSpawnRequest) -> models.ItemInstance:
    """Spawns an item, either on the ground or in an NPC's inventory."""
    db_item = models.ItemInstance(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def delete_item(db: Session, item_id: int) -> bool:
    """This is how a player picks up an item."""
    db_item = db.query(models.ItemInstance).filter(models.ItemInstance.id == item_id).first()
    if db_item:
        db.delete(db_item)
        db.commit()
        return True
    return False

def get_location_context(db: Session, location_id: int):
    """
    Retrieves the full context for a given location, including region,
    NPCs, and items.
    """
    logger.info(f"Getting full context for location_id: {location_id}")
    location = db.query(models.Location).filter(models.Location.id == location_id).first()
    if not location:
        logger.error(f"Location not found for id: {location_id}")
        raise HTTPException(status_code=404, detail="Location not found")

    npcs = db.query(models.NpcInstance).filter(models.NpcInstance.location_id == location_id).all()
    items = db.query(models.ItemInstance).filter(models.ItemInstance.location_id == location_id).all()
    
    # Get Region name
    region = db.query(models.Region).filter(models.Region.id == location.region_id).first()
    
    # --- START OF NEW FIX ---
    if not region:
        logger.error(f"Data integrity error: Location {location_id} has region_id {location.region_id} but no matching region was found.")
        # This was the cause of the 500 error
        raise HTTPException(status_code=500, detail=f"Data integrity error: Region {location.region_id} not found for location {location_id}.")
    # --- END OF NEW FIX ---

    return {
        "location_id": location.id,
        "name": location.name,
        "region_name": region.name,
        "description": location.description,
        "generated_map_data": location.generated_map_data,
        "map_seed": location.map_seed,
        "ai_annotations": location.ai_annotations,
        "npcs": [schemas.NpcInstanceContext.from_orm(npc) for npc in npcs],
        "items": [schemas.ItemInstanceContext.from_orm(item) for item in items],
    }