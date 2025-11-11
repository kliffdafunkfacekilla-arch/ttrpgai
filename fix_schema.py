import sqlite3

db_path = r"c:\Users\krazy\Documents\GitHub\ttrpgai\AI-TTRPG\world_engine\world.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if columns exist
cursor.execute("PRAGMA table_info(locations)")
columns = [row[1] for row in cursor.fetchall()]
print(f"Existing columns: {columns}")

# Add missing columns if they don't exist
if 'ai_annotations' not in columns:
    cursor.execute("ALTER TABLE locations ADD COLUMN ai_annotations JSON DEFAULT NULL")
    print("Added ai_annotations column")

if 'spawn_points' not in columns:
    cursor.execute("ALTER TABLE locations ADD COLUMN spawn_points JSON DEFAULT NULL")
    print("Added spawn_points column")

# Check NpcInstance columns
cursor.execute("PRAGMA table_info(npc_instances)")
npc_columns = [row[1] for row in cursor.fetchall()]
print(f"\nNPC Instance columns: {npc_columns}")

if 'coordinates' not in npc_columns:
    cursor.execute("ALTER TABLE npc_instances ADD COLUMN coordinates JSON DEFAULT NULL")
    print("Added coordinates column to npc_instances")

if 'behavior_tags' not in npc_columns:
    cursor.execute("ALTER TABLE npc_instances ADD COLUMN behavior_tags JSON DEFAULT '[]'")
    print("Added behavior_tags column to npc_instances")

# Check ItemInstance columns
cursor.execute("PRAGMA table_info(item_instances)")
item_columns = [row[1] for row in cursor.fetchall()]
print(f"\nItem Instance columns: {item_columns}")

if 'coordinates' not in item_columns:
    cursor.execute("ALTER TABLE item_instances ADD COLUMN coordinates JSON DEFAULT NULL")
    print("Added coordinates column to item_instances")

conn.commit()
conn.close()
print("\nDatabase schema updated!")
