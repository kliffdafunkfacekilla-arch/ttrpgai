@echo off
setlocal enabledelayedexpansion



REM Define the directory CONTAINING the services
set SERVICES_PARENT_DIR=%~dp0AI-TTRPG

REM Check if the AI-TTRPG directory exists
if not exist "!SERVICES_PARENT_DIR!" (
    echo ERROR: AI-TTRPG directory not found inside the current directory.
    echo Please ensure AI-TTRPG is in the same folder as this script.
    pause
    exit /b 1
)


REM Function-like section to start a service
:start_service
    set SERVICE_NAME=%~1
    set PORT=%~2
    echo -------------------------------------
    echo Starting !SERVICE_NAME! on port !PORT!...
    echo -------------------------------------

    set SERVICE_PATH=!SERVICES_PARENT_DIR!\!SERVICE_NAME!

    if not exist "!SERVICE_PATH!" (
        echo WARNING: Directory not found for service: !SERVICE_NAME!. Skipping.
        goto :eof
    )

    REM *** MODIFIED START COMMAND ***
    REM Pass the command directly to cmd /k without intermediate echo
    start "Uvicorn !SERVICE_NAME!" cmd /k "pushd \"!SERVICE_PATH!\" && uvicorn app.main:app --host 127.0.0.1 --port !PORT! --reload"

    REM Correct timeout syntax
    timeout /t 3 /nobreak > nul 2>&1
    goto :eof

REM Start all services
call :start_service "rules_engine" 8000 #
call :start_service "character_engine" 8001
call :start_service "world_engine" 8002
call :start_service "story_engine" 8003
call :start_service "encounter_generator" 8004
call :start_service "npc_generator" 8005
call :start_service "map_generator" 8006

echo -------------------------------------
echo All services started in separate windows.
echo Each window shows the output for its service.
echo Close each window manually to stop the services.
echo -------------------------------------

endlocal
pause REM Keep this window open until user presses a key