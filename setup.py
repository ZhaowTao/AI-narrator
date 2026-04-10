#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Narrator 统一配置向导
自动检测平台并提供配置指导
"""
import platform
import subprocess
import sys
import os

def print_header():
    """打印标题"""
    print("=" * 60)
    print("    AI Narrator 配置向导")
    print("=" * 60)
    print()

def detect_platform():
    """检测操作系统平台"""
    system = platform.system()
    if system == "Windows":
        return "windows"
    elif system == "Darwin":
        return "mac"
    else:
        return "unsupported"

def check_python_version():
    """检查 Python 版本"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✓ Python 版本: {platform.python_version()}")
        return True
    else:
        print(f"✗ Python 版本过低: {platform.python_version()}")
        print("  需要 Python 3.8 或更高版本")
        return False

def windows_check_vb_cable():
    """Windows: 检查 VB-Cable 是否安装"""
    try:
        result = subprocess.run(
            ['powershell', '-Command', 
             'Get-WmiObject Win32_SoundDevice | Where-Object { $_.Name -like "*VB-Audio*" -or $_.Name -like "*CABLE*" } | Select-Object Name'],
            capture_output=True, text=True
        )
        print(f"[调试] 检测到的设备: {result.stdout}")
        if "VB-Audio" in result.stdout or "CABLE" in result.stdout:
            print("✓ VB-Cable 已安装")
            return True
        else:
            print("✗ VB-Cable 未安装")
            return False
    except Exception as e:
        print(f"✗ 无法检查 VB-Cable: {e}")
        return False

def windows_setup_guide():
    """Windows 配置指导"""
    print()
    print("【Windows 配置步骤】")
    print()
    print("1. 安装 VB-Cable")
    print("   下载: https://vb-audio.com/Cable/")
    print("   安装后重启电脑")
    print()
    print("2. 配置音频设备")
    print("   播放设备: CABLE Input")
    print("   录制设备: CABLE Output")
    print("   监听: 启用 → 选择耳机")
    print()
    print("3. 配置 OBS")
    print("   使用 Application Audio Capture 采集游戏")
    print("   禁用桌面音频")
    print()
    print("详细指南: docs/WINDOWS_SETUP.md")
    print()

def mac_check_blackhole():
    """Mac: 检查 BlackHole 是否安装"""
    try:
        result = subprocess.run(
            ['system_profiler', 'SPAudioDataType'],
            capture_output=True, text=True
        )
        if "BlackHole" in result.stdout:
            print("✓ BlackHole 已安装")
            return True
        else:
            print("✗ BlackHole 未安装")
            return False
    except:
        print("✗ 无法检查 BlackHole")
        return False

def mac_setup_guide():
    """Mac 配置指导"""
    print()
    print("【Mac 配置步骤】")
    print()
    print("1. 安装 BlackHole")
    print("   brew install blackhole-2ch")
    print("   或从 GitHub 下载安装")
    print()
    print("2. 配置音频设备")
    print("   输入设备: BlackHole 2ch")
    print("   Mac 版本会自动切换输出设备")
    print()
    print("3. 配置 OBS")
    print("   添加音频输入采集: BlackHole 2ch")
    print("   桌面音频: 耳机/扬声器")
    print()
    print("详细指南: docs/MAC_SETUP.md")
    print()

def test_tts():
    """测试 TTS 功能"""
    print()
    print("【测试 TTS】")
    try:
        if platform.system() == "Windows":
            ps_script = '''
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.Speak("配置测试")
'''
            subprocess.run(
                ['powershell', '-Command', ps_script],
                timeout=10, capture_output=True
            )
        else:
            # Mac 使用 say 命令
            subprocess.run(['say', '配置测试'], timeout=10, capture_output=True)
        print("✓ TTS 测试成功")
        return True
    except:
        print("✗ TTS 测试失败")
        return False


def show_prompt_example():
    """显示优化的提示词示例"""
    print()
    print("【提示词优化建议】")
    print()
    print("为避免豆包AI抢答或打断提示词，请使用以下格式：")
    print()
    print("-" * 60)
    print("SYSTEM_PROMPT = (")
    print('    "【角色设定】"')
    print('    "你是游戏主播正在直播"')
    print('    "主播不说话你是单口直播"')
    print('    "你能看到游戏画面和弹幕"')
    print('    "有弹幕提问就回答"')
    print('    "有礼物就感谢"')
    print('    "同时解说游戏画面"')
    print('    "没有弹幕就解说游戏"')
    print('    "只描述游戏画面内容"')
    print('    "不编造不脑补"')
    print('    "不提游戏以外内容"')
    print('    "风格口语化像朋友聊天"')
    print('    "适当用卧槽哈哈哈等词"')
    print('    "每次换表达方式不重复"')
    print('    "【重要】"')
    print('    "现在只回复收到两个字"')
    print('    "不要开始解说"')
    print('    "等我说继续再说"')
    print(")")
    print("-" * 60)
    print()
    print("【关键要点】")
    print("  • 使用短句，避免长句子")
    print("  • 不要使用标点符号（句号、逗号等）")
    print("  • 使用【】标记重要段落")
    print("  • 分段发送，减少单次TTS时长")
    print()
    print("这样可以防止豆包在TTS播放过程中抢答或打断")
    print()

def show_menu():
    """显示主菜单"""
    print()
    print("【主菜单】")
    print("1. 查看配置指南")
    print("2. 测试 TTS")
    print("3. 查看提示词优化建议")
    print("4. 启动 AI Narrator")
    print("5. 退出")
    print()

    choice = input("请选择 (1-5): ").strip()
    return choice

def get_script_dir():
    """获取脚本所在目录"""
    return os.path.dirname(os.path.abspath(__file__))

def main():
    """主函数"""
    print_header()
    
    # 获取脚本目录
    script_dir = get_script_dir()
    os.chdir(script_dir)
    
    # 检测平台
    plat = detect_platform()
    print(f"检测到的平台: {platform.system()}")
    print(f"脚本目录: {script_dir}")
    print()
    
    if plat == "unsupported":
        print("✗ 不支持的操作系统")
        print("  仅支持 Windows 和 macOS")
        input("\n按回车退出...")
        return
    
    # 检查 Python 版本
    if not check_python_version():
        input("\n按回车退出...")
        return
    
    # 平台特定检查
    print()
    if plat == "windows":
        print("【检查虚拟音频设备】")
        if not windows_check_vb_cable():
            windows_setup_guide()
    else:
        print("【检查虚拟音频设备】")
        if not mac_check_blackhole():
            mac_setup_guide()
    
    # 主循环
    while True:
        choice = show_menu()
        
        if choice == "1":
            # 查看配置指南
            guide_path = os.path.join(script_dir, "docs", "WINDOWS_SETUP.md" if plat == "windows" else "MAC_SETUP.md")
            if os.path.exists(guide_path):
                print()
                print(f"配置指南: {guide_path}")
                if plat == "windows":
                    os.system(f'start "" "{guide_path}"')
                else:
                    os.system(f'open "{guide_path}"')
            else:
                print()
                print(f"✗ 找不到配置指南: {guide_path}")
        
        elif choice == "2":
            # 测试 TTS
            test_tts()
        
        elif choice == "3":
            # 查看提示词优化建议
            show_prompt_example()

        elif choice == "4":
            # 启动 AI Narrator
            print()
            print("启动 AI Narrator...")
            narrator_script = os.path.join(script_dir, "doubao_narrator_v2.py" if plat == "windows" else "doubao_narrator_mac.py")
            if os.path.exists(narrator_script):
                subprocess.run([sys.executable, narrator_script, "--once"])
            else:
                print(f"✗ 找不到主程序: {narrator_script}")

        elif choice == "5":
            # 退出
            print()
            print("感谢使用 AI Narrator！")
            break
        
        else:
            print()
            print("无效的选择，请重试")
    
    print()
    input("按回车退出...")

if __name__ == "__main__":
    main()
