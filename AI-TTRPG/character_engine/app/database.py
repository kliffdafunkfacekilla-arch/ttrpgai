import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Construct an absolute path to the database file in the project root.
# This ensures the service can find the DB regardless of where it's launched from.
# The script is in AI-TTRPG/character_engine/app, the DB is in the root.
_current_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.abspath(os.path.join(_current_dir, "..", "..", ".."))
_db_path = os.path.join(_project_root, "characters.db")
DATABASE_URL = f"sqlite:///{_db_path}"

# The connect_args is recommended for SQLite with FastAPI to allow multithreading.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
