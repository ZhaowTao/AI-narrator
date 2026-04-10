# -*- coding: utf-8 -*-
"""
豆包AI自动解说脚本 - macOS 版本
使用 BlackHole 虚拟音频设备实现音频路由
"""
import time
import random
import logging
import sys
import os
import argparse
import subprocess
import platform

# ============================================================
# 配置区域
# ============================================================

# 优化后的提示词 - 短句无标点，防止豆包抢答
SYSTEM_PROMPT = (
    "【角色设定】"
    "你是游戏主播正在直播"
    "主播不说话你是单口直播"
    "你能看到游戏画面和弹幕"
    "有弹幕提问就回答"
    "有礼物就感谢"
    "同时解说游戏画面"
    "没有弹幕就解说游戏"
    "只描述游戏画面内容"
    "不编造不脑补"
    "不提游戏以外内容"
    "风格口语化像朋友聊天"
    "适当用卧槽哈哈哈等词"
    "每次换表达方式不重复"
    "【重要】"
    "现在只回复收到两个字"
    "不要开始解说"
    "等我说继续再说"
)

TRIGGER_PROMPTS = ["继续"]
INTERVAL_MIN = 10
INTERVAL_MAX = 30
SEND_SYSTEM_PROMPT = True
ENABLE_LOG = True
LOG_FILE = "doubao_narrator_mac.log"

# macOS 语音设置
MAC_VOICE = "Ting-Ting"  # 中文女声
MAC_RATE = 180  # 语速

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
# macOS 音频设备管理
# ============================================================

def get_default_output_device():
    """获取当前默认输出设备"""
    try:
        result = subprocess.run(
            ["osascript", "-e", 'output volume of (get volume settings)'],
            capture_output=True, text=True, timeout=5
        )
        # 获取设备名称
        result2 = subprocess.run(
            ["osascript", "-e", 'output device of (get volume settings)'],
            capture_output=True, text=True, timeout=5
        )
        return result2.stdout.strip()
    except:
        return None

def set_output_device(device_name):
    """设置系统默认输出设备"""
    try:
        script = f'tell application "System Events" to set volume output device to "{device_name}"'
        subprocess.run(["osascript", "-e", script], capture_output=True, timeout=5)
        return True
    except:
        return False

def switch_to_blackhole():
    """切换到 BlackHole 输出"""
    try:
        subprocess.run(
            ["osascript", "-e", 'set volume output device "BlackHole 2ch"'],
            capture_output=True, timeout=5
        )
        return True
    except:
        return False

def switch_to_speakers():
    """切换回扬声器"""
    try:
        # 尝试切换回内置扬声器
        subprocess.run(
            ["osascript", "-e", 'set volume output device "内置扬声器"'],
            capture_output=True, timeout=5
        )
        return True
    except:
        return False

def check_blackhole():
    """检查是否安装了 BlackHole"""
    try:
        result = subprocess.run(
            ["system_profiler", "SPAudioDataType"],
            capture_output=True, text=True, timeout=10
        )
        return "BlackHole" in result.stdout
    except:
        return False

# ============================================================
# macOS TTS
# ============================================================

class MacTTS:
    """macOS TTS 类"""

    def __init__(self, voice=None, rate=None):
        self.voice = voice or MAC_VOICE
        self.rate = rate or MAC_RATE
        logging.info(f"[OK] macOS TTS 初始化成功")
        logging.info(f"[INFO] 语音: {self.voice}, 语速: {self.rate}")

    def speak(self, text: str) -> bool:
        """播放语音"""
        try:
            # 限制文本长度
            if len(text) > 200:
                text = text[:200] + "..."

            # 使用 say 命令播放
            subprocess.run(
                ["say", "-v", self.voice, "-r", str(self.rate), text],
                timeout=60,
                capture_output=True
            )
            return True

        except subprocess.TimeoutExpired:
            logging.error("TTS 播放超时")
            return False
        except Exception as e:
            logging.error(f"TTS 失败: {e}")
            return False

    def speak_to_blackhole(self, text: str) -> bool:
        """播放语音到 BlackHole"""
        try:
            # 限制文本长度
            if len(text) > 200:
                text = text[:200] + "..."

            # 保存当前设备
            original_device = get_default_output_device()

            # 切换到 BlackHole
            if not switch_to_blackhole():
                logging.warning("无法切换到 BlackHole，使用默认设备")

            # 播放语音
            subprocess.run(
                ["say", "-v", self.voice, "-r", str(self.rate), text],
                timeout=60,
                capture_output=True
            )

            # 恢复原来的设备
            if original_device:
                set_output_device(original_device)

            return True

        except subprocess.TimeoutExpired:
            logging.error("TTS 播放超时")
            return False
        except Exception as e:
            logging.error(f"TTS 失败: {e}")
            return False

# ============================================================
# 核心功能
# ============================================================

class DoubaoNarratorMac:
    """豆包自动解说控制器 - macOS 版本"""

    def __init__(self, use_blackhole=True):
        self.prompt_index = 0
        self.running = True
        self.send_count = 0
        self.platform = "macOS"
        self.system_prompt_sent = False
        self.use_blackhole = use_blackhole
        self.tts = MacTTS()

    def get_next_prompt(self) -> str:
        """获取解说提示语"""
        if SEND_SYSTEM_PROMPT and not self.system_prompt_sent:
            self.system_prompt_sent = True
            return SYSTEM_PROMPT

        prompt = random.choice(TRIGGER_PROMPTS)
        return prompt

    def speak_to_doubao(self, text: str):
        """用语音向豆包发送提示"""
        display_text = text[:50] + "..." if len(text) > 50 else text
        logging.info(f"准备语音提示: {display_text}")

        if self.use_blackhole:
            success = self.tts.speak_to_blackhole(text)
        else:
            success = self.tts.speak(text)

        if success:
            self.send_count += 1
            logging.info(f"第 {self.send_count} 条语音提示已播放")
        else:
            logging.error("语音播放失败")

    def wait_for_reply(self):
        """等待一段时间后发送下一条"""
        wait_time = random.uniform(INTERVAL_MIN, INTERVAL_MAX)
        logging.info(f"等待 {wait_time:.1f} 秒后发送下一条提示...")
        time.sleep(wait_time)

    def run(self):
        """主循环"""
        logging.info("=" * 60)
        logging.info("豆包AI自动解说脚本（macOS 版）已启动")
        logging.info("=" * 60)
        logging.info(f"运行平台: {self.platform}")
        logging.info(f"TTS引擎: macOS say 命令")
        logging.info(f"语音: {MAC_VOICE}, 语速: {MAC_RATE}")

        if SEND_SYSTEM_PROMPT:
            logging.info(f"角色设定: 已启用（第1阶段）")
            logging.info(f"触发词数量: {len(TRIGGER_PROMPTS)}（第2阶段）")

        logging.info(f"发送间隔: {INTERVAL_MIN}-{INTERVAL_MAX} 秒")
        logging.info("")
        logging.info("重要提示:")
        logging.info("   1. 豆包使用 BlackHole 2ch 作为输入设备")
        logging.info("   2. 确保 BlackHole 已正确安装")
        logging.info("   3. OBS 添加音频输入采集: BlackHole 2ch")
        logging.info("   4. 按 Ctrl+C 停止脚本")
        logging.info("")
        logging.info("5秒后开始自动解说...")
        logging.info("=" * 60)

        for i in range(5, 0, -1):
            print(f"\r   倒计时: {i} 秒...", end="", flush=True)
            time.sleep(1)
        print("\r   开始！                    ")

        try:
            while self.running:
                prompt = self.get_next_prompt()
                self.speak_to_doubao(prompt)
                if getattr(self, 'once_mode', False):
                    logging.info("\n\n单次模式：已发送一条提示")
                    break
                self.wait_for_reply()
        except KeyboardInterrupt:
            logging.info("\n\n脚本已手动停止")
            logging.info(f"本次共发送 {self.send_count} 条语音提示")


# ============================================================
# 入口
# ============================================================

def print_setup_guide():
    """打印设置指南"""
    guide = """
╔══════════════════════════════════════════════════════════════╗
║                  豆包AI解说 - macOS 设置指南                  ║
╚══════════════════════════════════════════════════════════════╝

【音频路由方案】

TTS → BlackHole 2ch → 豆包（听到）
              ↓
         监听 → 耳机（你听到）

游戏声音 → 扬声器/耳机 → OBS → 直播
豆包解说 → 扬声器/耳机 → OBS → 直播

【配置步骤】

1. 安装 BlackHole
   brew install blackhole-2ch

2. 配置录制设备
   系统偏好设置 → 声音 → 输入 → BlackHole 2ch

3. 配置 OBS
   - 添加音频输入采集: BlackHole 2ch
   - 桌面音频: 耳机/扬声器

4. 启动豆包客户端
   - 发起语音通话
   - 开启屏幕共享

5. 运行脚本
   python doubao_narrator_mac.py

═══════════════════════════════════════════════════════════════
"""
    print(guide)


def main():
    setup_logging()

    parser = argparse.ArgumentParser(
        description="豆包AI自动解说脚本（macOS 版）",
        epilog="示例:\n"
               "  python doubao_narrator_mac.py\n"
               "  python doubao_narrator_mac.py --guide\n"
               "  python doubao_narrator_mac.py --interval-min 20 --interval-max 40\n"
               "  python doubao_narrator_mac.py --once",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--guide", action="store_true", help="显示音频设置指南")
    parser.add_argument("--no-blackhole", action="store_true", help="不使用 BlackHole 自动切换")
    parser.add_argument("--interval-min", type=int, default=None, help="最小发送间隔（秒）")
    parser.add_argument("--interval-max", type=int, default=None, help="最大发送间隔（秒）")
    parser.add_argument("--once", action="store_true", help="只发送一条提示然后退出")
    args = parser.parse_args()

    if args.guide:
        print_setup_guide()
        return

    # 检查是否安装了 BlackHole
    if check_blackhole():
        logging.info("[INFO] 检测到 BlackHole 已安装")
    else:
        logging.warning("[WARN] 未检测到 BlackHole")
        logging.info("[INFO] 安装命令: brew install blackhole-2ch")
        logging.info("[INFO] 或使用 --no-blackhole 参数运行")

    # 更新全局配置
    global INTERVAL_MIN, INTERVAL_MAX
    if args.interval_min is not None:
        INTERVAL_MIN = args.interval_min
    if args.interval_max is not None:
        INTERVAL_MAX = args.interval_max

    # 创建解说器
    narrator = DoubaoNarratorMac(use_blackhole=not args.no_blackhole)

    # 单次模式
    if args.once:
        narrator.once_mode = True

    narrator.run()


if __name__ == "__main__":
    main()
