from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from . import core, data_loader, models

# --- Lifespan Event ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load generation rules on startup."""
    print("INFO: Loading NPC generation rules...")
    try:
        data_loader.load_rules()
        print("INFO: NPC generation rules loaded.")
    except Exception as e:
        print(f"FATAL: Failed to load NPC generation rules: {e}")
    yield
    print("INFO: Shutting down NPC Generator.")

# Create the FastAPI app
app = FastAPI(
    title="NPC Generator",
    description="A stateless service to procedurally generate NPC templates.",
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
    return {"status": "NPC Generator is running."}

# --- MODIFICATION: Changed to 'async def' ---
@app.post("/v1/generate", response_model=models.NpcTemplateResponse)
async def generate_npc(request: models.NpcGenerationRequest):
    """
    (AI DM) Provide parameters (kingdom, styles, difficulty)
    to generate a new NPC template.
    """
    try:
        # --- MODIFICATION: Changed to 'await' ---
        template = await core.generate_npc_template(request)
        return template
    except HTTPException as e:
        # Catch errors bubbled up from core
        print(f"ERROR: Failed to generate NPC: {e.detail}")
        raise e # Re-raise the HTTPException
    except Exception as e:
        # Catch any other unexpected errors
        print(f"ERROR: Failed to generate NPC: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal error during NPC generation: {e}"
        )
