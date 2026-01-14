---
name: pptx
description: 读取 PowerPoint 演示文稿，转换为 Markdown + 幻灯片预览图，AI 智能生成纯文本内容
allowed-tools: Bash, Read, Write, Task
---

请帮我读取 PowerPoint 演示文稿并转换为 Markdown 格式。

## 参数

$ARGUMENTS

## 执行步骤

### 1. 检查虚拟环境

```bash
cd ~/.claude/office-deps && uv sync
```

### 2. 转换文档

```bash
cd ~/.claude/office-deps && uv run python ~/.claude/skills/pptx/scripts/convert.py "<文件路径>"
```

输出：
- `program-output.md` - 程序转换结果（Markdown + 预览图引用）
- `previews/` - 幻灯片预览图（如果 LibreOffice 可用）

### 3. AI 智能转换（核心步骤）

读取 `program-output.md` 和 `previews/` 中的预览图，生成纯文本 `content.md`。

**处理流程**：

1. 读取 `program-output.md` 内容
2. 逐幻灯片处理：
   - 读取对应的预览图 (`previews/slide_XX.png`)
   - 对比 program-output.md 中的文本与预览图
   - 修正数据错误或遗漏
   - 补充预览图中可见但程序未提取的内容（图表数据、表格等）
   - 移除预览图引用，保留纯文本
3. 保存为 `content.md`（纯文本，无图片引用）

**处理规则**：

| 问题类型 | 处理方式 |
|---------|---------|
| 文本遗漏 | 参考预览图补充 |
| 图表数据 | 转换为文本/表格描述 |
| 表格内容 | 参考预览图修正 |
| 图片引用 | 移除 |

**示例**：

program-output.md:
```markdown
## Slide 1

### 公司介绍

我们是一家科技公司

![Slide 1 Preview](previews/slide_01.png)
```

content.md:
```markdown
## Slide 1

### 公司介绍

我们是一家科技公司

**公司数据**：
- 成立时间：2020年
- 员工人数：500+
- 业务范围：全球
```

### 4. 验证转换结果

使用 Task 工具启动验证 subagent：

```
Task(
  subagent_type: "general-purpose",
  prompt: "按照 ~/.claude/agents/pptx-validator.md 的指引，验证转换结果：
    - output_dir: <文件路径>.claude/
    - report_path: <文件所在目录>/<文件名>-verify-report.md
  对比 previews/ 预览图 + program-output.md 与 content.md，检查内容一致性和完整性。"
)
```

**示例**：对于 `/path/to/presentation.pptx`
- output_dir: `/path/to/presentation.pptx.claude/`
- report_path: `/path/to/presentation-verify-report.md`

## 输出格式

转换后的目录结构：
```
<原文件>.claude/
├── program-output.md   # 程序转换结果（含预览图引用）
├── content.md          # 最终内容（纯文本，已修正）
└── previews/           # 幻灯片预览图（如有）
    ├── slide_01.png
    └── ...
```

## 使用示例

```
/pptx ~/Documents/presentation.pptx
```

## 系统依赖

- **必需**: LibreOffice（用于生成幻灯片预览图）
  ```bash
  brew install libreoffice
  ```
- **必需**: Poppler（pdf2image 依赖）
  ```bash
  brew install poppler
  ```

## 错误处理

- 文件不存在 → 提示用户检查路径
- 转换失败 → 显示错误信息
- LibreOffice 不可用 → 仅输出文本，无预览图
