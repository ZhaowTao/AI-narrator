# -*- coding: utf-8 -*-
"""
AI Narrator 启动器
自动切换音频设备并运行解说脚本
"""
import subprocess
import time
import sys
import os

def run_command(cmd, timeout=30):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=True
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Timeout"
    except Exception as e:
        return False, "", str(e)

def set_audio_device(device_name, device_type="playback"):
    """使用 Windows 控制面板设置默认音频设备"""
    # 打开声音设置让用户手动设置
    if device_type == "playback":
        print(f"\n[设置] 请将播放设备设置为: {device_name}")
        print("步骤:")
        print("  1. 右键任务栏音量图标 → 声音设置")
        print("  2. 点击'更多声音设置'")
        print("  3. 播放选项卡 → 右键设备 → 设置为默认")
        os.system("start mmsys.cpl")
    else:
        print(f"\n[设置] 请将录制设备设置为: {device_name}")
        print("步骤:")
        print("  1. 录制选项卡 → 右键设备 → 设置为默认")
        print("  2. 双击设备 → 监听 → 取消勾选'监听此设备'")
        os.system("start mmsys.cpl")
    
    input("\n设置完成后按回车继续...")
    return True

def test_tts():
    """测试 TTS"""
    print("\n[测试] 播放测试音频...")
    ps_script = '''
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.Speak("测试")
'''
    try:
        subprocess.run(
            ["powershell", "-Command", ps_script],
            timeout=10,
            capture_output=True
        )
        print("✓ TTS 测试成功")
        return True
    except:
        print("✗ TTS 测试失败")
        return False

def main():
    print("=" * 60)
    print("AI Narrator 启动器")
    print("=" * 60)
    print()
    
    # 步骤 1: 设置播放设备
    print("[步骤 1/4] 设置播放设备为 VB-Cable")
    print("这样 TTS 会输出到 VB-Cable")
    set_audio_device("VB-Audio Virtual Cable", "playback")
    
    # 步骤 2: 设置录制设备
    print("\n[步骤 2/4] 设置录制设备为 VB-Cable")
    print("这样豆包才能听到 TTS")
    set_audio_device("VB-Audio Virtual Cable", "recording")
    
    # 步骤 3: 等待设置生效
    print("\n[步骤 3/4] 等待设置生效...")
    time.sleep(3)
    
    # 步骤 4: 测试并运行
    print("\n[步骤 4/4] 测试 TTS...")
    if test_tts():
        print("\n✓ TTS 工作正常")
        print("\n准备启动 AI Narrator...")
        print("=" * 60)
        print("提示:")
        print("  - TTS 会输出到 VB-Cable（豆包能听到）")
        print("  - 你自己听不到 TTS（这是正常的）")
        print("  - 通过 OBS 监听听到豆包和游戏声音")
        print("=" * 60)
        input("\n按回车启动 AI Narrator...")
        
        # 运行主程序
        try:
            subprocess.run([sys.executable, "doubao_narrator_v2.py", "--once"])
        except KeyboardInterrupt:
            print("\n[用户中断]")
    else:
        print("\n✗ TTS 测试失败，请检查音频设置")
    
    print("\n" + "=" * 60)
    print("完成!")
    print("=" * 60)
    input("\n按回车退出...")

if __name__ == "__main__":
    main()
