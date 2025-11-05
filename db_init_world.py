import sqlite3
import os
import json

# Set the database path to be in the root of the project.
_script_dir = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(_script_dir, "world.db")

def initialize_database():
    """
    Initializes the world.db database, creating all tables from all migrations
    and pre-populating it with a starting location.
    """
    print(f"Initializing world database at: {DB_PATH}")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Drop tables in reverse order of creation to respect foreign keys
        cursor.execute("DROP TABLE IF EXISTS trap_instances")
        cursor.execute("DROP TABLE IF EXISTS item_instances")
        cursor.execute("DROP TABLE IF EXISTS npc_instances")
        cursor.execute("DROP TABLE IF EXISTS locations")
        cursor.execute("DROP TABLE IF EXISTS regions")
        cursor.execute("DROP TABLE IF EXISTS factions")

        # --- Migration: 0001_create_world_tables ---
        cursor.execute("""
            CREATE TABLE factions (
                id INTEGER NOT NULL,
                name VARCHAR,
                status VARCHAR,
                disposition JSON,
                resources INTEGER,
                PRIMARY KEY (id)
            )
        """)
        cursor.execute("CREATE UNIQUE INDEX ix_factions_name ON factions (name)")

        cursor.execute("""
            CREATE TABLE regions (
                id INTEGER NOT NULL,
                name VARCHAR,
                current_weather VARCHAR,
                environmental_effects JSON,
                faction_influence JSON,
                PRIMARY KEY (id)
            )
        """)
        cursor.execute("CREATE UNIQUE INDEX ix_regions_name ON regions (name)")

        cursor.execute("""
            CREATE TABLE locations (
                id INTEGER NOT NULL,
                name VARCHAR,
                tags JSON,
                exits JSON,
                generated_map_data JSON,
                map_seed VARCHAR,
                region_id INTEGER,
                ai_annotations JSON,
                PRIMARY KEY (id),
                FOREIGN KEY(region_id) REFERENCES regions (id)
            )
        """)

        cursor.execute("""
            CREATE TABLE npc_instances (
                id INTEGER NOT NULL,
                template_id VARCHAR,
                name_override VARCHAR,
                current_hp INTEGER,
                max_hp INTEGER,
                status_effects JSON,
                location_id INTEGER,
                behavior_tags JSON,
                coordinates JSON,
                PRIMARY KEY (id),
                FOREIGN KEY(location_id) REFERENCES locations (id)
            )
        """)

        cursor.execute("""
            CREATE TABLE item_instances (
                id INTEGER NOT NULL,
                template_id VARCHAR,
                quantity INTEGER,
                location_id INTEGER,
                npc_id INTEGER,
                coordinates JSON,
                PRIMARY KEY (id),
                FOREIGN KEY(location_id) REFERENCES locations (id),
                FOREIGN KEY(npc_id) REFERENCES npc_instances (id)
            )
        """)

        # --- Migration: 2edc8d502cb2_add_traps_annotations_behavior ---
        cursor.execute("""
            CREATE TABLE trap_instances (
                id INTEGER NOT NULL,
                template_id VARCHAR,
                location_id INTEGER,
                coordinates JSON,
                status VARCHAR,
                PRIMARY KEY (id),
                FOREIGN KEY(location_id) REFERENCES locations (id)
            )
        """)
        print("All tables created successfully.")

        # --- Pre-population Step ---
        # Insert a default region
        cursor.execute("INSERT INTO regions (id, name) VALUES (?, ?)", (1, "Default Region"))

        # Insert the starting location (location_id = 1)
        starting_location_data = {
            "id": 1,
            "name": "STARTING_ZONE",
            "tags": json.dumps(["safe-zone", "town"]),
            "exits": json.dumps({"north": 2}), # Example exit
            "generated_map_data": json.dumps([[1, 1, 1], [1, 0, 1], [1, 1, 1]]), # Simple 3x3 map
            "map_seed": "initial_seed",
            "region_id": 1,
            "ai_annotations": json.dumps({})
        }
        cursor.execute("""
            INSERT INTO locations (id, name, tags, exits, generated_map_data, map_seed, region_id, ai_annotations)
            VALUES (:id, :name, :tags, :exits, :generated_map_data, :map_seed, :region_id, :ai_annotations)
        """, starting_location_data)

        print("Pre-populated with default region and STARTING_ZONE (location_id=1).")

        conn.commit()
        conn.close()
        print(f"Database '{DB_PATH}' initialized and populated successfully.")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    initialize_database()
