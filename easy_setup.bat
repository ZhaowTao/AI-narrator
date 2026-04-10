@echo off
chcp 65001 >nul
title Easy Audio Setup for AI Narrator
cd /d "%~dp0"

echo ========================================
echo    Easy Audio Setup (No Download)
echo ========================================
echo.

echo This will open Windows Sound Settings.
echo Please follow the steps below:
echo.
echo ========================================
echo STEP 1: Set Playback Device
echo ========================================
echo.
echo 1. Right-click volume icon in taskbar
echo 2. Click 'Sound settings'
echo 3. Click 'More sound settings' at bottom
echo 4. Go to 'Playback' tab
echo 5. Find 'VB-Audio Virtual Cable'
echo 6. Right-click -> 'Set as Default Device'
echo.
pause

echo Opening Playback settings...
start mmsys.cpl

echo.
echo ========================================
echo STEP 2: Set Recording Device
echo ========================================
echo.
echo 1. Go to 'Recording' tab
echo 2. Find 'VB-Audio Virtual Cable'
echo 3. Right-click -> 'Set as Default Device'
echo 4. Double-click 'VB-Audio Virtual Cable'
echo 5. Go to 'Listen' tab
echo 6. UNCHECK 'Listen to this device'
echo 7. Click Apply -> OK
echo.
pause

echo.
echo ========================================
echo STEP 3: Test
echo ========================================
echo.
echo Now testing TTS...
echo Doubao should hear this, but you won't.
echo.

powershell -Command "Add-Type -AssemblyName System.Speech; $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; $synth.Speak('Testing audio route')" > nul 2>&1

echo Test complete!
echo.
echo ========================================
echo Setup Finished!
echo ========================================
echo.
echo Audio Route:
echo   TTS -> VB-Cable -> Doubao (hears it)
echo.
echo You won't hear TTS (normal)
echo Use OBS monitoring to hear Doubao and game
echo.
echo Next: Run launch_stream.bat
echo.
pause
