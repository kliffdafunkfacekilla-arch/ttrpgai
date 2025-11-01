# main.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
from contextlib import asynccontextmanager
import logging
logger = logging.getLogger("uvicorn.error")

# Use relative imports for local modules
from . import core
from . import data_loader
from . import models
from .models import (
    SkillCheckRequest, AbilityCheckRequest, TalentLookupRequest,
    RollResult, TalentInfo, FeatureStatsResponse, SkillCategoryResponse,
    AbilitySchoolResponse
)

# --- Lifespan Event for Startup ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load rules data on startup and store in app.state."""
    print("INFO:     Loading rules data...")
    try:
        loaded_rules = data_loader.load_data()
        # Store each loaded component onto app.state
        app.state.stats_list = loaded_rules.get('stats_list', [])
        app.state.skill_categories = loaded_rules.get('skill_categories', {})
        app.state.all_skills = loaded_rules.get('all_skills', {})
        app.state.ability_data = loaded_rules.get('ability_data', {})
        app.state.talent_data = loaded_rules.get('talent_data', {})
        app.state.feature_stats_map = loaded_rules.get('feature_stats_map', {})
        app.state.melee_weapons = loaded_rules.get('melee_weapons', {})
        app.state.ranged_weapons = loaded_rules.get('ranged_weapons', {})
        app.state.armor = loaded_rules.get('armor', {})
        app.state.injury_effects = loaded_rules.get('injury_effects', {})
        app.state.status_effects = loaded_rules.get('status_effects', {})
        app.state.equipment_category_to_skill_map = loaded_rules.get('equipment_category_to_skill_map', {})
        print("INFO:     Rules data loaded successfully and stored in app.state.")
    except Exception as e:
        print(f"FATAL:    Failed to load rules data on startup: {e}")
        # Initialize state with empty values on failure to prevent crashes later
        app.state.stats_list = []
        app.state.skill_categories = {}
        app.state.all_skills = {}
        app.state.ability_data = {}
        app.state.talent_data = {}
        app.state.feature_stats_map = {}
        app.state.melee_weapons = {}
        app.state.ranged_weapons = {}
        app.state.armor = {}
        app.state.injury_effects = {}
        app.state.status_effects = {}
        # Optionally re-raise to prevent server start on load failure
        # raise
    yield
    print("INFO:     Shutting down Rules Engine.")

# Create FastAPI app
app = FastAPI(
    title="AI-TT RPG Rules Engine",
    description="Stateless rules calculator for the Fulcrum System. (v1)",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # The origin of the frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Helper Function (Dependency) to Check State ---
def check_state_loaded(request: Request):
    """Dependency raises 503 if essential data isn't loaded in app.state"""
    required_attrs = ['stats_list', 'all_skills', 'ability_data', 'talent_data', 'feature_stats_map']
    missing = [attr for attr in required_attrs if not hasattr(request.app.state, attr) or not getattr(request.app.state, attr)]
    if missing:
        detail = f"Rules data not available. Missing components: {', '.join(missing)}. Server might be starting or encountered load error."
        logger.error(f"State check failed: {detail}")
        raise HTTPException(status_code=503, detail=detail)

# --- API Endpoints (Modified to use app.state) ---

@app.get("/")
async def get_status(request: Request):
    """Check if the Rules Engine is running and data is loaded."""
    try:
        # Access data via app.state
        stats_list = getattr(request.app.state, 'stats_list', [])
        all_skills = getattr(request.app.state, 'all_skills', {})
        ability_data = getattr(request.app.state, 'ability_data', {})
        talent_data = getattr(request.app.state, 'talent_data', {})
        feature_stats_map = getattr(request.app.state, 'feature_stats_map', {})
        melee_weapons = getattr(request.app.state, 'melee_weapons', {})
        ranged_weapons = getattr(request.app.state, 'ranged_weapons', {})
        armor = getattr(request.app.state, 'armor', {})
        injury_effects = getattr(request.app.state, 'injury_effects', {})


        stats_loaded = bool(stats_list)
        skills_loaded = bool(all_skills)
        abilities_loaded = bool(ability_data)
        talents_loaded = bool(talent_data)
        features_loaded = bool(feature_stats_map)
        melee_weapons_loaded = bool(melee_weapons)
        ranged_weapons_loaded = bool(ranged_weapons)
        armor_loaded = bool(armor)
        injury_effects_loaded = bool(injury_effects)

        if not all([stats_loaded, skills_loaded, abilities_loaded, talents_loaded, features_loaded, melee_weapons_loaded, ranged_weapons_loaded, armor_loaded, injury_effects_loaded]):
             status_msg = "error - data loading incomplete"
        else:
             status_msg = "online"

        return {
            "status": status_msg,
            "message": f"Fulcrum Rules Engine status: {status_msg}.",
            "stats_loaded_count": len(stats_list),
            "skills_loaded_count": len(all_skills),
            "abilities_loaded_count": len(ability_data),
            "talents_loaded": talents_loaded, # Keep simple boolean for TALENT_DATA check
            "features_loaded_count": len(feature_stats_map),
            "melee_weapons_loaded_count": len(melee_weapons),
            "ranged_weapons_loaded_count": len(ranged_weapons),
            "armor_loaded_count": len(armor),
            "injury_effects_loaded_count": len(injury_effects)
        }
    except Exception as e:
         logger.exception(f"Error in get_status accessing app.state: {e}")
         return {"status": "error - unknown", "message": f"An unexpected error occurred: {e}"}


@app.post("/v1/validate/skill_check", response_model=RollResult)
async def api_validate_skill_check(request_data: SkillCheckRequest): # Renamed variable
    """Performs a standard d20 Skill Check."""
    try:
        return core.calculate_skill_check(
            stat_mod=request_data.stat_modifier,
            skill_rank=request_data.skill_rank,
            dc=request_data.dc
        )
    except Exception as e:
        logger.exception(f"Error in api_validate_skill_check: {e}")
        raise HTTPException(status_code=500, detail=f"Error calculating skill check: {e}")

@app.post("/v1/validate/ability_check", response_model=RollResult)
async def api_validate_ability_check(request_data: AbilityCheckRequest): # Renamed variable
    """Performs a d20 Ability Check."""
    try:
        return core.calculate_ability_check(
            rank=request_data.ability_school_rank,
            stat_mod=request_data.associated_stat_modifier,
            tier=request_data.ability_tier
        )
    except Exception as e:
        logger.exception(f"Error in api_validate_ability_check: {e}")
        raise HTTPException(status_code=500, detail=f"Error calculating ability check: {e}")

@app.get("/v1/lookup/kingdom_feature_stats", response_model=FeatureStatsResponse)
async def api_get_feature_stats(request: Request, feature_name: str):
    """Looks up stat mods for a Kingdom Feature."""
    check_state_loaded(request) # Run dependency check
    logger.info(f"--- Endpoint api_get_feature_stats received request for: '{feature_name}'")
    try:
        # Pass the map from app.state to the core function
        return core.get_kingdom_feature_stats(feature_name, request.app.state.feature_stats_map)
    except ValueError as e: # Catch error from core function if feature not in map
        logger.error(f"Lookup failed in core function: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
         logger.exception(f"Unexpected error in api_get_feature_stats for '{feature_name}': {e}")
         raise HTTPException(status_code=500, detail=f"Internal error looking up feature: {e}")

@app.post("/v1/lookup/talents", response_model=List[TalentInfo])
async def api_lookup_talents(req_data: TalentLookupRequest, request: Request):
    """Gets eligible talents based on stats and skills."""
    check_state_loaded(request) # Run dependency check
    try:
        # Pass necessary data from app.state to the core function
        return core.find_eligible_talents(
            stats_in=req_data.stats,
            skills_in=req_data.skills,
            talent_data=request.app.state.talent_data,
            stats_list=request.app.state.stats_list,
            all_skills_map=request.app.state.all_skills
        )
    except Exception as e:
        logger.exception(f"Error in api_lookup_talents: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error looking up talents: {e}")

@app.get("/v1/lookup/skills_by_category", response_model=SkillCategoryResponse)
async def api_get_skills_by_category(request: Request):
    """Returns skills grouped by category."""
    check_state_loaded(request) # Run dependency check
    try:
        # Pass necessary data from app.state to the core function
        return {"categories": core.get_skills_by_category(request.app.state.skill_categories)}
    except Exception as e:
         logger.exception(f"Error in api_get_skills_by_category: {e}")
         raise HTTPException(status_code=500, detail=f"Internal error getting skills by category: {e}")

@app.get("/v1/lookup/ability_school/{school_name}", response_model=AbilitySchoolResponse)
async def api_get_ability_school(request: Request, school_name: str):
    """Returns data for a single ability school."""
    check_state_loaded(request) # Run dependency check
    try:
        ability_data = request.app.state.ability_data # Get from state
        if school_name not in ability_data:
            raise HTTPException(status_code=404, detail=f"Ability school '{school_name}' not found.")
        data = ability_data[school_name]
        # Ensure response matches Pydantic model structure
        return AbilitySchoolResponse(
            school=school_name,
            # Check both keys for flexibility, default to Unknown
            resource_pool=data.get("resource_pool", data.get("resource", "Unknown")),
            associated_stat=data.get("associated_stat", "Unknown"),
            tiers=data.get("tiers", [])
        )
    except Exception as e:
         logger.exception(f"Error in api_get_ability_school for '{school_name}': {e}")
         raise HTTPException(status_code=500, detail=f"Internal error getting ability school data: {e}")

@app.get("/v1/lookup/all_stats", response_model=List[str])
async def api_get_all_stats(request: Request):
    """Returns the list of the 12 official stat names."""
    check_state_loaded(request) # Run dependency check
    return request.app.state.stats_list # Get from state

@app.get("/v1/lookup/all_skills", response_model=Dict[str, Dict[str, str]])
async def api_get_all_skills(request: Request):
    """Returns the master map of all 72 skills."""
    check_state_loaded(request) # Run dependency check
    return request.app.state.all_skills # Get from state

@app.get("/v1/lookup/all_ability_schools", response_model=List[str])
async def api_get_all_ability_schools(request: Request):
    """Returns the list of the 12 official ability school names."""
    check_state_loaded(request) # Run dependency check
    logger.info("Received request for /v1/lookup/all_ability_schools")
    try:
        ability_data = request.app.state.ability_data # Get from state
        keys = list(ability_data.keys())
        logger.info(f"Successfully retrieved ability school keys: {keys}")
        return keys
    except Exception as e:
         logger.exception(f"Unexpected ERROR in api_get_all_ability_schools: {e}")
         raise HTTPException(status_code=500, detail=f"Internal server error getting ability schools list.")


# ADD THIS ENDPOINT
@app.post("/v1/calculate/base_vitals", response_model=models.BaseVitalsResponse, tags=["Combat Calculations"])
async def api_calculate_base_vitals(request_data: models.BaseVitalsRequest):
    """
    Calculates Max HP and all 6 Resource Pools based on a character's stats.
    Called by character_engine during character creation.
    """
    logger.info(f"Received base vitals calculation request.")
    try:
        result = core.calculate_base_vitals(request_data.stats)
        logger.info(f"Calculated base vitals: HP={result.max_hp}")
        return result
    except ValueError as ve:
        logger.warning(f"Validation error during base vitals calculation: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.exception(f"Error calculating base vitals: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error calculating base vitals: {str(e)}")


@app.post("/v1/roll/initiative", response_model=models.InitiativeResponse, tags=["Combat Rolls"])
async def api_roll_initiative(request_data: models.InitiativeRequest):
    """
    Rolls initiative based on the provided attribute scores according to Fulcrum rules.
    Requires Endurance(B), Agility(D), Fortitude(F), Logic(H), Intuition(J), Willpower(L).
    """
    logger.info(f"Received initiative roll request with data: {request_data.dict()}")
    try:
        # The core.calculate_initiative function is self-contained and doesn't rely
        # on loaded data files, so no need for check_state_loaded here.
        result = core.calculate_initiative(request_data)
        logger.info(f"Calculated initiative result: {result.dict()}")
        return result
    except Exception as e:
        logger.exception(f"Error calculating initiative: {e}") # Use logger.exception for traceback
        # Provide a more specific error message if possible
        raise HTTPException(status_code=500, detail=f"Internal server error calculating initiative: {str(e)}")


# ADD THIS ENDPOINT
@app.post("/v1/roll/contested_attack", response_model=models.ContestedAttackResponse, tags=["Combat Rolls"])
async def api_roll_contested_attack(request_data: models.ContestedAttackRequest):
    """
    Performs a contested attack roll based on Fulcrum rules.
    Requires attacker's attacking stat/skill and defender's armor stat/skill, plus weapon penalty.
    Determines outcome: critical_fumble, miss, hit, solid_hit (margin >= 5), critical_hit (nat 20).
    """
    logger.info(f"Received contested attack roll request.")
    # Log request data carefully if needed, avoid logging sensitive info in production
    # logger.debug(f"Request data: {request_data.dict()}")
    try:
        result = core.calculate_contested_attack(request_data)
        logger.info(f"Calculated contested attack result: Outcome={result.outcome}, Margin={result.margin}")
        return result
    except ValueError as ve: # Catch potential validation errors passed up
        logger.warning(f"Validation error during contested attack: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.exception(f"Error calculating contested attack: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error calculating contested attack: {str(e)}")


# ADD THIS ENDPOINT
@app.post("/v1/calculate/damage", response_model=models.DamageResponse, tags=["Combat Calculations"])
async def api_calculate_damage(request_data: models.DamageRequest):
    """
    Calculates final damage from a dice roll, stat, bonus, and target DR.
    """
    logger.info(f"Received damage calculation request.")
    try:
        result = core.calculate_damage(request_data)
        logger.info(f"Calculated damage result: {result.dict()}")
        return result
    except ValueError as ve:
        logger.warning(f"Validation error during damage calculation: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.exception(f"Error calculating damage: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error calculating damage: {str(e)}")


@app.get("/v1/lookup/melee_weapon/{category_name}", response_model=Dict[str, Any], tags=["Lookups"])
async def api_get_melee_weapon(request: Request, category_name: str):
    """Looks up the stats for a specific melee weapon category."""
    check_state_loaded(request)
    weapons = getattr(request.app.state, 'melee_weapons', {})
    if category_name in weapons:
        return weapons[category_name]
    raise HTTPException(status_code=404, detail=f"Melee weapon category '{category_name}' not found.")

@app.get("/v1/lookup/ranged_weapon/{category_name}", response_model=Dict[str, Any], tags=["Lookups"])
async def api_get_ranged_weapon(request: Request, category_name: str):
    """Looks up the stats for a specific ranged weapon category."""
    check_state_loaded(request)
    weapons = getattr(request.app.state, 'ranged_weapons', {})
    if category_name in weapons:
        return weapons[category_name]
    raise HTTPException(status_code=404, detail=f"Ranged weapon category '{category_name}' not found.")

@app.get("/v1/lookup/armor/{category_name}", response_model=Dict[str, Any], tags=["Lookups"])
async def api_get_armor(request: Request, category_name: str):
    """Looks up the stats for a specific armor category."""
    check_state_loaded(request)
    armor = getattr(request.app.state, 'armor', {})
    if category_name in armor:
        return armor[category_name]
    raise HTTPException(status_code=404, detail=f"Armor category '{category_name}' not found.")


@app.get("/v1/lookup/skill_for_category/{category_name}", response_model=str, tags=["Lookups"])
async def api_get_skill_for_category(request: Request, category_name: str):
    """Looks up the skill for a given equipment category."""
    check_state_loaded(request)
    skill_map = getattr(request.app.state, 'equipment_category_to_skill_map', {})
    try:
        return core.get_skill_for_category(category_name, skill_map)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/v1/lookup/injury_effects", response_model=models.InjuryEffectResponse, tags=["Lookups"])
async def api_get_injury_effects(request_data: models.InjuryLookupRequest, request: Request):
    """Looks up the mechanical effects of a specific injury."""
    check_state_loaded(request)
    try:
        return core.get_injury_effects(request_data, request.app.state.injury_effects)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Error in api_get_injury_effects: {e}")
        raise HTTPException(status_code=500, detail="Internal server error looking up injury effects.")


@app.get("/v1/lookup/status_effect/{status_name}", response_model=models.StatusEffectResponse, tags=["Lookups"])
async def api_get_status_effect(status_name: str, request: Request):
    """Looks up the definition and effects for a status by name (e.g., 'Staggered', 'Bleeding')."""

    # Verify status data loaded during startup
    # Accessing via app.state where data_loader placed it
    loaded_statuses = getattr(request.app.state, 'status_effects', None)
    if loaded_statuses is None: # Check if attribute exists at all
        raise HTTPException(status_code=503, detail="Status effects data structure not initialized in app state.")
    if not loaded_statuses: # Check if it's empty (e.g., file not found or empty)
        # Logged warning during startup, return appropriate error now
        raise HTTPException(status_code=404, detail="Status effects data is not loaded or is empty. Check server logs.")

    logger.info(f"Looking up status effect: {status_name}")
    try:
        # Call the core logic function
        result = core.get_status_effect(status_name, request.app.state.status_effects)
        return result
    except ValueError as e: # Catch 'not found' or data structure errors from core function
        logger.warning(f"Status effect lookup failed for '{status_name}': {e}")
        # Use 404 if it's a 'not found' error, 400/500 for data issues
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        else: # Likely a data structure mismatch
            raise HTTPException(status_code=500, detail=f"Data error retrieving status '{status_name}': {e}")
    except Exception as e:
        logger.exception(f"Unexpected error looking up status effect '{status_name}': {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error looking up status effect: {str(e)}")
