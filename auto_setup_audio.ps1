#Requires -RunAsAdministrator
<#
.SYNOPSIS
    AI Narrator 音频自动配置脚本
.DESCRIPTION
    自动配置 VB-Cable、Windows 音频设备和 OBS 设置，确保：
    - 豆包能听到 TTS 提示
    - 观众听不到 TTS（OBS 采集不到）
    - 用户自己能听到声音
    - 无回音和音频反馈
#>

param(
    [switch]$SkipVBCheck,
    [switch]$VerifyOnly,
    [switch]$Help
)

if ($Help) {
    Write-Host @"
AI Narrator 音频自动配置脚本

用法:
    .\auto_setup_audio.ps1              # 完整配置
    .\auto_setup_audio.ps1 -VerifyOnly  # 仅验证配置
    .\auto_setup_audio.ps1 -SkipVBCheck # 跳过 VB-Cable 检查
    .\auto_setup_audio.ps1 -Help        # 显示帮助

功能:
    1. 检测并安装 VB-Cable
    2. 配置 Windows 音频设备
    3. 设置 VB-Cable 监听
    4. 生成 OBS 配置指南
    5. 创建一键启动脚本
    6. 验证配置是否正确
"@ -ForegroundColor Cyan
    exit
}

# 配置变量
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir
$VBSetupUrl = "https://download.vb-audio.com/Download_CABLE/VBCABLE_Setup_x64.exe"
$VBSetupPath = "$env:TEMP\VBCABLE_Setup_x64.exe"
$LogFile = "$ProjectDir\audio_setup.log"

# 初始化日志
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    Add-Content -Path $LogFile -Value $logEntry -ErrorAction SilentlyContinue
    
    switch ($Level) {
        "ERROR" { Write-Host $Message -ForegroundColor Red }
        "WARN"  { Write-Host $Message -ForegroundColor Yellow }
        "SUCCESS" { Write-Host $Message -ForegroundColor Green }
        "INFO"  { Write-Host $Message -ForegroundColor White }
    }
}

# 清屏并显示标题
Clear-Host
Write-Host @"
╔══════════════════════════════════════════════════════════════╗
║         AI Narrator 音频自动配置脚本                          ║
║                                                              ║
║  自动配置音频设备，确保豆包能听到TTS，观众听不到               ║
╚══════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan
Write-Host ""

Write-Log "脚本启动，项目目录: $ProjectDir" "INFO"

# ============================================
# Task 1: 检测和安装 VB-Cable
# ============================================
function Test-VBCableInstalled {
    Write-Log "检测 VB-Cable 是否已安装..." "INFO"
    
    $playbackDevices = Get-WmiObject Win32_SoundDevice | Where-Object { $_.Name -like "*CABLE*" }
    $recordingDevices = Get-WmiObject Win32_SoundDevice | Where-Object { $_.Name -like "*CABLE*" }
    
    if ($playbackDevices -and $recordingDevices) {
        Write-Log "✓ VB-Cable 已安装" "SUCCESS"
        return $true
    } else {
        Write-Log "✗ VB-Cable 未安装" "WARN"
        return $false
    }
}

function Install-VBCable {
    Write-Log "开始下载 VB-Cable..." "INFO"
    
    try {
        # 下载 VB-Cable
        Write-Log "下载地址: $VBSetupUrl" "INFO"
        Invoke-WebRequest -Uri $VBSetupUrl -OutFile $VBSetupPath -UseBasicParsing
        
        if (Test-Path $VBSetupPath) {
            Write-Log "✓ 下载完成" "SUCCESS"
            
            # 安装 VB-Cable
            Write-Log "开始安装 VB-Cable（需要管理员权限）..." "INFO"
            Write-Log "安装过程中请允许驱动程序安装..." "WARN"
            
            $process = Start-Process -FilePath $VBSetupPath -ArgumentList "/S" -Wait -PassThru
            
            if ($process.ExitCode -eq 0) {
                Write-Log "✓ VB-Cable 安装完成" "SUCCESS"
                Write-Log "请重启电脑以完成安装！" "WARN"
                
                $restart = Read-Host "是否立即重启电脑？(Y/N)"
                if ($restart -eq "Y" -or $restart -eq "y") {
                    Restart-Computer -Force
                } else {
                    Write-Log "请手动重启电脑后再运行此脚本" "WARN"
                    exit
                }
            } else {
                Write-Log "✗ 安装失败，退出代码: $($process.ExitCode)" "ERROR"
                return $false
            }
        } else {
            Write-Log "✗ 下载失败，文件不存在" "ERROR"
            return $false
        }
    } catch {
        Write-Log "✗ 下载或安装失败: $_" "ERROR"
        return $false
    }
}

# ============================================
# Task 2: 配置 Windows 音频设备
# ============================================
function Get-AudioDeviceName {
    param([string]$DeviceType)
    
    if ($DeviceType -eq "Playback") {
        $device = Get-WmiObject Win32_SoundDevice | Where-Object { 
            $_.Status -eq "OK" -and 
            $_.Name -notlike "*CABLE*" -and
            $_.Name -notlike "*Voicemeeter*"
        } | Select-Object -First 1
    } else {
        $device = Get-WmiObject Win32_SoundDevice | Where-Object { 
            $_.Status -eq "OK" -and 
            $_.Name -like "*CABLE*"
        } | Select-Object -First 1
    }
    
    return $device.Name
}

function Set-DefaultAudioDevice {
    param(
        [string]$DeviceName,
        [string]$DeviceType  # "Playback" or "Recording"
    )
    
    Write-Log "设置默认$DeviceType设备: $DeviceName" "INFO"
    
    try {
        # 使用 nircmd 设置默认设备（需要下载）
        $nircmdPath = "$env:TEMP\nircmd.exe"
        if (-not (Test-Path $nircmdPath)) {
            Invoke-WebRequest -Uri "https://www.nirsoft.net/utils/nircmd-x64.zip" -OutFile "$env:TEMP\nircmd.zip" -UseBasicParsing
            Expand-Archive -Path "$env:TEMP\nircmd.zip" -DestinationPath "$env:TEMP" -Force
        }
        
        if ($DeviceType -eq "Playback") {
            & $nircmdPath setdefaultsounddevice "$DeviceName" 1
        } else {
            & $nircmdPath setdefaultsounddevice "$DeviceName" 2
        }
        
        Write-Log "✓ 默认$DeviceType设备已设置" "SUCCESS"
        return $true
    } catch {
        Write-Log "✗ 设置默认设备失败: $_" "ERROR"
        return $false
    }
}

function Disable-PhysicalMicrophone {
    Write-Log "禁用物理麦克风以防止音频反馈..." "INFO"
    
    try {
        # 获取所有非 VB-Cable 的录音设备
        $microphones = Get-WmiObject Win32_SoundDevice | Where-Object { 
            $_.Status -eq "OK" -and 
            $_.Name -notlike "*CABLE*" -and
            $_.Name -notlike "*Voicemeeter*"
        }
        
        foreach ($mic in $microphones) {
            Write-Log "找到麦克风: $($mic.Name)，建议手动禁用或调低音量" "WARN"
        }
        
        # 显示操作指南
        Write-Host ""
        Write-Host "【手动操作】请按以下步骤禁用物理麦克风：" -ForegroundColor Yellow
        Write-Host "1. 右键任务栏音量图标 → 声音设置" -ForegroundColor White
        Write-Host "2. 点击'更多声音设置'" -ForegroundColor White
        Write-Host "3. 切换到'录制'选项卡" -ForegroundColor White
        Write-Host "4. 右键你的物理麦克风 → 禁用" -ForegroundColor White
        Write-Host ""
        
        return $true
    } catch {
        Write-Log "✗ 禁用麦克风失败: $_" "ERROR"
        return $false
    }
}

function Set-VBCableMonitoring {
    Write-Log "配置 VB-Cable 监听..." "INFO"
    
    try {
        # 使用 PowerShell 设置监听
        # 注意：这需要 Windows 8/10/11 的音频设备管理功能
        
        Write-Host ""
        Write-Host "【手动操作】请配置 VB-Cable 监听：" -ForegroundColor Yellow
        Write-Host "1. 右键任务栏音量图标 → 声音设置" -ForegroundColor White
        Write-Host "2. 点击'更多声音设置'" -ForegroundColor White
        Write-Host "3. 切换到'录制'选项卡" -ForegroundColor White
        Write-Host "4. 双击'CABLE Output'" -ForegroundColor White
        Write-Host "5. 切换到'监听'选项卡" -ForegroundColor White
        Write-Host "6. 勾选'监听此设备'" -ForegroundColor White
        Write-Host "7. '通过此设备播放'选择你的耳机（不要用扬声器！）" -ForegroundColor Red
        Write-Host "8. 点击'应用'→'确定'" -ForegroundColor White
        Write-Host ""
        Write-Host "⚠️  重要：必须使用耳机，否则会产生音频反馈！" -ForegroundColor Red
        Write-Host ""
        
        return $true
    } catch {
        Write-Log "✗ 配置监听失败: $_" "ERROR"
        return $false
    }
}

# ============================================
# Task 3: OBS 配置指南
# ============================================
function Show-OBSConfigGuide {
    Write-Host ""
    Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║              OBS 音频设置指南                                 ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    
    $guide = @"
【OBS 音频设置步骤】

1. 打开 OBS → 设置 → 音频

2. 全局音频设备：
   桌面音频: 你的扬声器/耳机
   麦克风/辅助音频: 禁用

3. 点击确定保存

【音频流向说明】

TTS 声音 → CABLE Input → CABLE Output → 豆包（听到提示）
                                      ↓
                                   监听 → 耳机（你听到）

游戏声音 → 扬声器 → OBS 采集 → 直播（观众听到）
豆包解说 → 扬声器 → OBS 采集 → 直播（观众听到）

【关键】
- TTS 走 CABLE 线路，不经过扬声器
- 所以你通过耳机听到 TTS
- OBS 采集扬声器，采集不到 TTS
- 观众只能听到游戏和豆包解说

【检查清单】
□ TTS 能正常播放
□ 豆包能听到 TTS（有反应）
□ 你能通过耳机听到 TTS
□ OBS 采集不到 TTS
□ OBS 能采集到游戏和豆包声音
"@
    
    Write-Host $guide -ForegroundColor White
    
    # 保存到文件
    $guide | Out-File -FilePath "$ProjectDir\OBS_CONFIG_GUIDE.txt" -Encoding UTF8
    Write-Log "OBS 配置指南已保存到: $ProjectDir\OBS_CONFIG_GUIDE.txt" "INFO"
}

# ============================================
# Task 4: 创建一键启动脚本
# ============================================
function Create-LaunchScript {
    Write-Log "创建一键启动脚本..." "INFO"
    
    $batchContent = @'@echo off
chcp 65001 >nul
title AI Narrator 直播助手
cls

echo ========================================
echo    AI Narrator 直播助手
echo ========================================
echo.

:: 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请安装 Python 3.8+
    pause
    exit /b 1
)

:: 检查脚本文件
if not exist "doubao_narrator_v2.py" (
    echo [错误] 未找到 doubao_narrator_v2.py
    pause
    exit /b 1
)

:: 显示提示
echo [提示] 即将启动 AI Narrator
echo [提示] 请确保：
echo   1. 豆包客户端已打开并登录
echo   2. 已与豆包发起语音通话并共享屏幕
echo   3. 佩戴耳机（重要！）
echo.
pause

:: 启动脚本
echo.
echo [启动] 正在运行 AI Narrator...
python doubao_narrator_v2.py

echo.
echo [结束] AI Narrator 已停止
echo.
pause
'@
    
    $batchPath = "$ProjectDir\launch_stream.bat"
    $batchContent | Out-File -FilePath $batchPath -Encoding UTF8
    
    Write-Log "✓ 一键启动脚本已创建: $batchPath" "SUCCESS"
}

# ============================================
# Task 5: 配置验证
# ============================================
function Test-Configuration {
    Write-Host ""
    Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║              配置验证                                         ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    
    $allPassed = $true
    
    # 检查 1: VB-Cable 安装
    Write-Host "[检查 1/5] VB-Cable 安装状态..." -NoNewline
    if (Test-VBCableInstalled) {
        Write-Host " ✓ 通过" -ForegroundColor Green
    } else {
        Write-Host " ✗ 失败" -ForegroundColor Red
        $allPassed = $false
    }
    
    # 检查 2: 音频设备
    Write-Host "[检查 2/5] 音频设备检测..." -NoNewline
    $playbackDevice = Get-AudioDeviceName -DeviceType "Playback"
    $recordingDevice = Get-AudioDeviceName -DeviceType "Recording"
    
    if ($playbackDevice -and $recordingDevice) {
        Write-Host " ✓ 通过" -ForegroundColor Green
        Write-Host "   播放设备: $playbackDevice" -ForegroundColor Gray
        Write-Host "   录音设备: $recordingDevice" -ForegroundColor Gray
    } else {
        Write-Host " ✗ 失败" -ForegroundColor Red
        $allPassed = $false
    }
    
    # 检查 3: 脚本文件
    Write-Host "[检查 3/5] 脚本文件存在..." -NoNewline
    if (Test-Path "$ProjectDir\doubao_narrator_v2.py") {
        Write-Host " ✓ 通过" -ForegroundColor Green
    } else {
        Write-Host " ✗ 失败" -ForegroundColor Red
        $allPassed = $false
    }
    
    # 检查 4: 启动脚本
    Write-Host "[检查 4/5] 启动脚本..." -NoNewline
    if (Test-Path "$ProjectDir\launch_stream.bat") {
        Write-Host " ✓ 通过" -ForegroundColor Green
    } else {
        Write-Host " ✗ 失败" -ForegroundColor Red
        $allPassed = $false
    }
    
    # 检查 5: 用户确认
    Write-Host "[检查 5/5] 用户确认..." -NoNewline
    Write-Host " 请手动确认以下设置:" -ForegroundColor Yellow
    Write-Host "   □ 已禁用物理麦克风" -ForegroundColor White
    Write-Host "   □ 已配置 VB-Cable 监听到耳机" -ForegroundColor White
    Write-Host "   □ 已设置 OBS 音频" -ForegroundColor White
    
    return $allPassed
}

# ============================================
# 主程序
# ============================================

if ($VerifyOnly) {
    Test-Configuration
    exit
}

# 步骤 1: 检查 VB-Cable
if (-not $SkipVBCheck) {
    if (-not (Test-VBCableInstalled)) {
        $install = Read-Host "VB-Cable 未安装，是否立即安装？(Y/N)"
        if ($install -eq "Y" -or $install -eq "y") {
            if (-not (Install-VBCable)) {
                Write-Log "VB-Cable 安装失败，退出" "ERROR"
                exit 1
            }
        } else {
            Write-Log "用户选择不安装 VB-Cable，退出" "WARN"
            exit 1
        }
    }
} else {
    Write-Log "跳过 VB-Cable 检查" "INFO"
}

# 步骤 2: 配置音频设备
Write-Host ""
Write-Host "【步骤 2/5】配置 Windows 音频设备..." -ForegroundColor Cyan

$playbackDevice = Get-AudioDeviceName -DeviceType "Playback"
if ($playbackDevice) {
    Write-Log "检测到播放设备: $playbackDevice" "INFO"
    Set-DefaultAudioDevice -DeviceName $playbackDevice -DeviceType "Playback"
}

Disable-PhysicalMicrophone
Set-VBCableMonitoring

# 步骤 3: 显示 OBS 配置指南
Write-Host ""
Write-Host "【步骤 3/5】生成 OBS 配置指南..." -ForegroundColor Cyan
Show-OBSConfigGuide

# 步骤 4: 创建启动脚本
Write-Host ""
Write-Host "【步骤 4/5】创建一键启动脚本..." -ForegroundColor Cyan
Create-LaunchScript

# 步骤 5: 验证配置
Write-Host ""
Write-Host "【步骤 5/5】验证配置..." -ForegroundColor Cyan
$success = Test-Configuration

# 完成
Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║              配置完成！                                       ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

if ($success) {
    Write-Host "✓ 所有检查通过！" -ForegroundColor Green
    Write-Host ""
    Write-Host "使用方法：" -ForegroundColor Cyan
    Write-Host "1. 双击运行 launch_stream.bat 启动 AI Narrator" -ForegroundColor White
    Write-Host "2. 查看 OBS_CONFIG_GUIDE.txt 配置 OBS" -ForegroundColor White
    Write-Host "3. 佩戴耳机，开始直播！" -ForegroundColor White
} else {
    Write-Host "⚠ 部分检查未通过，请根据提示手动完成配置" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "日志文件: $LogFile" -ForegroundColor Gray
Write-Host ""

Pause
