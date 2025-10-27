# AI-TTRPG/story_engine/app/combat_handler.py
from sqlalchemy.orm import Session
from fastapi import HTTPException
import httpx
from typing import List, Dict, Any, Tuple, Optional
from . import crud, models, schemas, services
import random
import re

# Helper function to extract initiative stats (adjust keys if needed)
def _extract_initiative_stats(stats_dict: Dict) -> Dict:
    """Extracts the 6 stats needed for initiative from a stats dictionary."""
    # Ensure default values if stats are missing
    return {
        "endurance": stats_dict.get("Endurance", 10),
        "agility": stats_dict.get("Agility", 10),
        "fortitude": stats_dict.get("Fortitude", 10),
        "logic": stats_dict.get("Logic", 10),
        "intuition": stats_dict.get("Intuition", 10),
        "willpower": stats_dict.get("Willpower", 10),
    }

# ADD THIS ASYNC FUNCTION
async def start_combat(db: Session, start_request: schemas.CombatStartRequest) -> models.CombatEncounter:
    """
    Initiates combat:
    1. Spawns requested NPCs in world_engine.
    2. Fetches stats for all participants (players & NPCs).
    3. Rolls initiative for all using rules_engine.
    4. Creates combat state records in story_engine DB.
    Returns the created CombatEncounter database object.
    """
    print(f"Starting combat at location {start_request.location_id}")
    participants_data: List[Tuple[str, str, int]] = [] # (actor_id, actor_type, initiative_total)
    spawned_npc_details: List[Dict] = [] # Store full details of spawned NPCs

    async with httpx.AsyncClient() as client:
        # 1. Spawn NPCs requested
        print(f"Spawning NPCs: {start_request.npc_template_ids}")
        for template_id in start_request.npc_template_ids:
            try:
                # Prepare spawn request for world_engine
                spawn_data = schemas.OrchestrationSpawnNpc(
                    template_id=template_id,
                    location_id=start_request.location_id
                    # Add behavior tags if npc_generator provides them
                )
                # Call world_engine to spawn
                npc_instance_data = await services.spawn_npc_in_world(client, spawn_data)
                spawned_npc_details.append(npc_instance_data)
                print(f"Spawned NPC instance ID: {npc_instance_data.get('id')} from template: {template_id}")
            except HTTPException as e:
                # If spawning fails, maybe abort combat start? Or just log and continue?
                print(f"ERROR: Failed to spawn NPC template '{template_id}': {e.detail}")
                # Decide on error handling - for now, we continue without this NPC
                continue # Skip this NPC
            except Exception as e:
                print(f"ERROR: Unexpected error spawning NPC template '{template_id}': {e}")
                continue # Skip

        # 2. Roll Initiative for Players
        print(f"Rolling initiative for players: {start_request.player_ids}")
        for player_id in start_request.player_ids:
            try:
                # Get player stats from character_engine
                char_context = await services.get_character_context(client, player_id)
                player_stats = char_context.get("character_sheet", {}).get("stats", {})

                # Extract stats relevant to initiative
                stats_for_init = _extract_initiative_stats(player_stats)

                # Call rules_engine to roll initiative
                init_result = await services.roll_initiative(client, **stats_for_init)
                initiative_total = init_result.get("total_initiative", 0)
                participants_data.append((player_id, "player", initiative_total))
                print(f"Player {player_id} initiative: {initiative_total}")
            except HTTPException as e:
                print(f"ERROR: Failed to get context or roll initiative for Player {player_id}: {e.detail}")
                participants_data.append((player_id, "player", 0)) # Add with init 0 if failed
            except Exception as e:
                print(f"ERROR: Unexpected error processing Player {player_id}: {e}")
                participants_data.append((player_id, "player", 0)) # Add with init 0

        # 3. Roll Initiative for Spawned NPCs
        print(f"Rolling initiative for {len(spawned_npc_details)} spawned NPCs.")
        for npc_data in spawned_npc_details:
            npc_id = npc_data.get('id')
            actor_id_str = f"npc_{npc_id}" # Use a consistent ID format
            try:
                # Get NPC stats from world_engine (assuming they are stored on spawn)
                # NOTE: world_engine's spawn response might need to include stats,
                # OR we need another call here, perhaps to npc_generator via AI DM,
                # or world_engine needs to store template stats.
                # For now, assume world_engine returns basic stats needed.
                npc_stats = npc_data.get("stats", {}) # Placeholder - adjust if world_engine provides stats differently

                # Extract stats relevant to initiative
                stats_for_init = _extract_initiative_stats(npc_stats)

                # Call rules_engine to roll initiative
                init_result = await services.roll_initiative(client, **stats_for_init)
                initiative_total = init_result.get("total_initiative", 0)
                participants_data.append((actor_id_str, "npc", initiative_total))
                print(f"NPC {npc_id} initiative: {initiative_total}")
            except HTTPException as e:
                print(f"ERROR: Failed to get context or roll initiative for NPC {npc_id}: {e.detail}")
                participants_data.append((actor_id_str, "npc", 0)) # Add with init 0 if failed
            except Exception as e:
                 print(f"ERROR: Unexpected error processing NPC {npc_id}: {e}")
                 participants_data.append((actor_id_str, "npc", 0)) # Add with init 0

    # 4. Sort Participants and Create Turn Order
    if not participants_data:
         raise HTTPException(status_code=400, detail="Cannot start combat with no participants.")

    participants_data.sort(key=lambda x: x[2], reverse=True) # Sort by initiative descending
    turn_order = [p[0] for p in participants_data] # Extract sorted IDs
    print(f"Final Turn Order: {turn_order}")

    # 5. Create Combat Encounter Record in DB
    try:
        db_combat = crud.create_combat_encounter(db, location_id=start_request.location_id, turn_order=turn_order)
        print(f"Created CombatEncounter record with ID: {db_combat.id}")
    except Exception as e:
         # Handle potential DB errors
         print(f"ERROR: Failed to create combat encounter in database: {e}")
         raise HTTPException(status_code=500, detail="Failed to save combat encounter state.")

    # 6. Create Combat Participant Records in DB
    for actor_id, actor_type, initiative in participants_data:
        try:
            crud.create_combat_participant(db, combat_id=db_combat.id, actor_id=actor_id, actor_type=actor_type, initiative=initiative)
        except Exception as e:
             # Log error but maybe continue? Or should this roll back the encounter creation?
             print(f"ERROR: Failed to save participant {actor_id} to database: {e}")
             # Consider cleanup logic here if needed

    print(f"Combat started successfully with ID {db_combat.id}")
    # Fetch the full encounter with participants to return it
    db_combat_full = crud.get_combat_encounter(db, db_combat.id)
    return db_combat_full

# ADD HELPER FUNCTIONS
async def get_actor_context(client: httpx.AsyncClient, actor_id: str) -> Tuple[str, Dict]:
    """
    Fetches the context (stats, skills, equipment, status) for a given actor ID.
    Returns a tuple: (actor_type: 'player' | 'npc', context_data: Dict)
    Raises HTTPException if actor not found.
    """
    if actor_id.startswith("player_"):
        try:
            # Assuming player ID format is "player_1", need actual ID '1'
            player_db_id = int(actor_id.split("_")[1])
            context_data = await services.get_character_context(client, player_db_id)
            return "player", context_data
        except (IndexError, ValueError):
             raise HTTPException(status_code=400, detail=f"Invalid player actor ID format: {actor_id}")
        except HTTPException as e:
             # Re-raise exceptions from the service call (like 404 Not Found)
             raise HTTPException(status_code=e.status_code, detail=f"Could not get context for {actor_id}: {e.detail}")
    elif actor_id.startswith("npc_"):
        try:
            npc_instance_id = int(actor_id.split("_")[1])
            context_data = await services.get_npc_context(client, npc_instance_id)
            return "npc", context_data
        except (IndexError, ValueError):
             raise HTTPException(status_code=400, detail=f"Invalid NPC actor ID format: {actor_id}")
        except HTTPException as e:
             raise HTTPException(status_code=e.status_code, detail=f"Could not get context for {actor_id}: {e.detail}")
    else:
        raise HTTPException(status_code=400, detail=f"Unknown actor ID format: {actor_id}")

def get_stat_score(actor_context: Dict, stat_name: str) -> int:
    """Safely retrieves a stat score from player or NPC context."""
    if actor_context.get("character_sheet"): # Player structure
         return actor_context.get("character_sheet", {}).get("stats", {}).get(stat_name, 10) # Default 10
    else: # NPC structure (assuming stats are top-level or nested differently)
         return actor_context.get("stats", {}).get(stat_name, 10)

def get_skill_rank(actor_context: Dict, skill_name: str) -> int:
    """Safely retrieves a skill rank from player or NPC context."""
    if actor_context.get("character_sheet"): # Player structure
        skills = actor_context.get("character_sheet", {}).get("skills", {})
        return skills.get(skill_name, {}).get("rank", 0) # Default 0
    else: # NPC structure
         return actor_context.get("skills", {}).get(skill_name, 0)

def get_equipped_weapon(actor_context: Dict) -> Tuple[Optional[str], Optional[str]]:
    """Pulls equipped weapon from a character sheet's equipment slots."""
    if actor_context.get("character_sheet"): # Player structure
        equipment = actor_context.get("character_sheet", {}).get("equipment", {})
        # Example: {"equipment": {"right_hand": {"category": "Great Weapons", "type": "melee"}, ...}}
        if "right_hand" in equipment:
            weapon = equipment["right_hand"]
            return weapon.get("category"), weapon.get("type")
    # NPC logic would go here
    return "Great Weapons", "melee"

def get_equipped_armor(actor_context: Dict) -> Optional[str]:
    """Pulls equipped armor from a character sheet's equipment slots."""
    if actor_context.get("character_sheet"): # Player structure
        equipment = actor_context.get("character_sheet", {}).get("equipment", {})
        if "body" in equipment:
            armor = equipment["body"]
            return armor.get("category")
    # NPC logic
    return "Plate Armor"

# ADD OR REPLACE THIS ASYNC FUNCTION
async def execute_combat_action(db: Session, combat_id: int, actor_id: str, action_details: schemas.PlayerActionRequest) -> Dict:
    """
    Executes a combat action (currently focusing on 'attack').
    Orchestrates calls to rules_engine, character_engine, and world_engine.
    Returns a dictionary summarizing the result.
    """
    results_log = [] # Log of what happened this action

    if action_details.action != "attack":
        # Handle other actions (move, use_ability, wait) later
        return {"success": False, "message": f"Action type '{action_details.action}' not yet implemented.", "log": results_log}

    target_id = action_details.target_id
    if not target_id:
        return {"success": False, "message": "Attack action requires a target_id.", "log": results_log}

    async with httpx.AsyncClient() as client:
        try:
            # 1. Get Context for Attacker and Defender
            actor_type, attacker_context = await get_actor_context(client, actor_id)
            target_type, defender_context = await get_actor_context(client, target_id)
            results_log.append(f"{actor_id} targets {target_id}.")

            # --- TEMP: Check if target already defeated ---
            if target_type == "npc" and defender_context.get("current_hp", 1) <= 0:
                 return {"success": False, "message": f"Target {target_id} is already defeated.", "log": results_log}
            # Add similar check for player HP if needed

            # 2. Determine Weapon and Armor Categories (Using Placeholders)
            # *** Replace placeholders with real logic to check equipment ***
            weapon_category, weapon_type = get_equipped_weapon(attacker_context)
            armor_category = get_equipped_armor(defender_context)

            if not weapon_category or not weapon_type:
                return {"success": False, "message": f"{actor_id} has no weapon equipped?", "log": results_log}
            # Armor can be optional (use default DR 0 if none)

            # 3. Get Weapon and Armor Data from rules_engine
            weapon_data = await services.get_weapon_data(client, weapon_category, weapon_type)
            armor_data = {}
            if armor_category:
                armor_data = await services.get_armor_data(client, armor_category)
            else: # Assume default DR 0 if no armor
                 armor_data = {"skill_stat": "Agility", "dr": 0, "specialty": "None"} # Example default

            # 4. Prepare Contested Attack Request
            attack_stat = weapon_data.get("skill_stat")
            armor_stat = armor_data.get("skill_stat")

            # *** Need to determine relevant skill names based on category ***
            # Placeholder mapping - THIS NEEDS TO BE ACCURATE
            weapon_skill_map = {"Precision Blades": "Dueling Blades"} # Example
            armor_skill_map = {"Leather/Hides": "Leather/Hides"} # Example
            weapon_skill = weapon_skill_map.get(weapon_category, "Unknown Skill")
            armor_skill = armor_skill_map.get(armor_category, "Unknown Skill")

            attack_params = {
                "attacker_attacking_stat_score": get_stat_score(attacker_context, attack_stat),
                "attacker_skill_rank": get_skill_rank(attacker_context, weapon_skill),
                "attacker_misc_bonus": 0,
                "attacker_misc_penalty": 0,

                "defender_armor_stat_score": get_stat_score(defender_context, armor_stat),
                "defender_armor_skill_rank": get_skill_rank(defender_context, armor_skill),
                "defender_weapon_penalty": weapon_data.get("defense_penalty", 0),
                "defender_misc_bonus": 0,
                "defender_misc_penalty": 0,
            }

            # 5. Call rules_engine: Contested Attack Roll
            attack_result = await services.roll_contested_attack(client, attack_params)
            results_log.append(f"Attack Roll: Attacker ({attack_result['attacker_final_total']}) vs Defender ({attack_result['defender_final_total']}). Margin: {attack_result['margin']}.")

            outcome = attack_result.get("outcome")

            # 6. Process Outcome
            if outcome == "critical_fumble":
                results_log.append("Result: Critical Fumble!")
                return {"success": True, "message": "Critical Fumble!", "log": results_log, "outcome": outcome}

            elif outcome == "miss":
                results_log.append("Result: Miss!")
                return {"success": True, "message": "Miss!", "log": results_log, "outcome": outcome}

            elif outcome in ["hit", "solid_hit", "critical_hit"]:
                hit_type = "Hit!"
                if outcome == "solid_hit": hit_type = "Solid Hit!"
                if outcome == "critical_hit": hit_type = "Critical Hit!"
                results_log.append(f"Result: {hit_type}")

                # 7. Prepare Damage Request
                base_dmg_str = weapon_data.get("base_damage", "0")
                num_hits = 1
                match = re.match(r"(.+)\(x(\d+)\)", base_dmg_str)
                if match:
                     base_dmg_str = match.group(1)
                     num_hits = int(match.group(2))

                final_damage_dealt = 0
                damage_details = []

                for hit_num in range(num_hits): # Loop for multi-attacks
                    damage_params = {
                        "base_damage_dice": base_dmg_str,
                        "relevant_stat_score": get_stat_score(attacker_context, attack_stat), # Use same stat for damage
                        "misc_damage_bonus": 0,
                        "target_damage_reduction": armor_data.get("dr", 0)
                    }

                    # 8. Call rules_engine: Calculate Damage
                    damage_result = await services.calculate_damage(client, damage_params)
                    final_damage = damage_result.get("final_damage", 0)
                    final_damage_dealt += final_damage
                    damage_details.append(damage_result)

                    results_log.append(f"Damage Roll {hit_num+1}: {damage_result['damage_roll_details']} + {damage_result['stat_bonus']} (Stat) + {damage_result['misc_bonus']} (Misc) = {damage_result['subtotal_damage']} subtotal.")
                    results_log.append(f"Applied DR: {damage_result['damage_reduction_applied']}. Final Damage {hit_num+1}: {final_damage}.")

                # 9. Apply Damage (Total)
                if target_type == "player":
                    current_hp = get_stat_score(defender_context, "HP")
                    new_hp = current_hp - final_damage_dealt
                    results_log.append(f"Applying {final_damage_dealt} damage to Player {target_id} (HP: {current_hp} -> {new_hp}).")
                    await services.apply_damage_to_character(client, target_id, final_damage_dealt)
                elif target_type == "npc":
                    current_hp = defender_context.get("current_hp", 0)
                    new_hp = current_hp - final_damage_dealt
                    results_log.append(f"Applying {final_damage_dealt} damage to NPC {target_id} (HP: {current_hp} -> {new_hp}).")
                    await services.apply_damage_to_npc(client, int(target_id.split("_")[1]), new_hp)

                # 10. Handle Hit Effects (Solid Hit / Critical Hit)
                if outcome == "solid_hit":
                    results_log.append("Applying Staggered status.")
                    if target_type == "player":
                         await services.apply_status_to_character(client, target_id, "Staggered")
                    elif target_type == "npc":
                        current_statuses = defender_context.get("status_effects", [])
                        if "Staggered" not in current_statuses:
                            current_statuses.append("Staggered")
                        await services.apply_status_to_npc(client, int(target_id.split("_")[1]), current_statuses)

                if outcome == "critical_hit":
                    results_log.append("Critical Hit! Applying Minor Injury.")
                    injury_location = "Torso"
                    injury_sub_location = "Ribs/Lungs"
                    injury_severity = 2

                    try:
                        injury_result = await services.get_injury_effects(client, injury_location, injury_sub_location, injury_severity)
                        effects_to_apply = injury_result.get("effects", [])
                        results_log.append(f"Applying Injury ({injury_result.get('severity_name')} to {injury_sub_location}): Effects={effects_to_apply}")

                    except Exception as injury_e:
                         results_log.append(f"ERROR applying injury effects: {injury_e}")

                if new_hp <= 0:
                     results_log.append(f"Target {target_id} defeated!")

                return {"success": True, "message": hit_type, "damage_dealt": final_damage_dealt, "target_hp_remaining": new_hp, "log": results_log, "outcome": outcome, "damage_details": damage_details}

            else:
                 return {"success": False, "message": "Unknown attack outcome.", "log": results_log, "outcome": outcome}

        except HTTPException as he:
            results_log.append(f"ERROR: Service call failed: {he.detail}")
            return {"success": False, "message": f"Action failed: {he.detail}", "log": results_log}
        except Exception as e:
            results_log.append(f"ERROR: Unexpected error during action execution: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "message": f"Action failed: An unexpected error occurred.", "log": results_log}
