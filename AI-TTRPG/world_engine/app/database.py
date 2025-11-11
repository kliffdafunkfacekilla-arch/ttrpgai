import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Construct a robust, absolute path to the database file inside the world_engine directory.
_current_dir = os.path.dirname(os.path.abspath(__file__))
# This navigates up from app/ to the world_engine/ directory.
_service_root = os.path.abspath(os.path.join(_current_dir, ".."))
_db_path = os.path.join(_service_root, "world.db")
DATABASE_URL = f"sqlite:///{_db_path}"

# The connect_args is recommended for SQLite with FastAPI to allow multithreading.
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# This SessionLocal is what our API endpoints will use
# to get a connection to the database.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is the class our database models will inherit from.
Base = declarative_base()
