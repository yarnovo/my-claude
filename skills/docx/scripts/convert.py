#!/usr/bin/env python3
"""
DOCX 转换脚本
将 Word 文档转换为 Markdown + 图片

改进：
- 从 DOCX 中提取图片为独立文件
- 替换 base64 data URI 为图片文件引用
"""

import sys
import re
import zipfile
from pathlib import Path


def extract_images_from_docx(docx_path: Path, images_dir: Path) -> dict:
    """从 DOCX 中提取图片文件

    Returns:
        dict: {原始文件名: 新文件名} 的映射
    """
    image_map = {}

    with zipfile.ZipFile(docx_path, 'r') as docx:
        for name in docx.namelist():
            # 只处理 word/media/ 下的实际文件（跳过目录本身）
            if name.startswith('word/media/') and not name.endswith('/'):
                # 获取原始文件名
                original_name = Path(name).name
                if not original_name:  # 跳过空文件名
                    continue

                # 生成新文件名
                new_name = original_name
                target_path = images_dir / new_name

                # 提取图片
                with docx.open(name) as src:
                    data = src.read()
                    if data:  # 只保存非空文件
                        target_path.write_bytes(data)
                        image_map[original_name] = new_name
                        print(f"📷 提取图片: {new_name}")

    return image_map


def replace_image_placeholders(markdown: str, images_dir: Path) -> str:
    """替换 Markdown 中的图片占位符为已提取的图片引用

    markitdown 会输出 `![...](data:image/png;base64...)` 占位符，
    需要替换为实际提取的图片文件引用。

    Args:
        markdown: 包含图片占位符的 Markdown 内容
        images_dir: 图片目录

    Returns:
        替换后的 Markdown 内容
    """
    # 获取已提取的图片文件列表（按名称排序）
    image_files = sorted([
        f.name for f in images_dir.glob('image*.png')
        if f.is_file() and f.stat().st_size > 0
    ])

    if not image_files:
        # 没有提取到图片，尝试其他格式
        image_files = sorted([
            f.name for f in images_dir.iterdir()
            if f.is_file() and f.stat().st_size > 0 and f.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.webp']
        ])

    # 匹配图片占位符：![alt](data:image/...) 包括截断的 base64...
    pattern = r'!\[([^\]]*)\]\(data:image/[^)]+\)'

    image_index = 0

    def replace_placeholder(match):
        nonlocal image_index

        alt_text = match.group(1)

        if image_index < len(image_files):
            filename = image_files[image_index]
            image_index += 1
            print(f"🔗 替换图片引用: {filename}")

            if alt_text:
                return f'![{alt_text}](images/{filename})'
            else:
                return f'![](images/{filename})'
        else:
            # 没有更多图片文件，保留占位符并警告
            print(f"⚠️ 图片不足，保留占位符", file=sys.stderr)
            return match.group(0)

    result = re.sub(pattern, replace_placeholder, markdown)

    if image_index < len(image_files):
        print(f"ℹ️ 剩余 {len(image_files) - image_index} 张图片未被引用")

    return result


def convert_docx(file_path: str) -> None:
    """转换 DOCX 文件为 Markdown + 独立图片"""
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

    # 方法1: 直接从 DOCX 提取图片
    print(f"📦 从 DOCX 提取图片...")
    docx_images = extract_images_from_docx(input_path, images_dir)

    # 使用 markitdown 转换
    print(f"📄 转换文档为 Markdown...")
    md = MarkItDown()
    result = md.convert(str(input_path))
    markdown_content = result.text_content

    # 替换图片占位符为已提取的图片引用
    if 'data:image' in markdown_content:
        print(f"🔄 替换图片占位符...")
        markdown_content = replace_image_placeholders(markdown_content, images_dir)

    # 保存程序转换结果（包含图片引用，待 AI 进一步处理）
    output_path = output_dir / "program-output.md"
    output_path.write_text(markdown_content, encoding='utf-8')

    # 统计图片数量
    image_files = list(images_dir.glob('*'))
    image_count = len([f for f in image_files if f.is_file()])

    print(f"✅ 转换完成!")
    print(f"📁 输出目录: {output_dir}")
    print(f"📄 程序结果: {output_path}")
    print(f"🖼️  图片数量: {image_count}")
    print(f"⏳ 待处理: AI 读取图片生成 content.md")


def main():
    if len(sys.argv) < 2:
        print("用法: python convert.py <docx文件路径>", file=sys.stderr)
        sys.exit(1)

    file_path = sys.argv[1]
    convert_docx(file_path)


if __name__ == "__main__":
    main()
