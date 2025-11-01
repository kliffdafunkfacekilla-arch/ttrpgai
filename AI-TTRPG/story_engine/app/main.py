from fastapi import Depends, FastAPI, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import logging

from . import crud, models, schemas, services, combat_handler, interaction_handler
from .database import SessionLocal, engine

app = FastAPI(
    title="Story Engine",
    description="Manages campaign state, quests, and orchestrates other services."
)

# Add CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # The origin of the frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter()

logger = logging.getLogger("uvicorn.error")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def read_root():
    return {"status": "Story Engine is running."}

@router.post("/v1/campaigns/", response_model=schemas.Campaign, status_code=201)
def create_campaign(campaign: schemas.CampaignCreate, db: Session = Depends(get_db)):
    return crud.create_campaign(db=db, campaign=campaign)

@router.get("/v1/campaigns/{campaign_id}", response_model=schemas.Campaign)
def read_campaign(campaign_id: int, db: Session = Depends(get_db)):
    db_campaign = crud.get_campaign(db, campaign_id=campaign_id)
    if db_campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return db_campaign

@router.post("/v1/quests/", response_model=schemas.ActiveQuest, status_code=201)
def create_quest(quest: schemas.ActiveQuestCreate, db: Session = Depends(get_db)):
    return crud.create_quest(db=db, quest=quest)

@router.put("/v1/quests/{quest_id}", response_model=schemas.ActiveQuest)
def update_quest(quest_id: int, updates: schemas.ActiveQuestUpdate, db: Session = Depends(get_db)):
    db_quest = crud.update_quest(db, quest_id, updates)
    if db_quest is None:
        raise HTTPException(status_code=404, detail="Quest not found")
    return db_quest

@router.get("/v1/quests/campaign/{campaign_id}", response_model=List[schemas.ActiveQuest])
def read_quests_for_campaign(campaign_id: int, db: Session = Depends(get_db)):
    return crud.get_quests_for_campaign(db, campaign_id)

@router.post("/v1/flags/", response_model=schemas.StoryFlag)
def set_story_flag(flag: schemas.StoryFlagBase, db: Session = Depends(get_db)):
    return crud.set_flag(db=db, flag=flag)

@router.get("/v1/flags/{flag_name}", response_model=schemas.StoryFlag)
def read_story_flag(flag_name: str, db: Session = Depends(get_db)):
    db_flag = crud.get_flag(db, flag_name)
    if db_flag is None:
        raise HTTPException(status_code=404, detail="Flag not found")
    return db_flag

@router.post("/v1/actions/spawn_npc", response_model=Dict)
async def action_spawn_npc(spawn_request: schemas.OrchestrationSpawnNpc):
    try:
        response = await services.spawn_npc_in_world(spawn_request)
        return response
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Error calling world_engine: {e}")

@router.post("/v1/actions/spawn_item", response_model=Dict)
async def action_spawn_item(spawn_request: schemas.OrchestrationSpawnItem):
    try:
        response = await services.spawn_item_in_world(spawn_request)
        return response
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Error calling world_engine: {e}")

@router.get("/v1/context/character/{char_id}")
async def get_character_context(char_id: str):
    try:
        return await services.get_character_context(char_id)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Error calling character_engine: {e}")

@router.get("/v1/context/location/{location_id}", response_model=schemas.OrchestrationWorldContext)
async def get_location_context(location_id: int):
    try:
        return await services.get_world_location_context(location_id)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Error calling world_engine: {e}")

@router.post("/v1/combat/start", response_model=schemas.CombatEncounter, status_code=201, tags=["Combat Orchestration"])
async def api_start_new_combat(start_request: schemas.CombatStartRequest, db: Session = Depends(get_db)):
    logger.info(f"Received request to start combat at location {start_request.location_id}")
    try:
        combat_state = await combat_handler.start_combat(db, start_request)
        if combat_state is None:
             raise HTTPException(status_code=500, detail="Combat handler failed to return state.")
        logger.info(f"Combat started with ID: {combat_state.id}")
        return combat_state
    except HTTPException as he:
         logger.error(f"HTTPException during combat start: {he.detail}")
         raise he
    except Exception as e:
        logger.exception(f"Unexpected error starting combat: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error starting combat: {str(e)}")

@router.post("/v1/combat/{combat_id}/player_action", response_model=schemas.PlayerActionResponse, tags=["Combat Orchestration"])
async def handle_player_combat_action(combat_id: int, action_request: schemas.PlayerActionRequest, db: Session = Depends(get_db)):
    logger.info(f"Received player action for combat {combat_id}: {action_request.dict()}")
    combat = crud.get_combat_encounter(db, combat_id)
    if not combat:
        raise HTTPException(status_code=404, detail="Combat not found")
    player_id = "player_1"
    try:
        action_result = await combat_handler.handle_player_action(db, combat, player_id, action_request)
        logger.info(f"Action result: {action_result.message}")
        return action_result
    except HTTPException as he:
         logger.error(f"HTTPException during player action: {he.detail}")
         raise he
    except Exception as e:
         logger.exception(f"Unexpected error during player action: {e}")
         raise HTTPException(status_code=500, detail=f"Internal server error processing player action: {str(e)}")

@router.post("/v1/combat/{combat_id}/npc_action", response_model=schemas.PlayerActionResponse, summary="Trigger the next NPC action in the turn order", tags=["Combat Orchestration"])
async def post_npc_action(combat_id: int, db: Session = Depends(get_db)):
    combat = crud.get_combat_encounter(db, combat_id)
    if not combat:
        raise HTTPException(status_code=404, detail="Combat encounter not found")
    if combat.is_finished:
        raise HTTPException(status_code=400, detail="Combat is already finished")
    current_actor_id = combat.turn_order[combat.current_turn_index]
    if current_actor_id.startswith("player_"):
        raise HTTPException(status_code=400, detail="It is not an NPC's turn")
    npc_action_request = await combat_handler.determine_npc_action(db, combat, current_actor_id)
    if npc_action_request is None:
        return combat_handler.handle_no_action(db, combat, current_actor_id)
    return await combat_handler.handle_player_action(
        db=db,
        combat=combat,
        actor_id=current_actor_id,
        action=npc_action_request
    )

@router.post("/v1/actions/interact", response_model=schemas.InteractionResponse, tags=["Player Actions"])
async def handle_player_interaction(interaction_request: schemas.InteractionRequest):
    logger.info(f"Received interaction request: {interaction_request.dict()}")
    try:
        result = await interaction_handler.handle_interaction(interaction_request)
        return result
    except HTTPException as he:
        logger.error(f"HTTPException during interaction: {he.detail}")
        raise he
    except Exception as e:
        logger.exception(f"Unexpected error handling interaction: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error handling interaction: {str(e)}")

app.include_router(router)
