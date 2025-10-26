import json
import requests
import os

# --- Configuration ---
WORLD_ENGINE_URL = "http://localhost:8002/v1"
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

def preload_data():
    """
    Reads JSON files from the data/ directory and posts them to the
    world_engine API to populate the database.
    """
    print("--- Starting World Engine Data Preload ---")

    # --- 1. Factions ---
    try:
        with open(os.path.join(DATA_DIR, "initial_factions.json"), "r") as f:
            factions = json.load(f)
        print(f"Loaded {len(factions)} factions from JSON.")
        for faction in factions:
            response = requests.post(f"{WORLD_ENGINE_URL}/factions/", json=faction)
            if response.status_code == 201:
                print(f"  > Created faction: {faction['name']}")
            else:
                print(f"  > Failed to create faction {faction['name']}. Status: {response.status_code}, Response: {response.text}")
    except FileNotFoundError:
        print("initial_factions.json not found. Skipping.")
    except Exception as e:
        print(f"An error occurred while loading factions: {e}")

    # --- 2. Regions ---
    try:
        with open(os.path.join(DATA_DIR, "initial_regions.json"), "r") as f:
            regions = json.load(f)
        print(f"\nLoaded {len(regions)} regions from JSON.")
        for region in regions:
            response = requests.post(f"{WORLD_ENGINE_URL}/regions/", json=region)
            if response.status_code == 201:
                print(f"  > Created region: {region['name']}")
            else:
                print(f"  > Failed to create region {region['name']}. Status: {response.status_code}, Response: {response.text}")
    except FileNotFoundError:
        print("initial_regions.json not found. Skipping.")
    except Exception as e:
        print(f"An error occurred while loading regions: {e}")


    # --- 3. Locations ---
    try:
        with open(os.path.join(DATA_DIR, "initial_locations.json"), "r") as f:
            locations = json.load(f)
        print(f"\nLoaded {len(locations)} locations from JSON.")
        for loc in locations:
            response = requests.post(f"{WORLD_ENGINE_URL}/locations/", json=loc)
            if response.status_code == 201:
                print(f"  > Created location: {loc['name']}")
            else:
                print(f"  > Failed to create location {loc['name']}. Status: {response.status_code}, Response: {response.text}")
    except FileNotFoundError:
        print("initial_locations.json not found. Skipping.")
    except Exception as e:
        print(f"An error occurred while loading locations: {e}")

    print("\n--- Data Preload Complete ---")

if __name__ == "__main__":
    preload_data()
