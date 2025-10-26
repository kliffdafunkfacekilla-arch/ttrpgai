# data_loader.py
import json
from typing import Dict, List, Any
import os

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

# --- Processing Functions ---

def _process_kingdom_features() -> Dict[str, Any]:
    """Processes kingdom data into a flat map AND RETURNS IT."""
    kingdom_data = _load_json("kingdom_features.json")
    feature_stats_map = {}
    if not isinstance(kingdom_data, dict):
         print("FATAL ERROR: kingdom_features.json did not load as a dictionary.")
         return {}

    for category_data in kingdom_data.values():
        if not isinstance(category_data, dict): continue
        for kingdom_list in category_data.values():
            if isinstance(kingdom_list, list):
                for feature in kingdom_list:
                    if not isinstance(feature, dict): continue
                    feature_name = feature.get("name")
                    if feature_name:
                        if "mods" in feature:
                             feature["mods"] = _correct_stat_names_in_mods(feature["mods"])
                        feature_stats_map[feature_name] = feature
    print(f"Processed {len(feature_stats_map)} kingdom features into flat map (Vitality corrected).")
    return feature_stats_map

def _process_skills() -> tuple[List[str], Dict[str, List[str]], Dict[str, Dict[str, str]]]:
    """Processes skills AND RETURNS stats list, categories dict, and all_skills dict."""
    stats_data = _load_json("stats_and_skills.json")
    stats_list = stats_data.get("stats", [])
    skill_categories = stats_data.get("skill_categories", {})
    all_skills = {}

    if not stats_list:
        print("FATAL ERROR: 'stats' list not found or empty in stats_and_skills.json")
        return [], {}, {}

    for category, skills in skill_categories.items():
        if isinstance(skills, list):
            for i, skill_name in enumerate(skills):
                stat_index = i % len(stats_list)
                governing_stat = stats_list[stat_index]
                all_skills[skill_name] = {
                    "category": category,
                    "stat": governing_stat
                }
        else:
            print(f"Warning: Expected list for skills in category '{category}', got {type(skills)}. Skipping category.")

    print(f"Processed {len(all_skills)} skills into master map.")
    return stats_list, skill_categories, all_skills

# --- Main Loading Function ---
# Global variables to hold the loaded data
STATS_LIST: List[str] = []
SKILL_CATEGORIES: Dict[str, List[str]] = {}
ALL_SKILLS: Dict[str, Dict[str, str]] = {}
ABILITY_DATA: Dict[str, Any] = {}
TALENT_DATA: Dict[str, Any] = {}
FEATURE_STATS_MAP: Dict[str, Any] = {}
MELEE_WEAPONS: Dict[str, Any] = {}
RANGED_WEAPONS: Dict[str, Any] = {}
ARMOR: Dict[str, Any] = {}
INJURY_EFFECTS: Dict[str, Any] = {}


def load_data() -> Dict[str, Any]:
    """Loads all rules data and returns it in a dictionary."""
    global STATS_LIST, SKILL_CATEGORIES, ALL_SKILLS, ABILITY_DATA, TALENT_DATA, FEATURE_STATS_MAP
    global MELEE_WEAPONS, RANGED_WEAPONS, ARMOR, INJURY_EFFECTS
    print("Starting data loading process...")

    try:
        # Load stats and skills
        STATS_LIST, SKILL_CATEGORIES, ALL_SKILLS = _process_skills()

        # Load abilities
        ABILITY_DATA = _load_json("abilities.json")
        if not isinstance(ABILITY_DATA, dict):
            print(f"--- WARNING: ABILITY_DATA did NOT load as a dictionary. Type: {type(ABILITY_DATA)} ---")
            ABILITY_DATA = {}

        # Load talents
        TALENT_DATA = _load_json("talents.json")
        if not isinstance(TALENT_DATA, dict):
            print(f"--- WARNING: TALENT_DATA did NOT load as a dictionary. Type: {type(TALENT_DATA)} ---")
            TALENT_DATA = {}

        # Process kingdom features
        FEATURE_STATS_MAP = _process_kingdom_features()

        # Load combat data
        MELEE_WEAPONS = _load_json("melee_weapons.json")
        RANGED_WEAPONS = _load_json("ranged_weapons.json")
        ARMOR = _load_json("armor.json")

        # Load injury data
        INJURY_EFFECTS = _load_json("injury_effects.json")

        loaded_data = {
            'stats_list': STATS_LIST,
            'skill_categories': SKILL_CATEGORIES,
            'all_skills': ALL_SKILLS,
            'ability_data': ABILITY_DATA,
            'talent_data': TALENT_DATA,
            'feature_stats_map': FEATURE_STATS_MAP,
            'melee_weapons': MELEE_WEAPONS,
            'ranged_weapons': RANGED_WEAPONS,
            'armor': ARMOR,
            'injury_effects': INJURY_EFFECTS
        }

        print(f"DEBUG: STATS_LIST len: {len(STATS_LIST)}")
        print(f"DEBUG: ALL_SKILLS len: {len(ALL_SKILLS)}")
        print(f"DEBUG: ABILITY_DATA len: {len(ABILITY_DATA)}")
        print(f"DEBUG: TALENT_DATA len: {len(TALENT_DATA)}")
        print(f"DEBUG: FEATURE_STATS_MAP len: {len(FEATURE_STATS_MAP)}")
        print(f"Loaded {len(MELEE_WEAPONS)} melee weapon categories.")
        print(f"Loaded {len(RANGED_WEAPONS)} ranged weapon categories.")
        print(f"Loaded {len(ARMOR)} armor categories.")
        print(f"Loaded {len(INJURY_EFFECTS)} major injury locations.")

        print("--- Rules Engine Data Parsed Successfully ---")
        return loaded_data

    except Exception as e:
        print(f"FATAL ERROR during load_data execution: {e}")
        raise
