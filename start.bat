@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo AI Narrator 启动脚本
echo ========================================
echo.

REM 检查虚拟环境是否存在
if exist ".\venv\Scripts\python.exe" (
    echo 使用虚拟环境运行...
    .\venv\Scripts\python doubao_narrator.py %*
) else (
    echo 虚拟环境不存在，尝试使用系统 Python...
    python doubao_narrator.py %*
)

echo.
pause
