#!/usr/bin/env python3
"""
PDF 转换脚本
使用 PyMuPDF4LLM 将 PDF 文档转换为 Markdown + 页面预览图

输出：
- origin.md: 原始转换结果（按页组织，包含图片引用）
- pages/: 页面预览图

后续由 AI 智能转换生成 content.md（纯文本，无图片引用）
"""

import sys
from pathlib import Path


def generate_page_images(file_path: Path, output_dir: Path) -> list:
    """使用 pdf2image 生成页面预览图"""
    pages_dir = output_dir / "pages"
    pages_dir.mkdir(exist_ok=True)

    page_images = []

    try:
        from pdf2image import convert_from_path

        images = convert_from_path(str(file_path), dpi=150)
        for i, image in enumerate(images, 1):
            img_path = pages_dir / f"page_{i:02d}.png"
            image.save(str(img_path), 'PNG')
            page_images.append(img_path)
            print(f"📷 生成页面预览: {img_path.name}")

    except ImportError:
        print("警告: pdf2image 未安装", file=sys.stderr)
        print("安装方法: cd ~/.claude/office-deps && uv sync", file=sys.stderr)
    except Exception as e:
        print(f"警告: 页面预览生成失败 - {e}", file=sys.stderr)
        print("可能需要安装 poppler: brew install poppler", file=sys.stderr)

    return page_images


def convert_pdf(file_path: str) -> None:
    """使用 PyMuPDF4LLM 转换 PDF 文件为 origin.md + 页面预览图"""
    import pymupdf4llm

    input_path = Path(file_path).resolve()

    if not input_path.exists():
        print(f"错误: 文件不存在 - {input_path}", file=sys.stderr)
        sys.exit(1)

    if input_path.suffix.lower() != '.pdf':
        print(f"错误: 不是 PDF 文件 - {input_path}", file=sys.stderr)
        sys.exit(1)

    # 创建输出目录
    output_dir = input_path.parent / f"{input_path.name}.claude"
    output_dir.mkdir(exist_ok=True)

    print(f"📄 使用 PyMuPDF4LLM 提取文本...")

    # 使用 PyMuPDF4LLM 提取 Markdown
    md_text = pymupdf4llm.to_markdown(str(input_path))

    # 生成页面预览图
    page_images = generate_page_images(input_path, output_dir)
    total_pages = len(page_images)

    # 构建 origin.md 内容（按页组织，包含图片引用）
    content_parts = [f"# PDF: {input_path.name}\n\n"]

    if total_pages > 0:
        lines = md_text.split('\n')
        lines_per_page = max(1, len(lines) // total_pages) if total_pages > 0 else len(lines)

        for i in range(total_pages):
            start_idx = i * lines_per_page
            end_idx = start_idx + lines_per_page if i < total_pages - 1 else len(lines)
            page_text = '\n'.join(lines[start_idx:end_idx]).strip()

            content_parts.append(f"## Page {i + 1}\n\n")
            if page_text:
                content_parts.append(f"{page_text}\n\n")
            content_parts.append(f"![Page {i + 1}](pages/page_{i + 1:02d}.png)\n\n")
            content_parts.append("---\n\n")
    else:
        # 没有预览图，直接输出全部 Markdown
        content_parts.append(md_text)
        content_parts.append("\n")

    # 保存程序转换结果（待 AI 进一步处理）
    output_path = output_dir / "program-output.md"
    output_path.write_text(''.join(content_parts), encoding='utf-8')

    print(f"✅ 转换完成!")
    print(f"📁 输出目录: {output_dir}")
    print(f"📄 程序结果: {output_path}")
    print(f"🖼️  预览图数量: {total_pages}")
    print(f"⏳ 待处理: AI 读取预览图生成 content.md")


def main():
    if len(sys.argv) < 2:
        print("用法: python convert.py <pdf文件路径>", file=sys.stderr)
        sys.exit(1)

    file_path = sys.argv[1]
    convert_pdf(file_path)


if __name__ == "__main__":
    main()
