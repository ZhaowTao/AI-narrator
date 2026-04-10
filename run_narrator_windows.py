# -*- coding: utf-8 -*-
"""
Windows 版 AI Narrator 启动脚本
运行时切换 TTS 输出到 VB-Cable，避免监听带来的问题
"""
import subprocess
import time
import sys
import os

def set_default_playback(device_name):
    """设置默认播放设备"""
    try:
        # 使用 nircmd 设置默认播放设备
        nircmd = os.path.expandvars("$TEMP\\nircmd.exe")
        if not os.path.exists(nircmd):
            print("[下载] 正在下载 nircmd...")
            subprocess.run([
                "powershell", "-Command",
                "Invoke-WebRequest -Uri 'https://www.nirsoft.net/utils/nircmd-x64.zip' -OutFile '$env:TEMP\\nircmd.zip' -UseBasicParsing; Expand-Archive -Path '$env:TEMP\\nircmd.zip' -DestinationPath '$env:TEMP' -Force"
            ], check=True)
        
        subprocess.run([nircmd, "setdefaultsounddevice", device_name, "1"], check=True)
        print(f"[OK] 默认播放设备已设置为: {device_name}")
        return True
    except Exception as e:
        print(f"[ERROR] 设置播放设备失败: {e}")
        return False

def get_current_playback():
    """获取当前默认播放设备名称"""
    try:
        result = subprocess.run(
            ["powershell", "-Command", "Get-WmiObject Win32_SoundDevice | Where-Object { $_.Status -eq 'OK' -and $_.Name -notlike '*CABLE*' -and $_.Name -notlike '*Voicemeeter*' } | Select-Object -First 1 -ExpandProperty Name"],
            capture_output=True, text=True
        )
        return result.stdout.strip()
    except:
        return None

def main():
    print("=" * 60)
    print("AI Narrator Windows 启动器")
    print("=" * 60)
    print()
    
    # 保存当前播放设备
    current_device = get_current_playback()
    if current_device:
        print(f"[INFO] 当前播放设备: {current_device}")
    else:
        print("[WARN] 无法获取当前播放设备")
        current_device = "扬声器"
    
    print()
    print("[步骤 1/3] 切换 TTS 输出到 CABLE Input...")
    print("这样豆包才能听到 TTS 声音")
    print()
    
    # 切换到 CABLE Input
    if not set_default_playback("CABLE Input"):
        print("[ERROR] 无法切换到 CABLE Input")
        print("请确保 VB-Cable 已安装")
        input("按回车退出...")
        return
    
    print()
    print("[步骤 2/3] 等待系统应用设置...")
    time.sleep(2)
    
    print()
    print("[步骤 3/3] 启动 AI Narrator...")
    print()
    print("=" * 60)
    print("重要提示：")
    print("  - 此时 TTS 会输出到 CABLE（豆包能听到）")
    print("  - 你自己听不到 TTS 声音（这是正常的）")
    print("  - 但你能通过 OBS 监听听到豆包和游戏声音")
    print("=" * 60)
    print()
    
    # 运行主程序
    try:
        subprocess.run([sys.executable, "doubao_narrator_v2.py"], check=True)
    except KeyboardInterrupt:
        print("\n[用户中断]")
    except Exception as e:
        print(f"\n[ERROR] 运行失败: {e}")
    
    print()
    print("=" * 60)
    print("恢复音频设置...")
    print("=" * 60)
    print()
    
    # 恢复原来的播放设备
    if set_default_playback(current_device):
        print(f"[OK] 已恢复为: {current_device}")
    else:
        print("[WARN] 恢复失败，请手动设置")
    
    print()
    input("按回车退出...")

if __name__ == "__main__":
    main()
