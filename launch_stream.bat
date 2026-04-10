@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo    AI Narrator Launcher
echo ========================================
echo.
echo Checking configuration...
echo.
echo [Tip] Make sure:
echo   1. Doubao client is open and logged in
echo   2. Voice call started with screen share
echo   3. Wear headphones (important!)
echo.
pause

echo.
echo Starting AI Narrator...
python doubao_narrator_v2.py --once

echo.
echo [Done] AI Narrator test completed
echo.
echo If TTS played and Doubao responded, configuration is correct!
echo.
pause
