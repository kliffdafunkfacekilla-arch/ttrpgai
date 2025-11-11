import sqlite3

db_path = r"c:\Users\krazy\Documents\GitHub\ttrpgai\AI-TTRPG\world_engine\world.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check alembic_version table
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='alembic_version'")
result = cursor.fetchone()

if result:
    print("alembic_version table exists")
    cursor.execute("SELECT version_num FROM alembic_version")
    versions = cursor.fetchall()
    print(f"Recorded versions: {versions}")
else:
    print("alembic_version table does NOT exist")

conn.close()
