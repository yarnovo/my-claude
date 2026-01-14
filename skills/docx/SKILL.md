---
name: docx
description: 读取 Word 文档，转换为 Markdown + 图片，AI 智能提取图片内容
allowed-tools: Bash, Read, Write, Task
---

请帮我读取 Word 文档并转换为 Markdown 格式。

## 参数

$ARGUMENTS

## 执行步骤

### 1. 检查虚拟环境

```bash
cd ~/.claude/office-deps && uv sync
```

### 2. 转换文档

```bash
cd ~/.claude/office-deps && uv run python ~/.claude/skills/docx/scripts/convert.py "<文件路径>"
```

输出：
- `program-output.md` - 原始转换结果（文本 + 图片引用）
- `images/` - 提取的图片文件

### 3. AI 智能转换（核心步骤）

读取 `program-output.md` 和 `images/` 中的图片，将图片内容转换为 Markdown 文本，生成 `content.md`。

**处理流程**：

1. 读取 `program-output.md` 内容
2. 遇到图片引用 `![...](images/xxx.png)` 时：
   - 读取对应图片
   - 识别图片内容（表格、文字、图表等）
   - 将图片内容转换为 Markdown 格式
   - 替换图片引用为转换后的 Markdown
3. 保存为 `content.md`

**图片转换规则**：

| 图片类型 | 转换为 |
|---------|-------|
| 表格截图 | Markdown 表格 |
| 文字截图 | 纯文本 |
| 图表 | 描述 + 关键数据 |
| 装饰性图片 | 简短描述或删除 |

**示例**：

program-output.md:
```markdown
1. **Base Rate:** Read base rate from the table below.

![](images/image1.png)
```

content.md:
```markdown
1. **Base Rate:** Read base rate from the table below.

| Rate Guide as of | Program | Rate | Base Price | Margin | Index |
|-----------------|---------|------|------------|--------|-------|
| 9/15/2025 | 7/6 Mo. ARM (5/1/5) | 6.125% | 99.75* | 3.000% | 30-Day Avg. |
| | | 6.250% | 100.00* | | |
```

### 4. 验证转换结果

使用 Task 工具启动验证 subagent：

```
Task(
  subagent_type: "general-purpose",
  prompt: "按照 ~/.claude/agents/docx-validator.md 的指引，验证转换结果：
    - output_dir: <文件路径>.claude/
    - report_path: <文件所在目录>/<文件名>-verify-report.md
  对比 program-output.md + 图片 与 content.md，检查内容一致性和完整性。"
)
```

## 输出格式

转换后的目录结构：
```
<原文件>.claude/
├── program-output.md           # 原始转换（文本 + 图片引用）
├── content.md          # 最终内容（图片已转为 Markdown）
└── images/             # 提取的图片
    ├── image1.png
    └── ...
```

## 使用示例

```
/docx ~/Documents/report.docx
```

## 错误处理

- 文件不存在 → 提示用户检查路径
- 转换失败 → 显示错误信息
- 图片识别失败 → 保留原图片引用并标注
