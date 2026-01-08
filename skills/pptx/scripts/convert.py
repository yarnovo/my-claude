#!/usr/bin/env python3
"""
PPTX 转换脚本
将 PowerPoint 演示文稿转换为 Markdown + 幻灯片预览图
"""

import sys
import os
import subprocess
import tempfile
from pathlib import Path


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

    # markitdown 会按幻灯片分隔内容
    # 尝试在每个幻灯片后添加预览图引用
    slides = result.text_content.split('\n---\n')

    for i, slide_content in enumerate(slides, 1):
        if slide_content.strip():
            content_parts.append(slide_content.strip())
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
