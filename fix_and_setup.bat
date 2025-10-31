@echo off
setlocal

:: -----------------------------------------------------------------
:: --- Project path set to your provided directory ---
:: -----------------------------------------------------------------
set "PROJECT_DIR=C:\Users\krazy\Documents\GitHub\Ruleengine"

echo ==========================================================
echo Starting TTRPG-AI Project Setup...
echo Project directory set to: %PROJECT_DIR%
echo ==========================================================
echo.

:: ---------------------------------
:: --- FIX 1: Install Dependencies
:: ---------------------------------
echo [FIX 1/3] Installing Python dependencies for all 7 services...
echo.

echo Installing for character_engine...
cd /D "%PROJECT_DIR%\AI-TTRPG\character_engine"
pip install -r requirements.txt

echo Installing for world_engine...
cd /D "%PROJECT_DIR%\AI-TTRPG\world_engine"
pip install -r requirements.txt

echo Installing for story_engine...
cd /D "%PROJECT_DIR%\AI-TTRPG\story_engine"
pip install -r requirements.txt

echo Installing for rules_engine...
cd /D "%PROJECT_DIR%\AI-TTRPG\rules_engine"
pip install -r requirements.txt

echo Installing for npc_generator...
cd /D "%PROJECT_DIR%\AI-TTRPG\npc_generator"
pip install -r requirements.txt

echo Installing for map_generator...
cd /D "%PROJECT_DIR%\AI-TTRPG\map_generator"
pip install -r requirements.txt

echo Installing for encounter_generator...
cd /D "%PROJECT_DIR%\AI-TTRPG\encounter_generator"
pip install -r requirements.txt

echo.
echo All Python dependencies installed.
echo.

:: ---------------------------------
:: --- FIX 2: Migrate World Database
:: ---------------------------------
echo [FIX 2/3] Upgrading the world_engine database...
echo.
cd /D "%PROJECT_DIR%\AI-TTRPG\world_engine"
alembic upgrade head
echo.
echo Database migration applied.
echo.

:: ---------------------------------
:: --- FIX 3: Reset Character Database
:: ---------------------------------
echo [FIX 3/3] Deleting old character database to prevent errors...
echo.
cd /D "%PROJECT_DIR%\AI-TTRPG"
if exist characters.db (
    del characters.db
    echo characters.db deleted. A new one will be created on service start.
) else (
    echo characters.db not found. No need to delete.
)
echo.

:: ---------------------------------
:: --- Done
:: ---------------------------------
echo ==========================================================
echo SETUP COMPLETE!
echo You can now run start_services.bat to start the backend.
echo ==========================================================
echo.
pause