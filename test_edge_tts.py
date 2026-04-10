"""
测试 edge-tts 是否正常工作
"""
import asyncio
import edge_tts

async def list_voices():
    """列出可用的中文语音"""
    voices = await edge_tts.list_voices()
    chinese = [v for v in voices if v['Locale'].startswith('zh-CN')]
    print("Available Chinese voices:")
    for v in chinese[:10]:
        print(f"  {v['ShortName']}")

async def test_tts():
    """测试 TTS 功能"""
    text = "你好，这是一个测试"
    voice = "zh-CN-YunxiNeural"
    output_file = "test_output.mp3"
    
    print(f"Testing TTS with voice: {voice}")
    print(f"Text: {text}")
    
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)
    
    print(f"Audio saved to: {output_file}")
    print("TTS test completed successfully!")

if __name__ == "__main__":
    print("=== Listing Voices ===")
    asyncio.run(list_voices())
    print("\n=== Testing TTS ===")
    asyncio.run(test_tts())
