@echo off
chcp 65001 >nul
title Quick Audio Setup for AI Narrator
cd /d "%~dp0"

echo ========================================
echo    Quick Audio Setup
echo ========================================
echo.

echo [Step 1/3] Opening Playback settings...
echo Please set 'VB-Audio Virtual Cable' as default:
echo.
rundll32.exe shell32.dll,Control_RunDLL mmsys.cpl,,0
echo.
pause

echo.
echo [Step 2/3] Opening Recording settings...
echo Please set 'VB-Audio Virtual Cable' as default:
echo.
rundll32.exe shell32.dll,Control_RunDLL mmsys.cpl,,1
echo.
pause

echo.
echo [Step 3/3] Testing TTS...
echo.
echo If setup is correct, Doubao should hear the TTS
echo You will NOT hear it (this is normal)
echo.
pause

echo Testing...
powershell -Command "Add-Type -AssemblyName System.Speech; $s = New-Object System.Speech.Synthesis.SpeechSynthesizer; $s.Speak('Test')"

echo.
echo ========================================
echo Setup complete!
echo ========================================
echo.
echo Now run: launch_stream.bat
echo.
pause
