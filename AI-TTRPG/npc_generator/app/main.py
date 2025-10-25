from fastapi import FastAPI, HTTPException
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

# --- API Endpoints ---
@app.get("/")
def read_root():
    return {"status": "NPC Generator is running."}

@app.post("/v1/generate", response_model=models.NpcTemplateResponse)
def generate_npc(request: models.NpcGenerationRequest):
    """
    (AI DM) Provide parameters (kingdom, styles, difficulty)
    to generate a new NPC template.
    """
    try:
        template = core.generate_npc_template(request)
        return template
    except Exception as e:
        # Catch potential errors during generation
        print(f"ERROR: Failed to generate NPC: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal error during NPC generation: {e}"
        )