# 设置 VB-Cable 监听功能
Write-Host "正在配置 VB-Cable 音频监听..." -ForegroundColor Green

# 启用 CABLE Output 的监听功能
$cable = Get-AudioDevice -List | Where-Object { $_.Name -like "*CABLE*" }

if ($cable) {
    Write-Host "找到 VB-Cable 设备: $($cable.Name)" -ForegroundColor Cyan
    
    # 设置为默认录制设备
    Set-AudioDevice -Recording -Index $cable.Index
    Write-Host "已将 VB-Cable 设为默认录制设备" -ForegroundColor Green
    
    Write-Host "`n请手动完成以下步骤:" -ForegroundColor Yellow
    Write-Host "1. 右键任务栏音量图标 → 声音设置" -ForegroundColor White
    Write-Host "2. 点击底部 '更多声音设置'" -ForegroundColor White
    Write-Host "3. 切换到 '录制' 选项卡" -ForegroundColor White
    Write-Host "4. 双击 'CABLE Output'" -ForegroundColor White
    Write-Host "5. 切换到 '监听' 选项卡" -ForegroundColor White
    Write-Host "6. 勾选 '监听此设备'" -ForegroundColor White
    Write-Host "7. '通过此设备播放' 选择你的扬声器" -ForegroundColor White
    Write-Host "8. 点击应用 → 确定" -ForegroundColor White
} else {
    Write-Host "未找到 VB-Cable 设备，请先安装 VB-Cable" -ForegroundColor Red
}

Read-Host "`n按回车键退出"
