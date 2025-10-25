# main.py
from fastapi import FastAPI, HTTPException
from typing import List, Dict
from contextlib import asynccontextmanager
import logging
logger = logging.getLogger("uvicorn.error") # Use uvicorn's logger for visibility
# Use direct imports assuming running from AI-TTRPG folder
from . import core
# Import specific items needed from data_loader
from .data_loader import (
    load_data, # Function for lifespan
    STATS_LIST,
    ALL_SKILLS,
    ABILITY_DATA,
    TALENT_DATA,
    FEATURE_STATS_MAP
)
# Keep the import from .models as is
from .models import (
    SkillCheckRequest, AbilityCheckRequest, TalentLookupRequest,
    RollResult, TalentInfo, FeatureStatsResponse, SkillCategoryResponse,
    AbilitySchoolResponse
)

# --- Lifespan Event for Startup ---
# (Keep the @asynccontextmanager lifespan function AS IS)
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("INFO:     Loading rules data...")
    try:
        load_data() # No change needed here
        print("INFO:     Rules data loaded successfully.")
    except Exception as e:
        print(f"FATAL:    Failed to load rules data on startup: {e}")
        # raise
    yield
    print("INFO:     Shutting down Rules Engine.")

# Create FastAPI app
# (Keep the app = FastAPI(...) line AS IS)
app = FastAPI(
    title="AI-TT RPG Rules Engine",
    description="Stateless rules calculator for the Fulcrum System. (v1)",
    version="1.0.0",
    lifespan=lifespan
)



# --- API Endpoints ---

@app.get("/")
async def get_status():
    """Check if the Rules Engine is running and data is loaded."""
    try:
        # Check if critical data lists/dicts exist and have content
        stats_loaded = bool(STATS_LIST)
        skills_loaded = bool(ALL_SKILLS)
        abilities_loaded = bool(ABILITY_DATA)
        talents_loaded = bool(TALENT_DATA)
        features_loaded = bool(FEATURE_STATS_MAP)

        if not all([stats_loaded, skills_loaded, abilities_loaded, talents_loaded, features_loaded]):
             status_msg = "error - data loading incomplete"
        else:
             status_msg = "online"

        return {
            "status": status_msg,
            "message": f"Fulcrum Rules Engine status: {status_msg}.",
            "stats_loaded_count": len(STATS_LIST) if stats_loaded else 0,
            "skills_loaded_count": len(ALL_SKILLS) if skills_loaded else 0,
            "abilities_loaded_count": len(ABILITY_DATA) if abilities_loaded else 0,
            "talents_loaded": talents_loaded,
            "features_loaded_count": len(FEATURE_STATS_MAP) if features_loaded else 0
        }
    except AttributeError:
         # If data_loader itself failed import or variables don't exist yet
         return {"status": "error - data loader failed", "message": "Critical error during data loading."}


@app.post("/v1/validate/skill_check", response_model=RollResult)
async def api_validate_skill_check(request: SkillCheckRequest):
    """
    Performs a standard d20 Skill Check.
    Returns the roll, total, DC, success state, and SRE trigger.
    """
    try:
        return core.calculate_skill_check(
            stat_mod=request.stat_modifier,
            skill_rank=request.skill_rank,
            dc=request.dc
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating skill check: {e}")

@app.post("/v1/validate/ability_check", response_model=RollResult)
async def api_validate_ability_check(request: AbilityCheckRequest):
    """
    Performs a d20 Ability Check against a Tiered DC.
    """
    try:
        return core.calculate_ability_check(
            rank=request.ability_school_rank,
            stat_mod=request.associated_stat_modifier,
            tier=request.ability_tier
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating ability check: {e}")


@app.get("/v1/lookup/kingdom_feature_stats", response_model=FeatureStatsResponse)
async def api_get_feature_stats(feature_name: str):
    """Looks up the stat modifications for a specific Kingdom Feature by its name."""
    logger.info(f"--- Endpoint api_get_feature_stats received request for: '{feature_name}'")
    try:
        # Ensure the imported map is loaded and not empty
        if not FEATURE_STATS_MAP: # Access the imported variable directly
             logger.error("FEATURE_STATS_MAP is not loaded or empty!")
             raise HTTPException(status_code=503, detail="Feature map not loaded.")

        # Call the core function AND PASS the map directly
        # The core function still needs the map passed as an argument
        return core.get_kingdom_feature_stats(feature_name, FEATURE_STATS_MAP) # Pass the imported variable

    except ValueError as e:
        logger.error(f"Lookup failed in core function: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
         logger.exception(f"Unexpected error in api_get_feature_stats for '{feature_name}': {e}")
         raise HTTPException(status_code=500, detail=f"Internal error looking up feature: {e}")

@app.post("/v1/lookup/talents", response_model=List[TalentInfo])
async def api_lookup_talents(request: TalentLookupRequest):
    """
    Gets all talents a character is eligible for based on their stats and skills.
    Corrects for 'Constitution' vs 'Vitality' from data files.
    """
    try:
        # Ensure core function handles potential missing keys gracefully if needed
        return core.find_eligible_talents(request.stats, request.skills)
    except Exception as e:
        # Log the actual error here for debugging
        print(f"Error in api_lookup_talents: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error looking up talents: {e}")

@app.get("/v1/lookup/skills_by_category", response_model=SkillCategoryResponse)
async def api_get_skills_by_category():
    """
    Returns all 72 skills, grouped by their 6 core categories.
    Essential for the Character Engine's 6x2 background rule.
    """
    try:
        return {"categories": core.get_skills_by_category()}
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Internal error getting skills by category: {e}")

@app.get("/v1/lookup/ability_school/{school_name}", response_model=AbilitySchoolResponse)
async def api_get_ability_school(school_name: str):
    """
    Returns all T1-T9 abilities and metadata for a single school.
    """
    try:
        # Check data loaded status first (optional, but safer)
        if not ABILITY_DATA:
            raise HTTPException(status_code=503, detail="Ability data not loaded yet.")

        if school_name not in ABILITY_DATA:
            raise HTTPException(status_code=404, detail=f"Ability school '{school_name}' not found.")

        data = ABILITY_DATA[school_name]
        # Ensure response matches Pydantic model structure
        return AbilitySchoolResponse(
            school=school_name,
            resource_pool=data.get("resource_pool", "Unknown"),
            associated_stat=data.get("associated_stat", "Unknown"),
            tiers=data.get("tiers", [])
        )
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Internal error getting ability school data: {e}")

@app.get("/v1/lookup/all_stats", response_model=List[str])
async def api_get_all_stats():
    """Returns the list of the 12 official stat names."""
    try:
        if not STATS_LIST:
             raise HTTPException(status_code=503, detail="Stats list not loaded yet.")
        return STATS_LIST
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Internal error getting stats list: {e}")

@app.get("/v1/lookup/all_skills", response_model=Dict[str, Dict[str, str]])
async def api_get_all_skills():
    """Returns the master map of all 72 skills with their category and governing stat."""
    try:
        if not ALL_SKILLS:
             raise HTTPException(status_code=503, detail="Skills data not loaded yet.")
        return ALL_SKILLS
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Internal error getting skills data: {e}")

@app.get("/v1/lookup/all_ability_schools", response_model=List[str])
async def api_get_all_ability_schools():
    """Returns the list of the 12 official ability school names."""
    logger.info("Received request for /v1/lookup/all_ability_schools") # Make sure logger is defined or remove this line
    try:
        # Check if the data dictionary is populated
        if not ABILITY_DATA or not isinstance(ABILITY_DATA, dict):
             # logger.error(f"ABILITY_DATA is invalid or empty. Type: {type(ABILITY_DATA)}") # Make sure logger is defined or remove this line
             raise HTTPException(status_code=503, detail="Ability data not loaded correctly.")

        # Try getting the keys
        keys = list(ABILITY_DATA.keys())
        logger.info(f"Successfully retrieved ability school keys: {keys}")
        return keys

    except HTTPException as e: # Re-raise known HTTP errors
        logger.warning(f"HTTPException in api_get_all_ability_schools: {e.detail}")
        raise e
    except Exception as e: # Catch unexpected errors
         logger.exception(f"Unexpected ERROR in api_get_all_ability_schools: {e}")
         raise HTTPException(status_code=500, detail=f"Internal server error getting ability schools list.")