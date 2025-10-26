import random
from . import models
from .data_loader import GENERATION_RULES

def generate_npc_template(
    request: models.NpcGenerationRequest
) -> models.NpcTemplateResponse:
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
                modifier = int(mod_str)
                final_stats[stat] += modifier
                # Ensure stats don't go below a minimum (e.g., 1)
                final_stats[stat] = max(1, final_stats[stat])
            except ValueError:
                print(f"Warning: Invalid modifier format '{mod_str}' for stat '{stat}'")

    # --- 3. Calculate HP ---
    # Simplified HP calculation (e.g., based on Endurance + Vitality)
    base_hp = final_stats.get("Endurance", 10) + final_stats.get("Vitality", 10) * 2
    hp_multiplier = GENERATION_RULES.get("hp_scaling_by_difficulty", {}).get(request.difficulty.lower(), 1.0)
    max_hp = int(base_hp * hp_multiplier)

    # --- 4. Determine Abilities (Simplified) ---
    abilities = []
    if request.ability_focus and request.ability_focus in GENERATION_RULES.get("ability_suggestions", {}):
        # Just grab the first suggested ability for now
        suggested = GENERATION_RULES["ability_suggestions"][request.ability_focus]
        if suggested:
            abilities.append(suggested[0])

    # --- 5. Determine Skills (Placeholder) ---
    # This would need more complex rules, potentially based on stats and style
    skills = {"Survival": 1}

    # --- 6. Generate ID, Name, Description ---
    generated_id = f"procgen_{request.biome or 'unk'}_{request.kingdom}_{request.offense_style}_{request.difficulty}_{random.randint(100,999)}"
    name = request.custom_name or f"{request.difficulty.capitalize()} {request.kingdom.capitalize()} {request.offense_style.replace('_',' ').title()}"
    description = f"A {request.difficulty} {request.kingdom} exhibiting a {request.offense_style} style and {request.defense_style} defense."
    if request.biome:
        description += f" Adapted to the {request.biome}."

    # --- 7. Get Behavior Tags ---
    behavior_tags = GENERATION_RULES.get("behavior_map",{}).get(request.behavior.lower(), [])

    # --- 8. Build Response ---
    return models.NpcTemplateResponse(
        generated_id=generated_id,
        name=name,
        description=description,
        stats=final_stats,
        skills=skills,
        abilities=abilities,
        max_hp=max_hp,
        behavior_tags=behavior_tags,
        loot_table_ref=f"{request.kingdom}_{request.difficulty}_loot" # Example loot ref
    )