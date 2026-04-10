# -*- coding: utf-8 -*-
"""
简化版豆包AI自动解说脚本测试
"""
import asyncio
import tempfile
import os
import sys

# 测试 edge-tts
async def test_edge_tts():
    """测试 edge-tts 功能"""
    try:
        import edge_tts
        import pygame
        
        text = "继续"
        voice = "zh-CN-YunxiNeural"
        
        print("Testing edge-tts...")
        print(f"Text: {text}")
        print(f"Voice: {voice}")
        
        # 创建临时文件
        temp_dir = tempfile.mkdtemp(prefix="doubao_tts_")
        audio_file = os.path.join(temp_dir, "prompt.mp3")
        
        # 生成语音
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(audio_file)
        
        print(f"Audio file created: {audio_file}")
        
        # 播放音频
        print("Playing audio...")
        pygame.mixer.init()
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            import time
            time.sleep(0.1)
        
        pygame.mixer.quit()
        
        # 清理
        os.remove(audio_file)
        os.rmdir(temp_dir)
        
        print("Test completed successfully!")
        return True
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("AI Narrator Test")
    print("=" * 50)
    
    # 运行测试
    success = asyncio.run(test_edge_tts())
    
    if success:
        print("\nAll tests passed!")
        sys.exit(0)
    else:
        print("\nTests failed!")
        sys.exit(1)
