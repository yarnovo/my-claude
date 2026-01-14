---
name: xlsx
description: 读取 Excel 表格，转换为 Markdown + 公式 + 截图，AI 智能生成纯文本内容
allowed-tools: Bash, Read, Write, Task
---

请帮我读取 Excel 文件并转换为 Markdown 格式。

## 参数

$ARGUMENTS

## 执行步骤

### 1. 检查虚拟环境

```bash
cd ~/.claude/office-deps && uv sync
```

### 2. 转换文档

```bash
cd ~/.claude/office-deps && uv run python ~/.claude/skills/xlsx/scripts/convert.py "<文件路径>"
```

输出：
- `program-output.md` - 程序转换结果（Markdown 表格 + 公式，含截图引用）
- `sheets/` - 工作表截图（如果 LibreOffice 可用）

### 3. AI 智能转换（核心步骤）

读取 `program-output.md` 和 `sheets/` 中的截图，生成纯文本 `content.md`。

**处理流程**：

1. 读取 `program-output.md` 内容
2. 逐工作表处理：
   - 读取对应的截图 (`sheets/sheet_XX.png`)
   - 对比 program-output.md 中的表格与截图
   - 修正数据错误或遗漏
   - 补充截图中可见但程序未提取的内容
   - 移除截图引用，保留纯文本
3. 保存为 `content.md`（纯文本，无图片引用）

**处理规则**：

| 问题类型 | 处理方式 |
|---------|---------|
| 数据遗漏 | 参考截图补充 |
| 格式错乱 | 参考截图修正表格结构 |
| 公式显示 | 保留公式结果，移除公式本身（如需要） |
| 图片引用 | 移除 |

**示例**：

program-output.md:
```markdown
# Sheet: Rate Sheet

| RATE | Price |
|------|-------|
| 6.250% | 100 |

![Sheet 1](sheets/sheet_01.png)
```

content.md:
```markdown
# Sheet: Rate Sheet

| RATE | Price |
|------|-------|
| 6.250% | 100 |
| 6.375% | 100.125 |
| 6.500% | 100.25 |
```

### 4. 验证转换结果

使用 Task 工具启动验证 subagent：

```
Task(
  subagent_type: "general-purpose",
  prompt: "按照 ~/.claude/agents/xlsx-validator.md 的指引，验证转换结果：
    - output_dir: <文件路径>.claude/
    - report_path: <文件所在目录>/<文件名>-verify-report.md
  对比 sheets/ 截图 + program-output.md 与 content.md，检查内容一致性和完整性。"
)
```

**示例**：对于 `/path/to/data.xlsx`
- output_dir: `/path/to/data.xlsx.claude/`
- report_path: `/path/to/data-verify-report.md`

## 输出格式

转换后的目录结构：
```
<原文件>.claude/
├── program-output.md   # 程序转换结果（含截图引用）
├── content.md          # 最终内容（纯文本，已修正）
└── sheets/             # 工作表截图（如有）
    ├── sheet_01.png
    └── ...
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
