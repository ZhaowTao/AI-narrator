# -*- coding: utf-8 -*-
"""
AI Narrator 启动脚本
"""
import subprocess
import time
import sys
import os

def main():
    print("=" * 60)
    print("AI Narrator 启动脚本")
    print("=" * 60)
    print()
    
    # 检查音频设置
    print("[检查] 请确认音频设置：")
    print()
    print("1. 播放设备（输出）：VB-Audio Virtual Cable")
    print("2. 录制设备（输入）：VB-Audio Virtual Cable")
    print("3. VB-Cable 监听：已禁用")
    print()
    
    ready = input("音频设置是否正确？(Y/N): ").strip().upper()
    
    if ready != "Y":
        print()
        print("请手动设置音频：")
        print("  1. 右键音量图标 → 声音设置 → 更多声音设置")
        print("  2. 播放 → VB-Cable → 设为默认")
        print("  3. 录制 → VB-Cable → 设为默认")
        print("  4. 双击 VB-Cable（录制）→ 监听 → 取消勾选")
        print()
        os.system("start mmsys.cpl")
        input("设置完成后按回车...")
    
    print()
    print("[测试] 正在测试 TTS...")
    
    # 测试 TTS
    ps_script = '''
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.Speak("测试音频")
'''
    
    try:
        subprocess.run(
            ["powershell", "-Command", ps_script],
            timeout=10,
            capture_output=True
        )
        print("✓ TTS 测试通过")
    except:
        print("✗ TTS 测试失败，但继续运行...")
    
    print()
    print("=" * 60)
    print("启动 AI Narrator")
    print("=" * 60)
    print()
    print("提示：")
    print("  - 豆包应该能听到 TTS")
    print("  - 你自己听不到（正常）")
    print("  - 按 Ctrl+C 停止")
    print()
    
    input("按回车开始...")
    
    # 运行主程序
    try:
        subprocess.run([sys.executable, "doubao_narrator_v2.py", "--once"])
    except KeyboardInterrupt:
        print("\n[已停止]")
    
    print()
    input("按回车退出...")

if __name__ == "__main__":
    main()
