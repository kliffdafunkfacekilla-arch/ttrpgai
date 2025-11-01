from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import time # For generating seeds

from . import core, data_loader, models

# --- Lifespan Event ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load map generation data on startup."""
    print("INFO: Lifespan startup...")
    try:
        print("INFO: Calling data_loader.load_data()...")
        data_loader.load_data()
        print("INFO: Map data loaded successfully.")
    except Exception as e:
        print(f"FATAL: Failed to load map data during lifespan startup: {e}")
    yield
    print("INFO: Lifespan shutdown. Shutting down Map Generator.")

# Create the FastAPI app
app = FastAPI(
    title="Map Generator",
    description="A stateless service to procedurally generate tile maps.",
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
    return {"status": "Map Generator is running."}

@app.post("/v1/generate", response_model=models.MapGenerationResponse)
def generate_map(request: models.MapGenerationRequest):
    """
    (AI DM / Story Engine) Provide tags (e.g., 'forest', 'cave')
    and optionally a seed or dimensions to generate a map.
    """
    # 1. Select the appropriate algorithm based on tags
    algorithm = core.select_algorithm(request.tags)
    if not algorithm:
        raise HTTPException(
            status_code=404,
            detail=f"No generation algorithm found for tags: {request.tags}"
        )

    # 2. Determine the seed
    seed = request.seed or str(time.time()) # Use provided seed or generate one

    # 3. Run the generation process
    try:
        generated_map = core.run_generation(
            algorithm,
            seed,
            request.width,
            request.height
        )
        return generated_map
    except Exception as e:
        print(f"ERROR during map generation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal error during map generation: {e}"
        )
