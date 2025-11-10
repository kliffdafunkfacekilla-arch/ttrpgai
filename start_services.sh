#!/bin/bash

# Set PYTHONPATH to the repository root to ensure correct module resolution
export PYTHONPATH=$(pwd)
echo "PYTHONPATH set to: $PYTHONPATH"

# Create a logs directory if it doesn't exist
mkdir -p logs

# Apply Alembic migrations
echo "Applying database migrations..."
alembic -c AI-TTRPG/character_engine/alembic.ini upgrade head > logs/alembic_character.log 2>&1
alembic -c AI-TTRPG/world_engine/alembic.ini upgrade head > logs/alembic_world.log 2>&1
echo "Migrations applied."

# Kill any previously running uvicorn processes to avoid port conflicts
echo "Killing any lingering uvicorn processes..."
pkill -f uvicorn
sleep 2

# Start each service in the background and log its output
echo "Starting backend services..."
uvicorn AI-TTRPG.rules_engine.app.main:app --host 127.0.0.1 --port 8000 > logs/rules_engine.log 2>&1 &
uvicorn AI-TTRPG.character_engine.app.main:app --host 127.0.0.1 --port 8001 > logs/character_engine.log 2>&1 &
uvicorn AI-TTRPG.world_engine.app.main:app --host 127.0.0.1 --port 8002 > logs/world_engine.log 2>&1 &
uvicorn AI-TTRPG.story_engine.app.main:app --host 127.0.0.1 --port 8003 > logs/story_engine.log 2>&1 &
uvicorn AI-TTRPG.encounter_generator.app.main:app --host 127.0.0.1 --port 8004 > logs/encounter_generator.log 2>&1 &
uvicorn AI-TTRPG.npc_generator.app.main:app --host 127.0.0.1 --port 8005 > logs/npc_generator.log 2>&1 &
uvicorn AI-TTRPG.map_generator.app.main:app --host 127.0.0.1 --port 8006 > logs/map_generator.log 2>&1 &

sleep 5 # Give servers a moment to start

# Start the frontend dev server
echo "Starting frontend server..."
cd player_interface
npm install > ../logs/npm_install.log 2>&1
npm run dev > ../logs/vite_server.log 2>&1 &
cd ..
sleep 10 # Give vite time to start

echo "All services launched. Check the /logs directory for output."
