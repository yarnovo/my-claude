---
name: docx
description: 读取 Word 文档，转换为 Markdown + 图片
allowed-tools: Bash, Read
---

请帮我读取 Word 文档并转换为 Markdown 格式。

## 参数

$ARGUMENTS

## 执行步骤

### 1. 检查虚拟环境

```bash
# 确保虚拟环境存在
cd ~/.claude/office-deps && uv sync
```

### 2. 转换文档

```bash
cd ~/.claude/office-deps && uv run python ~/.claude/skills/docx/scripts/convert.py "<文件路径>"
```

### 3. 读取转换结果

转换完成后，读取以下文件：
- `<文件路径>.claude/content.md` - Markdown 内容
- `<文件路径>.claude/images/` - 内嵌图片（如果有）

## 输出格式

转换后的目录结构：
```
<原文件>.claude/
├── content.md          # Markdown 内容
└── images/             # 内嵌图片（如有）
    ├── image_1.png
    └── ...
```

## 使用示例

```
/docx ~/Documents/report.docx
```

## 错误处理

- 文件不存在 → 提示用户检查路径
- 转换失败 → 显示错误信息
- 虚拟环境不存在 → 自动创建
