# -*- coding: utf-8 -*-
"""
豆包AI自动解说脚本 - Windows 实用版
针对豆包不能设置独立音频设备的情况优化
"""
import time
import random
import logging
import sys
import os
import argparse
import subprocess
import json

# ============================================================
# 启动时强制设置音频设备
# ============================================================
def force_set_vb_cable():
    """强制设置 VB-Cable 为默认音频设备"""
    print("[系统] 正在配置音频设备...")
    print("[提示] 请确保以下设置：")
    print("  播放设备: CABLE Input")
    print("  录制设备: CABLE Output")
    
    # 打开声音设置让用户确认
    import os
    os.system("start mmsys.cpl")
    
    input("\n请手动设置音频设备后按回车继续...")
    return True

# 启动时执行
force_set_vb_cable()

# ============================================================
# 配置区域
# ============================================================

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
# Windows TTS - 支持指定音频设备
# ============================================================

class WindowsTTS:
    """Windows TTS 类 - 支持输出到指定音频设备"""
    
    def __init__(self, output_device=None):
        self.output_device = output_device
        logging.info(f"[OK] Windows TTS 初始化成功")
        if output_device:
            logging.info(f"[INFO] 音频输出设备: {output_device}")
    
    def speak(self, text: str) -> bool:
        """播放语音"""
        try:
            # 限制文本长度
            if len(text) > 200:
                text = text[:200] + "..."
            
            # 转义特殊字符
            safe_text = text.replace('"', '`"').replace("'", "`'")
            
            # 构建 PowerShell 脚本
            if self.output_device:
                # 指定输出设备
                ps_script = f'''
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.SetOutputToDefaultAudioDevice()
$synth.Speak("{safe_text}")
'''
            else:
                # 使用默认设备
                ps_script = f'''
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.Speak("{safe_text}")
'''
            
            result = subprocess.run(
                ["powershell", "-Command", ps_script],
                timeout=60,
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            return result.returncode == 0
                
        except subprocess.TimeoutExpired:
            logging.error("TTS 播放超时")
            return False
        except Exception as e:
            logging.error(f"TTS 失败: {e}")
            return False


# ============================================================
# 音频设备管理
# ============================================================

def list_audio_devices():
    """列出所有音频设备"""
    try:
        ps_script = '''
Get-WmiObject Win32_SoundDevice | Select-Object Name, Status | ConvertTo-Json
'''
        result = subprocess.run(
            ["powershell", "-Command", ps_script],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        if result.returncode == 0:
            devices = json.loads(result.stdout)
            print("\n系统音频设备列表:")
            print("=" * 60)
            if isinstance(devices, list):
                for i, dev in enumerate(devices):
                    print(f"{i}. {dev.get('Name', 'Unknown')} - {dev.get('Status', 'Unknown')}")
            else:
                print(f"0. {devices.get('Name', 'Unknown')}")
            print("=" * 60)
        else:
            print("无法获取音频设备列表")
    except Exception as e:
        print(f"获取音频设备失败: {e}")


def check_vb_cable():
    """检查是否安装了 VB-Cable"""
    try:
        ps_script = '''
Get-WmiObject Win32_SoundDevice | Where-Object { $_.Name -like "*CABLE*" } | Select-Object Name
'''
        result = subprocess.run(
            ["powershell", "-Command", ps_script],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        return "CABLE" in result.stdout
    except:
        return False


# ============================================================
# 核心功能
# ============================================================

class DoubaoNarrator:
    """豆包自动解说控制器"""

    def __init__(self, output_device=None):
        self.prompt_index = 0
        self.running = True
        self.send_count = 0
        self.platform = "Windows"
        self.system_prompt_sent = False
        self.tts = WindowsTTS(output_device=output_device)

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
        logging.info("豆包AI自动解说脚本（Windows 实用版）已启动")
        logging.info("=" * 60)
        logging.info(f"运行平台: {self.platform}")
        logging.info(f"TTS引擎: Windows PowerShell TTS")
        
        if SEND_SYSTEM_PROMPT:
            logging.info(f"角色设定: 已启用（第1阶段）")
            logging.info(f"触发词数量: {len(TRIGGER_PROMPTS)}（第2阶段）")
        
        logging.info(f"发送间隔: {INTERVAL_MIN}-{INTERVAL_MAX} 秒")
        logging.info("")
        logging.info("重要提示:")
        logging.info("   1. 豆包使用系统默认音频设备")
        logging.info("   2. 确保系统麦克风能采集到扬声器声音")
        logging.info("   3. 或使用 Stereo Mix 作为默认录制设备")
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
║                  豆包AI解说 - 音频设置指南                    ║
╚══════════════════════════════════════════════════════════════╝

由于豆包桌面客户端无法单独设置音频设备，请使用以下方案：

【方案一】立体声混音（推荐）
1. 右键任务栏音量图标 → 声音 → 录制
2. 右键空白处 → 显示禁用的设备
3. 启用 "立体声混音" (Stereo Mix)
4. 将 "立体声混音" 设为默认录制设备
5. 这样豆包就能听到系统播放的TTS声音

【方案二】物理回环
1. 将麦克风靠近扬声器
2. 调整麦克风增益，确保能清晰采集到TTS声音
3. 在OBS中禁用麦克风采集，避免观众听到TTS

【方案三】VB-Cable（高级）
1. 安装 VB-Cable 虚拟音频线
2. 将系统默认播放设备设为 CABLE Input
3. 使用监听功能将声音同时输出到扬声器
4. 这样豆包通过CABLE听到TTS，观众通过扬声器听到游戏和豆包声音

═══════════════════════════════════════════════════════════════
"""
    print(guide)


def main():
    setup_logging()

    parser = argparse.ArgumentParser(
        description="豆包AI自动解说脚本（Windows 实用版）",
        epilog="示例:\n"
               "  python doubao_narrator_v2.py\n"
               "  python doubao_narrator_v2.py --guide\n"
               "  python doubao_narrator_v2.py --interval-min 20 --interval-max 40\n"
               "  python doubao_narrator_v2.py --once",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--guide", action="store_true", help="显示音频设置指南")
    parser.add_argument("--list-devices", action="store_true", help="列出音频设备")
    parser.add_argument("--interval-min", type=int, default=None, help="最小发送间隔（秒）")
    parser.add_argument("--interval-max", type=int, default=None, help="最大发送间隔（秒）")
    parser.add_argument("--once", action="store_true", help="只发送一条提示然后退出")
    args = parser.parse_args()

    if args.guide:
        print_setup_guide()
        return

    if args.list_devices:
        list_audio_devices()
        return

    # 检查是否安装了 VB-Cable
    if check_vb_cable():
        logging.info("[INFO] 检测到 VB-Cable 已安装")
    else:
        logging.info("[INFO] 未检测到 VB-Cable，使用默认音频设备")
        logging.info("[INFO] 如需查看设置指南，请运行: python doubao_narrator_v2.py --guide")

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
