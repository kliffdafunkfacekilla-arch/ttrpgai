
import sqlite3
import os

# Get the directory where the script is located.
_script_dir = os.path.dirname(os.path.abspath(__file__))
# Set the database path to be in the root of the project, not in a service folder.
DB_PATH = os.path.join(_script_dir, "characters.db")


def initialize_database():
    """
    Connects to the SQLite database and creates the 'characters' table
    with the full, correct schema.
    """
    print(f"Initializing database at: {DB_PATH}")
    try:
        # Connect to the database (this will create the file if it doesn't exist)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Drop the table if it already exists to ensure a clean slate
        cursor.execute("DROP TABLE IF EXISTS characters")

        # Create the 'characters' table with all columns from both migrations
        create_table_sql = """
        CREATE TABLE characters (
            id VARCHAR NOT NULL,
            name VARCHAR,
            kingdom VARCHAR,
            level INTEGER,
            stats JSON,
            skills JSON,
            max_hp INTEGER,
            current_hp INTEGER,
            resource_pools JSON,
            talents JSON,
            abilities JSON,
            inventory JSON,
            equipment JSON,
            status_effects JSON,
            injuries JSON,
            position_x INTEGER,
            position_y INTEGER,
            current_location_id INTEGER,
            PRIMARY KEY (id)
        );
        """
        cursor.execute(create_table_sql)
        print("Table 'characters' created successfully.")

        # Create the indexes
        cursor.execute("CREATE INDEX ix_characters_id ON characters (id)")
        cursor.execute("CREATE INDEX ix_characters_name ON characters (name)")
        print("Indexes for 'characters' table created successfully.")

        # Commit the changes and close the connection
        conn.commit()
        conn.close()
        print(f"Database '{DB_PATH}' initialized successfully.")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    initialize_database()
