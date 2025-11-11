import sqlite3
import json
import os

db_path = r"c:\Users\krazy\Documents\GitHub\ttrpgai\AI-TTRPG\world_engine\world.db"
data_dir = r"c:\Users\krazy\Documents\GitHub\ttrpgai\AI-TTRPG\world_engine\data"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Load and insert factions
with open(os.path.join(data_dir, "initial_factions.json"), "r") as f:
    factions_data = json.load(f)
    for faction in factions_data:
        cursor.execute("""
            INSERT OR IGNORE INTO factions (name, status, disposition, resources)
            VALUES (?, ?, ?, ?)
        """, (faction.get("name"), faction.get("status", "neutral"), 
              json.dumps(faction.get("disposition", {})), faction.get("resources", 100)))

# Load and insert regions
with open(os.path.join(data_dir, "initial_regions.json"), "r") as f:
    regions_data = json.load(f)
    for region in regions_data:
        cursor.execute("""
            INSERT OR IGNORE INTO regions (name, current_weather, environmental_effects, faction_influence)
            VALUES (?, ?, ?, ?)
        """, (region.get("name"), region.get("current_weather", "clear"),
              json.dumps(region.get("environmental_effects", [])),
              json.dumps(region.get("faction_influence", {}))))

# Load and insert locations
with open(os.path.join(data_dir, "initial_locations.json"), "r") as f:
    locations_data = json.load(f)
    for location in locations_data:
        cursor.execute("""
            INSERT OR IGNORE INTO locations (name, region_id, tags, exits)
            VALUES (?, ?, ?, ?)
        """, (location.get("name"), location.get("region_id"),
              json.dumps(location.get("tags", [])),
              json.dumps(location.get("exits", {}))))

conn.commit()
conn.close()

print("Seed data inserted successfully!")
