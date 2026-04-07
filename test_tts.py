"""
测试macOS TTS功能
"""
import subprocess

def test_tts():
    print("🎤 正在测试macOS TTS功能...")
    test_text = "你好，这是一个测试，豆包AI自动解说脚本"
    
    try:
        # 使用macOS say命令播放
        print(f"📝 测试文本: {test_text}")
        subprocess.run(["say", "-v", "Ting-Ting", "-r", "200", test_text], check=True)
        print("✅ TTS测试成功！")
    except Exception as e:
        print(f"❌ TTS测试失败: {e}")

if __name__ == "__main__":
    test_tts()
