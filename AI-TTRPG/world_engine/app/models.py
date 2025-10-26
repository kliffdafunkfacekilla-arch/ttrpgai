from sqlalchemy import Column, Integer, String, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship

# Import the 'Base' we created in database.py
from .database import Base

class TrapInstance(Base):
    __tablename__ = "trap_instances"
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(String, index=True) # e.g., "pit_trap_t1"
    location_id = Column(Integer, ForeignKey("locations.id"))
    coordinates = Column(JSON, nullable=True) # e.g., [x, y] or [[x1,y1],[x2,y2]]
    status = Column(String, default="armed", index=True) # armed, disarmed, triggered

    # Relationships
    location = relationship("Location", back_populates="trap_instances")

class Faction(Base):
    """
    Tracks factions like 'The Silver Hand'.
    This is high-level data for the AI DM.
    """
    __tablename__ = "factions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    status = Column(String, default="neutral")
    disposition = Column(JSON, default={}) # e.g., {"faction_id_2": "war"}
    resources = Column(Integer, default=100)

class Region(Base):
    """
    Tracks large areas like 'The Dragon's Spine Mountains'.
    This provides environmental context (weather, etc.)
    """
    __tablename__ = "regions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    current_weather = Column(String, default="clear")
    environmental_effects = Column(JSON, default=[]) # e.g., ["blight_level_2"]
    faction_influence = Column(JSON, default={}) # e.g., {"faction_id_1": 0.75}

    # This links a Region to its many Locations
    locations = relationship("Location", back_populates="region")

class Location(Base):
    """
    A specific, traversable map like 'Whispering Forest - Clearing'.
    This is where the player 'is'.
    """
    __tablename__ = "locations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    tags = Column(JSON, default=[]) # e.g., ["forest", "outside", "hostile"]
    exits = Column(JSON, default={}) # e.g., {"north": "location_id_2"}

    # This stores the tile map array (e.g., [[0,1,0],[0,1,0]])
    # It starts as NULL until procedurally generated.
    generated_map_data = Column(JSON, nullable=True)
    map_seed = Column(String, nullable=True)

    # This links this Location to its parent Region
    region_id = Column(Integer, ForeignKey("regions.id"))

    # These link the Location to all NPCs and Items currently in it
    region = relationship("Region", back_populates="locations")
    npc_instances = relationship("NpcInstance", back_populates="location")
    item_instances = relationship("ItemInstance", back_populates="location")
    trap_instances = relationship("TrapInstance", back_populates="location") # Add this line
    ai_annotations = Column(JSON, nullable=True) # Store descriptions, interactions flags etc.

class NpcInstance(Base):
    """
    An *instance* of an NPC (e.g., 'Goblin_1') that
    has been spawned on a map.
    """
    __tablename__ = "npc_instances"
    id = Column(Integer, primary_key=True, index=True)
    # The 'blueprint' ID (e.g., "goblin_raider")
    template_id = Column(String, index=True)
    name_override = Column(String, nullable=True) # e.g., "Grak the Goblin"
    current_hp = Column(Integer)
    max_hp = Column(Integer)
    status_effects = Column(JSON, default=[])

    # This links the NPC to the Location it is currently in
    location_id = Column(Integer, ForeignKey("locations.id"))
    behavior_tags = Column(JSON, default=[]) # Store tags like ["aggressive"]

    location = relationship("Location", back_populates="npc_instances")
    # This links the NPC to the Items it is carrying (its inventory)
    item_instances = relationship("ItemInstance", back_populates="npc")

class ItemInstance(Base):
    """
    An *instance* of an item (e.g., 'a small potion') that
    exists in the world.
    """
    __tablename__ = "item_instances"
    id = Column(Integer, primary_key=True, index=True)
    # The 'blueprint' ID (e.g., "potion_health_small")
    template_id = Column(String, index=True)
    quantity = Column(Integer, default=1)

    # An item can be on the ground (location_id is set)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)
    # OR it can be in an NPC's inventory (npc_id is set)
    npc_id = Column(Integer, ForeignKey("npc_instances.id"), nullable=True)

    location = relationship("Location", back_populates="item_instances")
    npc = relationship("NpcInstance", back_populates="item_instances")
