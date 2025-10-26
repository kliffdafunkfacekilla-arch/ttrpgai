from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# This is our new, separate database for story and quests.
DATABASE_URL = "sqlite:///./story_engine/story.db"

# connect_args is needed for SQLite.
engine = create_engine(
DATABASE_URL, connect_args={"check_same_thread": False}
)

# This SessionLocal is what our API endpoints will use
# to get a connection to the database.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is the class our database models will inherit from.
Base = declarative_base()