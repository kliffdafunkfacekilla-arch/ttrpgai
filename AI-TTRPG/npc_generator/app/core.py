import random
import httpx # Ensure this is imported
import asyncio # Add asyncio for running async function
from fastapi import HTTPException # Add for error handling
from . import models
from .data_loader import GENERATION_RULES

# --- Configuration (Add this) ---
RULES_ENGINE_URL = "http://127.0.0.1:8000" # URL of your running Rules Engine

# --- Helper to get all skills ---
async def get_all_skill_names_from_rules() -> list[str]:
    """Fetches the master skill list from the Rules Engine."""
    url = f"{RULES_ENGINE_URL}/v1/lookup/all_skills"
    try:
        async with httpx.AsyncClient() as client:
            print(f"NPC Generator: Fetching skill list from {url}") # Add print statement
            response = await client.get(url)
            response.raise_for_status()
            # The endpoint returns a dict {skill: {details}}, we need the keys
            skills_dict = response.json()
            skill_names = list(skills_dict.keys())
            print(f"NPC Generator: Successfully fetched {len(skill_names)} skills.") # Add print statement
            return skill_names
    except httpx.RequestError as e:
        print(f"ERROR: NPC Generator could not connect to Rules Engine at {url}: {e}")
        raise HTTPException(status_code=503, detail=f"Rules Engine service unavailable: {e}")
    except httpx.HTTPStatusError as e:
        print(f"ERROR: Rules Engine returned error {e.response.status_code} fetching skills: {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=f"Rules Engine error fetching skills: {e.response.text}")
    except Exception as e:
        print(f"ERROR: Unexpected error fetching skill list from rules_engine: {e}")
        # Fallback to a basic list if rules_engine is unavailable? Or raise error?
        # Raising error is safer to indicate dependency failure.
        raise HTTPException(status_code=500, detail=f"Unexpected error fetching skills: {e}")

# --- Modify generate_npc_template ---
# Make the main function synchronous for FastAPI, but call the async helper inside
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
    try:
        # Run the async function to get skill names
        all_skill_names = asyncio.run(get_all_skill_names_from_rules())
    except HTTPException as e:
        # If fetching fails, we cannot proceed reliably
        print(f"FATAL: Failed to get skill list during NPC generation: {e.detail}")
        # Re-raise or handle differently? For now, re-raise to signal failure.
        raise HTTPException(status_code=e.status_code, detail=f"Dependency Error: {e.detail}")

    # Initialize all fetched skills to rank 0
    for skill_name in all_skill_names:
        skills[skill_name] = 0

    # Get relevant skills based on styles and difficulty (logic remains the same)
    skill_rules = GENERATION_RULES.get("skills_by_style_and_difficulty", {})
    offense_skills_for_diff = skill_rules.get("offense", {}).get(request.offense_style.lower(), {}).get(request.difficulty.lower(), [])
    defense_skills_for_diff = skill_rules.get("defense", {}).get(request.defense_style.lower(), {}).get(request.difficulty.lower(), [])
    skill_rank_value = skill_rules.get("skill_ranks", {}).get(request.difficulty.lower(), 1)
    skills_to_rank = set(offense_skills_for_diff + defense_skills_for_diff)

    # Assign ranks
    for skill_name in skills_to_rank:
        if skill_name in skills:
            skills[skill_name] = skill_rank_value
        else:
            # This warning is now more important, as the list comes from rules_engine
            print(f"Warning: Skill '{skill_name}' defined in NPC rules but not found in list from rules_engine.")

    # --- (ID, Name, Description, Behavior Tags logic remains the same) ---
    # ...

    # --- 8. Build Response ---
    # ... (remains the same) ...
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
