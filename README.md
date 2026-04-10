# AI Narrator

让AI助手（如豆包）通过语音通话 + 屏幕共享的方式，自动对你的屏幕内容进行实时解说，适用于直播场景。

## 工作原理

1. 与AI助手发起语音通话并共享屏幕，AI能看到你的屏幕
2. 脚本定时用TTS（文字转语音）播放提示语
3. TTS声音通过VB-Cable传给AI助手（观众听不到）
4. AI助手听到后根据屏幕内容进行语音解说
5. OBS采集豆包和游戏的声音（观众能听到）

## 跨平台支持

| 平台 | TTS引擎 | 额外依赖 |
|------|---------|---------|
| macOS | say + sounddevice | `pip install sounddevice soundfile` |
| Windows | edge-tts（微软免费TTS） | `pip install edge-tts` |
| Linux | espeak | `sudo apt install espeak` |

## 快速开始

### 1. 环境准备

- 安装 [豆包桌面客户端](https://www.doubao.com/) 并登录
- 安装 Python 3.8+
- 安装 [OBS Studio](https://obsproject.com/)（用于直播）
- 安装 [VB-Cable](https://vb-audio.com/Cable/)（虚拟音频线缆）

### 2. 安装依赖

```bash
# macOS
pip install sounddevice soundfile

# Windows
pip install edge-tts
```

### 3. 配置系统音频

#### macOS 系统设置：

1. 打开 **音频MIDI设置**（启动台搜索）
2. 点击 **+** → **创建多输出设备**
3. 勾选：
   - ✅ MacBook Air扬声器
   - ✅ BlackHole 2ch
4. 右键点击多输出设备 → **使用此设备用于声音输出**
5. 系统设置 → 声音：
   - **输出**：多输出设备
   - **输入**：VB-Cable

### 4. 配置豆包

1. 打开豆包桌面客户端，找到语音通话功能
2. 发起语音通话并开启屏幕共享
3. 选择要共享的窗口（建议只共享需要解说的窗口）
4. 豆包会自动使用系统默认的麦克风（VB-Cable）

### 5. 配置OBS

1. **设置 → 音频**：
   - 桌面音频：BlackHole 2ch
   - 麦克风/辅助：禁用
2. **来源**：
   - Display Capture 或 窗口采集（游戏画面）
   - Application Audio Capture（游戏声音）

### 6. 运行脚本

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

# 查看音频设备列表
python doubao_narrator.py --list-audio
```

## 命令行参数

| 参数 | 说明 |
|------|------|
| `--voice NAME` | 指定TTS音色（macOS: `Ting-Ting`；Windows: `zh-CN-YunxiNeural`） |
| `--rate N` | 语速（macOS: 数字如 `180`；Windows: 如 `+10%`） |
| `--interval-min N` | 最小发送间隔（秒），默认 25 |
| `--interval-max N` | 最大发送间隔（秒），默认 40 |
| `--audio-device N` | 音频输出设备ID，默认 4（VB-Cable） |
| `--vision` | 启用视觉分析模式（需要火山引擎API Key） |
| `--api-key KEY` | 火山引擎API Key |
| `--list-voices` | 列出所有可用的中文TTS音色 |
| `--list-audio` | 列出所有可用的音频设备 |
| `--once` | 只发送一条提示然后退出 |

## 可用的TTS音色

### macOS

| 音色 | 说明 |
|------|------|
| Ting-Ting | 女声（默认） |
| Mei-Jia | 女声 |
| Li-Mu | 男声 |

运行 `say -v '?' | grep zh` 查看完整列表。

### Windows（edge-tts）

| 音色 | 说明 |
|------|------|
| zh-CN-YunxiNeural | 云希，男声，自然活泼（默认） |
| zh-CN-XiaoxiaoNeural | 晓晓，女声，温柔自然 |
| zh-CN-YunjianNeural | 云健，男声，沉稳大气 |
| zh-CN-XiaoyiNeural | 晓伊，女声，知性优雅 |

## 音频流向（核心原理）

```
TTS音频 → say生成AIFF → sounddevice直接写入VB-Cable → 豆包听到 ✅
                              ↓
                        OBS完全接触不到 ✅

豆包解说 → 系统输出 → 扬声器 + BlackHole → OBS → 观众听到 ✅
游戏声音 → 系统输出 → 扬声器 + BlackHole → OBS → 观众听到 ✅
```

### 为什么这个方案能成功？

之前所有方案失败的根本原因：
- macOS的CoreAudio系统音频栈会把所有发到扬声器的声音同步到多输出设备
- 无论用`say -a`还是改系统输出，TTS声音最终都会被BlackHole采集到

新方案的突破：
- 使用sounddevice通过PortAudio直接与VB-Cable通信
- 完全绕过macOS的系统音频栈
- 音频数据直接写入VB-Cable的缓冲区，不经过系统默认输出

## 自定义解说提示语

脚本采用两阶段提示词设计：角色设定承担90%的工作，触发词只是10%的"戳一下"。

### 第1阶段：角色设定（启动时发送一次）

告诉豆包它是谁、该怎么表现。编辑 `doubao_narrator.py` 中的 `SYSTEM_PROMPT`：

```python
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
```

### 第2阶段：触发词（循环发送）

触发词只负责"戳"一下，让豆包自己根据角色设定决定说什么。编辑 `TRIGGER_PROMPTS` 列表：

```python
TRIGGER_PROMPTS = [
    "继续",
]
```

### 设计理念

- **极简触发词**：只说"继续"，判断权完全交给豆包
- **三合一融合**：每次解说自然融合"画面+弹幕+感谢"
- **防幻觉**：只能说看到的游戏画面，不能编造
- **防隐私**：非游戏画面当没看见，不提任何隐私内容
- **防空谢**：没有礼物别凭空感谢

### 配置选项

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `SEND_SYSTEM_PROMPT` | 是否发送角色设定 | `True` |
| `PROMPT_STRATEGY` | 触发词策略 (`random`/`sequential`) | `"random"` |
| `INTERVAL_MIN` | 最小间隔（秒） | 10 |
| `INTERVAL_MAX` | 最大间隔（秒） | 30 |

## 常见问题

**Q: 豆包共享屏幕卡死？**
A: 关闭不必要的后台程序释放内存；只共享特定窗口而非整个屏幕；降低共享分辨率。

**Q: 豆包听不到TTS声音？**
A: 确认系统声音输入设置为VB-Cable；检查VB-Cable是否正确安装

**Q: 观众听到了TTS提示声音？**
A: 确保使用的是sounddevice直接输出方案，不是系统say命令

**Q: OBS采集不到豆包声音？**
A: 在OBS的设置→音频中，桌面音频选择BlackHole 2ch

**Q: 找不到VB-Cable设备？**
A: 运行 `python3 doubao_narrator.py --list-audio` 查看设备列表

## 许可证

MIT License

## 作者

ZhaowTao
