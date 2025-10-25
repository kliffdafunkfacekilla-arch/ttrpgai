from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any

# Import all our other files
from . import crud, models, schemas
from .database import SessionLocal, engine

# This creates the FastAPI application instance
app = FastAPI(
    title="World Engine",
    description="Manages the state of all locations, NPCs, items, and world data."
)

# --- Dependency ---
def get_db():
    """
    This function is a 'dependency'.
    Each API call will run this function to get a
    database session, and it automatically closes
    the session when the API call is finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- API Endpoints ---
# These are the 'doors' our story_engine will use.

@app.get("/")
def read_root():
    return {"status": "World Engine is running."}

# --- Location Endpoints ---

@app.get("/v1/locations/{location_id}", response_model=schemas.Location)
def read_location(location_id: int, db: Session = Depends(get_db)):
    """
    Get all data for a single location by its ID.
    This is the main 'get' function for the story_engine.
    """
    db_loc = crud.get_location(db, location_id=location_id)
    if db_loc is None:
        raise HTTPException(status_code=404, detail="Location not found")
    return db_loc

@app.put("/v1/locations/{location_id}/map", response_model=schemas.Location)
def update_location_generated_map(
    location_id: int,
    map_update: schemas.LocationMapUpdate,
    db: Session = Depends(get_db)
):
    """
    Used by the story_engine to save a procedurally generated
    map to the database, making it persistent.
    """
    db_loc = crud.update_location_map(db, location_id, map_update)
    if db_loc is None:
        raise HTTPException(status_code=404, detail="Location not found")
    return db_loc

# --- NPC Endpoints ---

@app.post("/v1/npcs/spawn", response_model=schemas.NpcInstance, status_code=201)
def spawn_new_npc(npc: schemas.NpcSpawnRequest, db: Session = Depends(get_db)):
    """
    Used by the story_engine to create a new NPC in the world
    during an encounter.
    """
    return crud.spawn_npc(db=db, npc=npc)

@app.get("/v1/npcs/{npc_id}", response_model=schemas.NpcInstance)
def read_npc(npc_id: int, db: Session = Depends(get_db)):
    """Get the current status of a single NPC."""
    db_npc = crud.get_npc(db, npc_id=npc_id)
    if db_npc is None:
        raise HTTPException(status_code=404, detail="NPC not found")
    return db_npc

@app.put("/v1/npcs/{npc_id}", response_model=schemas.NpcInstance)
def update_existing_npc(
    npc_id: int,
    updates: schemas.NpcUpdate,
    db: Session = Depends(get_db)
):
    """
    Used to update an NPC (deal damage, move them, etc.)
    """
    db_npc = crud.update_npc(db, npc_id, updates)
    if db_npc is None:
        raise HTTPException(status_code=404, detail="NPC not found")
    return db_npc

@app.delete("/v1/npcs/{npc_id}", response_model=Dict[str, bool])
def delete_existing_npc(npc_id: int, db: Session = Depends(get_db)):
    """Used to remove a dead NPC from the world."""
    if not crud.delete_npc(db, npc_id):
        raise HTTPException(status_code=404, detail="NPC not found")
    return {"success": True}

# --- Item Endpoints ---

@app.post("/v1/items/spawn", response_model=schemas.ItemInstance, status_code=201)
def spawn_new_item(item: schemas.ItemSpawnRequest, db: Session = Depends(get_db)):
    """
    Used to create a new item (loot, quest item, etc.)
    """
    return crud.spawn_item(db=db, item=item)

@app.delete("/v1/items/{item_id}", response_model=Dict[str, bool])
def delete_existing_item(item_id: int, db: Session = Depends(get_db)):
    """
    Used when a player picks up an item from the ground.
    """
    if not crud.delete_item(db, item_id):
        raise HTTPException(status_code=44, detail="Item not found")
    return {"success": True}

# --- Region/Faction Endpoints (for setup) ---

@app.post("/v1/regions/", response_model=schemas.Region, status_code=201)
def create_new_region(region: schemas.RegionCreate, db: Session = Depends(get_db)):
    """Used to set up a new region in the world."""
    return crud.create_region(db, region)

@app.get("/v1/regions/{region_id}", response_model=schemas.Region)
def read_region(region_id: int, db: Session = Depends(get_db)):
    """Get high-level data about a region (weather, factions)."""
    db_region = crud.get_region(db, region_id)
    if db_region is None:
        raise HTTPException(status_code=404, detail="Region not found")
    return db_region

@app.post("/v1/factions/", response_model=schemas.Faction, status_code=201)
def create_new_faction(faction: schemas.FactionCreate, db: Session = Depends(get_db)):
    """Used to set up a new faction in the world."""
    return crud.create_faction(db, faction)

@app.get("/v1/factions/{faction_id}", response_model=schemas.Faction)
def read_faction(faction_id: int, db: Session = Depends(get_db)):
    """Get high-level data about a faction."""
    db_faction = crud.get_faction(db, faction_id)
    if db_faction is None:
        raise HTTPException(status_code=404, detail="Faction not found")
    return db_faction
