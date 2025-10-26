@echo off
setlocal

REM Activate virtual environment
echo Activating virtual environment...
call .\venv\Scripts\activate.bat #
if errorlevel 1 (
echo Failed to activate virtual environment. Exiting.
exit /b 1
)

REM Define base directory
set BASE_DIR=AI-TTRPG

REM Function-like section to start a service
:start_service
set SERVICE_NAME=%~1
set PORT=%~2
echo -------------------------------------
echo Starting %SERVICE_NAME% on port %PORT%...
echo -------------------------------------
cd "%BASE_DIR%\%SERVICE_NAME%" || ( echo Failed to cd into %SERVICE_NAME% && exit /b 1 )

REM Start uvicorn in a new window
start "Uvicorn %SERVICE_NAME%" cmd /c "uvicorn app.main:app --host 127.0.0.1 --port %PORT% --reload"

cd ..\.. REM Go back to the project root
timeout /t 2 /nobreak > nul REM Wait 2 seconds
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
echo Close each window manually to stop the services.
echo -------------------------------------

endlocal
pause REM Keep this window open until user presses a key
