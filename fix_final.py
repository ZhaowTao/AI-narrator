# -*- coding: utf-8 -*-
"""
最终音频路由修复
确保：
- 豆包能听到 TTS
- 你能通过耳机听到 TTS
- OBS 采集不到 TTS
"""
import subprocess
import os

def main():
    print("=" * 60)
    print("最终音频路由修复")
    print("=" * 60)
    print()
    
    print("【问题分析】")
    print("OBS 能采集到 TTS → TTS 进入了扬声器")
    print("你听不到 → 监听设置有问题")
    print()
    
    print("【正确设置】")
    print()
    print("步骤 1: 设置播放设备为 CABLE Input")
    print("  - 这样 TTS 进入 CABLE，不经过扬声器")
    print("  - OBS 采集扬声器，就听不到 TTS")
    print()
    
    print("步骤 2: 设置录制设备为 CABLE Output")
    print("  - 豆包从 CABLE Output 听到 TTS")
    print()
    
    print("步骤 3: 启用监听（关键！）")
    print("  - 双击 CABLE Output（录制设备）")
    print("  - 监听选项卡 → 勾选'监听此设备'")
    print("  - '通过此设备播放' → 选择你的耳机")
    print("  - 这样你就能听到 TTS 了")
    print()
    
    print("【音频流向】")
    print("  TTS → CABLE Input → CABLE Output → 豆包（听到）")
    print("                              ↓")
    print("                           监听 → 耳机（你听到）")
    print()
    print("  游戏声音 → 扬声器 → OBS → 直播（观众听到）")
    print("  豆包解说 → 扬声器 → OBS → 直播（观众听到）")
    print()
    print("  TTS 不经过扬声器 → OBS 采集不到 TTS ✓")
    print()
    
    print("【检查清单】")
    print("□ 播放设备：CABLE Input（不是扬声器！）")
    print("□ 录制设备：CABLE Output")
    print("□ CABLE Output 监听：已启用")
    print("□ 监听播放设备：你的耳机")
    print("□ 扬声器：不是默认播放设备")
    print()
    
    input("按回车打开声音设置...")
    os.system("start mmsys.cpl")
    
    print()
    input("设置完成后按回车测试...")
    
    # 测试 TTS
    print()
    print("【测试 TTS】")
    ps_script = '''
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.Speak("测试音频，如果你能听到这段文字，说明设置正确")
'''
    
    try:
        subprocess.run(
            ["powershell", "-Command", ps_script],
            timeout=15,
            capture_output=True
        )
        print("✓ TTS 播放完成")
    except:
        print("✗ TTS 播放失败")
    
    print()
    print("=" * 60)
    print("检查：")
    print("  1. 你能在耳机中听到 TTS 吗？")
    print("  2. 豆包有反应吗？")
    print("  3. OBS 没有采集到 TTS？")
    print("=" * 60)
    print()
    
    input("按回车退出...")

if __name__ == "__main__":
    main()
