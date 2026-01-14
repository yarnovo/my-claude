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

**⚠️ 重要：此步骤决定最终输出质量，必须认真执行每个子步骤！**

**处理流程**：

1. **读取 `program-output.md` 内容**
2. **识别所有需要表格提取的幻灯片**：
   - 搜索所有 `likely_table=true` 标记
   - 记录这些幻灯片编号（如 Slide 3, 4, 5, 6, 26, 27 等）
   - **必须处理所有标记的幻灯片，不能跳过**
3. **逐幻灯片处理**：
   - 对于 `likely_table=true` 的幻灯片：
     - **必须**读取预览图 (`previews/slide_XX.png`)
     - **必须**将图中的表格转换为 Markdown 表格
     - **必须**验证表格行数/列数与预览图一致
   - 对于其他幻灯片：
     - 检查文本是否完整
     - 移除预览图引用
4. **保存为 `content.md`**（纯文本，无图片引用）

**处理规则**：

| 问题类型 | 处理方式 |
|---------|---------|
| 文本遗漏 | 参考预览图补充 |
| 图表数据 | 转换为 Markdown 表格 |
| 表格内容 | **必须**从预览图提取完整数据 |
| 图片引用 | 移除 |

#### 3.1 表格提取专项指导（重要）

**识别表格幻灯片**：
- 查看 `<!-- SLIDE_ANALYSIS: ... likely_table=true -->` 标记
- 预览图中看到网格状数据
- markitdown 提取结果明显缺少数据

**表格提取步骤**：

1. **读取预览图**：仔细查看 `previews/slide_XX.png`
2. **识别表格结构**：
   - 确定行数和列数
   - 识别表头行
   - 识别合并单元格
3. **逐单元格提取**：从左到右、从上到下
4. **格式化为 Markdown 表格**：
   ```markdown
   | 列1 | 列2 | 列3 |
   |-----|-----|-----|
   | 数据 | 数据 | 数据 |
   ```
5. **验证完整性**：对比预览图确认无遗漏

**处理优先级**：

| 优先级 | 内容类型 | 说明 |
|--------|----------|------|
| P0 必须提取 | 定价矩阵、资格矩阵、LTV Matrix | 核心业务数据 |
| P1 应该提取 | 储备要求表、费用明细表 | 重要参考数据 |
| P2 可以简化 | 示例文档、合规清单 | 非核心数据 |

#### 3.2 常见表格类型模板

**LTV Matrix 模板**：
```markdown
| Property Type | Loan Amount | Max LTV |
|---------------|-------------|---------|
| 1 Unit SFR | Up to $1.5M | 70% |
| 1 Unit SFR | $1.5M-$2M | 65% |
| Condo | Up to $1.5M | 65% |
```

**Fee Adjustments 模板**：
```markdown
| FICO Score | LTV ≤65% | 65-70% | 70-75% | 75-80% |
|------------|----------|--------|--------|--------|
| ≥740 | 0.000% | 0.125% | 0.250% | 0.375% |
| 700-739 | 0.125% | 0.250% | 0.375% | 0.500% |
```

**Reserve Requirements 模板**：
```markdown
| Occupancy | FICO ≥700 | FICO 680-699 | FICO <680 |
|-----------|-----------|--------------|-----------|
| Primary | 6 months | 9 months | 12 months |
| Investment | 12 months | 18 months | 24 months |
```

#### 3.3 提取质量自检

在保存 `content.md` 前，检查以下项目：

**表格完整性检查**：
- [ ] 所有标记为 `likely_table=true` 的幻灯片都已处理
- [ ] 每个表格的行数和列数与预览图一致
- [ ] 数值数据（百分比、金额）准确无误
- [ ] 表头行正确识别

**格式检查**：
- [ ] 使用标准 Markdown 表格语法
- [ ] 表格前后有空行
- [ ] 无多余的图片引用

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

使用 Task 工具调用 `pptx-validator` subagent 进行验证：

- **subagent_type**: `pptx-validator`
- **description**: `验证 pptx 转换结果`
- **prompt**: 传入 output_dir 和 report_path 参数

```
验证转换结果：
- output_dir: <文件路径>.claude/
- report_path: <文件所在目录>/<文件名>-verify-report.md
```

验证器会对比 previews/ 预览图 + program-output.md 与 content.md，检查内容一致性和完整性。

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
