# AI-TTRPG/story_engine/app/combat_handler.py
from sqlalchemy.orm import Session
from fastapi import HTTPException
import httpx
from typing import List, Dict, Any, Tuple, Optional
from . import crud, models, schemas, services
import random
import re
import logging

logger = logging.getLogger("uvicorn.error")

def _find_spawn_points(map_data: List[List[int]], num_points: int) -> List[List[int]]:
    if not map_data:
        logger.warning("Map data is empty, cannot find spawn points.")
        return [[5, 5]] * num_points
    valid_spawns = []
    height = len(map_data)
    width = len(map_data[0]) if height > 0 else 0
    for y in range(height):
        for x in range(width):
            tile_id = map_data[y][x]
            if tile_id in [0, 3]: # 0=Grass, 3=Stone Floor
                valid_spawns.append([x, y])
    if not valid_spawns:
        logger.warning("No valid spawn tiles found on map. Falling back to default.")
        return [[5, 5]] * num_points
    random.shuffle(valid_spawns)
    return [valid_spawns[i % len(valid_spawns)] for i in range(num_points)]

def _extract_initiative_stats(stats_dict: Dict) -> Dict:
    return {
        "endurance": stats_dict.get("Endurance", 10),
        "agility": stats_dict.get("Agility", 10),
        "fortitude": stats_dict.get("Fortitude", 10),
        "logic": stats_dict.get("Logic", 10),
        "intuition": stats_dict.get("Intuition", 10),
        "willpower": stats_dict.get("Willpower", 10),
    }

async def start_combat(db: Session, start_request: schemas.CombatStartRequest) -> models.CombatEncounter:
    logger.info(f"Starting combat at location {start_request.location_id}")
    participants_data: List[Tuple[str, str, int]] = []
    spawned_npc_details: List[Dict] = []
    async with httpx.AsyncClient() as client:
        spawn_points = []
        try:
            location_context = await services.get_world_location_context(client, start_request.location_id)
            map_data = location_context.get("generated_map_data")
            num_npcs = len(start_request.npc_template_ids)
            spawn_points = _find_spawn_points(map_data, num_npcs)
            logger.info(f"Found {len(spawn_points)} spawn points for {num_npcs} NPCs.")
        except Exception as e:
            logger.exception(f"Error finding spawn points: {e}. NPCs will spawn at default location.")
            spawn_points = [[5, 5]] * len(start_request.npc_template_ids)
        logger.info(f"Spawning NPCs: {start_request.npc_template_ids}")
        for i, template_id in enumerate(start_request.npc_template_ids):
            try:
                coords = spawn_points[i]
                spawn_data = schemas.OrchestrationSpawnNpc(
                    template_id=template_id,
                    location_id=start_request.location_id,
                    coordinates=coords
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
        logger.info(f"Rolling initiative for players: {start_request.player_ids}")
        for player_id_str in start_request.player_ids:
            try:
                if not isinstance(player_id_str, str) or not player_id_str.startswith("player_"):
                     logger.warning(f"Skipping invalid player ID format: {player_id_str}")
                     continue
                char_context = await services.get_character_context(client, player_id_str)
                player_stats = char_context.get("character_sheet", {}).get("stats", {})
                stats_for_init = _extract_initiative_stats(player_stats)
                init_result = await services.roll_initiative(client, **stats_for_init)
                initiative_total = init_result.get("total_initiative", 0)
                participants_data.append((player_id_str, "player", initiative_total))
                logger.info(f"Player {player_id_str} initiative: {initiative_total}")
            except HTTPException as e:
                logger.error(f"Failed to get context or roll initiative for Player {player_id_str}: {e.detail}")
                participants_data.append((player_id_str, "player", 0))
            except Exception as e:
                logger.exception(f"Unexpected error processing Player {player_id_str}: {e}")
                participants_data.append((player_id_str, "player", 0))
        logger.info(f"Rolling initiative for {len(spawned_npc_details)} spawned NPCs.")
        for npc_data in spawned_npc_details:
            npc_id = npc_data.get('id')
            if npc_id is None:
                logger.warning("Spawned NPC data missing ID, cannot roll initiative.")
                continue
            actor_id_str = f"npc_{npc_id}"
            try:
                npc_context = await services.get_npc_context(client, npc_id)
                npc_stats = npc_context.get("stats", {})
                if not npc_stats:
                     logger.warning(f"NPC {npc_id} context missing stats, using defaults for initiative.")
                     npc_stats = {}
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
    if not participants_data:
        raise HTTPException(status_code=400, detail="Cannot start combat: No valid participants found.")
    participants_data.sort(key=lambda x: x[2], reverse=True)
    turn_order = [p[0] for p in participants_data]
    logger.info(f"Final Turn Order: {turn_order}")
    try:
        db_combat = crud.create_combat_encounter(db, location_id=start_request.location_id, turn_order=turn_order)
        logger.info(f"Created CombatEncounter record with ID: {db_combat.id}")
    except Exception as e:
        logger.exception(f"Failed to create combat encounter in database: {e}")
        raise HTTPException(status_code=500, detail="Failed to save combat encounter state.")
    for actor_id, actor_type, initiative in participants_data:
        try:
            crud.create_combat_participant(db, combat_id=db_combat.id, actor_id=actor_id, actor_type=actor_type, initiative=initiative)
        except Exception as e:
            logger.exception(f"Failed to save participant {actor_id} to database: {e}")
    logger.info(f"Combat started successfully with ID {db_combat.id}")
    db.refresh(db_combat)
    return db_combat

async def get_actor_context(client: httpx.AsyncClient, actor_id: str) -> Tuple[str, Dict]:
    logger.debug(f"Getting context for actor: {actor_id}")
    if actor_id.startswith("player_"):
        try:
            context_data = await services.get_character_context(client, actor_id)
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
    if actor_context.get("character_sheet"):
        return actor_context.get("character_sheet", {}).get("stats", {}).get(stat_name, 10)
    else:
         stats = actor_context.get("stats", {})
         if stat_name in stats:
             return stats[stat_name]
         return actor_context.get("character_sheet", {}).get("stats", {}).get(stat_name, 10)

def get_skill_rank(actor_context: Dict, skill_name: str) -> int:
    if actor_context.get("character_sheet"):
        skills = actor_context.get("character_sheet", {}).get("skills", {})
        skill_data = skills.get(skill_name)
        if isinstance(skill_data, dict):
            return skill_data.get("rank", 0)
        elif isinstance(skill_data, int):
            return skill_data
        return 0
    else:
        skills = actor_context.get("skills", {})
        if isinstance(skills, dict):
             skill_data = skills.get(skill_name)
             if isinstance(skill_data, int):
                  return skill_data
        return 0

def get_equipped_weapon(actor_context: Dict) -> Tuple[Optional[str], Optional[str]]:
    logger.warning(f"Using placeholder weapon for actor {actor_context.get('id', actor_context.get('name', 'Unknown'))}")
    if actor_context.get("character_sheet"):
         return "Resolute Edges", "melee"
    else:
         if "melee_heavy" in actor_context.get("template_id", ""):
             return "Heavy Bludgeons", "melee"
         elif "ranged" in actor_context.get("template_id", ""):
              return "Short Bow", "ranged"
         return "Unarmed & Fist Weapons", "melee"

def get_equipped_armor(actor_context: Dict) -> Optional[str]:
    logger.warning(f"Using placeholder armor for actor {actor_context.get('id', actor_context.get('name', 'Unknown'))}")
    if actor_context.get("character_sheet"):
        return "Medium Armor"
    else:
        if "heavy_armor" in actor_context.get("template_id", ""):
             return "Heavy Armor"
        elif "evasive" in actor_context.get("template_id", ""):
             return "Light Armor"
        return "Medium Armor"

async def check_combat_end_condition(db: Session, combat: models.CombatEncounter) -> bool:
    players_alive = False
    npcs_alive = False
    async with httpx.AsyncClient() as client:
        for p in combat.participants:
            try:
                actor_type, context = await get_actor_context(client, p.actor_id)
                hp = 1
                if actor_type == "player":
                    hp = context.get("character_sheet", {}).get("combat_stats", {}).get("current_hp", 1)
                    if hp > 0: players_alive = True
                elif actor_type == "npc":
                    hp = context.get("current_hp", 1)
                    if hp > 0: npcs_alive = True
            except HTTPException as e:
                logger.warning(f"Could not get context for participant {p.actor_id} during end check: {e.detail}. Assuming defeated.")
    if not players_alive or not npcs_alive:
        end_status = "npcs_win" if not players_alive else "players_win"
        combat.status = end_status
        db.commit()
        logger.info(f"Combat {combat.id} ended: {end_status}")
        return True
    return False

async def determine_npc_action(db: Session, combat: models.CombatEncounter, npc_actor_id: str) -> Optional[schemas.PlayerActionRequest]:
    async with httpx.AsyncClient() as client:
        try:
            _, npc_context = await get_actor_context(client, npc_actor_id)
        except HTTPException:
            logger.error(f"Could not get context for NPC {npc_actor_id} to determine action.")
            return None
        behavior_tags = npc_context.get("behavior_tags", [])
        npc_current_hp = npc_context.get("current_hp", 1)
        npc_max_hp = npc_context.get("max_hp", 1)
        living_players = []
        for p in combat.participants:
            if p.actor_id.startswith("player_"):
                try:
                    _, p_context = await get_actor_context(client, p.actor_id)
                    if p_context.get("character_sheet", {}).get("combat_stats", {}).get("current_hp", 0) > 0:
                        living_players.append(p_context)
                except HTTPException:
                    continue
        if not living_players:
            logger.info(f"NPC {npc_actor_id} found no living players to target.")
            return None
        target_id = None
        action_type = "attack"
        if "cowardly" in behavior_tags and npc_current_hp < npc_max_hp * 0.3:
            action_type = "wait"
        elif "targets_weakest" in behavior_tags:
            living_players.sort(key=lambda p: p["character_sheet"]["combat_stats"]["current_hp"])
            target_id = f"player_{living_players[0]['id']}"
        else:
            target_id = f"player_{random.choice(living_players)['id']}"
        if action_type == "attack" and target_id:
            return schemas.PlayerActionRequest(action="attack", target_id=target_id)
        else:
            return None

def handle_no_action(db: Session, combat: models.CombatEncounter, actor_id: str) -> schemas.PlayerActionResponse:
    log = [f"{actor_id} waits."]
    combat.current_turn_index = (combat.current_turn_index + 1) % len(combat.turn_order)
    db.commit()
    db.refresh(combat)
    return schemas.PlayerActionResponse(
        success=True,
        message=f"{actor_id} took no action.",
        log=log,
        new_turn_index=combat.current_turn_index,
        combat_over=False
    )

async def handle_player_action(db: Session, combat: models.CombatEncounter, actor_id: str, action: schemas.PlayerActionRequest) -> schemas.PlayerActionResponse:
    log = []
    current_actor_id = combat.turn_order[combat.current_turn_index]
    if actor_id != current_actor_id:
        raise HTTPException(status_code=403, detail=f"It is not {actor_id}'s turn.")
    if action.action == "wait":
        return handle_no_action(db, combat, actor_id)
    if action.action != "attack":
        log.append(f"Action '{action.action}' not fully implemented. Waiting instead.")
        return handle_no_action(db, combat, actor_id)
    target_id = action.target_id
    if not target_id:
        raise HTTPException(status_code=400, detail="Attack action requires a target_id.")
    async with httpx.AsyncClient() as client:
        try:
            _, attacker_context = await get_actor_context(client, actor_id)
            target_type, defender_context = await get_actor_context(client, target_id)
            log.append(f"{actor_id} targets {target_id} with an attack.")
            hp = 0
            if target_type == "player":
                hp = defender_context.get("character_sheet", {}).get("combat_stats", {}).get("current_hp", 0)
            else:
                hp = defender_context.get("current_hp", 0)
            if hp <= 0:
                raise HTTPException(status_code=400, detail=f"Target {target_id} is already defeated.")
            weapon_category, weapon_type = get_equipped_weapon(attacker_context)
            armor_category = get_equipped_armor(defender_context)
            weapon_data = await services.get_weapon_data(client, weapon_category, weapon_type)
            armor_data = await services.get_armor_data(client, armor_category) if armor_category else {"dr": 0, "skill_stat": "Agility", "skill": "Natural/Unarmored"}
            attack_params = {
                "attacker_attacking_stat_score": get_stat_score(attacker_context, weapon_data["skill_stat"]),
                "attacker_skill_rank": get_skill_rank(attacker_context, weapon_data["skill"]),
                "defender_armor_stat_score": get_stat_score(defender_context, armor_data["skill_stat"]),
                "defender_armor_skill_rank": get_skill_rank(defender_context, armor_data["skill"]),
                "attacker_misc_bonus": 0, "attacker_misc_penalty": 0, "defender_misc_bonus": 0, "defender_misc_penalty": 0,
                "defender_weapon_penalty": weapon_data.get("penalty", 0)
            }
            attack_result = await services.roll_contested_attack(client, attack_params)
            log.append(f"Attack Roll: Attacker ({attack_result['attacker_final_total']}) vs Defender ({attack_result['defender_final_total']}). Margin: {attack_result['margin']}.")
            outcome = attack_result.get("outcome")
            if outcome in ["miss", "critical_fumble"]:
                log.append(f"Result: {actor_id} misses {target_id}.")
            elif outcome in ["hit", "solid_hit", "critical_hit"]:
                log.append(f"Result: {actor_id} hits {target_id}!")
                damage_params = {
                    "base_damage_roll": weapon_data["damage"],
                    "damage_stat_score": get_stat_score(attacker_context, weapon_data["skill_stat"]),
                    "misc_damage_bonus": 0,
                    "target_damage_reduction": armor_data["dr"]
                }
                damage_result = await services.calculate_damage(client, damage_params)
                final_damage = damage_result.get("final_damage", 0)
                log.append(f"Damage: {final_damage}")
                if final_damage > 0:
                    if target_type == "player":
                        await services.apply_damage_to_character(client, target_id, final_damage)
                    else: # npc
                        npc_instance_id = int(target_id.split("_")[1])
                        new_hp = defender_context.get("current_hp", 0) - final_damage
                        await services.apply_damage_to_npc(client, npc_instance_id, new_hp)
            else:
                log.append(f"Unknown outcome: {outcome}")
            combat.current_turn_index = (combat.current_turn_index + 1) % len(combat.turn_order)
            combat_over = await check_combat_end_condition(db, combat)
            db.commit()
            db.refresh(combat)
            return schemas.PlayerActionResponse(
                success=True,
                message=f"{actor_id} performed {action.action}.",
                log=log,
                new_turn_index=combat.current_turn_index,
                combat_over=combat_over
            )
        except HTTPException as he:
            raise he
        except Exception as e:
            logger.exception(f"Unexpected error in handle_player_action for {actor_id}: {e}")
            raise HTTPException(status_code=500, detail="An unexpected error occurred while processing the action.")
