# -*- coding: utf-8 -*-
"""
AI Narrator 全功能测试脚本
测试所有核心功能是否正常工作
"""
import asyncio
import tempfile
import os
import sys
import time

def test_imports():
    """测试所有依赖是否能正常导入"""
    print("\n" + "="*60)
    print("测试1: 依赖导入测试")
    print("="*60)
    
    tests = [
        ("edge_tts", "edge-tts 语音合成库"),
        ("pygame", "pygame 音频播放库"),
        ("asyncio", "异步IO库"),
        ("tempfile", "临时文件库"),
    ]
    
    all_passed = True
    for module, description in tests:
        try:
            __import__(module)
            print(f"  [OK] {description} ({module})")
        except ImportError as e:
            print(f"  [FAIL] {description} ({module}): {e}")
            all_passed = False
    
    return all_passed


async def test_voice_list():
    """测试获取语音列表功能"""
    print("\n" + "="*60)
    print("测试2: 语音列表获取")
    print("="*60)
    
    try:
        import edge_tts
        voices = await edge_tts.list_voices()
        
        # 筛选中文语音
        zh_voices = [v for v in voices if v['Locale'].startswith('zh')]
        zh_cn_voices = [v for v in voices if v['Locale'].startswith('zh-CN')]
        
        print(f"  总语音数: {len(voices)}")
        print(f"  中文语音数: {len(zh_voices)}")
        print(f"  简体中文语音数: {len(zh_cn_voices)}")
        
        print("\n  可用的中文语音:")
        for v in zh_cn_voices[:8]:
            gender = "男" if "Male" in v.get("Gender", "") else "女"
            print(f"    - {v['ShortName']} ({gender})")
        
        return len(zh_cn_voices) > 0
    except Exception as e:
        print(f"  [FAIL] 获取语音列表失败: {e}")
        return False


async def test_tts_generation():
    """测试语音合成功能"""
    print("\n" + "="*60)
    print("测试3: 语音合成测试")
    print("="*60)
    
    try:
        import edge_tts
        
        test_cases = [
            ("继续", "zh-CN-YunxiNeural"),
            ("你好，这是测试", "zh-CN-XiaoxiaoNeural"),
        ]
        
        for text, voice in test_cases:
            print(f"\n  测试: '{text}' with voice '{voice}'")
            
            # 创建临时文件
            temp_dir = tempfile.mkdtemp(prefix="tts_test_")
            audio_file = os.path.join(temp_dir, "test.mp3")
            
            # 生成语音
            start_time = time.time()
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(audio_file)
            elapsed = time.time() - start_time
            
            # 检查文件
            if os.path.exists(audio_file):
                file_size = os.path.getsize(audio_file)
                print(f"    [OK] 生成成功 ({file_size} bytes, {elapsed:.2f}s)")
                
                # 清理
                os.remove(audio_file)
                os.rmdir(temp_dir)
            else:
                print(f"    [FAIL] 文件未生成")
                return False
        
        return True
    except Exception as e:
        print(f"  [FAIL] 语音合成失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_audio_playback():
    """测试音频播放功能"""
    print("\n" + "="*60)
    print("测试4: 音频播放测试")
    print("="*60)
    
    try:
        import pygame
        
        # 检查 pygame 是否可用
        pygame.mixer.init()
        pygame.mixer.quit()
        print("  [OK] pygame 音频初始化成功")
        return True
    except Exception as e:
        print(f"  [FAIL] 音频播放初始化失败: {e}")
        return False


async def test_full_workflow():
    """测试完整工作流程"""
    print("\n" + "="*60)
    print("测试5: 完整工作流程测试")
    print("="*60)
    
    try:
        import edge_tts
        import pygame
        
        # 模拟主程序的工作流程
        text = "继续"
        voice = "zh-CN-YunxiNeural"
        
        print(f"\n  步骤1: 生成语音 - '{text}'")
        temp_dir = tempfile.mkdtemp(prefix="workflow_")
        audio_file = os.path.join(temp_dir, "prompt.mp3")
        
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(audio_file)
        print(f"    [OK] 语音文件已保存")
        
        print(f"\n  步骤2: 播放语音")
        pygame.mixer.init()
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()
        
        # 等待播放完成
        wait_count = 0
        while pygame.mixer.music.get_busy() and wait_count < 50:
            time.sleep(0.1)
            wait_count += 1
        
        pygame.mixer.quit()
        print(f"    [OK] 语音播放完成")
        
        # 清理
        os.remove(audio_file)
        os.rmdir(temp_dir)
        
        print(f"\n  步骤3: 清理临时文件")
        print(f"    [OK] 临时文件已清理")
        
        return True
    except Exception as e:
        print(f"  [FAIL] 工作流程测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_doubao_narrator_class():
    """测试 DoubaoNarrator 类的基本功能"""
    print("\n" + "="*60)
    print("测试6: DoubaoNarrator 类测试")
    print("="*60)
    
    try:
        # 导入主程序中的类
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from doubao_narrator import DoubaoNarrator, SYSTEM_PROMPT, TRIGGER_PROMPTS
        
        # 创建实例
        narrator = DoubaoNarrator()
        print("  [OK] DoubaoNarrator 实例创建成功")
        
        # 测试获取提示词
        prompt = narrator.get_next_prompt()
        print(f"  [OK] 获取提示词: '{prompt[:30]}...' " if len(prompt) > 30 else f"  [OK] 获取提示词: '{prompt}'")
        
        # 测试配置
        print(f"  [OK] 平台检测: {narrator.platform}")
        print(f"  [OK] 触发词数量: {len(TRIGGER_PROMPTS)}")
        
        return True
    except Exception as e:
        print(f"  [FAIL] DoubaoNarrator 类测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_multiple_voices():
    """测试多个语音音色"""
    print("\n" + "="*60)
    print("测试7: 多语音音色测试")
    print("="*60)
    
    try:
        import edge_tts
        
        voices_to_test = [
            "zh-CN-YunxiNeural",
            "zh-CN-XiaoxiaoNeural",
            "zh-CN-YunjianNeural",
        ]
        
        text = "测试"
        
        for voice in voices_to_test:
            print(f"\n  测试语音: {voice}")
            
            temp_dir = tempfile.mkdtemp(prefix="voice_test_")
            audio_file = os.path.join(temp_dir, "test.mp3")
            
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(audio_file)
            
            if os.path.exists(audio_file):
                file_size = os.path.getsize(audio_file)
                print(f"    [OK] 生成成功 ({file_size} bytes)")
                os.remove(audio_file)
                os.rmdir(temp_dir)
            else:
                print(f"    [FAIL] 生成失败")
                return False
        
        return True
    except Exception as e:
        print(f"  [FAIL] 多语音测试失败: {e}")
        return False


async def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("AI Narrator 全功能测试")
    print("="*60)
    print(f"Python版本: {sys.version}")
    print(f"平台: {sys.platform}")
    print("="*60)
    
    results = []
    
    # 运行所有测试
    results.append(("依赖导入", test_imports()))
    results.append(("语音列表", await test_voice_list()))
    results.append(("语音合成", await test_tts_generation()))
    results.append(("音频播放", test_audio_playback()))
    results.append(("完整流程", await test_full_workflow()))
    results.append(("DoubaoNarrator类", test_doubao_narrator_class()))
    results.append(("多语音测试", await test_multiple_voices()))
    
    # 打印测试结果汇总
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    
    passed = 0
    failed = 0
    for name, result in results:
        status = "通过" if result else "失败"
        symbol = "[OK]" if result else "[FAIL]"
        print(f"  {symbol} {name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("="*60)
    print(f"总计: {len(results)} 项测试")
    print(f"通过: {passed} 项")
    print(f"失败: {failed} 项")
    
    if failed == 0:
        print("\n  所有测试通过！系统运行正常。")
        return 0
    else:
        print(f"\n  有 {failed} 项测试失败，请检查配置。")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
