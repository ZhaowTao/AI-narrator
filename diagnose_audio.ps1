#Requires -RunAsAdministrator
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    Audio Route Diagnostic Tool" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 检查 VB-Cable 设备
Write-Host "[1/5] Checking VB-Cable devices..." -ForegroundColor Yellow
$devices = Get-WmiObject Win32_SoundDevice | Where-Object { $_.Name -like "*CABLE*" }
if ($devices) {
    Write-Host "    Found VB-Cable devices:" -ForegroundColor Green
    $devices | ForEach-Object { Write-Host "      - $($_.Name)" -ForegroundColor Gray }
} else {
    Write-Host "    ERROR: VB-Cable not found!" -ForegroundColor Red
}
Write-Host ""

# 2. 检查默认音频设备
Write-Host "[2/5] Checking default audio devices..." -ForegroundColor Yellow
try {
    $playback = Get-WmiObject Win32_SoundDevice | Where-Object { $_.Status -eq "OK" -and $_.Name -notlike "*CABLE*" -and $_.Name -notlike "*Voicemeeter*" } | Select-Object -First 1
    Write-Host "    Default playback should be: $($playback.Name)" -ForegroundColor Gray
    
    $recording = Get-WmiObject Win32_SoundDevice | Where-Object { $_.Name -like "*CABLE*" } | Select-Object -First 1
    if ($recording) {
        Write-Host "    Default recording should be: $($recording.Name)" -ForegroundColor Green
    } else {
        Write-Host "    ERROR: CABLE Output not set as default recording!" -ForegroundColor Red
    }
} catch {
    Write-Host "    Error checking devices: $_" -ForegroundColor Red
}
Write-Host ""

# 3. 检查 CABLE Output 监听设置
Write-Host "[3/5] Checking CABLE Output listen settings..." -ForegroundColor Yellow
Write-Host "    Please verify manually:" -ForegroundColor Cyan
Write-Host "    1. Right-click volume icon -> Sound settings" -ForegroundColor White
Write-Host "    2. Click 'More sound settings'" -ForegroundColor White
Write-Host "    3. Recording tab -> Double-click 'CABLE Output'" -ForegroundColor White
Write-Host "    4. Listen tab -> Check if 'Listen to this device' is enabled" -ForegroundColor White
Write-Host "    5. Make sure 'Playback through' is set to your headphones" -ForegroundColor White
Write-Host ""

# 4. 测试 TTS 播放
Write-Host "[4/5] Testing TTS playback..." -ForegroundColor Yellow
Write-Host "    Playing test sound..." -ForegroundColor Cyan

$testText = "测试音频"
$psScript = @"
Add-Type -AssemblyName System.Speech
`synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
`synth.Speak("$testText")
"@

try {
    Start-Process powershell -ArgumentList "-Command", $psScript -Wait -WindowStyle Hidden
    Write-Host "    TTS test completed" -ForegroundColor Green
} catch {
    Write-Host "    TTS test failed: $_" -ForegroundColor Red
}
Write-Host ""

# 5. 音频流向验证
Write-Host "[5/5] Audio flow verification..." -ForegroundColor Yellow
Write-Host @"
Expected audio flow:

TTS Sound --> CABLE Input --> CABLE Output --> Doubao (should hear)
                                      |
                                      +--> Listen --> Headphones (you should hear)

If you don't hear anything in headphones:
- CABLE Output listen is not enabled
- Wrong playback device selected for listen

If Doubao doesn't hear:
- CABLE Output is not default recording device
- Doubao is not using system default device
"@ -ForegroundColor Gray

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Diagnostic complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Read-Host "Press Enter to exit"
