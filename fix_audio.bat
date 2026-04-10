@echo off
chcp 65001 >nul
title Fix Audio Route
cd /d "%~dp0"

echo ========================================
echo    Fix Audio Route for AI Narrator
echo ========================================
echo.

:: Check admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [Info] Need admin rights, restarting...
    powershell -Command "Start-Process '%~f0' -Verb runAs"
    exit /b
)

echo [Step 1/3] Setting CABLE Output as default recording device...
echo.

:: Use PowerShell to set default recording device
powershell -Command "
    # Get CABLE Output device
    $cable = Get-WmiObject Win32_SoundDevice | Where-Object { $_.Name -like '*CABLE Output*' }
    if ($cable) {
        Write-Host 'Found: ' $cable.Name -ForegroundColor Green
        
        # Use nircmd to set as default (if available)
        $nircmd = '$env:TEMP\nircmd.exe'
        if (Test-Path $nircmd) {
            & $nircmd setdefaultsounddevice 'CABLE Output' 2
            Write-Host 'Set CABLE Output as default recording device' -ForegroundColor Green
        } else {
            Write-Host 'Please set CABLE Output as default recording device manually:' -ForegroundColor Yellow
            Write-Host '1. Right-click volume icon -> Sound settings' -ForegroundColor White
            Write-Host '2. More sound settings -> Recording tab' -ForegroundColor White
            Write-Host '3. Right-click CABLE Output -> Set as Default Device' -ForegroundColor White
        }
    } else {
        Write-Host 'ERROR: CABLE Output not found!' -ForegroundColor Red
    }
"

echo.
echo [Step 2/3] Enabling Listen feature for CABLE Output...
echo.
echo Please configure manually:
echo.
echo 1. Right-click volume icon -^> Sound settings
echo 2. Click 'More sound settings'
echo 3. Go to 'Recording' tab
echo 4. Double-click 'CABLE Output'
echo 5. Go to 'Listen' tab
echo 6. CHECK 'Listen to this device'
echo 7. Set 'Playback through' to your HEADPHONES
echo 8. Click Apply -^> OK
echo.
echo IMPORTANT: Select HEADPHONES, not speakers!
echo.
pause

echo.
echo [Step 3/3] Disabling physical microphone...
echo.
echo Please disable your physical microphone:
echo.
echo 1. In Sound settings -^> Recording tab
echo 2. Find your physical microphone (not CABLE)
echo 3. Right-click -^> Disable
echo.
pause

echo.
echo ========================================
echo Testing audio route...
echo ========================================
echo.
echo Playing test sound through CABLE...
echo.

:: Test TTS
powershell -Command "
    Add-Type -AssemblyName System.Speech
    $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
    $synth.Speak('Testing audio route')
"

echo.
echo [Test Complete]
echo.
echo If you hear the sound in your HEADPHONES, the route is correct!
echo If Doubao responds, everything is working!
echo.
pause
