import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# --- MODIFICATION: Remove complex path calculation. ---
# The DB file will now live alongside alembic.ini inside the world_engine directory.
DATABASE_URL = "sqlite:///./world.db" # Simple relative path within the service directory

# The connect_args is recommended for SQLite with FastAPI to allow multithreading.
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# This SessionLocal is what our API endpoints will use
# to get a connection to the database.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is the class our database models will inherit from.
Base = declarative_base()
