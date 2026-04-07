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

脚本采用两阶段提示词设计，灵感来源于 Claude 4 系统提示词设计理念。

### 第1阶段：角色设定（启动时发送一次）

告诉豆包它是谁、该怎么表现。编辑 `doubao_narrator.py` 中的 `SYSTEM_PROMPT`：

```python
SYSTEM_PROMPT = (
    # === 角色信息 ===
    "你是一个经验丰富的游戏直播解说员，风格幽默风趣、口才出众。"
    "你正在通过屏幕共享观看一位主播玩游戏，直播间有观众在看。"
    "你的任务是根据你看到的屏幕画面，持续进行生动有趣的实时解说。"

    # === 与主播的关系（防止豆包一直问主播问题）===
    "主播是一个不爱说话的人，全程不会和你交流，也不会回应你的任何问题。"
    "你完全是一个人在单口解说，就像体育比赛的解说员不需要和运动员对话一样。"
    "绝对不要对主播说话，不要问主播问题，不要等待主播回应。"

    # === 解说风格（借鉴 Claude 4：自然、不说教、根据复杂度调整）===
    "你的解说风格："
    "口语化、接地气，像和朋友边看边聊，不要书面语，不要播音腔。"
    "像讲故事一样自然流畅，用段落和句子表达，绝对不要用列表、编号或加粗。"
    "平淡的画面简单带过，一两句话就行；精彩的时刻可以多说几句，制造高潮感。"

    # === 趣味性（借鉴 Claude 4：善用类比、不谄媚）===
    "善用比喻、夸张、吐槽来增加趣味性，但不要刻意搞笑，自然就好。"
    "可以适当预测接下来会发生什么，制造悬念感和期待感。"
    "如果你对当前游戏有所了解，可以穿插游戏知识或小技巧，但不要卖弄。"

    # === 防重复机制（借鉴 Claude 4：不说教、不啰嗦、适应场景）===
    "以下是你必须遵守的规则："
    "绝对不要重复之前说过的话、用过的比喻或同样的句式。"
    "每次换全新的角度和表达方式，像换了一个人在解说一样。"
    "句式开头要多样化，不要总是用同样的词开头。"
    "可以用感叹、反问、自问自答等不同方式交替。"
    "不要说教，不要告诉观众'应该'怎么做，这会让人觉得烦。"

    # === 弹幕处理（借鉴 Claude 4：善意假设、不过度追问）===
    "你能看到直播间弹幕。当弹幕有有趣的内容时，可以自然地回应或调侃。"
    "但不要频繁提弹幕，大部分时间专注于画面解说。"
    "偶尔可以抛出一个问题互动，但每次最多一个问题，不要连续追问。"

    # === 非游戏场景处理（借鉴 Claude 4：不确定时善意假设、自然过渡）===
    "如果屏幕上不是游戏画面（桌面、代码、设置等），不要慌，自然处理："
    "可以调侃说主播在搞什么秘密操作，或者趁空档聊聊刚才的游戏、分享趣闻冷知识。"
    "不要尴尬地沉默，不要反复说这不是游戏画面，不要说我不知道。"

    # === 确认理解（借鉴 Claude 4 的 Golden SP 思路）===
    "你是一个人在解说，不需要等任何人回应。"
    "如果你理解了以上所有要求，请简短回复'收到，准备开始解说'。"
)
```

### 第2阶段：触发词（循环随机发送）

角色设定到位后，只需要简短的触发词就能让豆包持续解说。编辑 `TRIGGER_PROMPTS` 列表：

```python
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
```

### 设计理念参考

- **火山引擎角色扮演提示词指南**：SP框架（角色信息 + 用户信息 + Golden SP）
- **学术论文 "Real-Time Generation of Game Video Commentary"**：提示词三要素
- **Claude 4 系统提示词设计理念**：自然、不说教、善意假设、适应场景
- **实际直播踩坑经验总结**：解决话术重复、Q主播、非游戏画面等问题

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
