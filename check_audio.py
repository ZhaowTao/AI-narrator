"""
检查macOS音频设备
帮助配置AI解说的音频路由
"""
import subprocess
import sys

def list_audio_devices():
    """列出macOS的音频设备"""
    print("🎵 macOS 音频设备检查\n")
    
    try:
        # 使用system_profiler获取音频设备信息
        result = subprocess.run(
            ["system_profiler", "SPAudioDataType"],
            capture_output=True,
            text=True,
            timeout=10
        )
        print("📋 音频设备信息：")
        print("=" * 60)
        print(result.stdout)
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ 获取音频设备失败: {e}")
    
    print("\n💡 配置提示：")
    print("-" * 60)
    print("1️⃣  终端/TTS输出 → VB-Cable (让豆包听到提示)")
    print("2️⃣  豆包麦克风输入 → VB-Cable (豆包听到提示)")
    print("3️⃣  OBS采集 → 豆包客户端 + 游戏音效 (观众听到)")
    print("-" * 60)

if __name__ == "__main__":
    list_audio_devices()
