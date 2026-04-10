# macOS 配置指南

本指南将帮助你在 macOS 系统上配置 AI Narrator，实现豆包AI自动解说功能。

## 📋 配置概览

### 音频路由方案

```
TTS → BlackHole 2ch → 豆包（听到）
              ↓
         监听 → 耳机（你听到）

游戏声音 → 扬声器/耳机 → OBS → 直播
豆包解说 → 扬声器/耳机 → OBS → 直播
```

**关键点**：
- TTS 输出到 BlackHole，不经过系统默认输出
- OBS 采集系统默认输出（游戏和豆包声音）
- 观众听不到 TTS，只能听到游戏和豆包解说

## 🔧 步骤一：安装虚拟音频设备

### 1. 安装 BlackHole

使用 Homebrew 安装（推荐）：

```bash
brew install blackhole-2ch
```

或手动下载安装：

1. 访问 [BlackHole GitHub](https://github.com/ExistentialAudio/BlackHole)
2. 下载最新版本
3. 双击安装包，按照提示安装

### 2. 验证安装

安装完成后，检查系统偏好设置 → 声音：
- 输出设备中应该出现 **BlackHole 2ch**
- 输入设备中应该出现 **BlackHole 2ch**

## 🎛️ 步骤二：配置 macOS 音频

### 方案一：运行时切换（推荐）

Mac 版本采用**运行时临时切换**音频设备的方案：

1. **运行前**：将系统输出切换到 BlackHole
2. **TTS 播放**：声音进入 BlackHole
3. **运行后**：恢复系统输出到扬声器/耳机

这样：
- TTS 只输出到 BlackHole（豆包能听到）
- 你自己听不到 TTS（但知道它在工作）
- 通过 OBS 监听听到豆包和游戏声音

### 方案二：使用多输出设备（高级）

创建**多输出设备**，同时输出到 BlackHole 和耳机：

1. 打开 **音频 MIDI 设置**（应用程序 → 实用工具）
2. 点击左下角 **+** → **创建多输出设备**
3. 勾选 **BlackHole 2ch** 和你的 **耳机**
4. 右键多输出设备 → **使用此设备输出**

### 配置录制设备

1. 系统偏好设置 → **声音** → **输入**
2. 选择 **BlackHole 2ch**

## 📹 步骤三：配置 OBS

### 1. 添加音频输入采集

1. OBS 中点击 **来源** 区域的 **+**
2. 选择 **"音频输入采集"**
3. 选择 **BlackHole 2ch**
4. 点击 **确定**

### 2. 配置桌面音频

1. OBS 设置 → **音频**
2. **桌面音频** → 选择你的 **耳机/扬声器**
3. 点击 **确定**

### 3. 验证混音器

在 OBS 混音器中，你应该看到：
- ✅ 桌面音频（游戏声音）
- ✅ 音频输入采集（BlackHole，TTS 声音）
- ✅ 如果需要，可以静音 BlackHole，这样观众听不到 TTS

## 🚀 步骤四：启动 AI Narrator

### 1. 启动豆包客户端

1. 打开豆包桌面客户端
2. 登录账号
3. 发起语音通话
4. 开启屏幕共享

### 2. 运行 AI Narrator

```bash
python doubao_narrator_mac.py
```

Mac 版本会自动：
1. 切换系统输出到 BlackHole
2. 播放 TTS
3. 恢复系统输出到原来的设备

### 3. 验证运行

检查以下项目：
- [ ] 豆包有反应（开始说话）
- [ ] OBS 中 BlackHole 音频源有音量条（TTS 正在播放）
- [ ] 如果需要，静音 BlackHole 音频源，观众就听不到 TTS
- [ ] OBS 采集到游戏声音

## 🔍 使用辅助脚本

### 检查音频设备

```bash
python check_audio.py
```

这个脚本会：
- 列出所有音频设备
- 检查 BlackHole 是否安装
- 显示当前默认设备

### 测试 TTS

```bash
python test_tts.py
```

这个脚本会：
- 切换音频输出到 BlackHole
- 播放测试 TTS
- 恢复音频输出

## ⚙️ 高级配置

### 修改触发间隔

编辑 `doubao_narrator_mac.py`：

```python
# 触发间隔（秒）
INTERVAL_MIN = 10
INTERVAL_MAX = 30
```

### 修改触发词

```python
TRIGGER_PROMPTS = ["继续", "请解说", "下一个"]
```

### 禁用角色设定

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
1. 确认输入设备是 **BlackHole 2ch**
2. 确认 BlackHole 已正确安装
3. 运行 `check_audio.py` 检查设备
4. 重启豆包客户端

### 问题：TTS 播放失败

**解决方案**：
1. 运行 `test_tts.py` 测试 TTS 功能
2. 检查系统 TTS 设置
3. 确认 Python 环境正确

### 问题：音频切换失败

**解决方案**：
1. 检查是否有其他应用占用音频设备
2. 重启电脑
3. 重新安装 BlackHole

### 问题：OBS 没有声音

**解决方案**：
1. 确认 OBS 音频源设置正确
2. 检查 BlackHole 音量
3. 确认 OBS 有音频输入权限

## 📚 相关文件

- [README.md](../README.md) - 项目总览
- [WINDOWS_SETUP.md](WINDOWS_SETUP.md) - Windows 配置指南
- `check_audio.py` - 音频设备检查
- `test_tts.py` - TTS 测试
- `doubao_narrator_mac.py` - Mac 主程序

## 💡 提示

1. **首次配置**建议运行 `check_audio.py` 检查设备
2. **测试 TTS**使用 `test_tts.py` 脚本
3. **运行模式**使用 `--once` 参数测试：`python doubao_narrator_mac.py --once`
4. **音频权限**确保 OBS 有麦克风权限

## 🔧 替代方案

如果 BlackHole 无法使用，可以尝试：

1. **Soundflower** - 经典的 Mac 虚拟音频设备
2. **Loopback** - Rogue Amoeba 的专业音频路由软件（付费）
3. **VB-Cable for Mac** - VB-Audio 的 Mac 版本（如果可用）

---

**遇到问题？** 运行 `python check_audio.py` 进行诊断。
