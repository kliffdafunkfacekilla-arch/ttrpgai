import random
import httpx # Import httpx
from . import models
from .data_loader import GENERATION_RULES

# --- Configuration (Add this) ---
# RULES_ENGINE_URL = "http://127.0.0.1:8000" # URL of your running Rules Engine

# --- Helper to get all skills (Placeholder - Ideally fetch from rules_engine) ---
# async def get_all_skill_names_from_rules() -> list[str]:
#     """(Placeholder) Fetches the master skill list from the Rules Engine."""
#     # url = f"{RULES_ENGINE_URL}/v1/lookup/all_skills"
#     # try:
#     #     async with httpx.AsyncClient() as client:
#     #         response = await client.get(url)
#     #         response.raise_for_status()
#     #         return list(response.json().keys())
#     # except Exception as e:
#     #     print(f"ERROR: Could not fetch skill list from rules_engine: {e}")
#     #     # Fallback to a basic list if rules_engine is unavailable
#     #     return ["Strength", "Survival", "Athletics", "Intimidation", "Bows", "Awareness", "Plate", "Resilience"] # Example fallback
#     # --- Simplified Placeholder ---
#     print("Warning: Using placeholder skill list in npc_generator.")
#     # Return a representative list based on stats_and_skills.json
#     # Ideally, this list should exactly match the one in rules_engine
#     return [
#         "Intimidation", "Resilience", "Slight of Hand", "Evasion", "Comfort", "Discipline",
#         "Debate", "Rhetoric", "Insight", "Empathy", "Persuasion", "Negotiations",
#         "Strength", "Survival", "Artifice", "Athletics", "Provisioning", "Resourcefulness",
#         "Navigation", "Pathfinding", "Security", "Nature Sense", "Communication", "Expedition",
#         "Lore: Tribal & Outlaw", "Lore: Common Folk", "Lore: Outlaw/Criminal", "Lore: Travel & Routes",
#         "Lore: Agricul. & Wilds", "Lore: Miners & Geology", "Lore: Science & Acad.", "Lore: Trades & Eng.",
#         "Lore: Merchant/Trade", "Lore: Religion & Spirit", "Lore: Nobility/Court", "Lore: Royalty/Political",
#         "Band/Scale/Ringmail", "Plate", "Camouflage", "Clothing/Utility", "Wood and Stone",
#         "None (Just Clothing)", "Robes/Cloaks", "Chainmail", "Leather/Hides", "Tribal/Spirit",
#         "Ornate/Showy", "Reinforced",
#         "Heavy Bludgeons", "Shields & Polearms", "Dueling Blades", "Dual Knives", "Staves & Rods",
#         "Unarmed & Fist Weapons", "Tech Blades", "Defensive/Chemical Weapons", "Hooks & Axes", "Swinging Weapons",
#         "Whips & Scepters", "Two-Handed Cleavers",
#         "Heavy Crossbows", "Flame-Based", "Hand Crossbows/Darts", "Throwing Knives", "Alchemic Grenades",
#         "Flying Strikes", "Thrown Spears", "Nets & Bolas", "Bows", "Boomerangs & Chakrams",
#         "Muskets", "Siege Weapons"
#     ]

def generate_npc_template(
    request: models.NpcGenerationRequest) -> models.NpcTemplateResponse:
    """
    Core logic to generate an NPC template based on request parameters.
    """

    # --- 1. Determine Base Stats ---
    base_stats = GENERATION_RULES.get("base_stats_by_kingdom", {}).get(
        request.kingdom.lower(),
        GENERATION_RULES.get("base_stats_by_kingdom", {}).get("mammal") # Fallback
    ).copy() # Use .copy() to avoid modifying the original dict

    # --- 2. Apply Style Modifiers ---
    final_stats = base_stats
    offense_mods = GENERATION_RULES.get("stat_modifiers_by_style", {}).get("offense", {}).get(request.offense_style.lower(), {})
    defense_mods = GENERATION_RULES.get("stat_modifiers_by_style", {}).get("defense", {}).get(request.defense_style.lower(), {})

    all_mods = {**offense_mods, **defense_mods} # Combine mods

    for stat, mod_str in all_mods.items():
        if stat in final_stats:
            try:
                modifier = int(mod_str.replace('+', '')) # Handle '+' sign
                final_stats[stat] += modifier
                # Ensure stats don't go below a minimum (e.g., 1)
                final_stats[stat] = max(1, final_stats[stat])
            except ValueError:
                print(f"Warning: Invalid modifier format '{mod_str}' for stat '{stat}'")

    # --- 3. Calculate HP ---
    base_hp = final_stats.get("Endurance", 10) + final_stats.get("Vitality", 10) * 2
    hp_multiplier = GENERATION_RULES.get("hp_scaling_by_difficulty", {}).get(request.difficulty.lower(), 1.0)
    max_hp = int(base_hp * hp_multiplier)

    # --- 4. Determine Abilities (Simplified - Unchanged) ---
    abilities = []
    if request.ability_focus and request.ability_focus in GENERATION_RULES.get("ability_suggestions", {}):
        suggested = GENERATION_RULES["ability_suggestions"][request.ability_focus]
        if suggested:
            abilities.append(suggested[0]) # Just grab the first one

    # --- 5. Determine Skills (NEW LOGIC) ---
    skills = {}
    # Initialize all known skills to rank 0 (using placeholder list for now)
    # In a future step, replace get_all_skill_names_from_rules() with an actual async call
    all_skill_names = await get_all_skill_names_from_rules() # If using async call
    # all_skill_names = [ # Using placeholder list directly for now
    #     "Intimidation", "Resilience", "Slight of Hand", "Evasion", "Comfort", "Discipline",
    #     "Debate", "Rhetoric", "Insight", "Empathy", "Persuasion", "Negotiations",
    #     "Strength", "Survival", "Artifice", "Athletics", "Provisioning", "Resourcefulness",
    #     "Navigation", "Pathfinding", "Security", "Nature Sense", "Communication", "Expedition",
    #     "Lore: Tribal & Outlaw", "Lore: Common Folk", "Lore: Outlaw/Criminal", "Lore: Travel & Routes",
    #     "Lore: Agricul. & Wilds", "Lore: Miners & Geology", "Lore: Science & Acad.", "Lore: Trades & Eng.",
    #     "Lore: Merchant/Trade", "Lore: Religion & Spirit", "Lore: Nobility/Court", "Lore: Royalty/Political",
    #     "Band/Scale/Ringmail", "Plate", "Camouflage", "Clothing/Utility", "Wood and Stone",
    #     "None (Just Clothing)", "Robes/Cloaks", "Chainmail", "Leather/Hides", "Tribal/Spirit",
    #     "Ornate/Showy", "Reinforced",
    #     "Heavy Bludgeons", "Shields & Polearms", "Dueling Blades", "Dual Knives", "Staves & Rods",
    #     "Unarmed & Fist Weapons", "Tech Blades", "Defensive/Chemical Weapons", "Hooks & Axes", "Swinging Weapons",
    #     "Whips & Scepters", "Two-Handed Cleavers",
    #     "Heavy Crossbows", "Flame-Based", "Hand Crossbows/Darts", "Throwing Knives", "Alchemic Grenades",
    #     "Flying Strikes", "Thrown Spears", "Nets & Bolas", "Bows", "Boomerangs & Chakrams",
    #     "Muskets", "Siege Weapons"
    # ]
    for skill_name in all_skill_names:
        skills[skill_name] = 0 # Initialize all skills to rank 0

    # Get relevant skills based on styles and difficulty
    skill_rules = GENERATION_RULES.get("skills_by_style_and_difficulty", {})
    offense_skills_for_diff = skill_rules.get("offense", {}).get(request.offense_style.lower(), {}).get(request.difficulty.lower(), [])
    defense_skills_for_diff = skill_rules.get("defense", {}).get(request.defense_style.lower(), {}).get(request.difficulty.lower(), [])

    # Get the rank value for this difficulty
    skill_rank_value = skill_rules.get("skill_ranks", {}).get(request.difficulty.lower(), 1) # Default rank 1

    # Assign ranks
    skills_to_rank = set(offense_skills_for_diff + defense_skills_for_diff)
    for skill_name in skills_to_rank:
        if skill_name in skills:
            skills[skill_name] = skill_rank_value
        else:
             print(f"Warning: Skill '{skill_name}' defined in rules but not in master list.")

    # --- 6. Generate ID, Name, Description (Unchanged) ---
    generated_id = f"procgen_{request.biome or 'unk'}_{request.kingdom}_{request.offense_style}_{request.difficulty}_{random.randint(100,999)}"
    name = request.custom_name or f"{request.difficulty.capitalize()} {request.kingdom.capitalize()} {request.offense_style.replace('_',' ').title()}"
    description = f"A {request.difficulty} {request.kingdom} exhibiting a {request.offense_style} style and {request.defense_style} defense."
    if request.biome:
        description += f" Adapted to the {request.biome}."

    # --- 7. Get Behavior Tags (Unchanged) ---
    behavior_tags = GENERATION_RULES.get("behavior_map",{}).get(request.behavior.lower(), [])

    # --- 8. Build Response ---
    return models.NpcTemplateResponse(
        generated_id=generated_id,
        name=name,
        description=description,
        stats=final_stats,
        skills=skills, # Now includes ranked skills
        abilities=abilities,
        max_hp=max_hp,
        behavior_tags=behavior_tags,
        loot_table_ref=f"{request.kingdom}_{request.difficulty}_loot" # Example loot ref
    )
