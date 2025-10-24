# data_loader.py
import json
from typing import Dict, List, Any
import os

# --- Global Variables to Hold Rulebook Data ---
# These are declared here and populated by load_data()
STATS_LIST: List[str] = []
SKILL_CATEGORIES: Dict[str, List[str]] = {}
ALL_SKILLS: Dict[str, Dict[str, str]] = {} # Maps skill name to its category and governing stat

ABILITY_DATA: Dict[str, Any] = {} # Abilities loaded directly as dict
TALENT_DATA: Dict[str, Any] = {} # Talents loaded as dict
KINGDOM_DATA: Dict[str, Any] = {} # Raw kingdom data (loaded within _process_kingdom_features)
FEATURE_STATS_MAP: Dict[str, Any] = {} # Processed feature map for fast lookups

# --- File Path Setup ---
# Get the directory where this data_loader.py file is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Construct the path to the 'data' subfolder
DATA_DIR = os.path.join(BASE_DIR, 'data')

# --- Helper Functions ---

def _load_json(filename: str) -> Any:
    """Helper function to load a JSON file from the data directory."""
    filepath = os.path.join(DATA_DIR, filename)
    print(f"Attempting to load: {filepath}") # Debug print
    try:
        with open(filepath, "r", encoding='utf-8') as f:
            data = json.load(f)
            print(f"Successfully loaded {filename}") # Debug print
            return data
    except FileNotFoundError:
        print(f"FATAL ERROR: Rules data file not found: {filepath}")
        raise
    except json.JSONDecodeError as e:
        print(f"FATAL ERROR: Failed to decode JSON from {filepath}. Error at char {e.pos}: {e.msg}") # More detailed error
        raise
    except Exception as e:
        print(f"FATAL ERROR: Unexpected error loading {filepath}: {e}")
        raise

def _correct_stat_names_in_mods(mods: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """Replaces 'Constitution' with 'Vitality' in stat modifier lists."""
    corrected_mods = {}
    if not isinstance(mods, dict):
        print(f"Warning: Expected dict for mods, got {type(mods)}. Skipping correction.")
        return mods # Return original if not a dict
    for key, stats in mods.items():
        if isinstance(stats, list):
             corrected_mods[key] = ["Vitality" if stat == "Constitution" else stat for stat in stats]
        else:
             print(f"Warning: Expected list for stats under key '{key}', got {type(stats)}. Keeping original.")
             corrected_mods[key] = stats # Keep original if not a list
    return corrected_mods

def _correct_stat_names_in_talents(talent_data: Any):
    """Recursively replaces 'Constitution' with 'Vitality' in talent data."""
    if isinstance(talent_data, dict):
        for key, value in list(talent_data.items()):
            if key == "stat" and value == "Constitution":
                talent_data[key] = "Vitality"
                # print("DEBUG: Corrected 'stat' in talent") # Debug print
            elif key == "pairedStats" and isinstance(value, list):
                 talent_data[key] = ["Vitality" if stat == "Constitution" else stat for stat in value]
                 # print("DEBUG: Corrected 'pairedStats' in talent") # Debug print
            else:
                _correct_stat_names_in_talents(value)
    elif isinstance(talent_data, list):
        for item in talent_data:
            _correct_stat_names_in_talents(item)

def _process_kingdom_features():
    """Processes kingdom data into a flat map, correcting stat names."""
    global FEATURE_STATS_MAP, KINGDOM_DATA # Need global KINGDOM_DATA too
    KINGDOM_DATA = _load_json("kingdom_features.json")
    FEATURE_STATS_MAP = {} # Clear map before processing
    if not isinstance(KINGDOM_DATA, dict):
         print("FATAL ERROR: kingdom_features.json did not load as a dictionary.")
         return # Stop processing if data is wrong type

    for category_data in KINGDOM_DATA.values(): # "F1", "F2", ...
        if not isinstance(category_data, dict): continue # Skip if category value isn't a dict
        for kingdom_data in category_data.values(): # "Mammal", "Reptile", ...
            if isinstance(kingdom_data, list):
                for feature in kingdom_data:
                    if not isinstance(feature, dict): continue # Skip if feature isn't a dict
                    feature_name = feature.get("name")
                    if feature_name:
                        if "mods" in feature:
                             feature["mods"] = _correct_stat_names_in_mods(feature["mods"])
                        FEATURE_STATS_MAP[feature_name] = feature
    print(f"Processed {len(FEATURE_STATS_MAP)} kingdom features into flat map (Vitality corrected).")


def _process_skills():
    """Processes the categorized skills into a master list."""
    global ALL_SKILLS, SKILL_CATEGORIES, STATS_LIST
    stats_data = _load_json("stats_and_skills.json")
    STATS_LIST = stats_data.get("stats", [])
    SKILL_CATEGORIES = stats_data.get("skill_categories", {})
    ALL_SKILLS = {} # Clear map before processing

    if not STATS_LIST:
        print("FATAL ERROR: 'stats' list not found or empty in stats_and_skills.json")
        return # Cannot proceed without stats list

    for category, skills in SKILL_CATEGORIES.items():
        if isinstance(skills, list): # Ensure skills is a list
            for i, skill_name in enumerate(skills):
                # Calculate stat index safely
                stat_index = i % len(STATS_LIST)
                governing_stat = STATS_LIST[stat_index]
                ALL_SKILLS[skill_name] = {
                    "category": category,
                    "stat": governing_stat
                }
        else:
            print(f"Warning: Expected list for skills in category '{category}', got {type(skills)}. Skipping category.")

    print(f"Processed {len(ALL_SKILLS)} skills into master map.")

# --- Main Loading Function ---

def load_data():
    """Main function called on server startup to load all rules into GLOBAL variables."""
    # Declare globals that will be assigned within this function
    global ABILITY_DATA, TALENT_DATA

    print("Starting data loading process...")
    try:
        # Load stats and skills first (populates STATS_LIST, SKILL_CATEGORIES, ALL_SKILLS)
        _process_skills()
        print(f"DEBUG: STATS_LIST type: {type(STATS_LIST)}, len: {len(STATS_LIST) if STATS_LIST else 0}")
        print(f"DEBUG: ALL_SKILLS type: {type(ALL_SKILLS)}, len: {len(ALL_SKILLS) if ALL_SKILLS else 0}")

        # Load abilities directly as dictionary
        ABILITY_DATA = _load_json("abilities.json")
        if not isinstance(ABILITY_DATA, dict):
            print(f"--- WARNING: ABILITY_DATA did NOT load as a dictionary. Type: {type(ABILITY_DATA)} ---")
            ABILITY_DATA = {} # Reset to empty dict to prevent downstream errors
        print(f"DEBUG: ABILITY_DATA type: {type(ABILITY_DATA)}, len: {len(ABILITY_DATA) if ABILITY_DATA else 0}")

        # Load talents
        TALENT_DATA = _load_json("talents.json")
        if not isinstance(TALENT_DATA, dict):
            print(f"--- WARNING: TALENT_DATA did NOT load as a dictionary. Type: {type(TALENT_DATA)} ---")
            TALENT_DATA = {} # Reset
        print(f"DEBUG: TALENT_DATA type: {type(TALENT_DATA)}, len: {len(TALENT_DATA) if TALENT_DATA else 0}")

        # Correct Stat Names in loaded talent data (modifies global TALENT_DATA)
        _correct_stat_names_in_talents(TALENT_DATA)
        print("DEBUG: Completed Vitality correction in TALENT_DATA.")

        # Pre-process kingdom features (loads KINGDOM_DATA and populates FEATURE_STATS_MAP globals)
        _process_kingdom_features()
        print(f"DEBUG: FEATURE_STATS_MAP type: {type(FEATURE_STATS_MAP)}, len: {len(FEATURE_STATS_MAP) if FEATURE_STATS_MAP else 0}")
        print(f"DEBUG: FEATURE_STATS_MAP keys found: {list(FEATURE_STATS_MAP.keys())}")
        # Final check
        if isinstance(ABILITY_DATA, dict) and ABILITY_DATA:
            print("--- Rules Engine Data Loaded Successfully (all major components processed) ---")
        else:
            print(f"--- WARNING: Final check shows ABILITY_DATA is not a populated dictionary. Type: {type(ABILITY_DATA)} ---")

    except Exception as e:
        print(f"FATAL ERROR during load_data execution: {e}")
        # Consider how to handle partial loads or stop server startup
        raise # Re-raise the exception to potentially stop server startup