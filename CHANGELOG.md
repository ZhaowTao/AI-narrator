# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-04-10

### Added
- 创建 macOS 版本主程序 `doubao_narrator_mac.py`，支持 BlackHole 虚拟音频设备
- 添加 `setup.py` 统一配置向导，支持 Windows 和 macOS 双平台
- 添加提示词优化建议功能到 `setup.py`，展示短句无标点的提示词格式
- 创建详细的平台配置文档：
  - `docs/WINDOWS_SETUP.md` - Windows 完整配置指南
  - `docs/MAC_SETUP.md` - macOS 完整配置指南
- 添加 macOS 辅助脚本：
  - `check_audio.py` - 音频设备检查
  - `test_tts.py` - TTS 功能测试
- 新增 `CHANGELOG.md` 记录版本变更

### Changed
- **优化提示词格式**：将 `SYSTEM_PROMPT` 改为短句无标点格式，防止豆包抢答或打断
  - 使用 `"【角色设定】"` 等标记代替长段落
  - 移除所有标点符号，使用空格分隔短句
  - 将 TTS 超时时间从 30 秒增加到 60 秒
- 更新 `README.md`：
  - 更新项目结构说明
  - 添加 Windows/macOS 分别的启动命令
  - 完善命令行参数示例
- 更新 `docs/WINDOWS_SETUP.md` 和 `docs/MAC_SETUP.md`：
  - 添加提示词优化章节
  - 详细说明短句无标点的重要性

### Fixed
- 修复 Windows 音频路由问题，使用 VB-Cable + 监听方案
- 修复 OBS 音频采集问题，使用 Application Audio Capture 单独采集游戏
- 修复 TTS 超时问题，增加超时时间到 60 秒
- 修复豆包抢答问题，通过优化提示词格式解决

### Technical Details

#### 音频路由方案（Windows）
```
TTS → CABLE Input → CABLE Output → 豆包（听到）
                          ↓
                       监听 → 耳机（你听到）

游戏声音 → OBS Application Audio Capture → 直播
豆包解说 → OBS Application Audio Capture → 直播
```

#### 提示词优化原理
- **问题**：长句子和标点符号会在 TTS 播放时产生停顿，豆包会在停顿处抢答
- **解决方案**：使用短句无标点格式，让 TTS 连续播放，不给豆包抢答机会
- **效果**：豆包会等待完整提示词播放完毕后再响应

## [0.1.0] - 2026-04-07

### Added
- 初始版本发布
- 跨平台主程序 `doubao_narrator.py`，支持 Windows 和 macOS
- 基础 TTS 功能（Windows: edge-tts/PowerShell, macOS: say）
- 定时触发豆包AI解说功能
- 两阶段提示词设计（角色设定 + 触发词）
- 命令行参数支持（--once, --interval-min, --interval-max, --guide 等）
- 日志记录功能
- `requirements.txt` 依赖列表

[Unreleased]: https://github.com/ZhaowTao/AI-narrator/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/ZhaowTao/AI-narrator/compare/v0.1.0...v1.0.0
[0.1.0]: https://github.com/ZhaowTao/AI-narrator/releases/tag/v0.1.0
