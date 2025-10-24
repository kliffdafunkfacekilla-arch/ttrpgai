import json
import os

# Get the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
INPUT_FILE = os.path.join(DATA_DIR, 'abilities.json')
OUTPUT_FILE = os.path.join(DATA_DIR, 'abilities_dict.json') # Save to a new file first

print(f"Loading list from: {INPUT_FILE}")

try:
    with open(INPUT_FILE, 'r', encoding='utf-8') as f_in:
        ability_list = json.load(f_in)

    # Check if it's actually a list
    if not isinstance(ability_list, list):
        print(f"Error: {INPUT_FILE} is not a JSON list. No conversion needed or file is corrupt.")
        exit()

    # Convert list to dictionary
    ability_dict = {}
    for i, item in enumerate(ability_list):
        school_name = item.get("school")
        if not school_name:
            print(f"Warning: Item at index {i} is missing 'school' key. Skipping.")
            continue
        # Remove the 'school' key from the item itself, as it's now the main key
        item.pop("school", None)
        ability_dict[school_name] = item

    print(f"Converted {len(ability_dict)} schools to dictionary format.")

    # Save the new dictionary structure to a new file
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f_out:
        json.dump(ability_dict, f_out, indent=2) # Use indent for readability

    print(f"Successfully saved dictionary structure to: {OUTPUT_FILE}")
    print("Please review abilities_dict.json, then rename it to abilities.json if correct.")

except FileNotFoundError:
    print(f"Error: Input file not found at {INPUT_FILE}")
except json.JSONDecodeError as e:
    print(f"Error decoding JSON from {INPUT_FILE}: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")