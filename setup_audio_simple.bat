@echo off
chcp 65001 >nul
title AI Narrator Audio Setup
cd /d "%~dp0"

echo ========================================
echo    AI Narrator Audio Setup
echo ========================================
echo.

:: Check admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [Info] Requesting admin rights...
    powershell -Command "Start-Process '%~f0' -Verb runAs"
    exit /b
)

echo [Step 1/5] Checking VB-Cable installation...
echo.

:: Check if VB-Cable is installed
powershell -Command "Get-WmiObject Win32_SoundDevice | Where-Object { $_.Name -like '*CABLE*' }" >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] VB-Cable is installed
) else (
    echo [WARN] VB-Cable not found
    echo.
    echo Please download and install VB-Cable from:
    echo https://vb-audio.com/Cable/
    echo.
    echo After installation, restart your computer and run this script again.
    pause
    exit /b
)

echo.
echo [Step 2/5] Audio Device Configuration
echo ========================================
echo.
echo Please configure Windows audio settings manually:
echo.
echo 1. Right-click volume icon in taskbar -> Sound settings
echo 2. Click "More sound settings" at the bottom
echo 3. In Playback tab: Set your speakers as default
echo 4. In Recording tab: Set "CABLE Output" as default
echo 5. Double-click "CABLE Output" -> Listen tab
echo 6. CHECK "Listen to this device"
echo 7. Set "Playback through" to your HEADPHONES (NOT speakers!)
echo 8. Click Apply -> OK
echo.
echo IMPORTANT: Use headphones to prevent audio feedback!
echo.
pause

echo.
echo [Step 3/5] Disable Physical Microphone
echo ========================================
echo.
echo To prevent audio feedback and echo:
echo.
echo 1. In Sound settings -> Recording tab
echo 2. Find your physical microphone
echo 3. Right-click -> Disable
echo.
echo This prevents the microphone from picking up speaker sound.
echo.
pause

echo.
echo [Step 4/5] OBS Configuration
echo ========================================
echo.
echo Create OBS configuration file...
echo.
(
echo ========================================
echo OBS Audio Configuration Guide
echo ========================================
echo.
echo 1. Open OBS -> Settings -> Audio
echo.
echo Global Audio Devices:
echo   Desktop Audio: Your speakers/headphones
echo   Mic/Auxiliary Audio: Disabled
echo.
echo 2. Click OK to save
echo.
echo ========================================
echo Audio Flow Diagram
echo ========================================
echo.
echo TTS Sound --> CABLE Input --> CABLE Output --> Doubao (hears prompt)
echo                                      ^
echo                                      |
echo                                   Listen --> Headphones (you hear)
echo.
echo Game Sound --> Speakers --> OBS captures --> Stream (viewers hear)
echo Doubao Voice --> Speakers --> OBS captures --> Stream (viewers hear)
echo.
echo KEY POINTS:
echo - TTS goes through CABLE, not through speakers
echo - You hear TTS through headphones via Listen feature
echo - OBS only captures speakers (game + doubao voice)
echo - Viewers CANNOT hear TTS prompts!
echo.
echo ========================================
echo Checklist Before Streaming
echo ========================================
echo [ ] TTS can play sound
echo [ ] Doubao can hear TTS (responds)
echo [ ] You can hear TTS through headphones
echo [ ] OBS does NOT capture TTS
echo [ ] OBS captures game sound
echo [ ] OBS captures doubao voice
echo.
) > "%~dp0OBS_CONFIG_GUIDE.txt"

echo [OK] OBS configuration guide saved to:
echo %~dp0OBS_CONFIG_GUIDE.txt
echo.

echo [Step 5/5] Create Launch Script
echo ========================================
echo.
(
echo @echo off
echo chcp 65001 >nul
echo cd /d "%%~dp0"
echo.
echo echo ========================================
echo echo    AI Narrator Launcher
echo ========================================
echo echo.
echo echo Checking configuration...
echo.
echo echo [Tip] Make sure:
echo echo   1. Doubao client is open and logged in
echo echo   2. Voice call started with screen share
echo echo   3. Wear headphones (important!)
echo echo.
echo pause
echo.
echo echo Starting AI Narrator...
echo python doubao_narrator_v2.py --once
echo.
echo echo.
echo echo [Done] AI Narrator test completed
echo echo.
echo echo If TTS played and Doubao responded, configuration is correct!
echo echo.
echo pause
) > "%~dp0launch_stream.bat"

echo [OK] Launch script created: launch_stream.bat
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Read OBS_CONFIG_GUIDE.txt for OBS settings
echo 2. Double-click launch_stream.bat to test
echo 3. If test passes, you're ready to stream!
echo.
pause
