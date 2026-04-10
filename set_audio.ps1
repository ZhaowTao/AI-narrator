# 设置默认音频设备
param(
    [string]$DeviceName,
    [int]$DeviceType = 1  # 1 = Playback, 2 = Recording
)

# 使用 Windows Core Audio API
Add-Type @"
using System;
using System.Runtime.InteropServices;

public class AudioDevice {
    [DllImport("user32.dll")]
    public static extern IntPtr SendMessage(IntPtr hWnd, uint Msg, IntPtr wParam, IntPtr lParam);
}
"@

# 打开声音设置
if ($DeviceType -eq 1) {
    Write-Host "设置播放设备: $DeviceName"
    # 使用控制面板命令
    rundll32.exe shell32.dll,Control_RunDLL mmsys.cpl,,0
} else {
    Write-Host "设置录制设备: $DeviceName"
    rundll32.exe shell32.dll,Control_RunDLL mmsys.cpl,,1
}

Write-Host "请在打开的窗口中手动设置默认设备"
