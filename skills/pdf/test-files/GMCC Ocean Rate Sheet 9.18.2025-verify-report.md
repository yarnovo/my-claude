# PDF 转换验证报告

## 基本信息

| 项目 | 值 |
|-----|---|
| 文件 | GMCC Ocean Rate Sheet 9.18.2025.pdf |
| 页数 | 3 |
| 验证时间 | 2026-01-14 |

## 文件检查

| 文件 | 状态 | 说明 |
|-----|------|-----|
| program-output.md | ✅ | PyMuPDF4LLM 提取 |
| content.md | ✅ | 纯文本，无图片引用 |
| pages/ | ✅ | 3 张预览图 |

## program-output.md 问题汇总

| 问题类型 | 示例 | 修正 |
|---------|------|------|
| 错误删除线格式 | ~~100~~ | 100 |
| OCR 拼写错误 | Underwritng | Underwriting |
| OCR 拼写错误 | Qualifying Ratos | Qualifying Ratios |
| OCR 拼写错误 | Flood Certfcaton | Flood Certification |
| OCR 拼写错误 | Gif | Gift |
| 重复列数据 | 多列重复相同内容 | 合并为单列 |
| 表格格式混乱 | 多余的 Col2, Col3 | 清理表格结构 |

## content.md 修正统计

| 修正类型 | 数量 |
|---------|------|
| 删除线移除 | 10+ |
| OCR 拼写修正 | 15+ |
| 表格结构重组 | 8 个表格 |
| 格式标准化 | 全文 |

## 数据核对

### Page 1 - Rate Tables

| 数据项 | 预览图 | content.md | 状态 |
|-------|--------|------------|------|
| 5/6 ARM 6.250% | 100 | 100 | ✅ |
| 5/6 ARM 6.750% | 100.5 | 100.5 | ✅ |
| 7/6 ARM 6.500% | 100 | 100 | ✅ |
| Cash out > 50% | 0.375% | 0.375% | ✅ |
| FICO < 700 | 0.375% | 0.375% | ✅ |

### Page 2 - LTV Matrix

| 数据项 | 预览图 | content.md | 状态 |
|-------|--------|------------|------|
| Primary 1 Unit Up to $1.5M | 70% | 70% | ✅ |
| Investment CONDO $1.5M+ | 55% | 55% | ✅ |
| Cash Out Primary Up to $1.5M | 65% | 65% | ✅ |
| File Review | $325 | $325 | ✅ |

### Page 3 - Guidelines

| 数据项 | 预览图 | content.md | 状态 |
|-------|--------|------------|------|
| Qualifying Ratios | 43% | 43% | ✅ |
| Minimum FICO | 680 | 680 | ✅ |
| Foreclosure | 4 Years | 4 Years | ✅ |
| Primary Reserve | 3 months | 3 months | ✅ |

## 总结

- **整体一致性**: ✅ 高
- **content.md 质量**: 纯文本 ✅ (无图片引用)
- **数据准确率**: 100%
- **OCR 质量**: 中等（多处拼写错误已修正）
- **主要问题**: PyMuPDF4LLM 错误识别删除线格式

## 建议

1. PDF 中的表格边框被误识别为删除线，需要 AI 修正
2. OCR 对某些专业术语识别不准确，需人工校验
3. 多列表格被重复提取，需要去重处理
