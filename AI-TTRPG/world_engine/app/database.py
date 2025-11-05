import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Construct an absolute path to the database file in the project root.
_current_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.abspath(os.path.join(_current_dir, "..", "..", ".."))
_db_path = os.path.join(_project_root, "world.db")
DATABASE_URL = f"sqlite:///{_db_path}"

# connect_args is needed for SQLite to allow it to be
# accessed by multiple parts of the app at once.
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# This SessionLocal is what our API endpoints will use
# to get a connection to the database.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is the class our database models will inherit from.
Base = declarative_base()
