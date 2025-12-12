@echo off
REM PeopleCounter-AI Web Interface Starter
REM This script starts the Flask web server

echo.
echo ================================================
echo    PeopleCounter-AI Web Interface
echo ================================================
echo.

REM Check if virtual environment exists
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Install requirements
echo Installing dependencies...
pip install -r requirements.txt -q

REM Start Flask app
echo.
echo ================================================
echo    Starting Web Server...
echo ================================================
echo.
echo Open your browser and navigate to:
echo    http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo ================================================
echo.

python app.py

pause
