@echo off
echo Checking Python installation...

where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Python is not installed or not found in PATH
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Starting Chess game...
python chess_game.py

if %ERRORLEVEL% neq 0 (
    echo An error occurred while running the game
    echo Please make sure all files are in the same directory:
    echo - chess_game.py
    echo - piece.py
)

pause 