#!/usr/bin/env python3
"""
PPTX 转换脚本
将 PowerPoint 演示文稿转换为 Markdown + 幻灯片预览图
"""

import sys
import os
import re
import subprocess
import tempfile
from pathlib import Path


def clean_slide_content(content: str) -> str:
    """清理幻灯片内容，移除不需要的元数据"""
    lines = content.split('\n')
    cleaned_lines = []

    skip_line_patterns = [
        # Windows/Mac 文件路径（作为独立行）
        r'^[A-Z]:\\',
        r'^/Users/',
        r'^/home/',
        # AI 生成的图片描述（作为独立行）
        r'^A (table|screenshot|image|diagram|chart|picture)',
        r'^Document preview',
        # Notes 部分标题
        r'^#{1,3}\s*Notes:?\s*$',
        # 空的 Slide 标题后面的占位符（包括带 # 的）
        r'^#{0,3}\s*NOTE\s*$',
        # HTML 注释（Slide number）
        r'^<!--.*-->$',
        # 只有数字的行（页码）
        r'^\d+$',
    ]

    # 图片行模式 - 移除包含 Windows 路径或 AI 描述的图片
    img_skip_patterns = [
        r'!\[.*[A-Z]:\\.*\]',  # Windows 路径在 alt text
        r'!\[.*AI-generated.*\]',  # AI 描述
        r'!\[.*screenshot.*\]',
        r'!\[\]\(',  # 空 alt text 的图片
    ]

    for line in lines:
        stripped = line.strip()

        # 检查是否匹配任何跳过模式
        should_skip = False

        # 检查行级跳过模式
        for pattern in skip_line_patterns:
            if re.match(pattern, stripped, re.IGNORECASE):
                should_skip = True
                break

        # 检查图片跳过模式
        if not should_skip:
            for pattern in img_skip_patterns:
                if re.search(pattern, stripped, re.IGNORECASE):
                    should_skip = True
                    break

        if not should_skip:
            cleaned_lines.append(line)

    # 移除连续的空行
    result = '\n'.join(cleaned_lines)
    result = re.sub(r'\n{3,}', '\n\n', result)

    return result.strip()


def generate_previews(file_path: Path, output_dir: Path) -> list:
    """使用 LibreOffice 生成幻灯片预览图"""
    previews_dir = output_dir / "previews"
    previews_dir.mkdir(exist_ok=True)

    previews = []

    # 检查 LibreOffice 是否可用
    libreoffice_paths = [
        '/Applications/LibreOffice.app/Contents/MacOS/soffice',
        '/usr/bin/libreoffice',
        '/usr/bin/soffice',
    ]

    soffice = None
    for path in libreoffice_paths:
        if os.path.exists(path):
            soffice = path
            break

    if not soffice:
        print("警告: LibreOffice 未安装，无法生成预览图", file=sys.stderr)
        print("安装方法: brew install libreoffice", file=sys.stderr)
        return previews

    try:
        # 转换为 PDF
        with tempfile.TemporaryDirectory() as tmpdir:
            result = subprocess.run([
                soffice,
                '--headless',
                '--convert-to', 'pdf',
                '--outdir', tmpdir,
                str(file_path)
            ], capture_output=True, text=True, timeout=120)

            if result.returncode != 0:
                print(f"警告: PDF 转换失败 - {result.stderr}", file=sys.stderr)
                return previews

            # 找到生成的 PDF
            pdf_files = list(Path(tmpdir).glob('*.pdf'))
            if not pdf_files:
                print("警告: 未找到生成的 PDF 文件", file=sys.stderr)
                return previews

            pdf_path = pdf_files[0]

            # PDF 转图片
            try:
                from pdf2image import convert_from_path

                images = convert_from_path(str(pdf_path), dpi=200)
                for i, image in enumerate(images, 1):
                    img_path = previews_dir / f"slide_{i:02d}.png"
                    image.save(str(img_path), 'PNG')
                    previews.append(img_path)
                    print(f"📷 生成预览: {img_path.name}")
            except ImportError:
                print("警告: pdf2image 未安装", file=sys.stderr)
            except Exception as e:
                print(f"警告: 图片转换失败 - {e}", file=sys.stderr)

    except subprocess.TimeoutExpired:
        print("警告: LibreOffice 转换超时", file=sys.stderr)
    except Exception as e:
        print(f"警告: 预览生成失败 - {e}", file=sys.stderr)

    return previews


def convert_pptx(file_path: str) -> None:
    """转换 PPTX 文件为 Markdown + 预览图"""
    from markitdown import MarkItDown

    input_path = Path(file_path).resolve()

    if not input_path.exists():
        print(f"错误: 文件不存在 - {input_path}", file=sys.stderr)
        sys.exit(1)

    if input_path.suffix.lower() not in ('.pptx', '.ppt'):
        print(f"错误: 不是 PowerPoint 文件 - {input_path}", file=sys.stderr)
        sys.exit(1)

    # 创建输出目录
    output_dir = input_path.parent / f"{input_path.name}.claude"
    output_dir.mkdir(exist_ok=True)

    # 使用 markitdown 转换
    md = MarkItDown()
    result = md.convert(str(input_path))

    # 生成预览图
    previews = generate_previews(input_path, output_dir)

    # 构建完整内容（添加预览图引用）
    content_parts = [f"# 演示文稿: {input_path.name}\n\n"]

    # markitdown 使用 <!-- Slide number: N --> 标记幻灯片
    # 按这个模式分割内容
    slide_pattern = r'<!-- Slide number: \d+ -->'
    slides = re.split(slide_pattern, result.text_content)

    # 第一个元素是空的或者是文件头，跳过
    slides = [s for s in slides if s.strip()]

    for i, slide_content in enumerate(slides, 1):
        cleaned_content = clean_slide_content(slide_content)
        if cleaned_content:
            # 添加幻灯片标题
            content_parts.append(f"## Slide {i}\n\n")
            content_parts.append(cleaned_content)
            content_parts.append("\n\n")

            # 添加预览图引用
            preview_path = output_dir / "previews" / f"slide_{i:02d}.png"
            if preview_path.exists():
                content_parts.append(f"![Slide {i} Preview](previews/slide_{i:02d}.png)\n\n")

            content_parts.append("---\n\n")

    # 保存 Markdown 内容
    content_path = output_dir / "content.md"
    content_path.write_text(''.join(content_parts), encoding='utf-8')

    print(f"✅ 转换完成!")
    print(f"📁 输出目录: {output_dir}")
    print(f"📄 Markdown: {content_path}")
    print(f"🖼️  预览图数量: {len(previews)}")


def main():
    if len(sys.argv) < 2:
        print("用法: python convert.py <pptx文件路径>", file=sys.stderr)
        sys.exit(1)

    file_path = sys.argv[1]
    convert_pptx(file_path)


if __name__ == "__main__":
    main()
