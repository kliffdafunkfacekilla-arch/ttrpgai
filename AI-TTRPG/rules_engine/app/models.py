from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional


# Game Data Models
# Ability Schools
class AbilityTier(BaseModel):
    tier: str
    description: str


class AbilityBranch(BaseModel):
    branch: str
    tiers: List[AbilityTier]


class AbilitySchool(BaseModel):
    school: str
    resource: str
    branches: List[AbilityBranch]


# Skills
class CombatSkill(BaseModel):
    stat: str
    armor_skill: str
    melee_skill: str
    ranged_skill: str


class NonCombatSkill(BaseModel):
    stat: str
    conversational_skill: str
    utility_skill: str
    lore_skill: str


class UrbanArchetype(BaseModel):
    stat: str
    urban_archetype: str
    conversational_skill: str
    utility_skill: str
    lore: str


# Crafting
class CraftingDiscipline(BaseModel):
    name: str
    description: str


# Character Creation
class DevotionChoice(BaseModel):
    category: str
    choice_num: int
    name: str
    description: str
    skill_1: str
    skill_2: str


class BirthCircumstance(BaseModel):
    choice_num: int
    skill: str
    name: str
    description: str


class ChildhoodDevelopment(BaseModel):
    choice_num: int
    skill: str
    name: str
    description: str


class ComingOfAgeEvent(BaseModel):
    choice_num: int
    skill: str
    name: str
    description: str


class CharacterCreation(BaseModel):
    devotion: List[DevotionChoice]
    birth_circumstance: List[BirthCircumstance]
    childhood_development: List[ChildhoodDevelopment]
    coming_of_age: List[ComingOfAgeEvent]


# Talents
class SingleStatTalent(BaseModel):
    stat: str
    talent_name: str
    effect: str
    associated_resource_pool: Optional[str] = None


class SingleSkillTalent(BaseModel):
    armor_skill: Optional[str] = None
    skill: Optional[str] = None
    stat_focus: str
    talent_name: str
    prerequisite_mt: str
    focus: str
    effect: str


class DualStatTalent(BaseModel):
    paired_stat: str
    synergy_focus: str
    tier: str
    talent_name: str
    effect: str


class Talents(BaseModel):
    single_stat_mastery: List[SingleStatTalent]
    single_skill_mastery: List[SingleSkillTalent]
    dual_stat_focus: List[DualStatTalent]


class Stat(BaseModel):
    name: str
    description: str


# --- API Request Models ---


class SkillCheckRequest(BaseModel):
    stat_modifier: int
    skill_rank: int
    dc: int = Field(default=15, description="Difficulty Class")


class AbilityCheckRequest(BaseModel):
    ability_school_rank: int
    associated_stat_modifier: int
    ability_tier: int = Field(gt=0, le=10, description="Tier 1-10")


class TalentLookupRequest(BaseModel):
    stats: Dict[str, int] = Field(
        description="Dictionary of all 12 stats and their scores"
    )
    skills: Dict[str, int] = Field(
        description="Dictionary of all 72 skills and their ranks"
    )


# --- API Response Models ---


class RollResult(BaseModel):
    roll_value: int
    total_value: int
    dc: int
    is_success: bool
    is_critical_success: bool = False
    is_critical_failure: bool = False
    sre_triggered: bool = False


class TalentInfo(BaseModel):
    name: str
    source: str
    effect: str


class FeatureStatsResponse(BaseModel):
    name: str
    mods: Dict[str, List[str]]


# --- ADD THIS MODEL ---
class BackgroundChoice(BaseModel):
    name: str
    description: str
    skills: List[str]


# --- END ADD ---


class SkillCategoryResponse(BaseModel):
    categories: Dict[str, List[str]]


class AbilitySchoolResponse(BaseModel):
    school: str
    resource_pool: str
    associated_stat: str
    tiers: List[Dict]  # Using Dict for tiers now (matching abilities.json structure)


# ADD THESE MODELS for Initiative
class InitiativeRequest(BaseModel):
    """
    Input required for rolling initiative. Requires the 6 relevant attribute scores.
    Rule: d20 + B Mod + D Mod + F Mod + H Mod + J Mod + L Mod
    """

    endurance: int = Field(..., description="Attribute B Score")
    reflexes: int = Field(..., description="Attribute D Score") # CHANGED from agility
    fortitude: int = Field(..., description="Attribute F Score")
    logic: int = Field(..., description="Attribute H Score")
    intuition: int = Field(..., description="Attribute J Score")
    willpower: int = Field(..., description="Attribute L Score")


class InitiativeResponse(BaseModel):
    """
    Output after rolling initiative.
    """

    roll_value: int = Field(description="The result of the d20 roll.")
    modifier_details: Dict[str, int] = Field(description="Breakdown of modifiers used.")
    total_initiative: int = Field(
        description="The final initiative score (roll + modifiers)."
    )


# ADD THESE MODELS for Contested Attack
class ContestedAttackRequest(BaseModel):
    """Input required for a contested attack roll, using specific aggregated modifiers."""

    # Attacker Info
    attacker_attacking_stat_score: int = Field(...)
    attacker_skill_rank: int = Field(...)
    # --- MODIFIED: Specific Bonuses/Penalties ---
    attacker_attack_roll_bonus: int = Field(
        default=0,
        description="Sum of bonuses DIRECTLY affecting the attacker's d20 roll (e.g., from Steady Aim, Bless).",
    )
    attacker_attack_roll_penalty: int = Field(
        default=0,
        description="Sum of penalties DIRECTLY affecting the attacker's d20 roll (e.g., from Shaken, Blinded).",
    )
    # --- END MODIFIED ---

    # Defender Info
    defender_armor_stat_score: int = Field(...)
    defender_armor_skill_rank: int = Field(...)
    defender_weapon_penalty: int = Field(
        default=0, description="Base penalty from the attacker's weapon category."
    )
    # --- MODIFIED: Specific Bonuses/Penalties ---
    defender_defense_roll_bonus: int = Field(
        default=0,
        description="Sum of bonuses DIRECTLY affecting the defender's d20 roll (e.g., from Cover, Heavy Cloaks vs Ranged).",
    )
    defender_defense_roll_penalty: int = Field(
        default=0,
        description="Sum of penalties DIRECTLY affecting the defender's d20 roll (e.g., from Prone vs Melee, injuries).",
    )
    # --- END MODIFIED ---

    # Removed target_hit_location, attacker_steady_aim_active, is_ranged_attack
    # The effects of these are now expected to be included in the bonus/penalty fields by the caller (story_engine)
    @validator("defender_weapon_penalty")
    def validate_weapon_penalty(cls, v):
        if v > 0:
            raise ValueError("defender_weapon_penalty should not be positive.")
        return v


class ContestedAttackResponse(BaseModel):
    """
    Output of the contested attack roll.
    """

    attacker_roll: int = Field(description="The raw d20 roll for the attacker.")
    attacker_stat_mod: int = Field(
        description="Attacker's relevant attribute modifier."
    )
    attacker_skill_bonus: int = Field(description="Attacker's bonus from skill rank.")
    attacker_total_modifier: int = Field(
        description="Sum of attacker's stat mod, skill bonus, and misc mods/penalties."
    )
    attacker_final_total: int = Field(
        description="Attacker's final roll result (d20 + total modifier)."
    )

    defender_roll: int = Field(description="The raw d20 roll for the defender.")
    defender_stat_mod: int = Field(
        description="Defender's relevant attribute modifier from armor stat."
    )
    defender_skill_bonus: int = Field(
        description="Defender's bonus from armor skill rank."
    )
    defender_total_modifier: int = Field(
        description="Sum of defender's stat mod, skill bonus, misc mods/penalties, minus attacker's weapon penalty."
    )
    defender_final_total: int = Field(
        description="Defender's final roll result (d20 + total modifier)."
    )

    outcome: str = Field(
        description="Result of the contest: 'critical_hit', 'solid_hit', 'hit', 'miss', 'critical_fumble'."
    )
    margin: int = Field(description="Attacker's Final Total - Defender's Final Total.")


def _core_parse_dice_string(dice_str: str) -> (int, int):
    """Helper for model validation. Parses a dice string like '2d6' into (number_of_dice, dice_sides)."""
    if dice_str == "0":
        return 0, 0
    if "d" not in dice_str:
        raise ValueError(f"Invalid dice string format: '{dice_str}'")
    parts = dice_str.lower().split("d")
    if len(parts) != 2 or not parts[0].isdigit() or not parts[1].isdigit():
        raise ValueError(f"Invalid dice string format: '{dice_str}'")
    return int(parts[0]), int(parts[1])


# ADD THESE MODELS for Damage Calculation
class DamageRequest(BaseModel):
    """Input required for calculating damage, using specific aggregated modifiers."""

    # Attacker Info
    base_damage_dice: str = Field(...)
    relevant_stat_score: int = Field(...)
    # --- MODIFIED: Specific Bonuses/Penalties ---
    attacker_damage_bonus: int = Field(
        default=0,
        description="Sum of flat damage bonuses (talents, abilities, weapon properties NOT included in dice).",
    )
    attacker_damage_penalty: int = Field(
        default=0, description="Sum of flat damage penalties."
    )
    attacker_dr_modifier: int = Field(
        default=0,
        description="Value to subtract from target's DR (e.g., 1 for Great Weapons/Heavy Artillery). Should be positive.",
    )
    # --- END MODIFIED ---

    # Defender Info
    defender_base_dr: int = Field(
        default=0, description="Target's base Damage Reduction from armor."
    )

    # Future: Add 'defender_resistance_multiplier', 'damage_type'
    @validator("base_damage_dice")
    def validate_dice_string(cls, v):
        try:
            _core_parse_dice_string(v)  # Use local helper
        except ValueError as e:
            raise ValueError(str(e))
        return v

    @validator("defender_base_dr", "attacker_dr_modifier")
    def validate_non_negative(cls, v):
        if v < 0:
            raise ValueError("DR values cannot be negative.")
        return v


class DamageResponse(BaseModel):
    """
    Output of the damage calculation.
    """

    damage_roll_details: List[int] = Field(
        description="The result of each damage die roll."
    )
    base_roll_total: int = Field(
        description="The result of rolling the base damage dice."
    )
    stat_bonus: int = Field(description="The modifier from the damage stat score.")
    misc_bonus: int = Field(description="The net bonus from talents, abilities, etc.")
    subtotal_damage: int = Field(
        description="Damage before reduction (roll + stat mod + bonus)."
    )
    damage_reduction_applied: int = Field(
        description="How much of the target's DR was applied."
    )
    final_damage: int = Field(
        description="The final damage dealt to the target's HP (cannot be negative)."
    )


class InjuryLookupRequest(BaseModel):
    """Input for looking up an injury's effects."""

    location: str = Field(
        ..., description="Major body location (e.g., 'Head', 'Torso')."
    )
    sub_location: str = Field(
        ..., description="Specific part of the location (e.g., 'Skull', 'Chest')."
    )
    severity: int = Field(
        ..., ge=1, le=5, description="Severity of the injury from 1 to 5."
    )


class InjuryEffectResponse(BaseModel):
    """The mechanical effects of a specific injury."""

    severity_name: str = Field(
        description="The descriptive name of the injury severity (e.g., 'Wound')."
    )
    effects: List[str] = Field(description="A list of machine-readable effect strings.")


# ADD THIS MODEL for Status Effects
class StatusEffectResponse(BaseModel):
    """Output describing the definition of a status effect, based on status_effects.json."""

    # --- Adjust these fields based on your status_effects.json ---
    name: str
    description: str
    effects: List[str] = Field(description="List of machine-readable effect strings.")
    type: str = Field(description="e.g., 'detrimental', 'beneficial'")
    duration_type: str = Field(
        description="How duration is tracked ('turns', 'condition', 'encounter')."
    )
    default_duration: Optional[int] = Field(
        None, description="Default duration in turns, if applicable."
    )
    # Add any other fields that exist in your JSON structure (e.g., "icon_ref", "severity_scaling")
    # --- End adjustments ---

    class Config:
        from_attributes = True  # Use this for Pydantic V2+
        # orm_mode = True # Use this for Pydantic V1


# ADD THESE MODELS for Base Vitals Calculation
class BaseVitalsRequest(BaseModel):
    """
    Input required for calculating base HP and Resources.
    Requires all 12 stat scores.
    """

    stats: Dict[str, int] = Field(
        ..., description="Dictionary of all 12 stats and their scores"
    )

    @validator("stats")
    def validate_stats(cls, v):
        if len(v) < 12:
            raise ValueError("Must provide all 12 stats.")
        # Add checks for specific stats if needed
        if "Vitality" not in v or "Endurance" not in v:
            raise ValueError("Stats dictionary missing required Vitality or Endurance.")
        return v


class BaseVitalsResponse(BaseModel):
    """
    Output of the base vitals calculation.
    """

    max_hp: int
    resources: Dict[str, Dict[str, int]] = Field(
        description="Dictionary of all 6 resource pools with current/max values."
    )

# --- ADDED NPC GENERATION MODELS (Consolidated from npc_generator) ---
class NpcGenerationRequest(BaseModel):
    """
    Inputs from the Story Engine to generate an NPC template.
    """
    biome: Optional[str] = None
    kingdom: str = "mammal"
    offense_style: str
    defense_style: str
    ability_focus: Optional[str] = None
    behavior: str = "aggressive"
    difficulty: str = "medium"
    custom_name: Optional[str] = None

class NpcTemplateResponse(BaseModel):
    """
    The generated NPC template/stat block returned to the Story Engine.
    """
    generated_id: str
    name: str
    description: str
    stats: Dict[str, int]
    skills: Dict[str, int]
    abilities: List[str]
    max_hp: int
    behavior_tags: List[str]
    loot_table_ref: Optional[str] = None
