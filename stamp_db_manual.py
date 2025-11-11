import sqlite3

db_path = r"c:\Users\krazy\Documents\GitHub\ttrpgai\AI-TTRPG\world_engine\world.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check current state
cursor.execute("SELECT * FROM alembic_version")
current = cursor.fetchall()
print(f"Current alembic_version entries: {current}")

# Clear any existing entries
cursor.execute("DELETE FROM alembic_version")

# Insert the latest migration version
cursor.execute("INSERT INTO alembic_version (version_num) VALUES (?)", ("a4d6d63e365c",))
conn.commit()

# Verify
cursor.execute("SELECT * FROM alembic_version")
updated = cursor.fetchall()
print(f"Updated alembic_version entries: {updated}")

conn.close()
print("Database stamped successfully!")
