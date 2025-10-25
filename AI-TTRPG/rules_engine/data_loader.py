# data_loader.py
import json
from typing import Dict, List, Any
import os

# --- Global Variables to Hold Rulebook Data ---
STATS_LIST: List[str] = []
SKILL_CATEGORIES: Dict[str, List[str]] = {}
ALL_SKILLS: Dict[str, Dict[str, str]] = {}
ABILITY_DATA: Dict[str, Any] = {}
TALENT_DATA: Dict[str, Any] = {}
KINGDOM_DATA: Dict[str, Any] = {}
FEATURE_STATS_MAP: Dict[str, Any] = {}

# --- File Path Setup ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

# --- Helper Functions ---

def _load_json(filename: str) -> Any:
    """Helper function to load a JSON file from the data directory."""
    filepath = os.path.join(DATA_DIR, filename)
    print(f"Attempting to load: {filepath}")
    try:
        with open(filepath, "r", encoding='utf-8') as f:
            data = json.load(f)
            print(f"Successfully loaded {filename}")
            return data
    except FileNotFoundError:
        print(f"FATAL ERROR: Rules data file not found: {filepath}")
        raise
    except json.JSONDecodeError as e:
        print(f"FATAL ERROR: Failed to decode JSON from {filepath}. Error at char {e.pos}: {e.msg}")
        raise
    except Exception as e:
        print(f"FATAL ERROR: Unexpected error loading {filepath}: {e}")
        raise

def _correct_stat_names_in_mods(mods: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """Replaces 'Constitution' with 'Vitality' in stat modifier lists."""
    corrected_mods = {}
    if not isinstance(mods, dict):
        print(f"Warning: Expected dict for mods, got {type(mods)}. Skipping correction.")
        return mods
    for key, stats in mods.items():
        if isinstance(stats, list):
             corrected_mods[key] = ["Vitality" if stat == "Constitution" else stat for stat in stats]
        else:
             print(f"Warning: Expected list for stats under key '{key}', got {type(stats)}. Keeping original.")
             corrected_mods[key] = stats
    return corrected_mods

# --- REMOVED _correct_stat_names_in_talents function ---

def _process_kingdom_features():
    """Processes kingdom data into a flat map, correcting stat names."""
    global FEATURE_STATS_MAP, KINGDOM_DATA
    KINGDOM_DATA = _load_json("kingdom_features.json")
    FEATURE_STATS_MAP = {}
    if not isinstance(KINGDOM_DATA, dict):
         print("FATAL ERROR: kingdom_features.json did not load as a dictionary.")
         return

    for category_data in KINGDOM_DATA.values():
        if not isinstance(category_data, dict): continue
        for kingdom_data in category_data.values():
            if isinstance(kingdom_data, list):
                for feature in kingdom_data:
                    if not isinstance(feature, dict): continue
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
    ALL_SKILLS = {}

    if not STATS_LIST:
        print("FATAL ERROR: 'stats' list not found or empty in stats_and_skills.json")
        return

    for category, skills in SKILL_CATEGORIES.items():
        if isinstance(skills, list):
            for i, skill_name in enumerate(skills):
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
    global ABILITY_DATA, TALENT_DATA # Declare globals being assigned

    print("Starting data loading process...")
    try:
        # Load stats and skills first
        _process_skills()
        print(f"DEBUG: STATS_LIST type: {type(STATS_LIST)}, len: {len(STATS_LIST) if STATS_LIST else 0}")
        print(f"DEBUG: ALL_SKILLS type: {type(ALL_SKILLS)}, len: {len(ALL_SKILLS) if ALL_SKILLS else 0}")

        # Load abilities directly as dictionary
        ABILITY_DATA = _load_json("abilities.json")
        if not isinstance(ABILITY_DATA, dict):
            print(f"--- WARNING: ABILITY_DATA did NOT load as a dictionary. Type: {type(ABILITY_DATA)} ---")
            ABILITY_DATA = {}
        print(f"DEBUG: ABILITY_DATA type: {type(ABILITY_DATA)}, len: {len(ABILITY_DATA) if ABILITY_DATA else 0}")

        # Load talents
        TALENT_DATA = _load_json("talents.json")
        if not isinstance(TALENT_DATA, dict):
            print(f"--- WARNING: TALENT_DATA did NOT load as a dictionary. Type: {type(TALENT_DATA)} ---")
            TALENT_DATA = {}
        print(f"DEBUG: TALENT_DATA type: {type(TALENT_DATA)}, len: {len(TALENT_DATA) if TALENT_DATA else 0}")

        # --- REMOVED CALL to _correct_stat_names_in_talents ---

        # Pre-process kingdom features
        _process_kingdom_features()
        print(f"DEBUG: FEATURE_STATS_MAP type: {type(FEATURE_STATS_MAP)}, len: {len(FEATURE_STATS_MAP) if FEATURE_STATS_MAP else 0}")

        # Final check
        if isinstance(ABILITY_DATA, dict) and ABILITY_DATA and isinstance(TALENT_DATA, dict) and TALENT_DATA and isinstance(FEATURE_STATS_MAP, dict) and FEATURE_STATS_MAP:
            print("--- Rules Engine Data Loaded Successfully (all major components processed) ---")
        else:
            print(f"--- WARNING: Final check shows one or more data components did not load correctly. ---")
            print(f"    ABILITY_DATA type: {type(ABILITY_DATA)}")
            print(f"    TALENT_DATA type: {type(TALENT_DATA)}")
            print(f"    FEATURE_STATS_MAP type: {type(FEATURE_STATS_MAP)}")


    except Exception as e:
        print(f"FATAL ERROR during load_data execution: {e}")
        raise