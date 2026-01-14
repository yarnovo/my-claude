---
name: pdf
description: 读取 PDF 文档，转换为 Markdown + 页面预览图，AI 智能生成纯文本内容
allowed-tools: Bash, Read, Write, Task
---

请帮我读取 PDF 文档并转换为 Markdown 格式。

## 参数

$ARGUMENTS

## 执行步骤

### 1. 检查虚拟环境

```bash
cd ~/.claude/office-deps && uv sync
```

### 2. 转换文档

```bash
cd ~/.claude/office-deps && uv run python ~/.claude/skills/pdf/scripts/convert.py "<文件路径>"
```

输出：
- `program-output.md` - 原始转换结果（按页组织，包含图片引用）
- `pages/` - 页面预览图

### 3. AI 智能转换（核心步骤）

读取 `program-output.md` 和 `pages/` 中的预览图，生成纯文本 `content.md`。

**处理流程**：

1. 读取 `program-output.md` 内容
2. 逐页处理：
   - 读取对应的页面预览图 (`pages/page_XX.png`)
   - 对比 program-output.md 中的文本与图片
   - 修正 OCR 错误（如 "Underwritng" → "Underwriting"）
   - 修正表格格式问题
   - 移除图片引用，保留纯文本
3. 保存为 `content.md`（纯文本，无图片引用）

**处理规则**：

| 问题类型 | 处理方式 |
|---------|---------|
| OCR 拼写错误 | 参考图片修正 |
| 表格格式错乱 | 参考图片重建表格 |
| 删除线误标 | 参考图片移除错误格式 |
| 图片引用 | 移除，内容已在文本中 |

**示例**：

program-output.md:
```markdown
## Page 1

| **Underwritng** | **Ratos** |
|-----------------|-----------|

![Page 1](pages/page_01.png)
```

content.md:
```markdown
## Page 1

| **Underwriting** | **Ratios** |
|------------------|------------|
```

### 4. 验证转换结果

使用 Task 工具启动验证 subagent：

```
Task(
  subagent_type: "general-purpose",
  prompt: "按照 ~/.claude/agents/pdf-validator.md 的指引，验证转换结果：
    - output_dir: <文件路径>.claude/
    - report_path: <文件所在目录>/<文件名>-verify-report.md
  对比 pages/ 预览图 + program-output.md 与 content.md，检查内容一致性和完整性。"
)
```

**示例**：对于 `/path/to/document.pdf`
- output_dir: `/path/to/document.pdf.claude/`
- report_path: `/path/to/document-verify-report.md`

## 输出格式

转换后的目录结构：
```
<原文件>.claude/
├── program-output.md           # 原始转换（按页组织，含图片引用）
├── content.md          # 最终内容（纯文本，已修正错误）
└── pages/              # 页面预览图
    ├── page_01.png
    ├── page_02.png
    └── ...
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
