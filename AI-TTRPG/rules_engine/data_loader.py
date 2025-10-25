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

def load_data() -> Dict[str, Any]:
    """Loads all rules data and returns it in a dictionary."""
    print("Starting data loading process...")
    loaded_data = {}
    try:
        # Load stats and skills
        stats_list, skill_categories, all_skills = _process_skills()
        loaded_data['stats_list'] = stats_list
        loaded_data['skill_categories'] = skill_categories
        loaded_data['all_skills'] = all_skills
        print(f"DEBUG: STATS_LIST len: {len(stats_list)}")
        print(f"DEBUG: ALL_SKILLS len: {len(all_skills)}")

        # Load abilities
        ability_data = _load_json("abilities.json")
        if not isinstance(ability_data, dict):
            print(f"--- WARNING: ABILITY_DATA did NOT load as a dictionary. Type: {type(ability_data)} ---")
            ability_data = {}
        loaded_data['ability_data'] = ability_data
        print(f"DEBUG: ABILITY_DATA len: {len(ability_data)}")

        # Load talents
        talent_data = _load_json("talents.json")
        if not isinstance(talent_data, dict):
            print(f"--- WARNING: TALENT_DATA did NOT load as a dictionary. Type: {type(talent_data)} ---")
            talent_data = {}
        # No need to correct stats here if talents.json is already fixed
        loaded_data['talent_data'] = talent_data
        print(f"DEBUG: TALENT_DATA len: {len(talent_data)}")

        # Process kingdom features
        feature_stats_map = _process_kingdom_features()
        loaded_data['feature_stats_map'] = feature_stats_map
        print(f"DEBUG: FEATURE_STATS_MAP len: {len(feature_stats_map)}")

        print("--- Rules Engine Data Parsed Successfully ---")
        return loaded_data # Return the dictionary

    except Exception as e:
        print(f"FATAL ERROR during load_data execution: {e}")
        raise