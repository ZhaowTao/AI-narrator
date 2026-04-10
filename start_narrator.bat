@echo off
chcp 65001 >nul
title AI Narrator Launcher
cd /d "%~dp0"

echo ========================================
echo    AI Narrator Launcher (Mac Style)
echo ========================================
echo.

:: Check admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [Info] Requesting admin rights...
    powershell -Command "Start-Process '%~f0' -Verb runAs"
    exit /b
)

echo [Step 1/4] Installing nircmd (audio switcher)...
if not exist "%TEMP%\nircmd.exe" (
    powershell -Command "Invoke-WebRequest -Uri 'https://www.nirsoft.net/utils/nircmd-x64.zip' -OutFile '$env:TEMP\nircmd.zip' -UseBasicParsing; Expand-Archive -Path '$env:TEMP\nircmd.zip' -DestinationPath '$env:TEMP' -Force" >nul 2>&1
    if exist "%TEMP%\nircmd.exe" (
        echo [OK] nircmd installed
    ) else (
        echo [WARN] Failed to download nircmd, will use manual switching
    )
) else (
    echo [OK] nircmd already exists
)

echo.
echo [Step 2/4] Saving current audio output...
for /f "tokens=*" %%a in ('powershell -Command "Get-WmiObject Win32_SoundDevice | Where-Object { $_.Status -eq 'OK' -and $_.Name -notlike '*CABLE*' -and $_.Name -notlike '*Voicemeeter*' } | Select-Object -First 1 -ExpandProperty Name"') do set "CURRENT_DEVICE=%%a"
echo [INFO] Current device: %CURRENT_DEVICE%

echo.
echo [Step 3/4] Switching TTS output to CABLE Input...
echo This allows Doubao to hear TTS...
if exist "%TEMP%\nircmd.exe" (
    "%TEMP%\nircmd.exe" setdefaultsounddevice "CABLE Input" 1
    echo [OK] Switched to CABLE Input
) else (
    echo [MANUAL] Please set default playback to "CABLE Input" manually:
    echo   1. Right-click volume icon -> Sound settings
    echo   2. Output: Select "CABLE Input"
    pause
)

echo.
echo [Step 4/4] Starting AI Narrator...
echo.
echo ========================================
echo IMPORTANT NOTES:
echo   - TTS will go to CABLE (Doubao hears it)
echo   - You won't hear TTS (normal behavior)
echo   - Use OBS monitoring to hear Doubao and game
echo ========================================
echo.
pause

echo.
echo Starting...
python doubao_narrator_v2.py --once

echo.
echo ========================================
echo Restoring audio output to: %CURRENT_DEVICE%
echo ========================================
if exist "%TEMP%\nircmd.exe" (
    "%TEMP%\nircmd.exe" setdefaultsounddevice "%CURRENT_DEVICE%" 1
    echo [OK] Restored
) else (
    echo [MANUAL] Please restore your audio output manually
)

echo.
pause
