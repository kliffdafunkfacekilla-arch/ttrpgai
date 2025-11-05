from sqlalchemy import Column, Integer, String, JSON
from .database import Base


class Character(Base):
    __tablename__ = "characters"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    kingdom = Column(String)

    # --- ADD THIS LINE ---
    current_location_id = Column(Integer, default=1) # Defaults to location 1 (STARTING_ZONE)
    # --- END ADD ---
    
    # These are the separate columns that match your migration and services.py
    level = Column(Integer)
    stats = Column(JSON)
    skills = Column(JSON)
    max_hp = Column(Integer)
    current_hp = Column(Integer)
    resource_pools = Column(JSON)
    talents = Column(JSON)
    abilities = Column(JSON)
    inventory = Column(JSON)
    equipment = Column(JSON)
    status_effects = Column(JSON)
    injuries = Column(JSON)
    position_x = Column(Integer)
    position_y = Column(Integer)