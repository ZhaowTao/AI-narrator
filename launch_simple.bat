@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo    AI Narrator - Simple Mode
echo ========================================
echo.
echo [Mode] Physical Loopback
echo.
echo Audio Route:
echo   TTS -^> CABLE -^> Doubao (hears)
echo     -^> Speaker -^> Microphone -^> Doubao
echo   OBS captures Speaker only
echo.
echo [Warning] Viewers may slightly hear TTS
echo.
pause

echo.
echo Starting AI Narrator...
python doubao_narrator_v2.py --once

echo.
pause
