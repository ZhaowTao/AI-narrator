"""
豆包AI自动解说脚本 - 跨平台语音触发版
==========================================
功能：定时用TTS语音向豆包发送提示，触发其语音解说当前屏幕内容。

原理：
1. 与豆包发起语音通话并共享屏幕，豆包能看到你的屏幕
2. 脚本用TTS生成语音，通过sounddevice直接输出到VB-Cable
3. TTS声音只走VB-Cable，OBS采集不到（观众听不到）
4. 豆包从VB-Cable听到提示后进行语音解说
5. OBS从BlackHole采集豆包和游戏的声音（观众能听到）

跨平台支持：
- macOS：say + sounddevice 直接输出到VB-Cable
- Windows：使用 edge-tts（微软免费TTS，需 pip install edge-tts）

使用前提：
- 已安装豆包桌面客户端并登录
- 已与豆包发起语音通话并共享屏幕
- Python 3.8+ 环境

依赖安装：
    macOS:  pip install sounddevice soundfile
    Windows: pip install edge-tts

作者：ZhaowTao
日期：2026-04-07
项目地址：https://github.com/ZhaowTao/AI-narrator
"""

import time
import random
import logging
import sys
import os
import tempfile
import argparse
import subprocess

# ============================================================
# 配置区域 - 根据你的实际情况修改以下参数
# ============================================================

# -------------------------------------------------------
# 第1阶段：角色设定（启动时发送一次）
# 告诉豆包它是谁、该怎么表现
#
# 设计参考：
# - 火山引擎角色扮演提示词指南（SP框架：角色信息 + 用户信息 + Golden SP）
# - 学术论文 "Real-Time Generation of Game Video Commentary" 提示词三要素
# - Claude 4 系统提示词设计理念（Anthropic 官方发布 + 泄露版分析）
# - 实际直播踩坑经验总结
# -------------------------------------------------------
SYSTEM_PROMPT = (
    "你现在是游戏直播解说员，通过屏幕共享看主播玩游戏，给直播间观众做实时解说。"
    "主播不说话不回应，你是单口解说，绝对不要对主播说话或提问。"
    "风格口语化接地气，像朋友边看边聊，不要书面语不要播音腔不要列表编号。"
    "平淡画面一两句带过，精彩时刻多说几句。善用比喻吐槽增加趣味，但别刻意搞笑。"
    "每次解说换个角度和表达方式，不要重复之前的话、比喻或句式。"
    "能看到弹幕，每次解说都结合弹幕内容互动，回应有趣的弹幕或顺着弹幕话题聊，让观众有参与感。"
    "不是游戏画面时别慌，调侃一下或聊刚才的游戏，别沉默别说不知道。"
    "理解了请回复收到。"
)

# -------------------------------------------------------
# 第2阶段：触发词（循环随机发送）
# 角色设定到位后，只需要简短的触发词就能让豆包持续解说
# 设计原则：每条触发词引导豆包关注不同的解说角度
# -------------------------------------------------------
TRIGGER_PROMPTS = [
    # --- 画面描述类 ---
    "描述一下当前画面",
    "画面有什么变化",
    "注意到了什么细节",
    # --- 评价分析类 ---
    "评价一下刚才的操作",
    "这个局面你怎么看",
    "刚才发生了什么，分析一下",
    # --- 预测悬念类 ---
    "猜猜接下来会怎样",
    "接下来会怎么发展",
    "如果换做你，你会怎么做",
    # --- 互动话题类 ---
    "抛个话题给观众聊聊",
    "有什么相关的趣事或冷知识吗",
    "这个游戏最吸引你的地方是什么",
    # --- 氛围调节类 ---
    "换个风格聊聊",
    "用不同的角度说说",
    "来段轻松的闲聊",
    # --- 弹幕互动类 ---
    "弹幕有什么有趣的吗",
    "回应一下弹幕",
]

# 两条触发之间的等待时间（秒）
INTERVAL_MIN = 10  # 最小间隔
INTERVAL_MAX = 30  # 最大间隔

# 角色设定发送后，等待豆包消化理解的额外时间（秒）
SYSTEM_PROMPT_DELAY = 5

# -------------------------------------------------------
# 提示词发送策略
# -------------------------------------------------------
# "random"  = 随机抽取（推荐，避免重复感）
# "sequential" = 按顺序循环
PROMPT_STRATEGY = "random"

# 是否在启动时发送角色设定（建议开启，让豆包进入解说员模式）
SEND_SYSTEM_PROMPT = True

# ============================================================
# TTS 配置（根据平台自动选择）
# ============================================================

IS_MAC = sys.platform == "darwin"
IS_WIN = sys.platform == "win32"

# --- macOS TTS 配置（使用 sounddevice 直接输出到 VB-Cable）---
MAC_VOICE = "Ting-Ting"  # 默认女声
# 其他可选：Mei-Jia（女声）、Li-Mu（男声）
# 查看所有语音：say -v '?' | grep zh
MAC_RATE = 180  # 语速（每分钟字数），默认175，范围80-300
MAC_OUTPUT_DEVICE = 4  # VB-Cable 设备ID（用 --list-audio 查看）

# --- Windows TTS 配置（使用 edge-tts）---
WIN_VOICE = "zh-CN-YunxiNeural"  # 中文男声（云希）
# 其他可选：
#   zh-CN-XiaoxiaoNeural  - 中文女声（晓晓），温柔自然
#   zh-CN-YunjianNeural   - 中文男声（云健），沉稳大气
#   zh-CN-XiaoyiNeural    - 中文女声（晓伊），知性优雅
WIN_RATE = "+0%"    # 语速调整
WIN_VOLUME = "+0%"  # 音量调整

# 是否启用日志
ENABLE_LOG = True
LOG_FILE = "doubao_narrator.log"


# ============================================================
# 日志配置
# ============================================================

def setup_logging():
    if not ENABLE_LOG:
        return
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


# ============================================================
# macOS TTS（使用系统内置 say 命令）
# ============================================================

def speak_macos(text: str, voice: str = None, rate: int = None) -> bool:
    ###"""使用 sounddevice 直接输出到 VB-Cable绕过 CoreAudio 系统音频栈"""
    v = voice or MAC_VOICE
    r = rate or MAC_RATE
    output_device = MAC_OUTPUT_DEVICE
    
    try:
        import sounddevice as sd
        import soundfile as sf
        import tempfile
        import numpy as np
        
        # 第1步：生成音频文件（不发声）
        with tempfile.NamedTemporaryFile(suffix='.aiff', delete=False) as f:
            temp_file = f.name
        
        subprocess.run(['say', '-v', v, '-r', str(r), '-o', temp_file, text], 
                      check=True, timeout=30)
        
        # 第2步：用 sounddevice 直接播放到 VB-Cable
        data, samplerate = sf.read(temp_file)
        sd.play(data, samplerate, device=output_device)
        sd.wait()
        
        # 清理
        os.unlink(temp_file)
        return True
        
    except subprocess.TimeoutExpired:
        logging.error("say 命令超时")
        return False
    except Exception as e:
        logging.error(f"macOS TTS失败: {e}")
        return False


def list_macos_voices():
    """列出 macOS 可用的中文语音"""
    try:
        result = subprocess.run(
            ["say", "-v", "?", "--voice=zh"],
            capture_output=True, text=True, timeout=10
        )
        print("\n🎤 macOS 可用的中文语音：\n")
        print(result.stdout)
    except Exception as e:
        print(f"获取语音列表失败: {e}")


# ============================================================
# Windows TTS（使用 edge-tts）
# ============================================================

def speak_windows(text: str, voice: str = None, rate: str = None, volume: str = None) -> bool:
    """使用 edge-tts 生成并播放语音（Windows）"""
    v = voice or WIN_VOICE
    r = rate or WIN_RATE
    vol = volume or WIN_VOLUME

    try:
        import edge_tts
    except ImportError:
        logging.error("Windows 平台需要安装 edge-tts: pip install edge-tts")
        logging.error("正在尝试使用系统自带 TTS...")
        return speak_windows_fallback(text)

    # 生成临时语音文件
    temp_dir = tempfile.mkdtemp(prefix="doubao_tts_")
    audio_file = os.path.join(temp_dir, "prompt.mp3")

    try:
        # 异步生成TTS
        async def _generate():
            communicate = edge_tts.Communicate(text, v, rate=r, volume=vol)
            await communicate.save(audio_file)

        import asyncio
        asyncio.run(_generate())

        # 播放音频文件
        play_success = play_audio_windows(audio_file)
        return play_success

    except Exception as e:
        logging.error(f"edge-tts 失败: {e}")
        return speak_windows_fallback(text)

    finally:
        try:
            os.remove(audio_file)
            os.rmdir(temp_dir)
        except Exception:
            pass


def speak_windows_fallback(text: str) -> bool:
    """Windows 备用方案：使用系统 SAPI"""
    try:
        import win32com.client
        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        speaker.Speak(text)
        return True
    except ImportError:
        pass
    except Exception as e:
        logging.error(f"SAPI TTS失败: {e}")

    # 最后的备用：使用 PowerShell
    try:
        ps_cmd = f'Add-Type -AssemblyName System.Speech; $s = New-Object System.Speech.Synthesis.SpeechSynthesizer; $s.Speak("{text}")'
        subprocess.run(["powershell", "-Command", ps_cmd], timeout=30)
        return True
    except Exception as e:
        logging.error(f"PowerShell TTS也失败了: {e}")
        return False


def play_audio_windows(file_path: str) -> bool:
    """在 Windows 上播放音频文件"""
    try:
        # 方案1：pygame
        import pygame
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        pygame.mixer.quit()
        return True
    except ImportError:
        pass

    try:
        # 方案2：winsound
        import winsound
        winsound.PlaySound(file_path, winsound.SND_FILENAME)
        return True
    except Exception:
        pass

    try:
        # 方案3：系统命令
        os.system(f'start /wait "" "{file_path}"')
        return True
    except Exception as e:
        logging.error(f"音频播放失败: {e}")
        return False


async def list_windows_voices():
    """列出 Windows edge-tts 可用的中文语音"""
    try:
        import edge_tts
        voices = await edge_tts.list_voices()
        chinese = [v for v in voices if v["Locale"].startswith("zh-CN")]
        male = [v for v in chinese if "Male" in v.get("Gender", "")]
        female = [v for v in chinese if "Female" in v.get("Gender", "")]
        print("\n🎤 Windows edge-tts 可用的中文语音：\n")
        print("👨 男声：")
        for v in male:
            print(f"   {v['ShortName']:30s} - {v.get('FriendlyName', '')}")
        print("\n👩 女声：")
        for v in female:
            print(f"   {v['ShortName']:30s} - {v.get('FriendlyName', '')}")
    except ImportError:
        print("需要先安装 edge-tts: pip install edge-tts")


# ============================================================
# 核心功能
# ============================================================

class DoubaoNarrator:
    """豆包自动解说控制器（跨平台语音触发版）"""

    def __init__(self):
        self.prompt_index = 0
        self.running = True
        self.send_count = 0
        self.platform = "macOS" if IS_MAC else ("Windows" if IS_WIN else "Linux")
        self.system_prompt_sent = False

    def get_next_prompt(self) -> str:
        """获取解说提示语（两阶段设计）"""
        # 第1阶段：还没发送角色设定，先发送角色设定
        if SEND_SYSTEM_PROMPT and not self.system_prompt_sent:
            self.system_prompt_sent = True
            return SYSTEM_PROMPT
        
        # 第2阶段：根据策略选择触发词
        if PROMPT_STRATEGY == "random":
            prompt = random.choice(TRIGGER_PROMPTS)
        else:
            # 顺序循环
            prompt = TRIGGER_PROMPTS[self.prompt_index % len(TRIGGER_PROMPTS)]
            self.prompt_index += 1
        return prompt

    def speak_to_doubao(self, text: str):
        """用语音向豆包发送提示"""
        logging.info(f"📝 准备语音提示: {text}")

        if IS_MAC:
            success = speak_macos(text)
        elif IS_WIN:
            success = speak_windows(text)
        else:
            # Linux: 尝试 espeak 或其他方案
            success = speak_linux(text)

        if success:
            self.send_count += 1
            logging.info(f"✅ 第 {self.send_count} 条语音提示已播放")
        else:
            logging.error("❌ 语音播放失败")

    def wait_for_reply(self):
        """等待豆包回复完毕后再发送下一条"""
        wait_time = random.uniform(INTERVAL_MIN, INTERVAL_MAX)
        logging.info(f"⏳ 等待 {wait_time:.1f} 秒后发送下一条提示...")
        time.sleep(wait_time)

    def run(self):
        """主循环：定时语音触发豆包解说"""
        logging.info("=" * 60)
        logging.info("🎮 豆包AI自动解说脚本（跨平台语音触发版）已启动")
        logging.info("=" * 60)
        logging.info(f"💻 运行平台: {self.platform}")
        logging.info(f"🎤 TTS引擎: {'系统内置 say' if IS_MAC else 'edge-tts'}")
        if IS_MAC:
            logging.info(f"🗣️  语音: {MAC_VOICE}, 语速: {MAC_RATE}")
        elif IS_WIN:
            logging.info(f"🗣️  语音: {WIN_VOICE}")
        if SEND_SYSTEM_PROMPT:
            logging.info(f"📋 角色设定: 已启用（第1阶段）")
            logging.info(f"📋 触发词数量: {len(TRIGGER_PROMPTS)}（第2阶段）")
        else:
            logging.info(f"📋 提示词: 禁用角色设定")
        logging.info(f"⏱️  发送间隔: {INTERVAL_MIN}-{INTERVAL_MAX} 秒")
        logging.info("")
        logging.info("⚠️  使用说明:")
        logging.info("   1. 请确保豆包客户端已打开并登录")
        logging.info("   2. 请先与豆包发起语音通话并共享屏幕")
        logging.info("   3. 确保电脑麦克风能拾取到TTS播放的声音")
        logging.info("      （推荐配置虚拟音频线路，详见教程文档）")
        logging.info("   4. 按 Ctrl+C 停止脚本")
        logging.info("")
        logging.info("⏳ 5秒后开始自动解说...")
        logging.info("=" * 60)

        for i in range(5, 0, -1):
            print(f"\r   倒计时: {i} 秒...", end="", flush=True)
            time.sleep(1)
        print("\r   🚀 开始！                    ")

        try:
            while self.running:
                prompt = self.get_next_prompt()
                self.speak_to_doubao(prompt)
                if getattr(self, 'once_mode', False):
                    logging.info("\n\n✅ 单次模式：已发送一条提示")
                    break
                self.wait_for_reply()
        except KeyboardInterrupt:
            logging.info("\n\n🛑 脚本已手动停止")
            logging.info(f"📊 本次共发送 {self.send_count} 条语音提示")


# ============================================================
# Linux TTS（备用）
# ============================================================

def speak_linux(text: str) -> bool:
    """Linux TTS：尝试 espeak"""
    try:
        subprocess.run(["espeak", "-v", "zh", text], check=True, timeout=30)
        return True
    except FileNotFoundError:
        logging.error("Linux 需要 espeak: sudo apt install espeak")
        return False
    except Exception as e:
        logging.error(f"Linux TTS失败: {e}")
        return False


# ============================================================
# 高级功能：屏幕截图感知（可选）
# ============================================================

class ScreenAwareNarrator(DoubaoNarrator):
    """带屏幕截图感知的解说器"""

    def __init__(self, volc_ark_api_key: str = None, model: str = "doubao-1.5-vision-pro-32k"):
        super().__init__()
        self.api_key = volc_ark_api_key
        self.model = model
        self.use_vision = volc_ark_api_key is not None

        if self.use_vision:
            try:
                import base64
                from openai import OpenAI
                self.base64 = base64
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url="https://ark.cn-beijing.volces.com/api/v3"
                )
                logging.info("👁️ 视觉分析功能已启用")
            except ImportError:
                logging.warning("⚠️ 缺少 openai 库: pip install openai")
                self.use_vision = False

    def capture_and_analyze(self) -> str:
        if not self.use_vision:
            return self.get_next_prompt()
        try:
            import pyautogui, io
            screenshot = pyautogui.screenshot()
            buf = io.BytesIO()
            screenshot.save(buf, format="PNG")
            img_b64 = self.base64.b64encode(buf.getvalue()).decode("utf-8")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是直播解说助手。根据截图生成20字以内的解说提示语。只输出提示语。"},
                    {"role": "user", "content": [
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}},
                        {"type": "text", "text": "根据截图生成解说提示语。"}
                    ]}
                ],
                max_tokens=100,
            )
            prompt = response.choices[0].message.content.strip()
            logging.info(f"👁️ 视觉分析提示: {prompt}")
            return prompt
        except Exception as e:
            logging.error(f"❌ 视觉分析失败: {e}")
            return self.get_next_prompt()

    def run(self):
        logging.info("=" * 60)
        logging.info("🎮 豆包AI自动解说脚本（视觉增强版）已启动")
        logging.info("=" * 60)
        for i in range(5, 0, -1):
            print(f"\r   倒计时: {i} 秒...", end="", flush=True)
            time.sleep(1)
        print("\r   🚀 开始！                    ")
        try:
            while self.running:
                prompt = self.capture_and_analyze() if self.use_vision else self.get_next_prompt()
                self.speak_to_doubao(prompt)
                self.wait_for_reply()
        except KeyboardInterrupt:
            logging.info(f"\n\n🛑 脚本已停止，共发送 {self.send_count} 条提示")


# ============================================================
# 入口
# ============================================================

def main():
    setup_logging()

    parser = argparse.ArgumentParser(
        description="豆包AI自动解说脚本（跨平台语音触发版）",
        epilog="示例:\n"
               "  macOS:   python3 doubao_narrator.py --voice Ting-Ting --rate 180\n"
               "  Windows: python doubao_narrator.py --voice zh-CN-YunxiNeural\n"
               "  查看音色: python doubao_narrator.py --list-voices",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--vision", action="store_true", help="启用视觉分析（需要火山引擎API Key）")
    parser.add_argument("--api-key", type=str, default=None, help="火山引擎API Key")
    parser.add_argument("--interval-min", type=int, default=None, help="最小发送间隔（秒）")
    parser.add_argument("--interval-max", type=int, default=None, help="最大发送间隔（秒）")
    parser.add_argument("--voice", type=str, default=None, help="TTS音色名称")
    parser.add_argument("--rate", type=str, default=None, help="语速（macOS: 数字如180；Windows: 如+10%%）")
    parser.add_argument("--list-voices", action="store_true", help="列出所有可用的中文TTS音色")
    parser.add_argument("--list-audio", action="store_true", help="列出所有可用的音频输出设备")
    parser.add_argument("--audio-device", type=str, default=None, help="TTS输出设备名称")
    parser.add_argument("--once", action="store_true", help="只发送一条提示然后退出")
    args = parser.parse_args()

    # 列出可用音频设备
    if args.list_audio:
        if IS_MAC:
            import sounddevice as sd
            print("\n🎤 可用的音频设备：\n")
            print(sd.query_devices())
        return

    # 列出可用音色
    if args.list_voices:
        if IS_MAC:
            list_macos_voices()
        elif IS_WIN:
            import asyncio
            asyncio.run(list_windows_voices())
        else:
            print("Linux: 使用 espeak，运行 espeak --voices=zh 查看可用语音")
        return

    # 更新全局配置
    global INTERVAL_MIN, INTERVAL_MAX, MAC_VOICE, MAC_RATE, MAC_OUTPUT_DEVICE, WIN_VOICE, WIN_RATE
    if args.interval_min is not None:
        INTERVAL_MIN = args.interval_min
    if args.interval_max is not None:
        INTERVAL_MAX = args.interval_max
    if args.voice is not None:
        if IS_MAC:
            MAC_VOICE = args.voice
        elif IS_WIN:
            WIN_VOICE = args.voice
    if args.rate is not None:
        if IS_MAC:
            MAC_RATE = int(args.rate)
        elif IS_WIN:
            WIN_RATE = args.rate
    if args.audio_device is not None:
        MAC_OUTPUT_DEVICE = int(args.audio_device)

    # 创建解说器
    if args.vision and args.api_key:
        narrator = ScreenAwareNarrator(volc_ark_api_key=args.api_key)
    else:
        narrator = DoubaoNarrator()

    # 单次模式
    if args.once:
        narrator.once_mode = True

    narrator.run()


if __name__ == "__main__":
    main()
