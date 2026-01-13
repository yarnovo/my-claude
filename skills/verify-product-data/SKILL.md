---
name: verify-product-data
description: 验证产品数据（定价规则、核保规则）与源文档的匹配关系
allowed-tools: Read, Glob, Grep, Skill, Task
---

验证产品规则数据（Rate Sheets、Underwriting Guidelines）是否与源文档（PDF/PPTX）内容一致。

## 目标

确保从源文档提取的产品数据准确无误：
- 定价基准利率
- 价格调整规则
- 核保资格条件
- LTV/DTI 限制

## 检查范围

### Rate Sheets（定价规则）
位置：`apps/web/src/agents/data/products/rate-sheets/`

| 产品 | 数据文件 | 源文档 |
|------|----------|--------|
| gmcc-ocean | gmcc-ocean.ts | Ocean Rate Sheet PDF, Ocean PPT |
| gmcc-hermes-ca | gmcc-hermes-ca.ts | Hermes CA Rate Sheet PDF |
| gmcc-hermes-non-ca | gmcc-hermes-non-ca.ts | Hermes Non-CA Rate Sheet PDF |
| gmcc-thunder | gmcc-thunder.ts | Thunder Rate Sheet PDF |
| universe-snow | universe-snow.ts | Universe Snow PPT |

### Underwriting（核保规则）
位置：`apps/web/src/agents/data/products/underwriting/`

| 产品 | 数据文件 | 源文档 |
|------|----------|--------|
| gmcc-ocean | gmcc-ocean.ts | Ocean UW Manual PDF |
| gmcc-hermes-ca | gmcc-hermes-ca.ts | Hermes PPT |
| gmcc-hermes-non-ca | gmcc-hermes-non-ca.ts | Hermes PPT |
| gmcc-thunder | gmcc-thunder.ts | Thunder PPT |
| universe-snow | universe-snow.ts | Universe PPT |

## 执行步骤

### 1. 读取产品数据文件

```bash
# 读取所有 rate-sheet 数据
Read: apps/web/src/agents/data/products/rate-sheets/*.ts

# 读取所有 underwriting 数据
Read: apps/web/src/agents/data/products/underwriting/*.ts
```

### 2. 读取源文档

使用 /pdf 和 /pptx 技能转换源文档：

```bash
# PDF 源文档
/pdf apps/web/public/products/ocean/rate-sheets/GMCC Ocean Rate Sheet 12.18.2025.pdf
/pdf apps/web/public/products/hermes/rate-sheets/GMCC Hermes Rate Sheet 9.15.25 - CA.pdf
/pdf apps/web/public/products/thunder/rate-sheets/GMCC Thunder Rate Sheet 12.23.2025.pdf
/pdf apps/web/public/products/ocean/underwriting/GMCC Ocean UW Manual Nov 2024.pdf

# PPTX 源文档
/pptx apps/web/public/products/ocean/presentations/Essential - GMCC Ocean 12-23-2025 v3.pptx
/pptx apps/web/public/products/hermes/presentations/Essential - GMCC Hermes v10 07-27-2025.pptx
/pptx apps/web/public/products/thunder/presentations/Essential - Thunder 12.23.2025.pptx
/pptx apps/web/public/products/universe/presentations/GMCC Universe V13 06-27-2025.pptx
```

### 3. 比对关键数据

对每个产品，比对以下字段：

#### Rate Sheet 检查项
- [ ] 基准利率（baseRates）：Index、Margin、利率值
- [ ] 价格调整（adjustments）：条件、调整值
- [ ] 叠加规则（stackingRules）：互斥规则描述

#### Underwriting 检查项
- [ ] 支持的州（supportedStates）
- [ ] 最低 FICO 要求
- [ ] 最大 LTV 限制
- [ ] 最大 DTI 限制
- [ ] 贷款金额范围
- [ ] 房产类型限制

### 4. 并行检查（可选）

使用 Task 工具并行检查多个产品：

```
可以为每个产品启动独立的 Task Agent 进行检查，加速验证过程。
```

## 输出格式

```markdown
# 产品数据验证报告

## 产品：GMCC Ocean

### Rate Sheet 验证
| 字段 | 代码值 | 源文档值 | 状态 |
|------|--------|----------|------|
| 5/1 ARM Base Rate | 7.25% | 7.25% | ✅ 匹配 |
| FICO 720-739 Adj | -0.125 | -0.125 | ✅ 匹配 |
| IO Adjustment | +0.25 | +0.375 | ❌ 不匹配 |

### Underwriting 验证
| 字段 | 代码值 | 源文档值 | 状态 |
|------|--------|----------|------|
| Min FICO | 660 | 660 | ✅ 匹配 |
| Max LTV (Primary) | 80% | 80% | ✅ 匹配 |

---

## 总结
- 检查产品数: 5
- 通过: 4
- 有差异: 1
- 需要更新的文件:
  - `gmcc-ocean.ts`: IO Adjustment 值不正确
```

## 注意事项

1. **只读操作**：此技能只做比对，不修改任何文件
2. **源文档优先**：如有差异，以源文档为准
3. **版本对齐**：确保比对的是同一版本的源文档
4. **数值精度**：利率比对精度为 0.001（如 7.25% vs 7.250%）
5. **字符串匹配**：州名等字符串忽略大小写和空格差异

## 快速检查单个产品

```bash
# 只检查 GMCC Ocean
/verify-product-data gmcc-ocean

# 只检查 rate-sheets
/verify-product-data --type=rate-sheets

# 只检查 underwriting
/verify-product-data --type=underwriting
```
