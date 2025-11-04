from sqlalchemy import Column, Integer, String, JSON
from .database import Base


class Character(Base):
    __tablename__ = "characters"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    kingdom = Column(String)
    
    # These are the separate columns the application expects
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
    
    # This data is redundant with the 'location' object in your final
    # frontend design, but the backend code relies on it.
    position_x = Column(Integer)
    position_y = Column(Integer)