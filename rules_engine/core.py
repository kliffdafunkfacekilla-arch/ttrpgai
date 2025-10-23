# core.py
import random
from typing import Dict, List
from models import RollResult, TalentInfo, FeatureStatsResponse
from data_loader import (
    TALENT_DATA, FEATURE_STATS_MAP, STATS_LIST, SKILL_CATEGORIES
)

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

    # SRE is gained on Critical Success or Failure
    sre_triggered = crit_success or crit_fail

    return RollResult(
        roll_value=roll,
        total_value=total,
        dc=dc,
        is_success=success,
        is_critical_success=crit_success,
        is_critical_failure=crit_fail,
        sre_triggered=sre_triggered
    )

def calculate_ability_check(rank: int, stat_mod: int, tier: int) -> RollResult:
    """Performs a d20 Ability check against a Tiered DC."""
    # This Tiered DC map is from your ability text file
    dc_map = {
        1: 12, 2: 12, 3: 12,  # T1-3 (Assuming a base DC, adjust as needed)
        4: 14, 5: 14, 6: 14,  # T4-6
        7: 16, 8: 16, 9: 18   # T7-9
    }
    # Per your file: "Tiered Difficulty Class (DC 12 for Tier 1, DC 14 for Tier 2, etc.)"
    # This implies T1-3=12, T4-6=14, T7-9=16? Let's use a simpler map for now:
    dc_map_simple = { 1: 12, 2: 12, 3: 12, 4: 14, 5: 14, 6: 14, 7: 16, 8: 16, 9: 18, 10: 20 }

    dc = dc_map_simple.get(tier, 99) # Default to 99 if invalid tier

    roll = _roll_d20()
    total = roll + rank + stat_mod

    return RollResult(
        roll_value=roll,
        total_value=total,
        dc=dc,
        is_success=total >= dc,
        is_critical_success=roll == 20,
        is_critical_failure=roll == 1
    )

# --- Core Lookup Logic ---

def get_kingdom_feature_stats(feature_name: str) -> FeatureStatsResponse:
    """
    Looks up the stat modifications for a given kingdom feature name.
    """
    if feature_name not in FEATURE_STATS_MAP:
        raise ValueError(f"Feature '{feature_name}' not found in rules.")

    feature_data = FEATURE_STATS_MAP[feature_name]
    return FeatureStatsResponse(
        name=feature_data["name"],
        mods=feature_data["mods"]
    )

def get_skills_by_category() -> Dict[str, List[str]]:
    """
    Returns a dictionary of all skills, grouped by their 6 categories.
    This is used by the Character Engine for the 6x2 background rule.
    """
    return SKILL_CATEGORIES

def find_eligible_talents(stats_in: Dict[str, int], skills_in: Dict[str, int]) -> List[TalentInfo]:
    """
    Finds all unlocked talents based on a character's stats and skills.
    """
    unlocked_talents = []

    # --- 1. Check Single Stat Mastery ---
    for talent_group in TALENT_DATA.get("singleStatMastery", []):
        stat_name = talent_group.get("stat")

        # *** DATA CORRECTION: Fix "Constitution" to "Vitality" ***
        if stat_name == "Constitution":
            stat_name = "Vitality"

        current_stat_score = stats_in.get(stat_name, 0)

        for milestone in talent_group.get("milestones", []):
            if current_stat_score >= milestone.get("score", 99):
                unlocked_talents.append(TalentInfo(
                    name=milestone["name"],
                    source=f"Stat: {stat_name} {milestone['score']}",
                    effect=milestone["effect"]
                ))

    # --- 2. Check Dual Stat Synergy ---
    for talent in TALENT_DATA.get("dualStatSynergy", []):
        req_score = talent.get("score", 99) # talent.json uses "value", not "score"
        stats_pair = talent.get("pairedStats", [])

        if len(stats_pair) == 2:
            stat1, stat2 = stats_pair

            # *** DATA CORRECTION ***
            if stat1 == "Constitution": stat1 = "Vitality"
            if stat2 == "Constitution": stat2 = "Vitality"

            if stats_in.get(stat1, 0) >= req_score and stats_in.get(stat2, 0) >= req_score:
                unlocked_talents.append(TalentInfo(
                    name=talent["name"],
                    source=f"Dual Stat: {stat1} & {stat2} {req_score}",
                    effect=talent["effect"]
                ))

    # --- 3. Check Skill Mastery ---
    # Loop through each skill category (armor, melee, etc.)
    for category_list in TALENT_DATA.get("skillMastery", {}).values():
        for skill_group in category_list:
            skill_name = skill_group.get("skill")
            current_skill_rank = skills_in.get(skill_name, 0)

            for talent in skill_group.get("talents", []):
                tier_name = talent.get("tier") # "MT3", "MT5", "MT7"
                req_rank = int(tier_name.replace("MT", "")) # Convert "MT3" to 3

                if current_skill_rank >= req_rank:
                    unlocked_talents.append(TalentInfo(
                        name=talent["name"],
                        source=f"Skill: {skill_name} ({tier_name})",
                        effect=talent["effect"]
                    ))

    return unlocked_talents
