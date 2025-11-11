import sqlite3
import os

db_path = r"c:\Users\krazy\Documents\GitHub\ttrpgai\AI-TTRPG\world_engine\world.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables:", [t[0] for t in tables])

# Check location count
if any('location' in t[0].lower() for t in tables):
    try:
        cursor.execute("SELECT COUNT(*) FROM locations")
        count = cursor.fetchone()[0]
        print(f"Location count: {count}")
        
        if count > 0:
            cursor.execute("SELECT id, name FROM locations LIMIT 5")
            for row in cursor.fetchall():
                print(f"  - {row}")
    except Exception as e:
        print(f"Could not query locations table: {e}")

conn.close()
