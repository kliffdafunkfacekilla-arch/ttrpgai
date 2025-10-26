from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# This is our new, separate database for the world.
DATABASE_URL = "sqlite:///./world_engine/world.db"

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