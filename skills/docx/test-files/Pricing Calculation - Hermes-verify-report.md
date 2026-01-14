# Word 文档转换验证报告

## 基本信息

| 项目 | 值 |
|-----|---|
| 文件 | Pricing Calculation - Hermes.docx |
| 图片数量 | 5 |
| 验证时间 | 2026-01-14 |

## 文件检查

| 文件 | 状态 | 说明 |
|-----|------|-----|
| program-output.md | ✅ | markitdown 提取，含图片引用 |
| content.md | ✅ | 纯文本，图片内容已转换为表格 |
| images/ | ✅ | 5 张图片 |

## 逐图片验证

### image1.png - Base Rate Table

**图片内容**：
- 类型：表格
- 关键数据：Rate Guide as of 9/15/2025, 7/6 Mo. ARM, 6.125% = 99.75*, 6.250% = 100.00*

**content.md 对应内容**：
| Rate | Base Price | Margin | Index |
|------|------------|--------|-------|
| 6.125% | 99.75* | 3.000% | 30-Day Avg. |
| 6.250% | 100.00* | | |

**验证结果**: ✅ 准确

### image2.png - Rate Adjustments Table (Full)

**图片内容**：
- 类型：大型表格
- 关键数据：Loan Amount/FICO adjustments, Other Terms adjustments

**content.md 对应内容**：
完整提取了所有调整项：
- Loan Amount ≤ $2MM (700+, 680-699)
- $2MM < Loan Amount ≤ $3MM
- $3MM < Loan Amount ≤ $4MM
- Cash-Out, Condo, 2-4 Unit, Investment Property 等

**验证结果**: ✅ 准确

### image3.png - Loan Amount/FICO Table

**图片内容**：
- 类型：表格片段
- 关键数据：Loan Amount ≤ $2MM 的 700+ 和 680-699 行

**验证结果**: ✅ 准确（已包含在 image2 完整表格中）

### image4.png - Cash-Out Table

**图片内容**：
- 类型：表格片段
- 关键数据：Cash-Out 0.000%, 0.250%, 0.375%, 0.500%

**验证结果**: ✅ 准确（已包含在 image2 完整表格中）

### image5.png - Extension Costs Table

**图片内容**：
- 类型：表格
- 关键数据：7-Day = 0.125%, 15-Day = 0.250%

**content.md 对应内容**：
| Extension Days | Extension Fee Costs |
|----------------|---------------------|
| 7-Day | 0.125% from price |
| 15-Day | 0.250% from price |

**验证结果**: ✅ 准确

## 数据核对

| 数据项 | 图片 | content.md | 状态 |
|-------|------|------------|------|
| Base Rate 6.125% | 99.75* | 99.75* | ✅ |
| Base Rate 6.250% | 100.00* | 100.00* | ✅ |
| Margin | 3.000% | 3.000% | ✅ |
| Loan ≤$2MM, 700+, LTV≤60 | 0.000% | 0.000% | ✅ |
| Cash-Out LTV 70.01-75 | 0.500% | 0.500% | ✅ |
| Investment Property LTV 60.01-65 | 0.250% | 0.250% | ✅ |
| 7-Day Extension | 0.125% | 0.125% | ✅ |
| Example Total Adjustment | 1.375% | 1.375% | ✅ |

## 文本内容验证

| 检查项 | 状态 | 说明 |
|-------|------|-----|
| 原始文本保留 | ✅ | 所有步骤说明已保留 |
| 列表结构 | ✅ | 步骤编号和列表完整 |
| 标题层级 | ✅ | 合理的层级结构 |
| 示例计算 | ✅ | 完整的计算过程 |

## 总结

- **整体一致性**: ✅ 高
- **图片转换准确率**: 5/5 (100%)
- **遗漏内容**: 无
- **错误内容**: 无

## 修正统计

| 修正类型 | 数量 | 说明 |
|---------|------|------|
| 图片→表格 | 5 | 所有图片内容已转为 Markdown 表格 |
| 结构优化 | 1 | 添加清晰的章节标题 |
| 格式统一 | 全文 | 统一百分比格式 |

## 建议

1. 原文档图片质量良好，OCR 识别准确
2. 表格数据完整，无需额外校验
3. 示例计算步骤清晰，便于理解
