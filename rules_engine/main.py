from fastapi import FastAPI
from .models import SkillCheckRequest, SkillCheckResponse
from .core import perform_skill_check
from .data_loader import game_data

app = FastAPI()

@app.post("/v1/validate/skill_check", response_model=SkillCheckResponse)
def validate_skill_check(request: SkillCheckRequest):
    success, roll = perform_skill_check(
        stat_modifier=request.stat_modifier,
        skill_rank=request.skill_rank,
        dc=request.dc,
    )
    return SkillCheckResponse(success=success, roll=roll)

@app.get("/v1/data/{data_type}")
def get_data(data_type: str):
    return game_data.get(data_type, {"error": "Data type not found"})
