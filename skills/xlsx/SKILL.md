---
name: xlsx
description: 读取 Excel 表格，转换为 Markdown + 公式 + 截图
allowed-tools: Bash, Read
---

请帮我读取 Excel 文件并转换为 Markdown 格式。

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
cd ~/.claude/office-deps && uv run python ~/.claude/skills/xlsx/scripts/convert.py "<文件路径>"
```

### 3. 读取转换结果

转换完成后，读取以下文件：
- `<文件路径>.claude/content.md` - Markdown 表格 + 公式
- `<文件路径>.claude/sheets/` - 每个工作表的截图（如果 LibreOffice 可用）

## 输出格式

转换后的目录结构：
```
<原文件>.claude/
├── content.md          # Markdown 表格 + 公式信息
└── sheets/             # 工作表截图（如有）
    ├── Sheet1.png
    └── ...
```

### Markdown 内容格式

```markdown
# Sheet: Sheet1

## 数据

| A | B | C |
|---|---|---|
| 1 | 2 | 3 |
| 4 | 5 | =SUM(A1:A2) |

## 公式

- C3: `=SUM(A1:A2)` → 结果: 5
```

## 使用示例

```
/xlsx ~/Documents/data.xlsx
```

## 系统依赖

- **可选**: LibreOffice（用于生成工作表截图）
  ```bash
  brew install libreoffice
  ```

## 错误处理

- 文件不存在 → 提示用户检查路径
- 转换失败 → 显示错误信息
- LibreOffice 不可用 → 跳过截图，仅输出文本
