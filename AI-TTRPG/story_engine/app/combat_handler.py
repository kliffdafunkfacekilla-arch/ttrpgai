# AI-TTRPG/story_engine/app/combat_handler.py
from sqlalchemy.orm import Session
from fastapi import HTTPException
import httpx
from typing import List, Dict, Any, Tuple, Optional
from . import crud, models, schemas, services
import random
import re
import logging # Import logging

logger = logging.getLogger("uvicorn.error") # Get the uvicorn logger

# --- Helper function to find valid spawn tiles ---
def _find_spawn_points(map_data: List[List[int]], num_points: int) -> List[List[int]]:
    """
    Finds valid, random spawn points on a map.
    Valid tiles are 0 (Grass) and 3 (Stone Floor) based on tile_definitions.json.
    """
    if not map_data:
        logger.warning("Map data is empty, cannot find spawn points.")
        return [[5, 5]] * num_points # Fallback to a default coordinate

    valid_spawns = []
    height = len(map_data)
    width = len(map_data[0]) if height > 0 else 0

    for y in range(height):
        for x in range(width):
            tile_id = map_data[y][x]
            if tile_id in [0, 3]: # 0=Grass, 3=Stone Floor
                valid_spawns.append([x, y]) # Store as [x, y]

    if not valid_spawns:
        logger.warning("No valid spawn tiles found on map. Falling back to default.")
        return [[5, 5]] * num_points

    random.shuffle(valid_spawns)

    # Return the requested number of points, reusing if necessary
    return [valid_spawns[i % len(valid_spawns)] for i in range(num_points)]
# Helper function to extract initiative stats (adjust keys if needed)
def _extract_initiative_stats(stats_dict: Dict) -> Dict:
    """Extracts the 6 stats needed for initiative from a stats dictionary."""
    # Ensure default values if stats are missing
    return {
        "endurance": stats_dict.get("Endurance", 10),
        "agility": stats_dict.get("Agility", 10), # Corrected stat name
        "fortitude": stats_dict.get("Fortitude", 10),
        "logic": stats_dict.get("Logic", 10),
        "intuition": stats_dict.get("Intuition", 10),
        "willpower": stats_dict.get("Willpower", 10),
    }

async def start_combat(db: Session, start_request: schemas.CombatStartRequest) -> models.CombatEncounter:
    """
    Initiates combat:
    1. Fetches map data to find spawn points.
    2. Spawns requested NPCs in world_engine *with coordinates*.
    3. Fetches stats for all participants (players & NPCs).
    4. Rolls initiative for all using rules_engine.
    5. Creates combat state records in story_engine DB.
    Returns the created CombatEncounter database object.
    """
    logger.info(f"Starting combat at location {start_request.location_id}")
    participants_data: List[Tuple[str, str, int]] = [] # (actor_id, actor_type, initiative_total)
    spawned_npc_details: List[Dict] = [] # Store full details of spawned NPCs

    async with httpx.AsyncClient() as client:

        # --- 1. Get Location Context to find map & spawn points ---
        spawn_points = []
        try:
            location_context = await services.get_world_location_context(client, start_request.location_id)
            map_data = location_context.get("generated_map_data")
            num_npcs = len(start_request.npc_template_ids)
            spawn_points = _find_spawn_points(map_data, num_npcs)
            logger.info(f"Found {len(spawn_points)} spawn points for {num_npcs} NPCs.")
        except Exception as e:
            logger.exception(f"Error finding spawn points: {e}. NPCs will spawn at default location.")
            spawn_points = [[5, 5]] * len(start_request.npc_template_ids) # Fallback

        # --- 2. Spawn NPCs requested ---
        logger.info(f"Spawning NPCs: {start_request.npc_template_ids}")
        for i, template_id in enumerate(start_request.npc_template_ids):
            try:
                # Get the coordinate for this NPC
                coords = spawn_points[i]

                spawn_data = schemas.OrchestrationSpawnNpc(
                    template_id=template_id,
                    location_id=start_request.location_id,
                    coordinates=coords  # --- PASS COORDINATES ---
                )
                npc_instance_data = await services.spawn_npc_in_world(client, spawn_data)
                spawned_npc_details.append(npc_instance_data)
                logger.info(f"Spawned NPC instance ID: {npc_instance_data.get('id')} at {coords} from template: {template_id}")
            except HTTPException as e:
                logger.error(f"Failed to spawn NPC template '{template_id}': {e.detail}")
                continue
            except Exception as e:
                logger.exception(f"Unexpected error spawning NPC template '{template_id}': {e}")
                continue

        # --- 3. Roll Initiative for Players ---
        logger.info(f"Rolling initiative for players: {start_request.player_ids}")
        for player_id_str in start_request.player_ids: # Ensure player_id is string
            try:
                # Validate player_id format if necessary, e.g., starts with "player_"
                if not isinstance(player_id_str, str) or not player_id_str.startswith("player_"):
                     logger.warning(f"Skipping invalid player ID format: {player_id_str}")
                     continue

                char_context = await services.get_character_context(client, player_id_str) # Pass string ID
                player_stats = char_context.get("character_sheet", {}).get("stats", {})
                stats_for_init = _extract_initiative_stats(player_stats)
                init_result = await services.roll_initiative(client, **stats_for_init)
                initiative_total = init_result.get("total_initiative", 0)
                participants_data.append((player_id_str, "player", initiative_total)) # Store string ID
                logger.info(f"Player {player_id_str} initiative: {initiative_total}")
            except HTTPException as e:
                logger.error(f"Failed to get context or roll initiative for Player {player_id_str}: {e.detail}")
                participants_data.append((player_id_str, "player", 0))
            except Exception as e:
                logger.exception(f"Unexpected error processing Player {player_id_str}: {e}")
                participants_data.append((player_id_str, "player", 0))

        # 3. Roll Initiative for Spawned NPCs
        logger.info(f"Rolling initiative for {len(spawned_npc_details)} spawned NPCs.")
        for npc_data in spawned_npc_details:
            npc_id = npc_data.get('id')
            if npc_id is None:
                logger.warning("Spawned NPC data missing ID, cannot roll initiative.")
                continue
            actor_id_str = f"npc_{npc_id}"
            try:
                # Fetch full NPC context again to ensure stats are present
                npc_context = await services.get_npc_context(client, npc_id)
                npc_stats = npc_context.get("stats", {}) # Assuming stats might be nested or added later
                # --- If stats are not directly in npc_context, need logic to fetch from template ---
                if not npc_stats:
                     logger.warning(f"NPC {npc_id} context missing stats, using defaults for initiative.")
                     npc_stats = {} # Use defaults below

                stats_for_init = _extract_initiative_stats(npc_stats)
                init_result = await services.roll_initiative(client, **stats_for_init)
                initiative_total = init_result.get("total_initiative", 0)
                participants_data.append((actor_id_str, "npc", initiative_total))
                logger.info(f"NPC {npc_id} initiative: {initiative_total}")
            except HTTPException as e:
                logger.error(f"Failed to get context or roll initiative for NPC {npc_id}: {e.detail}")
                participants_data.append((actor_id_str, "npc", 0))
            except Exception as e:
                logger.exception(f"Unexpected error processing NPC {npc_id}: {e}")
                participants_data.append((actor_id_str, "npc", 0))

    # 4. Sort Participants and Create Turn Order
    if not participants_data:
        raise HTTPException(status_code=400, detail="Cannot start combat: No valid participants found.")

    participants_data.sort(key=lambda x: x[2], reverse=True)
    turn_order = [p[0] for p in participants_data]
    logger.info(f"Final Turn Order: {turn_order}")

    # 5. Create Combat Encounter Record in DB
    try:
        db_combat = crud.create_combat_encounter(db, location_id=start_request.location_id, turn_order=turn_order)
        logger.info(f"Created CombatEncounter record with ID: {db_combat.id}")
    except Exception as e:
        logger.exception(f"Failed to create combat encounter in database: {e}")
        raise HTTPException(status_code=500, detail="Failed to save combat encounter state.")

    # 6. Create Combat Participant Records in DB
    for actor_id, actor_type, initiative in participants_data:
        try:
            crud.create_combat_participant(db, combat_id=db_combat.id, actor_id=actor_id, actor_type=actor_type, initiative=initiative)
        except Exception as e:
            logger.exception(f"Failed to save participant {actor_id} to database: {e}")
            # Consider cleanup logic here if needed

    logger.info(f"Combat started successfully with ID {db_combat.id}")
    db.refresh(db_combat) # Ensure relationships are loaded if needed immediately
    return db_combat

# --- Helper Functions ---
async def get_actor_context(client: httpx.AsyncClient, actor_id: str) -> Tuple[str, Dict]:
    """ Fetches context for player or NPC. Raises HTTPException if not found or invalid ID."""
    logger.debug(f"Getting context for actor: {actor_id}")
    if actor_id.startswith("player_"):
        try:
            # Assuming player ID format is "player_1", need actual ID '1'
            # player_db_id_str = actor_id.split("_")[1] # Keep as string if service expects string
            context_data = await services.get_character_context(client, actor_id) # Pass full "player_1" string
            return "player", context_data
        except IndexError:
            logger.error(f"Invalid player actor ID format: {actor_id}")
            raise HTTPException(status_code=400, detail=f"Invalid player actor ID format: {actor_id}")
        except HTTPException as e:
            logger.error(f"Could not get context for {actor_id}: {e.detail} (Status: {e.status_code})")
            raise HTTPException(status_code=e.status_code, detail=f"Could not get context for {actor_id}: {e.detail}")
    elif actor_id.startswith("npc_"):
        try:
            npc_instance_id = int(actor_id.split("_")[1])
            context_data = await services.get_npc_context(client, npc_instance_id)
            return "npc", context_data
        except (IndexError, ValueError):
            logger.error(f"Invalid NPC actor ID format: {actor_id}")
            raise HTTPException(status_code=400, detail=f"Invalid NPC actor ID format: {actor_id}")
        except HTTPException as e:
            logger.error(f"Could not get context for {actor_id}: {e.detail} (Status: {e.status_code})")
            raise HTTPException(status_code=e.status_code, detail=f"Could not get context for {actor_id}: {e.detail}")
    else:
        logger.error(f"Unknown actor ID format: {actor_id}")
        raise HTTPException(status_code=400, detail=f"Unknown actor ID format: {actor_id}")

def get_stat_score(actor_context: Dict, stat_name: str) -> int:
    """Safely retrieves a stat score from player or NPC context."""
    if actor_context.get("character_sheet"): # Player structure
        return actor_context.get("character_sheet", {}).get("stats", {}).get(stat_name, 10)
    else: # NPC structure
        # Check top level first, then nested (assuming structure might vary)
         stats = actor_context.get("stats", {})
         if stat_name in stats:
             return stats[stat_name]
         # Fallback check if stats are nested under character_sheet even for NPCs? Unlikely.
         return actor_context.get("character_sheet", {}).get("stats", {}).get(stat_name, 10)

def get_skill_rank(actor_context: Dict, skill_name: str) -> int:
    """Safely retrieves a skill rank from player or NPC context."""
    if actor_context.get("character_sheet"): # Player structure
        skills = actor_context.get("character_sheet", {}).get("skills", {})
        # Handle both {"skill": {"rank": X}} and {"skill": X} structures
        skill_data = skills.get(skill_name)
        if isinstance(skill_data, dict):
            return skill_data.get("rank", 0)
        elif isinstance(skill_data, int):
            return skill_data
        return 0
    else: # NPC structure
        skills = actor_context.get("skills", {})
        if isinstance(skills, dict):
             skill_data = skills.get(skill_name)
             if isinstance(skill_data, int):
                  return skill_data
        return 0 # Default if skills format is unexpected or skill absent

def get_equipped_weapon(actor_context: Dict) -> Tuple[Optional[str], Optional[str]]:
    """Pulls equipped weapon. Needs refinement based on actual sheet structure."""
    # --- Placeholder --- Needs actual equipment structure
    logger.warning(f"Using placeholder weapon for actor {actor_context.get('id', actor_context.get('name', 'Unknown'))}")
    # Example: Assume an aggressive mammal NPC uses heavy bludgeons
    if actor_context.get("character_sheet"): # Player
        # TODO: Implement actual player equipment lookup
         return "Resolute Edges", "melee" # Placeholder
    else: # NPC
         if "melee_heavy" in actor_context.get("template_id", ""): # Guess based on template ID
             return "Heavy Bludgeons", "melee"
         elif "ranged" in actor_context.get("template_id", ""):
              return "Short Bow", "ranged"
         # Default fallback
         return "Unarmed & Fist Weapons", "melee"

def get_equipped_armor(actor_context: Dict) -> Optional[str]:
    """Pulls equipped armor. Needs refinement."""
    # --- Placeholder --- Needs actual equipment structure
    logger.warning(f"Using placeholder armor for actor {actor_context.get('id', actor_context.get('name', 'Unknown'))}")
    if actor_context.get("character_sheet"): # Player
        # TODO: Implement actual player equipment lookup
        return "Medium Armor" # Placeholder
    else: # NPC
        if "heavy_armor" in actor_context.get("template_id", ""):
             return "Heavy Armor"
        elif "evasive" in actor_context.get("template_id", ""):
             return "Light Armor" # or "No Armor"
        # Default fallback
        return "Medium Armor"

async def check_combat_end(db: Session, combat_id: int, client: httpx.AsyncClient) -> Optional[str]:
    """Checks if combat should end (all players down or all NPCs down). Returns 'players_win', 'npcs_win', or None."""
    db_combat = crud.get_combat_encounter(db, combat_id)
    if not db_combat or db_combat.status != "active":
        return db_combat.status if db_combat else None # Return existing status if not active

    players_alive = False
    npcs_alive = False

    participants = db_combat.participants
    if not participants:
         logger.warning(f"Combat {combat_id} has no participants, ending.")
         return "draw" # Or some other status

    for p in participants:
         try:
            actor_type, context = await get_actor_context(client, p.actor_id)
            # Check HP based on type
            if actor_type == "player":
                # --- MODIFIED HP PATH ---
                hp = context.get("character_sheet", {}).get("combat_stats", {}).get("current_hp", 1)
                if hp > 0: players_alive = True
            elif actor_type == "npc":
                hp = context.get("current_hp", 1)
                if hp > 0: npcs_alive = True
         except HTTPException as e:
              logger.warning(f"Could not get context for participant {p.actor_id} during end check: {e.detail}. Assuming defeated.")
              # If we can't get context, assume they are down for safety.
         except Exception as e:
              logger.exception(f"Unexpected error getting context for {p.actor_id} during end check: {e}")

    if not players_alive:
         logger.info(f"Combat {combat_id} ended: All players defeated.")
         return "npcs_win"
    if not npcs_alive:
         logger.info(f"Combat {combat_id} ended: All NPCs defeated.")
         return "players_win"

    return None # Combat continues

async def advance_turn(db: Session, combat_id: int):
    """Advances the turn index, checks for combat end, and triggers NPC turn if necessary."""
    db_combat = crud.get_combat_encounter(db, combat_id)
    if not db_combat or db_combat.status != "active":
        logger.warning(f"Attempted to advance turn for inactive/non-existent combat {combat_id}")
        return # Don't advance if combat isn't active

    async with httpx.AsyncClient() as client: # Use client for end check
        end_status = await check_combat_end(db, combat_id, client)
        if end_status:
            crud.update_combat_encounter(db, combat_id, {"status": end_status})
            logger.info(f"Combat {combat_id} status updated to {end_status}.")
            # Maybe trigger end-of-combat logic here (XP, loot, etc.)? Future step.
            return # Stop processing turns

        # Advance turn index
        current_index = db_combat.current_turn_index
        turn_order = db_combat.turn_order
        next_index = (current_index + 1) % len(turn_order)
        next_actor_id = turn_order[next_index]

        logger.info(f"Advancing turn for combat {combat_id}: {turn_order[current_index]} -> {next_actor_id}")
        updated_combat = crud.update_combat_encounter(db, combat_id, {"current_turn_index": next_index})
        db.refresh(updated_combat) # Refresh to get latest state

        # Check if the next actor is an NPC
        if next_actor_id.startswith("npc_"):
            logger.info(f"Next turn belongs to NPC: {next_actor_id}. Triggering NPC action.")
            # Use a background task or handle directly? For now, direct await.
            try:
                await execute_npc_turn(db, combat_id, next_actor_id)
            except Exception as e:
                # Log error, but maybe don't crash the whole combat?
                logger.exception(f"Error during NPC turn execution for {next_actor_id} in combat {combat_id}: {e}")
                # Decide if turn should advance anyway or halt
                # For now, let's advance to prevent getting stuck
                await advance_turn(db, combat_id)

async def determine_npc_action(npc_context: Dict, participants: List[models.CombatParticipant], client: httpx.AsyncClient) -> Tuple[str, Optional[str]]:
    """
    Basic NPC AI. Determines action (attack) and target based on behavior tags.
    Returns (action_type: str, target_id: Optional[str])
    """
    behavior_tags = npc_context.get("behavior_tags", [])
    npc_id_str = f"npc_{npc_context.get('id')}" # Use f-string for clarity
    npc_current_hp = npc_context.get("current_hp", 1)
    npc_max_hp = npc_context.get("max_hp", 1) # Needed for 'cowardly' check

    action_type = "wait" # Default action
    target_id = None

    # 1. Gather potential targets (living players) and their HP
    living_players_with_hp = []
    for p in participants:
        if p.actor_id.startswith("player_"):
            try:
                _, p_context = await get_actor_context(client, p.actor_id)
                hp = p_context.get("character_sheet", {}).get("combat_stats", {}).get("current_hp", 0) # Use correct path
                if hp > 0:
                    living_players_with_hp.append({"id": p.actor_id, "hp": hp})
            except HTTPException:
                logger.warning(f"Could not get context for potential target {p.actor_id} in NPC AI.")
                continue

    if not living_players_with_hp:
        logger.info(f"NPC {npc_id_str} found no living players to target.")
        return "wait", None # No targets, wait

    # 2. Apply behavior logic
    if "cowardly" in behavior_tags and npc_current_hp < npc_max_hp * 0.3: # Example: flee below 30% HP
        logger.info(f"NPC {npc_id_str} is cowardly and low HP, attempting to flee (action 'wait' for now).")
        # TODO: Implement actual flee logic (e.g., move away)
        action_type = "wait" # Placeholder for flee
        target_id = None
    elif "targets_weakest" in behavior_tags or "cowardly" in behavior_tags:
        # Find player with lowest HP
        living_players_with_hp.sort(key=lambda p: p["hp"])
        target_id = living_players_with_hp[0]["id"]
        action_type = "attack"
        logger.info(f"NPC {npc_id_str} targets weakest Player {target_id} (HP: {living_players_with_hp[0]['hp']}).")
    elif "aggressive" in behavior_tags or "focuses_highest_threat" in behavior_tags: # Simple: attack random living player
        target_id = random.choice(living_players_with_hp)["id"]
        action_type = "attack"
        logger.info(f"NPC {npc_id_str} aggressively targets random Player {target_id}.")
    # Add 'territorial' logic (attack closest?), 'support' logic, etc. later
    else: # Default: attack random if no specific behavior matches
        target_id = random.choice(living_players_with_hp)["id"]
        action_type = "attack"
        logger.info(f"NPC {npc_id_str} using default behavior, targets random Player {target_id}.")


    # 3. Final check if a target was selected for attack
    if action_type == "attack" and target_id:
        return "attack", target_id
    else:
        # If logic decided not to attack (e.g., flee), return wait
        return "wait", None

async def execute_npc_turn(db: Session, combat_id: int, npc_actor_id: str):
    """Determines and executes an NPC's action for the current turn."""
    logger.info(f"Executing turn for NPC: {npc_actor_id} in combat {combat_id}")
    db_combat = crud.get_combat_encounter(db, combat_id)
    if not db_combat or db_combat.status != "active":
         logger.warning(f"Combat {combat_id} not active, skipping NPC turn.")
         return

    async with httpx.AsyncClient() as client:
        try:
            _, npc_context = await get_actor_context(client, npc_actor_id)

            # Check if NPC is defeated or incapacitated
            if npc_context.get("current_hp", 1) <= 0:
                 logger.info(f"NPC {npc_actor_id} is defeated, skipping turn.")
                 await advance_turn(db, combat_id) # Advance turn immediately
                 return
            # TODO: Add check for other incapacitating status effects

            action_type, target_id = await determine_npc_action(npc_context, db_combat.participants, client)

            if action_type == "attack" and target_id:
                logger.info(f"NPC {npc_actor_id} performing 'attack' action against {target_id}.")
                # Prepare action details similar to PlayerActionRequest
                action_details = schemas.PlayerActionRequest(action="attack", target_id=target_id)
                # Use the existing execute_combat_action logic, passing the NPC's ID as the actor
                action_result = await execute_combat_action(db, combat_id, npc_actor_id, action_details, is_npc_turn=True)
                logger.info(f"NPC {npc_actor_id} action result: {action_result.get('message')}")
                # Turn is advanced automatically inside execute_combat_action if successful and is_npc_turn=True

            elif action_type == "wait":
                logger.info(f"NPC {npc_actor_id} performing 'wait' action.")
                # If NPC waits, just advance the turn
                await advance_turn(db, combat_id)
            else:
                logger.warning(f"NPC {npc_actor_id} determined unknown action type '{action_type}'. Waiting instead.")
                await advance_turn(db, combat_id)

        except HTTPException as e:
            logger.error(f"HTTPException executing NPC turn for {npc_actor_id}: {e.detail}. Advancing turn.")
            await advance_turn(db, combat_id) # Advance turn even if NPC fails
        except Exception as e:
            logger.exception(f"Unexpected error executing NPC turn for {npc_actor_id}: {e}. Advancing turn.")
            await advance_turn(db, combat_id) # Advance turn even if NPC fails

async def execute_combat_action(db: Session, combat_id: int, actor_id: str, action_details: schemas.PlayerActionRequest, is_npc_turn: bool = False) -> Dict:
    """
    Executes a combat action. If successful, advances the turn.
    Handles both player and NPC actions based on actor_id.
    Added is_npc_turn flag to prevent recursion during NPC turns.
    """
    results_log = []
    success = False # Flag to track if action completed successfully for turn advancement

    # --- Verify it's the correct actor's turn ---
    db_combat = crud.get_combat_encounter(db, combat_id)
    if not db_combat:
         raise HTTPException(status_code=404, detail=f"Combat encounter {combat_id} not found.")
    if db_combat.status != "active":
         raise HTTPException(status_code=400, detail=f"Combat encounter {combat_id} is not active ({db_combat.status}).")

    current_actor_id = db_combat.turn_order[db_combat.current_turn_index]
    if actor_id != current_actor_id:
        logger.warning(f"Action attempt by {actor_id} but it is {current_actor_id}'s turn.")
        raise HTTPException(status_code=403, detail=f"It is not {actor_id}'s turn (currently {current_actor_id}'s turn).")
    # --- End Turn Verification ---

    if action_details.action != "attack":
        results_log.append(f"Action type '{action_details.action}' not yet fully implemented.")
        # For now, just log wait and advance turn
        if action_details.action == "wait":
             logger.info(f"Actor {actor_id} performs 'wait' action.")
             results_log.append(f"{actor_id} waits.")
             success = True # Waiting is a successful action
        # Add placeholders for other actions (move, use_ability) here if needed
        else:
             logger.warning(f"Unsupported action '{action_details.action}' attempted by {actor_id}.")

    elif action_details.action == "attack":
        target_id = action_details.target_id
        if not target_id:
            return {"success": False, "message": "Attack action requires a target_id.", "log": results_log}

        async with httpx.AsyncClient() as client:
            try:
                # 1. Get Context for Attacker and Defender
                actor_type, attacker_context = await get_actor_context(client, actor_id)
                target_type, defender_context = await get_actor_context(client, target_id)
                results_log.append(f"{actor_id} targets {target_id} with an attack.")

                # Check if target already defeated
                target_hp = 1 # Default alive
                if target_type == "npc":
                    target_hp = defender_context.get("current_hp", 1)
                elif target_type == "player":
                    # --- MODIFIED HP PATH ---
                    target_hp = defender_context.get("character_sheet", {}).get("combat_stats", {}).get("current_hp", 1)

                if target_hp <= 0:
                    return {"success": False, "message": f"Target {target_id} is already defeated.", "log": results_log}

                # 2. Determine Weapon and Armor
                weapon_category, weapon_type = get_equipped_weapon(attacker_context)
                armor_category = get_equipped_armor(defender_context)

                if not weapon_category or not weapon_type:
                    return {"success": False, "message": f"{actor_id} has no weapon equipped?", "log": results_log}

                # 3. Get Weapon and Armor Data from rules_engine
                weapon_data = await services.get_weapon_data(client, weapon_category, weapon_type)
                armor_data = {}
                if armor_category:
                    try:
                        armor_data = await services.get_armor_data(client, armor_category)
                    except HTTPException as e:
                        if e.status_code == 404:
                            logger.warning(f"Armor category '{armor_category}' not found in rules_engine. Using default DR 0.")
                            armor_data = {"skill_stat": "Agility", "dr": 0, "properties": []}
                        else: raise # Re-raise other errors
                else:
                    armor_data = {"skill_stat": "Agility", "dr": 0, "properties": []}

                # 4. Prepare Contested Attack Request
                attack_stat = weapon_data.get("skill_stat")
                armor_stat = armor_data.get("skill_stat") # Usually Endurance or Agility from armor.json

                # --- NEW Skill Mapping Logic ---
                weapon_skill = weapon_data.get("skill")
                if not weapon_skill:
                    logger.error(f"Weapon category {weapon_category} is missing a 'skill' field in rules_engine data!")
                    return {"success": False, "message": f"Data error: Weapon {weapon_category} has no skill defined.", "log": results_log}
                armor_skill = armor_data.get("skill", "Natural/Unarmored") # Get skill from data, default to Natural/Unarmored
                # Skill mapping is now read directly from weapon/armor data.
                # --- End NEW Skill Mapping ---

                attack_params = {
                    "attacker_attacking_stat_score": get_stat_score(attacker_context, attack_stat),
                    "attacker_skill_rank": get_skill_rank(attacker_context, weapon_skill), # Use derived skill
                    "attacker_misc_bonus": 0, # TODO: Add bonuses (status effects, talents)
                    "attacker_misc_penalty": 0, # TODO: Add penalties

                    "defender_armor_stat_score": get_stat_score(defender_context, armor_stat),
                    "defender_armor_skill_rank": get_skill_rank(defender_context, armor_skill), # Use derived skill
                    "defender_weapon_penalty": weapon_data.get("penalty", 0), # Ensure key matches JSON ('penalty')
                    "defender_misc_bonus": 0,
                    "defender_misc_penalty": 0,
                }

                # 5. Call rules_engine: Contested Attack Roll
                attack_result = await services.roll_contested_attack(client, attack_params)
                results_log.append(f"Attack Roll: Attacker ({attack_result['attacker_final_total']}) vs Defender ({attack_result['defender_final_total']}). Margin: {attack_result['margin']}.")
                outcome = attack_result.get("outcome")

                # 6. Process Outcome
                if outcome == "critical_fumble":
                    results_log.append(f"Result: Critical Fumble by {actor_id}!")
                    success = True # Action was taken, even if bad
                    # Add fumble effects later?

                elif outcome == "miss":
                    results_log.append(f"Result: {actor_id} misses {target_id}.")
                    success = True

                elif outcome in ["hit", "solid_hit", "critical_hit"]:
                    hit_type = "Hit!"
                    if outcome == "solid_hit": hit_type = "Solid Hit!"
                    if outcome == "critical_hit": hit_type = "Critical Hit!"
                    results_log.append(f"Result: {actor_id} lands a {hit_type} on {target_id}!")

                    # 7. Prepare Damage Request
                    base_dmg_str = weapon_data.get("damage", "0") # Use correct key 'damage'
                    num_hits = 1
                    # Example: Handle multi-hit like '1d4+1d4' or '1d6(x2)' - needs robust parsing
                    # Simple placeholder for now:
                    if '+' in base_dmg_str: # e.g., '1d4+1d4' -> treat as 2 hits of 1d4
                         parts = base_dmg_str.split('+')
                         if len(parts) == 2 and parts[0] == parts[1]: # Basic check
                              base_dmg_str = parts[0]
                              num_hits = 2
                    elif '(x' in base_dmg_str: # e.g., '1d6(x2)'
                         match = re.match(r"(.+)\(x(\d+)\)", base_dmg_str)
                         if match:
                              base_dmg_str = match.group(1)
                              num_hits = int(match.group(2))

                    final_damage_dealt = 0
                    damage_details_list = []
                    new_hp = target_hp # Initialize with current HP

                    for hit_num in range(num_hits):
                        damage_params = {
                            "base_damage_roll": base_dmg_str,
                            "damage_stat_score": get_stat_score(attacker_context, attack_stat),
                            "misc_damage_bonus": 0, # TODO: Add damage bonuses
                            "target_damage_reduction": armor_data.get("dr", 0)
                        }

                        # 8. Call rules_engine: Calculate Damage
                        damage_result = await services.calculate_damage(client, damage_params)
                        final_damage = damage_result.get("final_damage", 0)
                        final_damage_dealt += final_damage
                        damage_details_list.append(damage_result)

                        results_log.append(f"Damage Roll {hit_num+1}: Base({damage_result['base_roll_total']}) + Stat({damage_result['stat_modifier']}) + Misc({damage_params['misc_damage_bonus']}) = Subtotal {damage_result['subtotal_damage']}. DR Applied: {damage_result['damage_reduction_applied']}. Final: {final_damage}.")

                    # 9. Apply Damage (Total)
                    if final_damage_dealt > 0:
                        if target_type == "player":
                            # --- MODIFIED HP PATH ---
                            target_hp_before = defender_context.get("character_sheet", {}).get("combat_stats", {}).get("current_hp", 0)
                            new_hp = target_hp_before - final_damage_dealt
                            new_hp = max(0, new_hp) # Clamp at 0
                            results_log.append(f"Applying {final_damage_dealt} damage to Player {target_id} (HP: {target_hp_before} -> {new_hp}).")
                            await services.apply_damage_to_character(client, target_id, final_damage_dealt)
                        elif target_type == "npc":
                              target_hp_before = defender_context.get("current_hp", 0)
                              new_hp = target_hp_before - final_damage_dealt
                              results_log.append(f"Applying {final_damage_dealt} damage to NPC {target_id} (HP: {target_hp_before} -> {new_hp}).")
                              # Ensure target_id is just the number for the service call
                              npc_instance_id = int(target_id.split("_")[1])
                              await services.apply_damage_to_npc(client, npc_instance_id, new_hp)

                    # 10. Handle Hit Effects
                    if outcome == "solid_hit":
                         results_log.append(f"Applying Staggered status to {target_id}.")
                         if target_type == "player":
                             await services.apply_status_to_character(client, target_id, "Staggered")
                         elif target_type == "npc":
                             npc_instance_id = int(target_id.split("_")[1])
                             # Fetch current statuses before updating
                             try:
                                 current_npc_context = await services.get_npc_context(client, npc_instance_id)
                                 current_statuses = current_npc_context.get("status_effects", [])
                                 if "Staggered" not in current_statuses:
                                     current_statuses.append("Staggered")
                                 await services.apply_status_to_npc(client, npc_instance_id, current_statuses)
                             except HTTPException as status_e:
                                  results_log.append(f"Warning: Failed to apply Staggered status to {target_id}: {status_e.detail}")

                    if outcome == "critical_hit":
                        results_log.append(f"Critical Hit on {target_id}! Applying Minor Injury.")
                        # Placeholder injury logic - needs more robust target location determination
                        injury_location = random.choice(["Head", "Torso", "Arms", "Legs"])
                        sub_loc_map = {"Head": ["Skull", "Face"], "Torso": ["Chest", "Abdomen"], "Arms": ["Shoulder", "Hand"], "Legs": ["Thigh", "Foot"]}
                        injury_sub_location = random.choice(sub_loc_map[injury_location])
                        injury_severity = 2 # Minor Injury

                        try:
                            injury_result = await services.get_injury_effects(client, injury_location, injury_sub_location, injury_severity)
                            effects_to_apply = injury_result.get("effects", [])
                            results_log.append(f"Applying Injury ({injury_result.get('severity_name')} to {injury_sub_location}): Effects={effects_to_apply}")
                            # TODO: Actually apply these effects (likely requires adding them as status effects)
                            # For now, just logging the lookup result.
                        except Exception as injury_e:
                            results_log.append(f"ERROR looking up injury effects: {injury_e}")

                    if new_hp <= 0:
                        results_log.append(f"Target {target_id} defeated!")
                        # Future: Could update target status immediately here

                    success = True # Hit is a successful action
                    # Prepare result dictionary for successful hit
                    hit_result_data = {
                         "success": True,
                         "message": hit_type,
                         "damage_dealt": final_damage_dealt,
                         "target_hp_remaining": new_hp,
                         "log": results_log,
                         "outcome": outcome,
                         "damage_details": damage_details_list
                    }
                    # --- Advance turn after successful action ---
                    if success:
                        logger.debug(f"Action by {actor_id} successful, advancing turn.")
                        await advance_turn(db, combat_id)
                    # --- Return result ---
                    return hit_result_data

                else: # Unknown outcome from rules_engine
                    results_log.append(f"Unknown attack outcome received: {outcome}")
                    success = False # Treat unknown outcome as failure for turn advancement

            except HTTPException as he:
                results_log.append(f"ERROR: Service call failed during attack: {he.detail}")
                success = False
            except Exception as e:
                logger.exception(f"Unexpected error during attack execution by {actor_id}: {e}")
                results_log.append(f"ERROR: Unexpected error during action execution: {e}")
                success = False

    # --- Advance turn after successful action (including 'wait') ---
    if success:
         logger.debug(f"Action '{action_details.action}' by {actor_id} completed, advancing turn.")
         # Avoid double-advancing if NPC attack already advanced it
         if not is_npc_turn:
              await advance_turn(db, combat_id)
         else:
              logger.debug("Skipping advance_turn call as it was likely handled by NPC logic.")

    # --- Determine final return message ---
    final_message = results_log[-1] if results_log else "Action processed."
    if not success and "ERROR" not in final_message:
         final_message = f"Action '{action_details.action}' failed or could not be completed."

    return {"success": success, "message": final_message, "log": results_log}
