# AI Narrator

让AI助手（如豆包）通过语音通话 + 屏幕共享的方式，自动对你的屏幕内容进行实时解说，适用于直播场景。

## 工作原理

1. 与AI助手发起语音通话并共享屏幕，AI能看到你的屏幕
2. 脚本定时用TTS（文字转语音）播放提示语
3. 声音通过麦克风/虚拟音频传给AI助手
4. AI助手听到后根据屏幕内容进行语音解说

## 跨平台支持

| 平台 | TTS引擎 | 额外依赖 |
|------|---------|---------|
| macOS | 系统内置 `say` 命令 | 无需安装 |
| Windows | edge-tts（微软免费TTS） | `pip install edge-tts` |
| Linux | espeak | `sudo apt install espeak` |

## 快速开始

### 1. 环境准备

- 安装 [豆包桌面客户端](https://www.doubao.com/) 并登录
- 安装 Python 3.8+
- 安装 [OBS Studio](https://obsproject.com/)（用于直播）
- 安装 [VB-CABLE](https://vb-audio.com/Cable/)（虚拟音频线缆，用于音频隔离）

### 2. 安装依赖

```bash
# macOS（无需额外安装）
python3 doubao_narrator.py

# Windows
pip install edge-tts
python doubao_narrator.py
```

### 3. 配置豆包

1. 打开豆包桌面客户端，找到语音通话功能
2. 发起语音通话并开启屏幕共享
3. 选择要共享的窗口（建议只共享需要解说的窗口）
4. 先手动对着麦克风说句话，确认豆包能听到并回复

### 4. 运行脚本

```bash
# macOS
python3 doubao_narrator.py

# 自定义语音和语速
python3 doubao_narrator.py --voice "Ting-Ting" --rate 180

# Windows
python doubao_narrator.py

# 自定义语音
python doubao_narrator.py --voice zh-CN-YunxiNeural

# 自定义间隔时间
python doubao_narrator.py --interval-min 30 --interval-max 60

# 查看所有可用的中文语音
python doubao_narrator.py --list-voices
```

## 命令行参数

| 参数 | 说明 |
|------|------|
| `--voice NAME` | 指定TTS音色（macOS: `Ting-Ting`；Windows: `zh-CN-YunxiNeural`） |
| `--rate N` | 语速（macOS: 数字如 `180`；Windows: 如 `+10%`） |
| `--interval-min N` | 最小发送间隔（秒），默认 25 |
| `--interval-max N` | 最大发送间隔（秒），默认 40 |
| `--vision` | 启用视觉分析模式（需要火山引擎API Key） |
| `--api-key KEY` | 火山引擎API Key |
| `--list-voices` | 列出所有可用的中文TTS音色 |

## 可用的TTS音色

### macOS

| 音色 | 说明 |
|------|------|
| Ting-Ting | 女声（默认） |
| Mei-Jia | 女声 |
| Li-Mu | 男声 |

运行 `say -v '?' \| grep zh` 查看完整列表。

### Windows（edge-tts）

| 音色 | 说明 |
|------|------|
| zh-CN-YunxiNeural | 云希，男声，自然活泼（默认） |
| zh-CN-XiaoxiaoNeural | 晓晓，女声，温柔自然 |
| zh-CN-YunjianNeural | 云健，男声，沉稳大气 |
| zh-CN-XiaoyiNeural | 晓伊，女声，知性优雅 |

## OBS直播音频路由

直播时需要配置音频路由，确保观众听到正确的声音：

**观众能听到：** 游戏音效 + AI解说声音 + 你的麦克风（如果开了）
**观众听不到：** TTS提示语声音

### 核心原理

TTS的声音只走虚拟音频线缆（VB-CABLE），不走扬声器，所以OBS采集不到。

### 配置步骤

1. **安装 VB-CABLE**：从 [vb-audio.com](https://vb-audio.com/Cable/) 下载安装，重启电脑
2. **TTS输出到虚拟线缆**：在系统声音设置中，将脚本/终端的输出设备改为 `CABLE Input`
3. **豆包麦克风输入**：在豆包语音通话设置中，将麦克风输入改为 `CABLE Output`
4. **OBS采集豆包声音**：添加 `Application Audio Capture (BETA)` 来源，选择豆包客户端
5. **OBS采集游戏声音**：使用 `游戏采集` 或 `窗口采集`（通常已包含音频）

详细配置请参考 [完整教程文档](./豆包AI自动解说方案_完整教程.docx)。

## 自定义解说提示语

编辑 `doubao_narrator.py` 中的 `NARRATION_PROMPTS` 列表：

```python
NARRATION_PROMPTS = [
    "解说一下当前的游戏画面，像专业解说一样生动有趣",
    "分析一下当前的局势，谁占优势？",
    "这个操作怎么样？给我们讲讲",
]
```

## 常见问题

**Q: 豆包共享屏幕卡死？**
A: 关闭不必要的后台程序释放内存；只共享特定窗口而非整个屏幕；降低共享分辨率。

**Q: 豆包听不到TTS声音？**
A: 确认麦克风输入设置为 `CABLE Output`（Windows）或 `BlackHole 2ch`（macOS）；尝试调大TTS音量。

**Q: 观众听到了TTS提示声音？**
A: 检查脚本/终端的音频输出是否正确设置为虚拟线缆而非扬声器。

**Q: 豆包回复不自然？**
A: 修改提示语让它更具体；在通话开始时先手动发几条消息让豆包理解上下文；调整发送间隔时间。

## 许可证

MIT License

## 作者

ZhaowTao
