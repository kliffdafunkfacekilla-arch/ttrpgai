from sqlalchemy import Column, Integer, String, JSON
from .database import Base


class Character(Base):
    __tablename__ = "characters"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    kingdom = Column(String)
    # This is the single JSON blob that holds all character data
    character_sheet = Column(JSON)