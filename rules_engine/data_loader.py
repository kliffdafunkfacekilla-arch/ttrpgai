# data_loader.py
import json
from typing import Dict, List, Any
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, filename="server.log", filemode="w")

# Global variables to hold our "Rulebook"
STATS_LIST: List[str] = []
SKILL_CATEGORIES: Dict[str, List[str]] = {}
ALL_SKILLS: Dict[str, Dict[str, str]] = {} # e.g., {"Intimidation": {"category": "Conversational", "stat": "Might"}}

ABILITY_DATA: Dict[str, Any] = {}
TALENT_DATA: Dict[str, Any] = {}
KINGDOM_DATA: Dict[str, Any] = {}

# A pre-processed map for fast feature lookups
FEATURE_STATS_MAP: Dict[str, Any] = {}

def _load_json(filepath: str) -> Any:
    """Helper function to load a JSON file."""
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error(f"FATAL ERROR: Rules data file not found: {filepath}")
        raise
    except json.JSONDecodeError:
        logging.error(f"FATAL ERROR: Failed to decode JSON from {filepath}")
        raise

def _process_kingdom_features():
    """
    Processes the nested kingdom data into a simple, flat dictionary
    for fast lookups by feature name.
    """
    global FEATURE_STATS_MAP

    # We must correct the stat name "Constitution" to "Vitality"
    # as we load the data, since our app uses "Vitality"
    def _correct_stat_names(mods: Dict[str, List[str]]) -> Dict[str, List[str]]:
        corrected_mods = {}
        for key, stats in mods.items():
            corrected_mods[key] = ["Vitality" if stat == "Constitution" else stat for stat in stats]
        return corrected_mods

    for category_data in KINGDOM_DATA.values(): # "F1", "F2", ...
        for kingdom_data in category_data.values(): # "Mammal", "Reptile", ...
            if isinstance(kingdom_data, list):
                for feature in kingdom_data:
                    feature_name = feature.get("name")
                    if feature_name:
                        # Correct stat names before storing
                        feature["mods"] = _correct_stat_names(feature["mods"])
                        FEATURE_STATS_MAP[feature_name] = feature

    logging.info(f"Processed {len(FEATURE_STATS_MAP)} kingdom features into flat map.")

def _process_skills():
    """Processes the categorized skills into a master list."""
    global ALL_SKILLS, SKILL_CATEGORIES

    data = _load_json(os.path.abspath(os.path.join(os.path.dirname(__file__), 'data/stats_and_skills.json')))
    SKILL_CATEGORIES = data.get("skill_categories", {})

    # This maps each skill to its category and governing stat (from skills.txt)
    # This logic assumes the skills in each category are in the same order
    # as the stats in the stats list (A-L).
    stats_list = data.get("stats", [])

    for category, skills in SKILL_CATEGORIES.items():
        for i, skill_name in enumerate(skills):
            stat_index = i % 12 # Maps skill to its A-L stat
            ALL_SKILLS[skill_name] = {
                "category": category,
                "stat": stats_list[stat_index]
            }
    logging.info(f"Processed {len(ALL_SKILLS)} skills into master map.")


def load_rules_data():
    """Main function called on server startup to load all rules."""
    global STATS_LIST, ABILITY_DATA, TALENT_DATA, KINGDOM_DATA

    # Load stats and skills first
    stats_data = _load_json(os.path.abspath(os.path.join(os.path.dirname(__file__), 'data/stats_and_skills.json')))
    STATS_LIST = stats_data.get("stats", [])
    _process_skills()

    # Load other data
    ABILITY_DATA = _load_json(os.path.abspath(os.path.join(os.path.dirname(__file__), 'data/abilities.json')))
    TALENT_DATA = _load_json(os.path.abspath(os.path.join(os.path.dirname(__file__), 'data/talents.json')))
    KINGDOM_DATA = _load_json(os.path.abspath(os.path.join(os.path.dirname(__file__), 'data/kingdom_features.json')))

    # Pre-process complex data
    _process_kingdom_features()

    logging.info("--- Rules Engine Data Loaded Successfully ---")
