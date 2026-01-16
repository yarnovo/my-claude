#!/usr/bin/env python3
"""
视频/音频转字幕脚本
使用本地 Whisper 模型进行语音识别

输出：
- transcript.md: 带时间戳的完整转录
- transcript.txt: 纯文本版本
- transcript.srt: SRT 字幕文件
- transcript.vtt: WebVTT 字幕文件
"""

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path


def check_ffmpeg() -> bool:
    """检查 FFmpeg 是否可用"""
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            check=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def extract_audio(video_path: Path, output_path: Path) -> bool:
    """使用 FFmpeg 从视频中提取音频"""
    print(f"🎵 提取音频...")
    try:
        subprocess.run(
            [
                "ffmpeg",
                "-i", str(video_path),
                "-vn",  # 不处理视频
                "-acodec", "pcm_s16le",  # 16-bit PCM
                "-ar", "16000",  # 16kHz 采样率（Whisper 推荐）
                "-ac", "1",  # 单声道
                "-y",  # 覆盖输出文件
                str(output_path),
            ],
            capture_output=True,
            check=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"错误: 音频提取失败 - {e.stderr.decode()}", file=sys.stderr)
        return False


def format_timestamp(seconds: float) -> str:
    """格式化时间戳为 HH:MM:SS.mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


def format_srt_timestamp(seconds: float) -> str:
    """格式化时间戳为 SRT 格式 HH:MM:SS,mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def transcribe_audio(
    audio_path: Path,
    output_dir: Path,
    model_name: str = "medium",
    language: str | None = None,
) -> None:
    """使用 Whisper 转录音频"""
    import whisper

    print(f"🤖 加载 Whisper 模型: {model_name}")
    print("   (首次使用会下载模型，请耐心等待...)")
    model = whisper.load_model(model_name)

    print(f"🎯 开始转录...")
    options = {}
    if language:
        options["language"] = language

    result = model.transcribe(str(audio_path), **options)

    # 检测到的语言
    detected_lang = result.get("language", "unknown")
    print(f"🌐 检测到语言: {detected_lang}")

    segments = result.get("segments", [])
    full_text = result.get("text", "").strip()

    # 1. 生成 Markdown 版本（带时间戳）
    md_lines = ["# 转录稿件\n"]
    md_lines.append(f"- **语言**: {detected_lang}\n")
    md_lines.append(f"- **模型**: {model_name}\n")
    md_lines.append(f"- **片段数**: {len(segments)}\n\n")
    md_lines.append("---\n\n")

    for seg in segments:
        start = format_timestamp(seg["start"])
        end = format_timestamp(seg["end"])
        text = seg["text"].strip()
        md_lines.append(f"**[{start} → {end}]**\n\n")
        md_lines.append(f"{text}\n\n")

    md_path = output_dir / "transcript.md"
    md_path.write_text("".join(md_lines), encoding="utf-8")
    print(f"📄 Markdown: {md_path}")

    # 2. 生成纯文本版本
    txt_path = output_dir / "transcript.txt"
    txt_path.write_text(full_text, encoding="utf-8")
    print(f"📝 纯文本: {txt_path}")

    # 3. 生成 SRT 字幕文件
    srt_lines = []
    for i, seg in enumerate(segments, 1):
        start = format_srt_timestamp(seg["start"])
        end = format_srt_timestamp(seg["end"])
        text = seg["text"].strip()
        srt_lines.append(f"{i}")
        srt_lines.append(f"{start} --> {end}")
        srt_lines.append(text)
        srt_lines.append("")

    srt_path = output_dir / "transcript.srt"
    srt_path.write_text("\n".join(srt_lines), encoding="utf-8")
    print(f"🎬 SRT: {srt_path}")

    # 4. 生成 WebVTT 字幕文件
    vtt_lines = ["WEBVTT\n"]
    for seg in segments:
        start = format_timestamp(seg["start"])
        end = format_timestamp(seg["end"])
        text = seg["text"].strip()
        vtt_lines.append(f"{start} --> {end}")
        vtt_lines.append(text)
        vtt_lines.append("")

    vtt_path = output_dir / "transcript.vtt"
    vtt_path.write_text("\n".join(vtt_lines), encoding="utf-8")
    print(f"🌐 WebVTT: {vtt_path}")


def main():
    parser = argparse.ArgumentParser(
        description="视频/音频转字幕（本地 Whisper 模型）"
    )
    parser.add_argument("file", help="视频或音频文件路径")
    parser.add_argument(
        "--model", "-m",
        default="medium",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper 模型大小 (默认: medium)",
    )
    parser.add_argument(
        "--language", "-l",
        default=None,
        help="语言代码 (zh/en/ja 等)，默认自动检测",
    )

    args = parser.parse_args()

    input_path = Path(args.file).resolve()

    if not input_path.exists():
        print(f"错误: 文件不存在 - {input_path}", file=sys.stderr)
        sys.exit(1)

    # 检查 FFmpeg
    if not check_ffmpeg():
        print("错误: FFmpeg 未安装", file=sys.stderr)
        print("安装方法: brew install ffmpeg", file=sys.stderr)
        sys.exit(1)

    # 创建输出目录
    output_dir = input_path.parent / f"{input_path.name}.claude"
    output_dir.mkdir(exist_ok=True)

    # 判断是否是音频文件
    audio_extensions = {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg", ".wma"}
    is_audio = input_path.suffix.lower() in audio_extensions

    if is_audio:
        # 直接使用音频文件
        print(f"🎵 输入文件: {input_path.name}")
        audio_path = input_path
        should_cleanup = False
    else:
        # 从视频提取音频
        print(f"🎬 输入文件: {input_path.name}")
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            audio_path = Path(tmp.name)
            should_cleanup = True

        if not extract_audio(input_path, audio_path):
            sys.exit(1)

    try:
        transcribe_audio(
            audio_path,
            output_dir,
            model_name=args.model,
            language=args.language,
        )
    finally:
        if should_cleanup and audio_path.exists():
            audio_path.unlink()

    print(f"\n✅ 转录完成!")
    print(f"📁 输出目录: {output_dir}")


if __name__ == "__main__":
    main()
