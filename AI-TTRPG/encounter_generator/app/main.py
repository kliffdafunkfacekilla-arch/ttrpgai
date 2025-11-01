from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import List, Union

from . import core
from . import data_loader
from .models import (
    EncounterRequest,
    CombatEncounterResponse,
    SkillEncounterResponse
)

# --- Lifespan Event ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    On startup, load all the encounter data from JSON files
    into memory.
    """
    print("INFO: Loading encounter data...")
    try:
        data_loader.load_all_data()
        print("INFO: Encounter data loaded successfully.")
    except Exception as e:
        print(f"FATAL: Failed to load encounter data: {e}")
        # In a real app, you might want to exit if data fails to load
    yield
    print("INFO: Shutting down Encounter Generator.")

# Create the FastAPI app
app = FastAPI(
    title="Encounter Generator",
    description="A stateless service to generate combat and skill encounters.",
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

# --- API Endpoints ---

@app.get("/")
def read_root():
    return {"status": "Encounter Generator is running."}

@app.post(
    "/v1/generate",
    response_model=Union[CombatEncounterResponse, SkillEncounterResponse]
)
def generate_encounter(request: EncounterRequest):
    """
    (AI DM) This is the main endpoint.
    Provide a list of tags (e.g., "forest", "medium", "combat")
    and it will return a matching encounter.
    """
    if not request.tags:
        raise HTTPException(
            status_code=400,
            detail="No tags provided. Please provide tags to filter by."
        )

    # 1. Find a matching encounter from the loaded data
    match = core.find_matching_encounter(request.tags)

    if not match:
        raise HTTPException(
            status_code=404,
            detail=f"No encounters found matching all tags: {request.tags}"
        )

    # 2. Convert the raw data into a structured response
    try:
        response = core.build_encounter_response(match)
        return response
    except ValueError as e:
        print(f"ERROR: Matched encounter {match.get('id')} has unknown type: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Encounter data for {match.get('id')} is corrupted."
        )
