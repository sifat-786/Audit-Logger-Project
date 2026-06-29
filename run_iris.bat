@echo off
title Iris Audit Dashboard Launcher
echo ===================================================
echo   Starting Iris Audit Dashboard (Streamlit)...
echo   Double-click launcher initialized.
echo ===================================================

:: Navigate to the directory of this batch file
cd /d "%~dp0"

:: Check if virtual environment exists and activate it
if exist venv\Scripts\activate.bat (
    echo [1/2] Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo [1/2] Warning: venv folder not found. Running using system python...
)

:: Run streamlit dashboard
echo [2/2] Launching Streamlit App...
streamlit run app.py

:: Keep terminal window open if it crashes or stops
echo ===================================================
echo   Dashboard stopped. Press any key to exit.
echo ===================================================
pause
