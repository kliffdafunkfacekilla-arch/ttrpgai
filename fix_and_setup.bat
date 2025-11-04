@echo off
setlocal

:: -----------------------------------------------------------------
:: --- !! SET THIS TO YOUR PROJECT PATH !! ---
:: -----------------------------------------------------------------
set "PROJECT_DIR=C:\Users\krazy\Documents\GitHub\Ruleengine"

echo ==========================================================
echo Starting TTRPG-AI Project Setup...
echo Project directory set to: %PROJECT_DIR%
echo ==========================================================
echo.

:: ---------------------------------
:: --- FIX 1: Migrate BOTH Databases
:: ---------------------------------
echo [FIX 1/2] Upgrading the world_engine database...
echo.
cd /D "%PROJECT_DIR%\AI-TTRPG\world_engine"
alembic upgrade head
echo.

echo Upgrading the character_engine database...
echo.
:: --- THIS LINE IS NOW FIXED (PROJECT_DIR) ---
cd /D "%PROJECT_DIR%\AI-TTRPG\character_engine" 
alembic upgrade head
echo.
echo Database migrations applied.
echo.

:: ---------------------------------
:: --- FIX 2: Reset Character Database
:: ---------------------------------
echo [FIX 2/2] Deleting old character database to force rebuild...
echo.
cd /D "%PROJECT_DIR%\AI-TTRPG\character_engine"
if exist characters.db (
    del characters.db
    echo characters.db deleted.
) else (
    echo characters.db not found. No need to delete.
)
echo.

:: --- Run Migrations AGAIN to create the new, clean DB ---
echo Re-running character_engine migration to create new database...
echo.
cd /D "%PROJECT_DIR%\AI-TTRPG\character_engine"
alembic upgrade head
echo.
echo New characters.db created.
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