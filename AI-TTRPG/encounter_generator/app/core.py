import random
from typing import List, Dict, Any, Optional, Union
from . import data_loader # To access the loaded data
from . import models

def find_matching_encounter(
    requested_tags: List[str]
) -> Optional[Dict[str, Any]]:
    """
    Finds a random encounter that matches ALL of the requested tags.
    """
    # Create a set for fast lookup
    tag_set = set(t.lower() for t in requested_tags)

    # --- 1. Combine all encounter lists ---
    # We can add social encounters, etc., to this list later
    all_encounters = (
        data_loader.COMBAT_ENCOUNTERS +
        data_loader.SKILL_ENCOUNTERS
    )

    # --- 2. Find all matches ---
    matches = []
    for encounter in all_encounters:
        # Create a set of the encounter's tags
        encounter_tags = set(t.lower() for t in encounter.get('tags', []))

        # Check if all requested tags are in this encounter's tags
        if tag_set.issubset(encounter_tags):
            matches.append(encounter)

    # --- 3. Pick one at random ---
    if not matches:
        return None

    return random.choice(matches)

def build_encounter_response(
    encounter_data: Dict[str, Any]
) -> Union[models.CombatEncounterResponse, models.SkillEncounterResponse]:
    """
    Converts the raw encounter data into a Pydantic
    response model.
    """
    encounter_type = encounter_data.get('type', 'combat') # Default

    # This is a bit of a hack to get the 'type' from the 'tags'
    if 'skill' in encounter_data.get('tags', []):
        encounter_type = 'skill'
    elif 'combat' in encounter_data.get('tags', []):
        encounter_type = 'combat'

    if encounter_type == 'combat':
        return models.CombatEncounterResponse(
            id=encounter_data.get('id'),
            description=encounter_data.get('description'),
            npcs_to_spawn=encounter_data.get('npcs_to_spawn', [])
        )

    elif encounter_type == 'skill':
        return models.SkillEncounterResponse(
            id=encounter_data.get('id'),
            title=encounter_data.get('title'),
            description=encounter_data.get('description'),
            success_threshold=encounter_data.get('success_threshold', 1),
            stages=encounter_data.get('stages', [])
        )

    # This will fail validation, which is what we want
    # if the type is unknown.
    raise ValueError(f"Unknown encounter type: {encounter_type}")