# -*- coding: utf-8 -*-
"""
豆包AI自动解说脚本 - Windows 简化版
使用系统自带 TTS，无需安装额外依赖
"""
import time
import random
import logging
import sys
import os
import tempfile
import argparse
import subprocess
import threading

# ============================================================
# 配置区域 - 根据你的实际情况修改以下参数
# ============================================================

# 角色设定（启动时发送一次）
SYSTEM_PROMPT = (
    "你现在是bilibili游戏主播，正在直播玩游戏，和观众边玩边聊。"
    "主播不说话不回应，你是单口直播，观众只通过弹幕和你互动。"
    "你能看到游戏画面和弹幕。每次被触发时，自己判断当前情况："
    "如果有新弹幕提问就回答，有礼物就感谢，同时解说游戏画面，自然融合。"
    "如果没有新弹幕也没有礼物，就解说游戏画面，别干等着，也别凭空感谢。"
    "你只能描述游戏画面里实际发生的内容，不能编造或脑补。"
    "如果屏幕上出现游戏以外的内容，就当没看见，继续聊游戏，绝对不能提游戏以外的任何东西，保护主播隐私。"
    "弹幕提问一定要认真回答，不知道就瞎猜或聊你的看法，绝对不能只复述问题不回答。"
    "已经回应过的弹幕不要重复。"
    "风格口语化接地气，像朋友边看边聊，不要书面语不要播音腔不要列表编号。"
    "善用比喻吐槽增加趣味，适当用'卧槽''哈哈哈'等感叹词，但别太过。"
    "每次换个角度和表达方式，不要重复之前的话或句式。"
    "理解了请只回复收到两个字，不要开始解说，等我说继续再说。"
)

# 触发词（循环发送）
TRIGGER_PROMPTS = ["继续"]

# 发送间隔（秒）
INTERVAL_MIN = 10
INTERVAL_MAX = 30

# 是否发送角色设定
SEND_SYSTEM_PROMPT = True

# 日志配置
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
# Windows TTS（使用系统 SAPI）
# ============================================================

class WindowsTTS:
    """Windows 系统 TTS 类 - 使用 PowerShell"""
    
    def __init__(self):
        logging.info("[OK] Windows TTS 初始化成功")
    
    def speak(self, text: str) -> bool:
        """播放语音 - 使用 PowerShell TTS"""
        try:
            # 限制文本长度，避免 PowerShell 命令过长
            if len(text) > 200:
                text = text[:200] + "..."
            
            # 转义特殊字符
            safe_text = text.replace('"', '`"').replace("'", "`'")
            
            # 构建 PowerShell 命令
            ps_script = f'''
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.Speak("{safe_text}")
'''
            
            # 执行 PowerShell 命令
            result = subprocess.run(
                ["powershell", "-Command", ps_script],
                timeout=30,
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0:
                return True
            else:
                logging.error(f"PowerShell TTS 错误: {result.stderr.decode('gbk', errors='ignore')}")
                return False
                
        except subprocess.TimeoutExpired:
            logging.error("TTS 播放超时")
            return False
        except Exception as e:
            logging.error(f"TTS 失败: {e}")
            return False


# ============================================================
# 核心功能
# ============================================================

class DoubaoNarrator:
    """豆包自动解说控制器"""

    def __init__(self):
        self.prompt_index = 0
        self.running = True
        self.send_count = 0
        self.platform = "Windows"
        self.system_prompt_sent = False
        self.tts = WindowsTTS()

    def get_next_prompt(self) -> str:
        """获取解说提示语"""
        # 第1阶段：还没发送角色设定，先发送角色设定
        if SEND_SYSTEM_PROMPT and not self.system_prompt_sent:
            self.system_prompt_sent = True
            return SYSTEM_PROMPT
        
        # 第2阶段：发送触发词
        prompt = random.choice(TRIGGER_PROMPTS)
        return prompt

    def speak_to_doubao(self, text: str):
        """用语音向豆包发送提示"""
        logging.info(f"准备语音提示: {text[:50]}..." if len(text) > 50 else f"准备语音提示: {text}")

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
        """主循环：定时语音触发豆包解说"""
        logging.info("=" * 60)
        logging.info("豆包AI自动解说脚本（Windows 简化版）已启动")
        logging.info("=" * 60)
        logging.info(f"运行平台: {self.platform}")
        logging.info(f"TTS引擎: Windows 系统 SAPI")
        if SEND_SYSTEM_PROMPT:
            logging.info(f"角色设定: 已启用（第1阶段）")
            logging.info(f"触发词数量: {len(TRIGGER_PROMPTS)}（第2阶段）")
        else:
            logging.info(f"提示词: 禁用角色设定")
        logging.info(f"发送间隔: {INTERVAL_MIN}-{INTERVAL_MAX} 秒")
        logging.info("")
        logging.info("使用说明:")
        logging.info("   1. 请确保豆包客户端已打开并登录")
        logging.info("   2. 请先与豆包发起语音通话并共享屏幕")
        logging.info("   3. 确保电脑麦克风能拾取到TTS播放的声音")
        logging.info("      （推荐配置虚拟音频线路，详见教程文档）")
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

def main():
    setup_logging()

    parser = argparse.ArgumentParser(
        description="豆包AI自动解说脚本（Windows 简化版）",
        epilog="示例:\n"
               "  python doubao_narrator_simple.py\n"
               "  python doubao_narrator_simple.py --interval-min 20 --interval-max 40\n"
               "  python doubao_narrator_simple.py --once",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--interval-min", type=int, default=None, help="最小发送间隔（秒）")
    parser.add_argument("--interval-max", type=int, default=None, help="最大发送间隔（秒）")
    parser.add_argument("--once", action="store_true", help="只发送一条提示然后退出")
    args = parser.parse_args()

    # 更新全局配置
    global INTERVAL_MIN, INTERVAL_MAX
    if args.interval_min is not None:
        INTERVAL_MIN = args.interval_min
    if args.interval_max is not None:
        INTERVAL_MAX = args.interval_max

    # 创建解说器
    narrator = DoubaoNarrator()

    # 单次模式
    if args.once:
        narrator.once_mode = True

    narrator.run()


if __name__ == "__main__":
    main()
