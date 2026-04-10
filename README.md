# AI Narrator - 豆包AI自动解说

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS-lightgrey.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)]()

AI Narrator 是一个自动化工具，通过定时触发豆包AI进行语音解说，适用于游戏直播、屏幕共享等场景。

让AI助手（如豆包）通过语音通话 + 屏幕共享的方式，自动对你的屏幕内容进行实时解说。

## ✨ 功能特点

- 🤖 **自动触发** - 定时向豆包发送语音提示，触发AI解说
- 🎮 **游戏直播** - 支持屏幕共享，豆包能看到游戏画面
- 🎙️ **语音交互** - 使用系统TTS生成语音提示
- 🖥️ **跨平台** - 支持 Windows 和 macOS
- 📹 **OBS兼容** - 完美配合OBS直播软件

## 🚀 快速开始

### 系统要求

- Python 3.8+
- 豆包桌面客户端
- 虚拟音频设备（VB-Cable/BlackHole）

### 安装步骤

1. **克隆仓库**
```bash
git clone https://github.com/ZhaowTao/AI-narrator.git
cd AI-narrator
```

2. **运行配置向导**
```bash
python setup.py
```

3. **根据提示完成音频设置**
- Windows用户: 参考 [WINDOWS_SETUP.md](docs/WINDOWS_SETUP.md)
- Mac用户: 参考 [MAC_SETUP.md](docs/MAC_SETUP.md)

### 启动解说

**Windows:**
```bash
python doubao_narrator_v2.py
```

**macOS:**
```bash
python doubao_narrator_mac.py
```

## 📁 项目结构

```
AI-narrator/
├── README.md                 # 本文件
├── setup.py                  # 一键配置脚本（推荐首先运行）
├── doubao_narrator_v2.py     # Windows 主程序（优化版）
├── doubao_narrator_mac.py    # macOS 主程序
├── doubao_narrator.py        # 跨平台主程序（原始版）
├── docs/
│   ├── WINDOWS_SETUP.md      # Windows 详细配置指南
│   └── MAC_SETUP.md          # macOS 详细配置指南
├── check_audio.py            # macOS 音频设备检查
├── test_tts.py               # macOS TTS 测试
└── requirements.txt          # 依赖列表
```

## 🖥️ 平台支持

### Windows
- 使用 **VB-Cable** 虚拟音频线
- 配合 **OBS Application Audio Capture** 实现音频分离
- 详细配置: [WINDOWS_SETUP.md](docs/WINDOWS_SETUP.md)

### macOS
- 使用 **BlackHole** 虚拟音频设备
- 使用 **Soundflower** 或 **Loopback** 作为替代
- 详细配置: [MAC_SETUP.md](docs/MAC_SETUP.md)

## 🎯 使用场景

1. **游戏直播** - 豆包AI实时解说游戏画面
2. **屏幕共享** - 自动触发AI进行内容讲解
3. **无人值守** - 定时触发，无需手动操作

## ⚙️ 配置说明

### 基本配置

编辑主程序中的配置区域：

```python
# 触发间隔（秒）
INTERVAL_MIN = 10
INTERVAL_MAX = 30

# 触发词
TRIGGER_PROMPTS = ["继续"]

# 是否发送角色设定
SEND_SYSTEM_PROMPT = True
```

### 提示词优化（重要）

为避免豆包抢答或打断提示词，建议使用**短句无标点**的格式：

```python
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
```

**关键要点：**
- 使用短句，避免长句子
- 不要使用标点符号（句号、逗号等）
- 使用【】标记重要段落
- 这样可以防止豆包在TTS播放过程中抢答或打断

### 命令行参数

```bash
# 单次模式（发送一条后退出）
python doubao_narrator_v2.py --once        # Windows
python doubao_narrator_mac.py --once       # macOS

# 自定义间隔
python doubao_narrator_v2.py --interval-min 20 --interval-max 40

# 显示帮助
python doubao_narrator_v2.py --help
```

## 🔧 故障排除

### 常见问题

**Q: 豆包听不到TTS声音？**
- 检查虚拟音频设备是否正确安装
- 确认录制设备设置为虚拟音频输出
- 参考平台配置文档

**Q: OBS采集到了TTS声音？**
- Windows: 使用 Application Audio Capture 单独采集游戏
- Mac: 检查音频路由设置

**Q: TTS播放失败？**
- 检查系统TTS功能是否正常
- 确认Python环境正确

**Q: 豆包共享屏幕卡死？**
- 关闭不必要的后台程序释放内存
- 只共享特定窗口而非整个屏幕
- 降低共享分辨率

### 获取帮助

- 查看 [WINDOWS_SETUP.md](docs/WINDOWS_SETUP.md) 或 [MAC_SETUP.md](docs/MAC_SETUP.md)
- 运行 `python setup.py` 进行诊断
- 提交 Issue 到 GitHub

## 📝 注意事项

1. **音频路由** - 正确配置虚拟音频设备是关键
2. **豆包客户端** - 需要登录并发起语音通话
3. **屏幕共享** - 确保豆包能看到要解说的内容
4. **耳机监听** - 建议佩戴耳机监听TTS提示

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

- [VB-Audio](https://vb-audio.com/) - 虚拟音频设备
- [BlackHole](https://github.com/ExistentialAudio/BlackHole) - Mac虚拟音频
- [OBS Studio](https://obsproject.com/) - 直播软件

---

**开始使用**: `python setup.py`
