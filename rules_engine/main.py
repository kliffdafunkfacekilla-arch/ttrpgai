# main.py
from fastapi import FastAPI, HTTPException, Depends
from typing import List, Dict, Any

# Import our custom models and logic
import core
import data_loader
from models import (
    SkillCheckRequest, AbilityCheckRequest, TalentLookupRequest,
    RollResult, TalentInfo, FeatureStatsResponse, SkillCategoryResponse,
    AbilitySchoolResponse
)

# Create the FastAPI app
app = FastAPI(
    title="AI-TTRPG Rules Engine",
    description="Stateless rules calculator for the Fulcrum System. (v1)",
    version="1.0.0"
)

# --- Server Startup Event ---

@app.on_event("startup")
async def startup_event():
    """On server start, load all our rules data from JSON."""
    data_loader.load_rules_data()

# --- API Endpoints ---

@app.get("/")
async def get_status():
    """Check if the Rules Engine is running."""
    return {
        "status": "online",
        "message": "Fulcrum Rules Engine is operational.",
        "stats_loaded": len(data_loader.STATS_LIST),
        "skills_loaded": len(data_loader.ALL_SKILLS),
        "abilities_loaded": len(data_loader.ABILITY_DATA),
        "talents_loaded": len(data_loader.TALENT_DATA),
        "features_loaded": len(data_loader.FEATURE_STATS_MAP)
    }

@app.post("/v1/validate/skill_check", response_model=RollResult)
async def api_validate_skill_check(request: SkillCheckRequest):
    """
    Performs a standard d20 Skill Check.
    Returns the roll, total, DC, success state, and SRE trigger.
    """
    return core.calculate_skill_check(
        stat_mod=request.stat_modifier,
        skill_rank=request.skill_rank,
        dc=request.dc
    )

@app.post("/v1/validate/ability_check", response_model=RollResult)
async def api_validate_ability_check(request: AbilityCheckRequest):
    """
    Performs a d20 Ability Check against a Tiered DC.
    """
    return core.calculate_ability_check(
        rank=request.ability_school_rank,
        stat_mod=request.associated_stat_modifier,
        tier=request.ability_tier
    )

@app.get("/v1/lookup/kingdom_feature_stats", response_model=FeatureStatsResponse)
async def api_get_feature_stats(feature_name: str):
    """
    Looks up the stat modifications for a specific Kingdom Feature by its name.
    """
    try:
        return core.get_kingdom_feature_stats(feature_name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/v1/lookup/talents", response_model=List[TalentInfo])
async def api_lookup_talents(request: TalentLookupRequest):
    """
    Gets all talents a character is eligible for based on their stats and skills.
    Corrects for 'Constitution' vs 'Vitality' from data files.
    """
    return core.find_eligible_talents(request.stats, request.skills)

@app.get("/v1/lookup/skills_by_category", response_model=SkillCategoryResponse)
async def api_get_skills_by_category():
    """
    Returns all 72 skills, grouped by their 6 core categories.
    This is essential for the Character Engine's 6x2 background rule.
    """
    return {"categories": core.get_skills_by_category()}

@app.get("/v1/lookup/ability_school/{school_name}", response_model=AbilitySchoolResponse)
async def api_get_ability_school(school_name: str):
    """
    Returns all T1-T9 abilities and metadata for a single school.
    """
    if school_name not in data_loader.ABILITY_DATA:
        raise HTTPException(status_code=404, detail=f"Ability school '{school_name}' not found.")

    data = data_loader.ABILITY_DATA[school_name]
    return AbilitySchoolResponse(
        school=school_name,
        resource_pool=data["resource_pool"],
        associated_stat=data["associated_stat"],
        tiers=data["tiers"]
    )
