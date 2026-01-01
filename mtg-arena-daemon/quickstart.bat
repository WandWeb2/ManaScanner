@echo off
REM Quick Start Script for MTG Arena Daemon (Windows)

echo MTG Arena Deck Monitor Daemon - Quick Start
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo Python version:
python --version
echo.

REM Check if we're in the right directory
if not exist "daemon.py" (
    echo Error: daemon.py not found
    echo Please run this script from the mtg-arena-daemon directory
    pause
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Dependencies installed successfully
echo.

REM Check if config exists
if not exist "config\daemon.yaml" (
    echo Creating default configuration...
    if not exist "config" mkdir config
    
    if exist "config\daemon.yaml.example" (
        copy config\daemon.yaml.example config\daemon.yaml
    ) else (
        echo Error: config\daemon.yaml.example not found
        pause
        exit /b 1
    )
    
    echo.
    echo WARNING: Please edit config\daemon.yaml and update the log_file_path
    echo          with your actual MTG Arena Player.log location
    echo.
    echo Default Windows path:
    echo    C:\Users\^<YourUsername^>\AppData\LocalLow\Wizards Of The Coast\MTGA\Player.log
    echo.
    echo Opening config file...
    timeout /t 2 >nul
    notepad config\daemon.yaml
)

echo.
echo Setup complete!
echo.
echo To start the daemon, run:
echo    python daemon.py
echo.
echo For more information, see README.md
echo.
pause
