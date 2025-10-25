# core.py
import random
from typing import Dict, List, Optional, Any
# Use relative import for models within the same package
from .models import RollResult, TalentInfo, FeatureStatsResponse

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
    else: dc = 20 # Assuming T10 might exist implicitly or have a higher DC

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

def get_kingdom_feature_stats(feature_name: str, feature_map: Dict[str, Any]) -> FeatureStatsResponse:
    """Looks up stat mods using the provided map."""
    if not feature_map:
        raise ValueError("Feature map not provided or empty.")
    if feature_name not in feature_map:
        raise ValueError(f"Feature '{feature_name}' not found in provided rules map.")
    feature_data = feature_map[feature_name]
    mods_data = feature_data.get("mods", {})
    return FeatureStatsResponse(
        name=feature_data.get("name", feature_name),
        mods=mods_data
    )

def get_skills_by_category(skill_categories_map: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """Returns skills grouped by category from the provided map."""
    if not skill_categories_map:
        raise ValueError("Skill categories map not provided or empty.")
    return skill_categories_map

def find_eligible_talents(stats_in: Dict[str, int],
                           skills_in: Dict[str, int], # {skill_name: rank}
                           talent_data: Dict[str, Any],
                           stats_list: List[str],
                           all_skills_map: Dict[str, Dict[str, str]]
                           ) -> List[TalentInfo]:
    """Finds unlocked talents based on stats, skills, and provided talent data."""
    unlocked_talents = []

    if not talent_data or not stats_list or not all_skills_map:
         print("Warning: Missing required data (talents, stats list, or skills map) for talent lookup.")
         return []

    stats_complete = {stat: stats_in.get(stat, 0) for stat in stats_list}
    skills_complete = skills_in # Assumes skills_in is {skill_name: rank}

    # --- 1. Check Single Stat Mastery ---
    for talent_group in talent_data.get("single_stat_mastery", []):
        stat_name = talent_group.get("stat")
        if not stat_name: continue
        current_stat_score = stats_complete.get(stat_name, 0)
        # Check 'score' field (ensure talents.json uses 'score')
        required_score = talent_group.get("score")
        if required_score is not None and current_stat_score >= required_score:
             unlocked_talents.append(TalentInfo(
                 name=talent_group.get("talent_name", "Unknown Talent"),
                 source=f"Stat: {stat_name} {required_score}",
                 effect=talent_group.get("effect", "")
             ))

    # --- 2. Check Dual Stat Synergy ---
    for talent in talent_data.get("dual_stat_focus", []):
        req_score = talent.get("score", 99) # Check 'score' field
        stats_pair = talent.get("paired_stats", []) # Check 'paired_stats' field
        if len(stats_pair) == 2:
            stat1, stat2 = stats_pair
            if stats_complete.get(stat1, 0) >= req_score and stats_complete.get(stat2, 0) >= req_score:
                unlocked_talents.append(TalentInfo(
                    name=talent.get("talent_name", "Unknown Talent"), # Check 'talent_name' field
                    source=f"Dual Stat: {stat1} & {stat2} {req_score}",
                    effect=talent.get("effect", "")
                ))

    # --- 3. Check Skill Mastery ---
    for category_key, category_list in talent_data.get("single_skill_mastery", {}).items():
         if isinstance(category_list, list):
            for skill_group in category_list:
                skill_name = skill_group.get("skill")
                if skill_name and skill_name in all_skills_map: # Check against provided map
                     current_skill_rank = skills_complete.get(skill_name, 0)
                     for talent in skill_group.get("talents", []):
                        # Check both 'tier' and 'prerequisite_mt' keys for flexibility
                        tier_name = talent.get("tier", talent.get("prerequisite_mt"))
                        req_rank = 99
                        if tier_name and tier_name.startswith("MT"):
                            try: req_rank = int(tier_name.replace("MT", ""))
                            except ValueError: pass

                        if current_skill_rank >= req_rank:
                            unlocked_talents.append(TalentInfo(
                                name=talent.get("talent_name", "Unknown Talent"), # Check 'talent_name' field
                                source=f"Skill: {skill_name} ({tier_name})",
                                effect=talent.get("effect", "")
                            ))
                elif skill_name:
                    print(f"Warning: Skill '{skill_name}' from talent data not found in master skill map.")

    return unlocked_talents