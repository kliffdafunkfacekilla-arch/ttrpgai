@echo off
setlocal

REM Define the directory CONTAINING the services
set "SERVICES_PARENT_DIR=%~dp0AI-TTRPG"

REM Check if the AI-TTRPG directory exists
if not exist "%SERVICES_PARENT_DIR%" (
    echo ERROR: AI-TTRPG directory not found inside the current directory.
    echo Please ensure AI-TTRPG is in the same folder as this script.
    pause
    exit /b 1
)

echo Starting all 7 services...
echo.

REM --- We are now starting each service manually to avoid batch file bugs ---

REM 1. rules_engine (Special case: main.py is in root)
echo Starting rules_engine on port 8000...
set "SERVICE_PATH=%SERVICES_PARENT_DIR%\rules_engine"
if exist "%SERVICE_PATH%\main.py" (
    start "Uvicorn rules_engine" cmd /k "pushd "%SERVICE_PATH%" && uvicorn main:app --host 127.0.0.1 --port 8000 --reload"
) else (
    echo WARNING: rules_engine not found at %SERVICE_PATH%\main.py. Skipping.
)
timeout /t 3 /nobreak > nul 2>&1

REM 2. character_engine
echo Starting character_engine on port 8001...
set "SERVICE_PATH=%SERVICES_PARENT_DIR%\character_engine"
if exist "%SERVICE_PATH%\app\main.py" (
    start "Uvicorn character_engine" cmd /k "pushd "%SERVICE_PATH%" && uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload"
) else (
    echo WARNING: character_engine not found at %SERVICE_PATH%\app\main.py. Skipping.
)
timeout /t 3 /nobreak > nul 2>&1

REM 3. world_engine
echo Starting world_engine on port 8002...
set "SERVICE_PATH=%SERVICES_PARENT_DIR%\world_engine"
if exist "%SERVICE_PATH%\app\main.py" (
    start "Uvicorn world_engine" cmd /k "pushd "%SERVICE_PATH%" && uvicorn app.main:app --host 127.0.0.1 --port 8002 --reload"
) else (
    echo WARNING: world_engine not found at %SERVICE_PATH%\app\main.py. Skipping.
)
timeout /t 3 /nobreak > nul 2>&1

REM 4. story_engine
echo Starting story_engine on port 8003...
set "SERVICE_PATH=%SERVICES_PARENT_DIR%\story_engine"
if exist "%SERVICE_PATH%\app\main.py" (
    start "Uvicorn story_engine" cmd /k "pushd "%SERVICE_PATH%" && uvicorn app.main:app --host 127.0.0.1 --port 8003 --reload"
) else (
    echo WARNING: story_engine not found at %SERVICE_PATH%\app\main.py. Skipping.
)
timeout /t 3 /nobreak > nul 2>&1

REM 5. encounter_generator
echo Starting encounter_generator on port 8004...
set "SERVICE_PATH=%SERVICES_PARENT_DIR%\encounter_generator"
if exist "%SERVICE_PATH%\app\main.py" (
    start "Uvicorn encounter_generator" cmd /k "pushd "%SERVICE_PATH%" && uvicorn app.main:app --host 127.0.0.1 --port 8004 --reload"
) else (
    echo WARNING: encounter_generator not found at %SERVICE_PATH%\app\main.py. Skipping.
)
timeout /t 3 /nobreak > nul 2>&1

REM 6. npc_generator
echo Starting npc_generator on port 8005...
set "SERVICE_PATH=%SERVICES_PARENT_DIR%\npc_generator"
if exist "%SERVICE_PATH%\app\main.py" (
    start "Uvicorn npc_generator" cmd /k "pushd "%SERVICE_PATH%" && uvicorn app.main:app --host 127.0.0.1 --port 8005 --reload"
) else (
    echo WARNING: npc_generator not found at %SERVICE_PATH%\app\main.py. Skipping.
)
timeout /t 3 /nobreak > nul 2>&1

REM 7. map_generator
echo Starting map_generator on port 8006...
set "SERVICE_PATH=%SERVICES_PARENT_DIR%\map_generator"
if exist "%SERVICE_PATH%\app\main.py" (
    start "Uvicorn map_generator" cmd /k "pushd "%SERVICE_PATH%" && uvicorn app.main:app --host 127.0.0.1 --port 8006 --reload"
) else (
    echo WARNING: map_generator not found at %SERVICE_PATH%\app\main.py. Skipping.
)
timeout /t 3 /nobreak > nul 2>&1

echo -------------------------------------
echo All services started in separate windows.
echo Close each window manually to stop the services.
echo -------------------------------------

endlocal
pause