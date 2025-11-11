import sqlite3
import json

db_path = r"c:\Users\krazy\Documents\GitHub\ttrpgai\AI-TTRPG\world_engine\world.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check regions
cursor.execute("SELECT * FROM regions")
regions = cursor.fetchall()
print(f"Regions ({len(regions)}):")
for r in regions:
    print(f"  {r}")

# Check location details
cursor.execute("SELECT * FROM locations")
locations = cursor.fetchall()
print(f"\nLocations ({len(locations)}):")
for l in locations:
    print(f"  {l}")

conn.close()
