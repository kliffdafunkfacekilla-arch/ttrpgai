# core.py
import random
import math
from typing import Dict, List, Optional, Any
# Use relative import for models within the same package
from . import models
from .data_loader import INJURY_EFFECTS, STATUS_EFFECTS
from .models import RollResult, TalentInfo, FeatureStatsResponse


# ADD THIS FUNCTION
def calculate_modifier(score: int) -> int:
    """Calculates the attribute modifier from a score based on floor((Score - 10) / 2)."""
    if not isinstance(score, int):
        # Basic type check for safety
        print(f"Warning: calculate_modifier received non-integer score: {score}. Using 10.")
        score = 10
    return math.floor((score - 10) / 2)


# ADD THIS FUNCTION
def calculate_skill_mt_bonus(rank: int) -> int:
    """
    Calculates Skill Mastery Tier bonus from rank.
    Assumption: Bonus = floor(Rank / 3).
    Rank 0-2 = +0, Rank 3-5 = +1, Rank 6-8 = +2, etc.
    """
    if not isinstance(rank, int) or rank < 0:
        print(f"Warning: calculate_skill_mt_bonus received invalid rank: {rank}. Using 0.")
        rank = 0
    return math.floor(rank / 3)

# --- Dice Rolling ---

def _roll_d20() -> int:
    return random.randint(1, 20)

def _roll_d6() -> int:
    return random.randint(1, 6)

def parse_dice_string(dice_str: str) -> (int, int):
    """Parses a dice string like '2d6' into (number_of_dice, dice_sides). Handles '0' for no roll."""
    if dice_str == "0":
        return 0, 0
    if 'd' not in dice_str:
        raise ValueError(f"Invalid dice string format: '{dice_str}'")

    parts = dice_str.lower().split('d')
    if len(parts) != 2 or not parts[0].isdigit() or not parts[1].isdigit():
        raise ValueError(f"Invalid dice string format: '{dice_str}'")

    return int(parts[0]), int(parts[1])

def _roll_dice(num_dice: int, sides: int) -> int:
    """Rolls a specified number of dice with a given number of sides."""
    if num_dice == 0:
        return 0
    return sum(random.randint(1, sides) for _ in range(num_dice))

def calculate_contested_attack(attack_data: models.ContestedAttackRequest) -> models.ContestedAttackResponse:
    """
    Performs a contested d20 attack roll based on Fulcrum rules.
    Determines Hit, Solid Hit, Critical Hit, Miss, or Fumble.
    """
    attacker_roll = _roll_d20()
    defender_roll = _roll_d20()

    # Calculate Attacker Modifiers and Total
    attacker_stat_mod = calculate_modifier(attack_data.attacker_attacking_stat_score)
    attacker_skill_bonus = calculate_skill_mt_bonus(attack_data.attacker_skill_rank)
    attacker_total_modifier = (
        attacker_stat_mod
        + attacker_skill_bonus
        + attack_data.attacker_misc_bonus
        - attack_data.attacker_misc_penalty
    )
    attacker_final_total = attacker_roll + attacker_total_modifier

    # Calculate Defender Modifiers and Total
    defender_stat_mod = calculate_modifier(attack_data.defender_armor_stat_score)
    defender_skill_bonus = calculate_skill_mt_bonus(attack_data.defender_armor_skill_rank)
    # Note: defender_weapon_penalty is subtracted (making it typically add to the defender's effective total if negative)
    defender_total_modifier = (
        defender_stat_mod
        + defender_skill_bonus
        - attack_data.defender_weapon_penalty # Subtracting the (usually negative) penalty
        + attack_data.defender_misc_bonus
        - attack_data.defender_misc_penalty
    )
    defender_final_total = defender_roll + defender_total_modifier

    margin = attacker_final_total - defender_final_total
    outcome = "miss" # Default outcome

    # Determine outcome based on rules
    if attacker_roll == 1:
        outcome = "critical_fumble"
    elif attacker_roll == 20:
        outcome = "critical_hit" # Nat 20 always crits (implies hit)
        # We can set a high margin for clarity on crits if desired, or leave as calculated
        # margin = 20 # Optional override for crit margin display
    elif margin >= 5:
        outcome = "solid_hit"
    elif margin >= 0: # Attacker Total >= Defender Total (Margin 0 to 4)
        outcome = "hit"
    # If margin < 0, outcome remains "miss"

    return models.ContestedAttackResponse(
        attacker_roll=attacker_roll,
        attacker_stat_mod=attacker_stat_mod,
        attacker_skill_bonus=attacker_skill_bonus,
        attacker_total_modifier=attacker_total_modifier,
        attacker_final_total=attacker_final_total,
        defender_roll=defender_roll,
        defender_stat_mod=defender_stat_mod,
        defender_skill_bonus=defender_skill_bonus,
        defender_total_modifier=defender_total_modifier,
        defender_final_total=defender_final_total,
        outcome=outcome,
        margin=margin
    )

# ADD THIS FUNCTION
def calculate_damage(damage_data: models.DamageRequest) -> models.DamageResponse:
    """
    Calculates final damage after rolling dice, adding mods, and applying DR.
    """
    # 1. Roll Base Damage
    num_dice, sides = parse_dice_string(damage_data.base_damage_roll)
    base_roll = _roll_dice(num_dice, sides)

    # 2. Calculate Stat Modifier
    stat_mod = calculate_modifier(damage_data.damage_stat_score)

    # 3. Calculate Subtotal
    subtotal = base_roll + stat_mod + damage_data.misc_damage_bonus

    # 4. Apply Damage Reduction
    dr_applied = min(subtotal, damage_data.target_damage_reduction)

    # 5. Calculate Final Damage (cannot be negative)
    final_damage = max(0, subtotal - damage_data.target_damage_reduction)

    return models.DamageResponse(
        base_roll_total=base_roll,
        stat_modifier=stat_mod,
        subtotal_damage=subtotal,
        damage_reduction_applied=dr_applied,
        final_damage=final_damage
    )

def calculate_initiative(stats: models.InitiativeRequest) -> models.InitiativeResponse:
    """
    Calculates initiative based on the Fulcrum rules:
    d20 + B Mod + D Mod + F Mod + H Mod + J Mod + L Mod
    """
    roll = _roll_d20()

    # Calculate modifiers using the helper function
    mod_b = calculate_modifier(stats.endurance)
    mod_d = calculate_modifier(stats.agility)
    mod_f = calculate_modifier(stats.fortitude)
    mod_h = calculate_modifier(stats.logic)
    mod_j = calculate_modifier(stats.intuition)
    mod_l = calculate_modifier(stats.willpower)

    modifier_details = {
        "Endurance (B) Mod": mod_b,
        "Agility (D) Mod": mod_d,
        "Fortitude (F) Mod": mod_f,
        "Logic (H) Mod": mod_h,
        "Intuition (J) Mod": mod_j,
        "Willpower (L) Mod": mod_l,
    }

    total_modifier = sum(modifier_details.values())
    total_initiative = roll + total_modifier

    return models.InitiativeResponse(
        roll_value=roll,
        modifier_details=modifier_details,
        total_initiative=total_initiative
    )

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


def get_status_effect(status_name: str) -> models.StatusEffectResponse:
    """Looks up the definition and effects for a specific status by name."""

    # Find the status definition (case-insensitive keys if needed)
    status_data = None
    for key, value in STATUS_EFFECTS.items():
         if key.lower() == status_name.lower():
              status_data = value
              break # Found match

    if not status_data:
        raise ValueError(f"Status effect '{status_name}' not found in rules data.")

    # Construct the response model from the loaded dictionary
    return models.StatusEffectResponse(
        name=status_data.get("name", status_name), # Use provided name or key
        description=status_data.get("description", "No description available."),
        effects=status_data.get("effects", []),
        type=status_data.get("type", "unknown"),
        duration_type=status_data.get("duration_type", "condition"),
        default_duration=status_data.get("default_duration") # Will be None if not present
    )

def get_injury_effects(request: models.InjuryLookupRequest) -> models.InjuryEffectResponse:
    """Looks up injury effects from the loaded injury data."""
    location_data = INJURY_EFFECTS.get(request.location)
    if not location_data:
        raise ValueError(f"Invalid injury location: '{request.location}'")

    sub_location_data = location_data.get(request.sub_location)
    if not sub_location_data:
        raise ValueError(f"Invalid sub-location '{request.sub_location}' for location '{request.location}'")

    severity_data = sub_location_data.get(str(request.severity))
    if not severity_data:
        # This case should ideally not be hit if request model validation is working (ge=1, le=5)
        raise ValueError(f"Invalid severity '{request.severity}' for injury at '{request.location} - {request.sub_location}'")

    return models.InjuryEffectResponse(
        severity_name=severity_data.get("name", "Unknown"),
        effects=severity_data.get("effects", [])
    )

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