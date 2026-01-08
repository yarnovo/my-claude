#!/usr/bin/env python3
"""
DOCX 转换脚本
将 Word 文档转换为 Markdown + 图片
"""

import sys
import os
from pathlib import Path


def convert_docx(file_path: str) -> None:
    """转换 DOCX 文件为 Markdown"""
    from markitdown import MarkItDown

    input_path = Path(file_path).resolve()

    if not input_path.exists():
        print(f"错误: 文件不存在 - {input_path}", file=sys.stderr)
        sys.exit(1)

    if not input_path.suffix.lower() == '.docx':
        print(f"错误: 不是 DOCX 文件 - {input_path}", file=sys.stderr)
        sys.exit(1)

    # 创建输出目录
    output_dir = input_path.parent / f"{input_path.name}.claude"
    output_dir.mkdir(exist_ok=True)
    images_dir = output_dir / "images"
    images_dir.mkdir(exist_ok=True)

    # 使用 markitdown 转换
    md = MarkItDown()
    result = md.convert(str(input_path))

    # 保存 Markdown 内容
    content_path = output_dir / "content.md"
    content_path.write_text(result.text_content, encoding='utf-8')

    print(f"✅ 转换完成!")
    print(f"📁 输出目录: {output_dir}")
    print(f"📄 Markdown: {content_path}")

    # 检查是否有图片（markitdown 可能提取图片到临时目录）
    # 目前 markitdown 内联处理图片，可能需要后续版本支持图片提取


def main():
    if len(sys.argv) < 2:
        print("用法: python convert.py <docx文件路径>", file=sys.stderr)
        sys.exit(1)

    file_path = sys.argv[1]
    convert_docx(file_path)


if __name__ == "__main__":
    main()
