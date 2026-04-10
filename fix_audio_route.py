# -*- coding: utf-8 -*-
"""
音频路由修复工具
直接控制 TTS 输出到指定设备，绕过系统默认设置问题
"""
import subprocess
import sys
import os

def test_tts_to_device():
    """测试 TTS 并输出到指定设备"""
    print("=" * 60)
    print("音频路由测试")
    print("=" * 60)
    print()
    
    # 测试 1: 直接播放 TTS
    print("[测试 1/3] 直接播放 TTS...")
    print("你应该能从默认音频设备听到声音")
    print()
    
    ps_script = '''
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.Speak("测试音频，如果你能听到这段文字，说明 TTS 工作正常")
'''
    
    try:
        subprocess.run(
            ["powershell", "-Command", ps_script],
            timeout=30,
            check=True
        )
        print("✓ TTS 播放完成")
    except Exception as e:
        print(f"✗ TTS 播放失败: {e}")
    
    print()
    print("=" * 60)
    print()
    
    # 询问用户结果
    print("[诊断]")
    print()
    print("请确认以下情况：")
    print()
    
    heard_in_headphones = input("1. 你能在耳机中听到 TTS 声音吗？(Y/N): ").strip().upper()
    doubao_heard = input("2. 豆包有反应吗（听到提示后说话）？(Y/N): ").strip().upper()
    obs_captured = input("3. OBS 采集到了 TTS 声音吗？(Y/N): ").strip().upper()
    
    print()
    print("=" * 60)
    print("诊断结果")
    print("=" * 60)
    print()
    
    # 分析结果
    if heard_in_headphones == "Y" and doubao_heard == "Y" and obs_captured == "N":
        print("✓ 完美！音频路由配置正确！")
        print()
        print("音频流向：")
        print("  TTS → CABLE → 豆包（听到）")
        print("       ↓")
        print("      监听 → 耳机（你听到）")
        print("  OBS 只采集扬声器（听不到 TTS）")
        return True
        
    elif heard_in_headphones == "N":
        print("✗ 问题：你听不到 TTS")
        print()
        print("可能原因：")
        print("  1. CABLE Output 的监听没有启用")
        print("  2. 监听设备没有选择耳机")
        print("  3. 耳机音量太低")
        print()
        print("解决方案：")
        print("  1. 右键音量图标 → 声音设置 → 更多声音设置")
        print("  2. 录制 → 双击 CABLE Output → 监听")
        print("  3. 勾选'监听此设备'")
        print("  4. '通过此设备播放' 选择你的耳机")
        print("  5. 点击应用 → 确定")
        
    elif doubao_heard == "N":
        print("✗ 问题：豆包听不到 TTS")
        print()
        print("可能原因：")
        print("  1. CABLE Output 不是默认录制设备")
        print("  2. 豆包没有使用系统默认设备")
        print("  3. 豆包语音通话没有开启")
        print()
        print("解决方案：")
        print("  1. 确保 CABLE Output 是默认录制设备（有绿色勾）")
        print("  2. 重启豆包客户端")
        print("  3. 确保已与豆包发起语音通话并共享屏幕")
        
    elif obs_captured == "Y":
        print("✗ 问题：OBS 采集到了 TTS（观众会听到）")
        print()
        print("可能原因：")
        print("  1. OBS 采集了 CABLE Output")
        print("  2. 监听设置到了扬声器而不是耳机")
        print()
        print("解决方案：")
        print("  1. OBS 设置 → 音频")
        print("  2. 桌面音频：选择你的扬声器（不是 CABLE）")
        print("  3. 麦克风/辅助音频：禁用")
        print("  4. 确保监听设置选择的是耳机！")
    
    print()
    return False


def create_working_solution():
    """创建一个可行的解决方案"""
    print()
    print("=" * 60)
    print("创建可行方案")
    print("=" * 60)
    print()
    
    # 由于 VB-Cable 监听方案复杂，提供一个简单可行的替代方案
    print("由于 VB-Cable 监听设置复杂，提供以下可行方案：")
    print()
    print("【方案】使用物理回环（最简单可靠）")
    print()
    print("设置步骤：")
    print("1. 禁用 CABLE Output 的监听功能")
    print("   （录制 → CABLE Output → 监听 → 取消勾选）")
    print()
    print("2. 启用物理麦克风")
    print("   （录制 → 右键麦克风 → 启用）")
    print()
    print("3. 将麦克风靠近扬声器/耳机")
    print("   （让麦克风能拾取到 TTS 声音）")
    print()
    print("4. OBS 设置：")
    print("   - 桌面音频：扬声器")
    print("   - 麦克风：禁用")
    print()
    print("音频流向：")
    print("  TTS → CABLE → 豆包（听到）")
    print("    ↓")
    print("  扬声器/耳机")
    print("    ↓")
    print("  麦克风 → 豆包（再次听到，不影响）")
    print()
    print("  OBS 只采集扬声器（游戏声音）")
    print()
    print("缺点：")
    print("  - 观众可能隐约听到 TTS（如果麦克风灵敏度高）")
    print("  - 但比 OBS 直接采集 TTS 要好")
    print()
    
    # 创建修改版启动脚本
    script_content = '''@echo off
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
'''
    
    with open("launch_simple.bat", "w", encoding="utf-8") as f:
        f.write(script_content)
    
    print("✓ 已创建 launch_simple.bat")
    print()


def main():
    print("\n" + "=" * 60)
    print("AI Narrator 音频路由诊断工具")
    print("=" * 60 + "\n")
    
    # 运行测试
    success = test_tts_to_device()
    
    if not success:
        create_working_solution()
    
    print()
    print("=" * 60)
    print("诊断完成")
    print("=" * 60)
    print()
    
    input("按回车键退出...")


if __name__ == "__main__":
    main()
