# -*- coding: utf-8 -*-
"""
全自动音频路由修复工具
使用 Windows Core Audio API 直接控制音频设备
"""
import subprocess
import time
import sys
import os
import json

def get_audio_devices():
    """获取所有音频设备"""
    try:
        result = subprocess.run(
            ['powershell', '-Command', 
             'Get-WmiObject Win32_SoundDevice | Select-Object Name, Status | ConvertTo-Json -Compress'],
            capture_output=True, text=True
        )
        devices = json.loads(result.stdout)
        if not isinstance(devices, list):
            devices = [devices]
        return devices
    except Exception as e:
        print(f"[DEBUG] 获取设备失败: {e}")
        return []

def find_vb_cable():
    """查找 VB-Cable 设备"""
    devices = get_audio_devices()
    
    for dev in devices:
        name = dev.get('Name', '')
        if 'VB-Audio Virtual Cable' in name or 'VB-Cable' in name:
            return name
    
    return None

def set_audio_device(device_name, device_type='playback'):
    """使用 PowerShell 设置默认音频设备"""
    try:
        # 使用 Windows 10/11 的音频设置命令
        if device_type == 'playback':
            # 设置默认播放设备
            ps_cmd = f'''
$device = Get-WmiObject Win32_SoundDevice | Where-Object {{ $_.Name -like "*{device_name}*" }}
if ($device) {{
    # 使用 SoundVolumeView 命令行工具（如果可用）
    $svv = "$env:TEMP\SoundVolumeView.exe"
    if (Test-Path $svv) {{
        & $svv /SetDefault "{device_name}" 1
        Write-Host "OK"
    }} else {{
        Write-Host "TOOL_NOT_FOUND"
    }}
}} else {{
    Write-Host "DEVICE_NOT_FOUND"
}}
'''
        else:
            # 设置默认录制设备
            ps_cmd = f'''
$svv = "$env:TEMP\SoundVolumeView.exe"
if (Test-Path $svv) {{
    & $svv /SetDefault "{device_name}" 2
    Write-Host "OK"
}} else {{
    Write-Host "TOOL_NOT_FOUND"
}}
'''
        
        result = subprocess.run(
            ['powershell', '-Command', ps_cmd],
            capture_output=True, text=True, timeout=10
        )
        return 'OK' in result.stdout
    except Exception as e:
        print(f"[DEBUG] 设置失败: {e}")
        return False

def download_soundvolumeview():
    """下载 SoundVolumeView 工具"""
    try:
        print("[下载] 正在下载音频控制工具...")
        url = "https://www.nirsoft.net/utils/soundvolumeview-x64.zip"
        zip_path = os.path.expandvars('$TEMP\\svv.zip')
        
        # 下载
        subprocess.run([
            'powershell', '-Command',
            f'Invoke-WebRequest -Uri "{url}" -OutFile "{zip_path}" -UseBasicParsing'
        ], check=True, capture_output=True, timeout=30)
        
        # 解压
        subprocess.run([
            'powershell', '-Command',
            f'Expand-Archive -Path "{zip_path}" -DestinationPath "$env:TEMP" -Force'
        ], check=True, capture_output=True)
        
        exe_path = os.path.expandvars('$TEMP\\SoundVolumeView.exe')
        if os.path.exists(exe_path):
            print("✓ 工具下载成功")
            return True
        else:
            print("✗ 解压失败")
            return False
    except Exception as e:
        print(f"✗ 下载失败: {e}")
        return False

def show_manual_guide(vb_cable_name):
    """显示手动设置指南"""
    print()
    print("=" * 60)
    print("请手动设置音频设备")
    print("=" * 60)
    print()
    print("【步骤 1】设置播放设备（输出）：")
    print("  1. 右键任务栏音量图标 → 声音设置")
    print("  2. 点击'更多声音设置'")
    print("  3. 播放选项卡 → 找到'VB-Audio Virtual Cable'")
    print("  4. 右键 → 设置为默认设备")
    print()
    print("【步骤 2】设置录制设备（输入）：")
    print("  1. 录制选项卡 → 找到'VB-Audio Virtual Cable'")
    print("  2. 右键 → 设置为默认设备")
    print()
    print("【步骤 3】禁用监听（如果之前启用了）：")
    print("  1. 双击'VB-Audio Virtual Cable'（录制）")
    print("  2. 监听选项卡 → 取消勾选'监听此设备'")
    print("  3. 点击应用 → 确定")
    print()
    print("=" * 60)
    print("设置完成后，音频路由：")
    print("  TTS → VB-Cable → 豆包（听到）")
    print("=" * 60)
    print()

def test_tts():
    """测试 TTS"""
    try:
        ps_script = '''
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.Speak("测试音频")
'''
        subprocess.run(
            ['powershell', '-Command', ps_script],
            timeout=10, capture_output=True
        )
        return True
    except:
        return False

def main():
    print("=" * 60)
    print("全自动音频路由修复")
    print("=" * 60)
    print()
    
    # 1. 检查 VB-Cable
    print("[1/3] 检查 VB-Cable...")
    vb_cable = find_vb_cable()
    
    if not vb_cable:
        print("✗ 未找到 VB-Cable")
        print()
        print("已安装的音频设备:")
        devices = get_audio_devices()
        for dev in devices:
            print(f"  - {dev.get('Name', 'Unknown')}")
        print()
        print("如果 VB-Cable 已安装但未显示，请重启电脑")
        input("按回车退出...")
        return
    
    print(f"✓ 找到 VB-Cable: {vb_cable}")
    
    # 2. 尝试下载工具
    print()
    print("[2/3] 准备音频控制工具...")
    exe_path = os.path.expandvars('$TEMP\\SoundVolumeView.exe')
    
    auto_setup = False
    if not os.path.exists(exe_path):
        print("尝试下载工具...")
        if download_soundvolumeview():
            auto_setup = True
        else:
            print("自动下载失败，将使用手动设置")
            auto_setup = False
    else:
        print("✓ 工具已存在")
        auto_setup = True
    
    # 3. 设置音频设备
    print()
    print("[3/3] 配置音频设备...")
    
    if auto_setup:
        print("尝试自动设置...")
        success_playback = set_audio_device(vb_cable, 'playback')
        success_recording = set_audio_device(vb_cable, 'recording')
        
        if success_playback and success_recording:
            print("✓ 自动设置成功")
            print()
            print("等待设置生效...")
            time.sleep(3)
            
            # 测试 TTS
            print("测试 TTS...")
            if test_tts():
                print("✓ TTS 测试完成")
            else:
                print("✗ TTS 测试失败")
        else:
            print("✗ 自动设置失败，切换到手动设置")
            show_manual_guide(vb_cable)
    else:
        show_manual_guide(vb_cable)
    
    print()
    print("=" * 60)
    print("配置完成！")
    print("=" * 60)
    print()
    print("音频路由:")
    print("  TTS → VB-Cable → 豆包（应该能听到）")
    print()
    print("你现在可以:")
    print("1. 检查豆包是否有反应")
    print("2. 运行 launch_stream.bat 开始直播")
    print()
    print("注意：你自己听不到 TTS（这是正常的）")
    print("      通过 OBS 监听听到豆包和游戏声音")
    print()
    
    input("按回车退出...")

if __name__ == "__main__":
    main()
