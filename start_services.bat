@echo off
setlocal

REM --- Configuration ---
set "LOG_DIR=%~dp0logs"
set "SERVICES_PARENT_DIR=%~dp0AI-TTRPG"
set "PLAYER_INTERFACE_DIR=%~dp0player_interface"

REM --- Setup ---
echo Creating log directory...
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

echo Killing any lingering uvicorn and node processes to avoid port conflicts...
taskkill /F /IM uvicorn.exe /T >nul 2>&1
taskkill /F /IM node.exe /T >nul 2>&1
echo.
timeout /t 2 /nobreak > nul

REM --- Database Migrations ---
echo Applying database migrations...
echo  - Applying character_engine migrations...
alembic -c "%~dp0AI-TTRPG\character_engine\alembic.ini" upgrade head > "%LOG_DIR%\alembic_character.log" 2>&1
echo  - Applying world_engine migrations...
alembic -c "%~dp0AI-TTRPG\world_engine\alembic.ini" upgrade head > "%LOG_DIR%\alembic_world.log" 2>&1
echo Migrations applied successfully.
echo.

REM --- Backend Services ---
echo Starting all 7 backend services...
echo (Each service will open in a new window. You can minimize them.)
echo.

start "rules_engine" cmd /c "cd /d "%SERVICES_PARENT_DIR%\rules_engine" && title rules_engine && uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"
timeout /t 2 /nobreak > nul
start "character_engine" cmd /c "cd /d "%SERVICES_PARENT_DIR%\character_engine" && title character_engine && uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload"
timeout /t 2 /nobreak > nul
start "world_engine" cmd /c "cd /d "%SERVICES_PARENT_DIR%\world_engine" && title world_engine && uvicorn app.main:app --host 127.0.0.1 --port 8002 --reload"
timeout /t 2 /nobreak > nul
start "story_engine" cmd /c "cd /d "%SERVICES_PARENT_DIR%\story_engine" && title story_engine && uvicorn app.main:app --host 127.0.0.1 --port 8003 --reload"
timeout /t 2 /nobreak > nul
start "encounter_generator" cmd /c "cd /d "%SERVICES_PARENT_DIR%\encounter_generator" && title encounter_generator && uvicorn app.main:app --host 127.0.0.1 --port 8004 --reload"
timeout /t 2 /nobreak > nul
REM Removed npc_generator (port 8005) - logic consolidated into rules_engine (port 8000)
timeout /t 2 /nobreak > nul
start "map_generator" cmd /c "cd /d "%SERVICES_PARENT_DIR%\map_generator" && title map_generator && uvicorn app.main:app --host 127.0.0.1 --port 8006 --reload"
timeout /t 2 /nobreak > nul

echo All backend services launched.
echo.

REM --- Frontend Service ---
echo Starting frontend service...
if not exist "%PLAYER_INTERFACE_DIR%\node_modules" (
    echo  - Running 'npm install' for the first time. This might take a moment...
    start "Frontend Install" cmd /c "cd /d "%PLAYER_INTERFACE_DIR%" && title Installing Frontend Dependencies && npm install > "%LOG_DIR%\npm_install.log" 2>&1 && exit"
    echo  - Waiting for install to complete...
    timeout /t 30 /nobreak > nul
)

echo  - Starting Vite dev server...
start "Vite Frontend" cmd /c "cd /d "%PLAYER_INTERFACE_DIR%" && title Vite Dev Server && npm run dev"

echo.
echo -----------------------------------------------------------------
echo All services are starting up.
echo - Backend logs are in the individual service windows.
echo - Frontend logs are in the 'Vite Dev Server' window.
echo - You can access the application in your browser (usually at http://localhost:5173).
echo -----------------------------------------------------------------
echo.

endlocal
pause