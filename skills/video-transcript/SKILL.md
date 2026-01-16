---
name: video-transcript
description: 使用本地 Whisper 模型将视频/音频转换为字幕稿件
allowed-tools: Bash, Read, Write
---

请帮我将视频或音频文件转换为字幕稿件。

## 参数

$ARGUMENTS

## 执行步骤

### 1. 检查虚拟环境

```bash
cd ~/.claude/office-deps && uv sync
```

### 2. 转换视频

```bash
cd ~/.claude/office-deps && uv run python ~/.claude/skills/video-transcript/scripts/transcribe.py "<文件路径>"
```

**可选参数**：
- `--model <size>`: 模型大小 (tiny/base/small/medium/large)，默认 medium
- `--language <lang>`: 语言代码 (zh/en/ja 等)，默认自动检测

**示例**：
```bash
# 使用中文，small 模型（更快）
uv run python ~/.claude/skills/video-transcript/scripts/transcribe.py "video.mp4" --model small --language zh

# 使用大模型（更准确）
uv run python ~/.claude/skills/video-transcript/scripts/transcribe.py "video.mp4" --model large
```

### 3. 输出文件

转换后的目录结构：
```
<原文件>.claude/
├── transcript.md      # 带时间戳的完整转录
├── transcript.txt     # 纯文本版本（无时间戳）
├── transcript.srt     # SRT 字幕文件
└── transcript.vtt     # WebVTT 字幕文件
```

## 使用示例

```
/video-transcript ~/Videos/meeting.mp4
/video-transcript ~/Music/podcast.mp3 --model large --language en
```

## 系统依赖

- **必需**: FFmpeg（音频提取）
  ```bash
  brew install ffmpeg
  ```

## Whisper 模型大小参考

| 模型 | VRAM | 相对速度 | 准确度 |
|------|------|----------|--------|
| tiny | ~1GB | 最快 | 一般 |
| base | ~1GB | 快 | 较好 |
| small | ~2GB | 中等 | 好 |
| medium | ~5GB | 较慢 | 很好 |
| large | ~10GB | 最慢 | 最佳 |

首次使用时会自动下载模型文件。

## 错误处理

- 文件不存在 → 提示用户检查路径
- FFmpeg 不可用 → 提示安装 FFmpeg
- 模型下载失败 → 检查网络连接
