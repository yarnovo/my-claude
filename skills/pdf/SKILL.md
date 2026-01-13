---
name: pdf
description: 读取 PDF 文档，转换为 Markdown + 页面预览图
allowed-tools: Bash, Read
---

请帮我读取 PDF 文档并转换为 Markdown 格式。

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
cd ~/.claude/office-deps && uv run python ~/.claude/skills/pdf/scripts/convert.py "<文件路径>"
```

### 3. 读取转换结果

转换完成后，读取以下文件：
- `<文件路径>.claude/content.md` - 按页组织的 Markdown 内容
- `<文件路径>.claude/pages/` - 每页的预览图

**重要**: 查看 pages 目录中的图片以理解 PDF 的视觉布局。

## 输出格式

转换后的目录结构：
```
<原文件>.claude/
├── content.md          # 按页组织的文本内容
└── pages/              # 页面预览图
    ├── page_01.png
    ├── page_02.png
    └── ...
```

### Markdown 内容格式

```markdown
# PDF: document.pdf

---

## Page 1

内容文本...

![Page 1](pages/page_01.png)

---

## Page 2

...
```

## 使用示例

```
/pdf ~/Documents/report.pdf
```

## 系统依赖

- **必需**: Poppler（pdf2image 依赖）
  ```bash
  brew install poppler
  ```

## 错误处理

- 文件不存在 → 提示用户检查路径
- 转换失败 → 显示错误信息
- Poppler 不可用 → 仅输出文本，无预览图
