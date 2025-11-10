# data_loader.py
import json
from typing import Dict, List, Any
import os

# --- File Path Setup ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

# --- Helper Functions ---


def _load_json(filename: str) -> Any:
    """Helper function to load a JSON file from the data directory."""
    filepath = os.path.join(DATA_DIR, filename)
    print(f"Attempting to load: {filepath}")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            print(f"Successfully loaded {filename}")
            return data
    except FileNotFoundError:
        print(f"FATAL ERROR: Rules data file not found: {filepath}")
        raise
    except json.JSONDecodeError as e:
        print(
            f"FATAL ERROR: Failed to decode JSON from {filepath}. Error at char {e.pos}: {e.msg}"
        )
        raise
    except Exception as e:
        print(f"FATAL ERROR: Unexpected error loading {filepath}: {e}")
        raise


# --- Processing Functions ---


def _process_kingdom_features() -> Dict[str, Any]:
    """Processes kingdom data into a flat map AND RETURNS IT."""
    kingdom_data = _load_json("kingdom_features.json")
    feature_stats_map = {}
    if not isinstance(kingdom_data, dict):
        print("FATAL ERROR: kingdom_features.json did not load as a dictionary.")
        return {}

    for category_data in kingdom_data.values():
        if not isinstance(category_data, dict):
            continue
        for kingdom_list in category_data.values():
            if isinstance(kingdom_list, list):
                for feature in kingdom_list:
                    if not isinstance(feature, dict):
                        continue
                    feature_name = feature.get("name")
                    if feature_name:
                        feature_stats_map[feature_name] = feature
    print(
        f"Processed {len(feature_stats_map)} kingdom features into flat map."
    )
    return feature_stats_map


def _process_skills() -> (
    tuple[List[str], Dict[str, Dict[str, str]], Dict[str, Dict[str, str]]]
):
    """Processes skills AND RETURNS stats list, categories dict, and all_skills dict."""
    stats_data = _load_json("stats_and_skills.json")
    stats_list = stats_data.get("stats", [])
    skill_categories = stats_data.get("skill_categories", {})
    all_skills = {}

    if not stats_list:
        print("FATAL ERROR: 'stats' list not found or empty in stats_and_skills.json")
        return [], {}, {}

    for category, skills_dict in skill_categories.items():
        if isinstance(skills_dict, dict):
            for skill_name, governing_stat in skills_dict.items():
                if governing_stat not in stats_list:
                    print(
                        f"Warning: Skill '{skill_name}' has invalid governing stat '{governing_stat}'. Skipping."
                    )
                    continue

                all_skills[skill_name] = {"category": category, "stat": governing_stat}
        else:
            print(
                f"Warning: Expected dict for skills in category '{category}', got {type(skills_dict)}. Skipping category."
            )

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
KINGDOM_FEATURES_DATA: Dict[str, Any] = {}
MELEE_WEAPONS: Dict[str, Any] = {}
RANGED_WEAPONS: Dict[str, Any] = {}
ARMOR: Dict[str, Any] = {}
INJURY_EFFECTS: Dict[str, Any] = {}
STATUS_EFFECTS: Dict[str, Any] = {}
EQUIPMENT_CATEGORY_TO_SKILL_MAP: Dict[str, str] = {}
NPC_TEMPLATES: Dict[str, Any] = {}
ITEM_TEMPLATES: Dict[str, Any] = {}


# --- ADD NEW BACKGROUND GLOBALS ---
ORIGIN_CHOICES: List[Dict[str, Any]] = []
CHILDHOOD_CHOICES: List[Dict[str, Any]] = []
COMING_OF_AGE_CHOICES: List[Dict[str, Any]] = []
TRAINING_CHOICES: List[Dict[str, Any]] = []
DEVOTION_CHOICES: List[Dict[str, Any]] = []


# --- END ADD ---


def load_data() -> Dict[str, Any]:
    """Loads all rules data and returns it in a dictionary."""
    global STATS_LIST, SKILL_CATEGORIES, ALL_SKILLS, ABILITY_DATA, TALENT_DATA, FEATURE_STATS_MAP
    global MELEE_WEAPONS, RANGED_WEAPONS, ARMOR, INJURY_EFFECTS, STATUS_EFFECTS, EQUIPMENT_CATEGORY_TO_SKILL_MAP, KINGDOM_FEATURES_DATA, NPC_TEMPLATES, ITEM_TEMPLATES
    global ORIGIN_CHOICES, CHILDHOOD_CHOICES, COMING_OF_AGE_CHOICES, TRAINING_CHOICES, DEVOTION_CHOICES

    print("Starting data loading process...")
    loaded_data = {}
    try:
        # Load stats and skills
        STATS_LIST, SKILL_CATEGORIES, ALL_SKILLS = _process_skills()

        # Load abilities
        ABILITY_DATA = _load_json("abilities.json")
        if not isinstance(ABILITY_DATA, dict):
            print(
                f"--- WARNING: ABILITY_DATA did NOT load as a dictionary. Type: {type(ABILITY_DATA)} ---"
            )
            ABILITY_DATA = {}

        # Load talents
        TALENT_DATA = _load_json("talents.json")
        if not isinstance(TALENT_DATA, dict):
            print(
                f"--- WARNING: TALENT_DATA did NOT load as a dictionary. Type: {type(TALENT_DATA)} ---"
            )
            TALENT_DATA = {}

        # Process kingdom features (flat map for lookups)
        FEATURE_STATS_MAP = _process_kingdom_features()

        # Load kingdom features (full structure for creation)
        KINGDOM_FEATURES_DATA = _load_json("kingdom_features.json")

        # Load combat data
        MELEE_WEAPONS = _load_json("melee_weapons.json")
        RANGED_WEAPONS = _load_json("ranged_weapons.json")
        ARMOR = _load_json("armor.json")

        # Load skill mappings
        EQUIPMENT_CATEGORY_TO_SKILL_MAP = _load_json("skill_mappings.json")

        # Load injury data
        INJURY_EFFECTS = _load_json("injury_effects.json")

        # Load Status Effects
        status_file = os.path.join(DATA_DIR, "status_effects.json")
        try:
            if os.path.exists(status_file):
                with open(status_file, "r", encoding="utf-8") as f:
                    STATUS_EFFECTS = json.load(f)
                print(
                    f"Loaded {len(STATUS_EFFECTS)} status effect definitions from status_effects.json."
                )
            else:
                print(
                    f"WARNING: status_effects.json not found at {status_file}. Status lookup will fail."
                )
                STATUS_EFFECTS = {}
        except json.JSONDecodeError as e:
            print(f"ERROR decoding status_effects.json: {e}. Status lookup will fail.")
            STATUS_EFFECTS = {}
        except Exception as e:
            print(f"ERROR loading status_effects.json: {e}. Status lookup will fail.")
            STATUS_EFFECTS = {}

        # --- LOAD NEW BACKGROUND CHOICES ---
        ORIGIN_CHOICES = _load_json("origin_choices.json")
        CHILDHOOD_CHOICES = _load_json("childhood_choices.json")
        COMING_OF_AGE_CHOICES = _load_json("coming_of_age_choices.json")
        TRAINING_CHOICES = _load_json("training_choices.json")
        DEVOTION_CHOICES = _load_json("devotion_choices.json")
        # --- END LOAD ---

        NPC_TEMPLATES = _load_json("npc_templates.json")
        ITEM_TEMPLATES = _load_json("item_templates.json")

        loaded_data = {
            "stats_list": STATS_LIST,
            "skill_categories": SKILL_CATEGORIES,
            "all_skills": ALL_SKILLS,
            "ability_data": ABILITY_DATA,
            "talent_data": TALENT_DATA,
            "feature_stats_map": FEATURE_STATS_MAP,
            "kingdom_features_data": KINGDOM_FEATURES_DATA,
            "melee_weapons": MELEE_WEAPONS,
            "ranged_weapons": RANGED_WEAPONS,
            "armor": ARMOR,
            "injury_effects": INJURY_EFFECTS,
            "status_effects": STATUS_EFFECTS,
            "equipment_category_to_skill_map": EQUIPMENT_CATEGORY_TO_SKILL_MAP,
            # --- ADD TO RETURN DICT ---
            "origin_choices": ORIGIN_CHOICES,
            "childhood_choices": CHILDHOOD_CHOICES,
            "coming_of_age_choices": COMING_OF_AGE_CHOICES,
            "training_choices": TRAINING_CHOICES,
            "devotion_choices": DEVOTION_CHOICES,
            # --- END ADD ---
            "npc_templates": NPC_TEMPLATES,
            "item_templates": ITEM_TEMPLATES,
        }

        print(f"DEBUG: STATS_LIST len: {len(STATS_LIST)}")
        print(f"DEBUG: ALL_SKILLS len: {len(ALL_SKILLS)}")
        print(f"DEBUG: ABILITY_DATA len: {len(ABILITY_DATA)}")
        print(f"DEBUG: TALENT_DATA len: {len(TALENT_DATA)}")
        print(f"DEBUG: FEATURE_STATS_MAP len: {len(FEATURE_STATS_MAP)}")
        print(
            f"DEBUG: KINGDOM_FEATURES_DATA keys: {len(KINGDOM_FEATURES_DATA.keys())}"
        )
        print(f"Loaded {len(MELEE_WEAPONS)} melee weapon categories.")
        print(f"Loaded {len(RANGED_WEAPONS)} ranged weapon categories.")
        print(f"Loaded {len(ARMOR)} armor categories.")
        print(f"Loaded {len(EQUIPMENT_CATEGORY_TO_SKILL_MAP)} skill mappings.")
        print(f"Loaded {len(INJURY_EFFECTS)} major injury locations.")
        print(f"Loaded {len(STATUS_EFFECTS)} status effect definitions.")
        # --- ADD PRINT STATEMENTS ---
        print(f"Loaded {len(ORIGIN_CHOICES)} origin choices.")
        print(f"Loaded {len(CHILDHOOD_CHOICES)} childhood choices.")
        print(f"Loaded {len(COMING_OF_AGE_CHOICES)} coming of age choices.")
        print(f"Loaded {len(TRAINING_CHOICES)} training choices.")
        print(f"Loaded {len(DEVOTION_CHOICES)} devotion choices.")
        print(f"Loaded {len(NPC_TEMPLATES)} NPC templates.")
        print(f"Loaded {len(ITEM_TEMPLATES)} item templates.")
        # --- END ADD ---

        print("--- Rules Engine Data Parsed Successfully ---")
        return loaded_data

    except Exception as e:
        print(f"FATAL ERROR during load_data execution: {e}")
        raise
