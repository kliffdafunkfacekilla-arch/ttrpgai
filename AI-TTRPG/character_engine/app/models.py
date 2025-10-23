from sqlalchemy import Column, Integer, String, JSON
from .database import Base

class Character(Base):
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    kingdom = Column(String)
    character_sheet = Column(JSON)
