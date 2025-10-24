import random

def perform_skill_check(stat_modifier: int, skill_rank: int, dc: int) -> tuple[bool, int]:
    """
    Performs a skill check by rolling a d20, adding modifiers, and comparing to a DC.
    """
    roll = random.randint(1, 20)
    total = roll + stat_modifier + skill_rank
    success = total >= dc
    return success, roll

# core.py
import random
from typing import Dict, List, Optional, Any
# Use relative import for models within the same package
from .models import RollResult, TalentInfo, FeatureStatsResponse
# Import globals from data_loader using relative import
from .data_loader import TALENT_DATA, FEATURE_STATS_MAP, STATS_LIST, SKILL_CATEGORIES, ALL_SKILLS

# --- Dice Rolling ---

def _roll_d20() -> int:
    return random.randint(1, 20)

def _roll_d6() -> int:
    return random.randint(1, 6)

# --- Core Validation Logic ---

def calculate_skill_check(stat_mod: int, skill_rank: int, dc: int) -> RollResult:
    """Performs a d20 skill check."""
    roll = _roll_d20()
    total = roll + stat_mod + skill_rank
    success = total >= dc
    crit_success = (roll == 20)
    crit_fail = (roll == 1)
    sre_triggered = crit_success or crit_fail

    return RollResult(
        roll_value=roll, total_value=total, dc=dc, is_success=success,
        is_critical_success=crit_success, is_critical_failure=crit_fail,
        sre_triggered=sre_triggered
    )

def calculate_ability_check(rank: int, stat_mod: int, tier: int) -> RollResult:
    """Performs a d20 Ability check against a Tiered DC."""
    if tier <= 3: dc = 12
    elif tier <= 6: dc = 14
    elif tier <= 9: dc = 16
    else: dc = 20 # Define a DC for T10?

    roll = _roll_d20()
    total = roll + rank + stat_mod
    success = total >= dc
    crit_success = (roll == 20)
    crit_fail = (roll == 1)

    return RollResult(
        roll_value=roll, total_value=total, dc=dc, is_success=success,
        is_critical_success=crit_success, is_critical_failure=crit_fail,
        sre_triggered=False
    )

# --- Core Lookup Logic ---

# In core.py
def get_kingdom_feature_stats(feature_name: str, feature_map: Dict[str, Any]) -> FeatureStatsResponse:
    """Looks up the stat modifications using the provided map."""
    if feature_name not in feature_map:
        # This function now raises the error if not found in the map IT RECEIVED
        raise ValueError(f"Feature '{feature_name}' not found in provided rules map.")
    feature_data = feature_map[feature_name]
    mods_data = feature_data.get("mods", {})
    return FeatureStatsResponse(
        name=feature_data.get("name", feature_name),
        mods=mods_data
    )

def get_skills_by_category() -> Dict[str, List[str]]:
    """Returns skills grouped by category."""
    # Ensure SKILL_CATEGORIES is loaded
    if not SKILL_CATEGORIES:
        raise ValueError("Skill categories not loaded.")
    return SKILL_CATEGORIES

def find_eligible_talents(stats_in: Dict[str, int], skills_in: Dict[str, int]) -> List[TalentInfo]:
    """Finds all unlocked talents based on stats and skills."""
    unlocked_talents = []

    # Ensure TALENT_DATA is loaded
    if not TALENT_DATA:
         print("Warning: Talent data not loaded, cannot find eligible talents.")
         return []

    # Ensure STATS_LIST is available for defaulting stats
    stats_complete = {stat: stats_in.get(stat, 0) for stat in STATS_LIST}
    # skills_in should be {skill_name: rank}
    skills_complete = skills_in

    # --- 1. Check Single Stat Mastery ---
    for talent_group in TALENT_DATA.get("singleStatMastery", []):
        stat_name = talent_group.get("stat") # Already corrected to Vitality
        if not stat_name: continue # Skip if stat name is missing
        current_stat_score = stats_complete.get(stat_name, 0)
        for milestone in talent_group.get("milestones", []):
            if current_stat_score >= milestone.get("score", 99):
                unlocked_talents.append(TalentInfo(
                    name=milestone.get("name", "Unknown Talent"),
                    source=f"Stat: {stat_name} {milestone.get('score', '?')}",
                    effect=milestone.get("effect", "")
                ))

    # --- 2. Check Dual Stat Synergy ---
    for talent in TALENT_DATA.get("dualStatSynergy", []):
        req_score = talent.get("score", 99)
        stats_pair = talent.get("pairedStats", []) # Already corrected
        if len(stats_pair) == 2:
            stat1, stat2 = stats_pair
            if stats_complete.get(stat1, 0) >= req_score and stats_complete.get(stat2, 0) >= req_score:
                unlocked_talents.append(TalentInfo(
                    name=talent.get("name", "Unknown Talent"),
                    source=f"Dual Stat: {stat1} & {stat2} {req_score}",
                    effect=talent.get("effect", "")
                ))

    # --- 3. Check Skill Mastery ---
    # Ensure ALL_SKILLS is loaded for skill name validation (optional but safer)
    if not ALL_SKILLS:
         print("Warning: Skill master list not loaded, skill mastery talents might be missed.")

    for category_key, category_list in TALENT_DATA.get("skillMastery", {}).items():
         if isinstance(category_list, list):
            for skill_group in category_list:
                skill_name = skill_group.get("skill")
                if skill_name and skill_name in ALL_SKILLS: # Check if skill is valid
                     current_skill_rank = skills_complete.get(skill_name, 0)
                     for talent in skill_group.get("talents", []):
                        tier_name = talent.get("tier")
                        req_rank = 99
                        if tier_name and tier_name.startswith("MT"):
                            try:
                                req_rank = int(tier_name.replace("MT", ""))
                            except ValueError: pass

                        if current_skill_rank >= req_rank:
                            unlocked_talents.append(TalentInfo(
                                name=talent.get("name", "Unknown Talent"),
                                source=f"Skill: {skill_name} ({tier_name})",
                                effect=talent.get("effect", "")
                            ))
                elif skill_name:
                    print(f"Warning: Skill '{skill_name}' from talent data not found in master skill list.")


    return unlocked_talents