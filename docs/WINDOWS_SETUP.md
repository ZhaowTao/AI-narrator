# Windows 配置指南

本指南将帮助你在 Windows 系统上配置 AI Narrator，实现豆包AI自动解说功能。

## 📋 配置概览

### 音频路由方案

```
TTS → CABLE Input → CABLE Output → 豆包（听到）
                          ↓
                       监听 → 耳机（你听到）

游戏声音 → 扬声器 → OBS Application Audio Capture → 直播
豆包解说 → 扬声器 → OBS Application Audio Capture → 直播
```

**关键点**：
- TTS 走 CABLE 线路，不经过扬声器
- OBS 使用 Application Audio Capture 单独采集游戏和豆包
- 观众听不到 TTS，只能听到游戏和豆包解说

## 🔧 步骤一：安装虚拟音频设备

### 1. 下载 VB-Cable

访问 [VB-Audio 官网](https://vb-audio.com/Cable/) 下载 VB-Cable。

或直接下载：
- [VBCABLE_Setup_x64.exe](https://download.vb-audio.com/Download_CABLE/VBCABLE_Setup_x64.exe) (64位系统)
- [VBCABLE_Setup.exe](https://download.vb-audio.com/Download_CABLE/VBCABLE_Setup.exe) (32位系统)

### 2. 安装 VB-Cable

1. 右键下载的安装包 → **以管理员身份运行**
2. 点击 **Install** 安装驱动
3. **重启电脑**（必须！）

### 3. 验证安装

重启后，检查是否出现以下设备：
- 播放设备：**CABLE Input**
- 录制设备：**CABLE Output**

## 🎛️ 步骤二：配置 Windows 音频

### 1. 设置播放设备

1. 右键任务栏音量图标 → **声音设置**
2. 点击 **更多声音设置**
3. 切换到 **播放** 选项卡
4. 找到 **CABLE Input**
5. 右键 → **设置为默认设备**

### 2. 设置录制设备

1. 切换到 **录制** 选项卡
2. 找到 **CABLE Output**
3. 右键 → **设置为默认设备**
4. **双击 CABLE Output** 打开属性
5. 切换到 **监听** 选项卡
6. ✅ **勾选** "监听此设备"
7. **"通过此设备播放"** 选择你的 **耳机**
8. 点击 **应用** → **确定**

### 3. 禁用物理麦克风（可选但推荐）

1. 在 **录制** 选项卡
2. 找到你的物理麦克风（不是 CABLE）
3. 右键 → **禁用**

> **注意**：禁用物理麦克风可以防止音频反馈和回音。

## 📹 步骤三：配置 OBS

### 1. 添加游戏音频源

1. 在 OBS 中，点击 **来源** 区域的 **+**
2. 选择 **"Application Audio Capture (BETA)"**
3. 命名来源（如：游戏音频）
4. 在 **窗口** 下拉菜单中选择你的 **游戏**
5. 点击 **确定**

### 2. 添加豆包音频源（可选）

如果需要采集豆包的声音：
1. 再次添加 **"Application Audio Capture (BETA)"**
2. 选择 **豆包客户端** 窗口
3. 点击 **确定**

### 3. 禁用桌面音频（重要！）

1. OBS 设置 → **音频**
2. **桌面音频** → 选择 **禁用**
3. **麦克风/辅助音频** → 选择 **禁用**
4. 点击 **确定**

### 4. 验证混音器

在 OBS 混音器中，你应该只看到：
- ✅ Application Audio Capture（游戏）
- ✅ Application Audio Capture（豆包，如果添加了）
- ❌ 不应该有"桌面音频"
- ❌ 不应该有"麦克风/Aux"

## 🚀 步骤四：启动 AI Narrator

### 1. 启动豆包客户端

1. 打开豆包桌面客户端
2. 登录账号
3. 发起语音通话
4. 开启屏幕共享（共享游戏窗口）

### 2. 运行 AI Narrator

```bash
python doubao_narrator.py
```

或运行配置向导：

```bash
python setup.py
```

### 3. 验证运行

检查以下项目：
- [ ] 耳机中听到 TTS 提示音
- [ ] 豆包有反应（开始说话）
- [ ] OBS 没有采集到 TTS（混音器中没有 TTS 音量条）
- [ ] OBS 采集到游戏声音
- [ ] OBS 采集到豆包声音（如果添加了豆包音频源）

## ⚙️ 高级配置

### 修改触发间隔

编辑 `doubao_narrator.py`：

```python
# 触发间隔（秒）
INTERVAL_MIN = 10  # 最小间隔
INTERVAL_MAX = 30  # 最大间隔
```

### 修改触发词

```python
TRIGGER_PROMPTS = ["继续", "请解说", "下一个"]
```

### 禁用角色设定

如果不想每次发送角色设定：

```python
SEND_SYSTEM_PROMPT = False
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

## 🐛 故障排除

### 问题：豆包听不到 TTS

**解决方案**：
1. 确认录制设备是 **CABLE Output**
2. 确认播放设备是 **CABLE Input**
3. 重启豆包客户端
4. 检查 CABLE Output 监听是否启用

### 问题：OBS 采集到了 TTS

**解决方案**：
1. 确认 OBS 没有使用"桌面音频"
2. 使用 Application Audio Capture 单独采集游戏
3. 确认 TTS 只输出到 CABLE，不经过扬声器

### 问题：有回音/音频反馈

**解决方案**：
1. 禁用物理麦克风
2. 降低麦克风增益
3. 使用耳机而不是扬声器
4. 检查监听设置是否正确

### 问题：TTS 播放失败

**解决方案**：
1. 检查 Windows TTS 功能是否正常
2. 运行 PowerShell 测试：
   ```powershell
   Add-Type -AssemblyName System.Speech
   $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
   $synth.Speak("测试")
   ```
3. 检查 Python 环境

## 📚 相关文件

- [README.md](../README.md) - 项目总览
- [MAC_SETUP.md](MAC_SETUP.md) - Mac 配置指南
- `setup.py` - 配置向导
- `doubao_narrator.py` - Windows 主程序

## 💡 提示

1. **首次配置**建议运行 `python setup.py` 进行引导
2. **佩戴耳机**监听 TTS，避免音频反馈
3. **测试模式**使用 `--once` 参数：`python doubao_narrator.py --once`
4. **日志文件**查看 `doubao_narrator.log` 排查问题

---

**遇到问题？** 运行 `python setup.py` 进行诊断。
