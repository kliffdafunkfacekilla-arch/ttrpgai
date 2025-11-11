import sys
from os.path import abspath, dirname
from logging.config import fileConfig

# Add the project's root directory to the Python path
sys.path.insert(0, abspath(dirname(dirname(__file__))))

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --- START CRITICAL MODIFICATION ---
# 1. Import the database object to get the absolute path constant
from app.database import Base, DATABASE_URL
target_metadata = Base.metadata
# --- END CRITICAL MODIFICATION ---


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    # 2. Use the imported absolute URL for offline mode
    url = DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    # 3. Temporarily set the SQLAlchemy URL in the config to the absolute path
    alembic_config_section = config.get_section(config.config_ini_section, {})
    alembic_config_section["sqlalchemy.url"] = DATABASE_URL # <-- FORCES ABSOLUTE PATH

    connectable = engine_from_config(
        alembic_config_section, # <-- Use the modified config section
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
