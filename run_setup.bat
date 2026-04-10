@echo off
chcp 65001 >nul
title AI Narrator 音频配置工具
cd /d "%~dp0"

echo ========================================
echo    AI Narrator 音频自动配置
echo ========================================
echo.

:: 检查是否以管理员身份运行
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [提示] 需要管理员权限，正在重新启动...
    powershell -Command "Start-Process '%~f0' -Verb runAs"
    exit /b
)

echo [1/2] 正在启动 PowerShell 脚本...
echo.

:: 运行 PowerShell 脚本
powershell -ExecutionPolicy Bypass -Command "& '%~dp0auto_setup_audio.ps1'"

echo.
echo [2/2] 配置完成
echo.
pause
