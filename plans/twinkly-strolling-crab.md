# Rate Sheet 准确度优化计划 - Universe 产品

## 问题概述

客户反馈 Rate Sheet 准确度不够高，经分析发现 **GMCC Universe 产品线**存在严重的计算错误。

> **注意**：会议记录中的 "Titanium Advantage" 是 Oaktree Funding 的产品，不是 GMCC 的。
> 会议示例仅展示目标输出格式，本次专注修复 GMCC Universe 产品。

### 核心问题：Price vs Rate 调整混淆

| 维度 | 官方文档 (GMCC Universe 9-19-2025 Cascade) | 当前代码 |
|------|---------|---------|
| 调整类型 | **Price 调整**（点数） | 误用为 Rate 调整 |
| FICO 660-679 | -0.25 price | `+0.0025` rate（错误！）|
| FICO 620-659 | -0.50 price | `+0.005` rate（错误！）|
| FICO < 620 | -1.00 price | `+0.01` rate（错误！）|

### 其他缺失功能

- **产品类型**：缺少 10/1 ARM (2/2/6 Caps)、NY 特殊定价 (6.75% @ 99.75)
- **Margin**：官方 3.25%，代码未定义
- **LTV 限制**：Primary/2nd 60%, Investment/Cash-Out 50%
- **DTA 验证**：Debts to Assets < 60%
- **储备金**：FICO>=700 → 12mo, FICO<700 → 18mo

---

## 实施计划

### Phase 1: 核心修复（必须）

#### 1.1 添加 Universe 产品常量
**文件**: `web/lib/loan-sdk/core/constants.ts`

```typescript
// 新增内容
export const UNIVERSE_PRODUCTS = {
  FIXED_30: {
    name: 'Universe 30 Yr. Fixed',
    rates: [
      { rate: 0.05875, price: 98.750 },
      { rate: 0.06000, price: 99.000 },
      { rate: 0.06125, price: 99.250 },
      { rate: 0.06250, price: 99.500 },
      { rate: 0.06375, price: 99.875 },
    ],
  },
  ARM_10_1: {
    name: 'Universe 10/1 ARM',
    caps: '2/2/6',
    margin: 0.0325,
    rates: [
      { rate: 0.05750, price: 98.750 },
      { rate: 0.05875, price: 99.000 },
      { rate: 0.06000, price: 99.250 },
      { rate: 0.06125, price: 99.500 },
      { rate: 0.06250, price: 99.875 },
    ],
  },
  NY_SPECIAL: { rate: 0.0675, price: 99.75 },
};

export const UNIVERSE_PRICE_ADJUSTMENTS = {
  FICO_660_679: -0.25,
  FICO_620_659: -0.50,
  FICO_BELOW_620: -1.00,
  REFINANCE_UNIVERSE_LOAN: -0.50,
  DOC_SIGNING_OUTSIDE_US: -0.25,
  SHORT_SALE_FORECLOSURE_5YRS: -0.50,
};

export const UNIVERSE_LTV_LIMITS = {
  PRIMARY_SECOND_HOME: 0.60,
  INVESTMENT_CASHOUT: 0.50,
};
```

#### 1.2 实现 Universe 利率计算函数
**文件**: `web/lib/loan-sdk/core/calculators.ts`

```typescript
export function calculateUniverseRate(params: UniverseRateParams): UniverseRateResult {
  // 1. NY 特殊定价检查
  // 2. 计算 Price 调整（不是 Rate 调整！）
  // 3. 生成多档利率/价格选项
  // 4. 计算 Cost to Borrower / Lender Credit
  // 5. 返回推荐选项
}
```

#### 1.3 修复 matchRateSheetTool
**文件**: `web/lib/agent/tools.ts` (行 529-538)

修改前（错误）:
```typescript
if (fico >= 660 && fico < 680) {
  adjustments.push({ name: "FICO 660-679", value: 0.0025 });  // 错误
}
```

修改后（正确）:
```typescript
if (product === "universe") {
  const result = calculateUniverseRate({ ... });
  return {
    ...result,
    priceOptions: result.rateOptions,  // 返回多档选择
  };
}
```

### Phase 2: 验证完善

#### 2.1 添加验证函数
**文件**: `web/lib/loan-sdk/core/validators.ts`
- `validateUniverseLTV()` - LTV 限制
- `validateDTA()` - Debts to Assets < 60%
- `validateUniverseCoverage()` - 覆盖区域检查

#### 2.2 更新储备金计算
- FICO >= 700: 12 个月 PITIA
- FICO < 700: 18 个月 PITIA
- 外国人: 12 个月 P&I 存入投资者银行

### Phase 3: 测试

#### 3.1 单元测试
- Price 调整计算正确性
- LTV 限制验证
- NY 特殊定价
- 储备金要求

#### 3.2 E2E 测试
- 对比官方 Rate Sheet 手动计算结果
- 验证会议记录中的示例场景

---

## 关键文件清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `web/lib/loan-sdk/core/constants.ts` | 修改 | 添加 Universe 常量 |
| `web/lib/loan-sdk/core/calculators.ts` | 修改 | 添加 calculateUniverseRate() |
| `web/lib/agent/tools.ts` | 修改 | 修复 matchRateSheetTool |
| `web/lib/loan-sdk/core/validators.ts` | 修改 | 添加 DTA/LTV 验证 |
| `web/lib/loan-sdk/index.ts` | 修改 | 导出新函数 |
| `web/public/rate_sheet.json` | 修改 | 添加 Universe 数据 |

---

## 验证标准

1. **FICO 660-679 场景**:
   - 输入: FICO 670, 利率选择 6.25%
   - 预期: 基础价格 99.50 → 调整后 99.25 → 成本 $7,500 (每百万贷款)

2. **NY 特殊定价**:
   - 输入: state='NY'
   - 预期: 利率 6.75% @ 99.75

3. **LTV 限制**:
   - Primary 购房 LTV 65% → 应被拒绝（最高 60%）
   - Investment Cash-Out LTV 55% → 应被拒绝（最高 50%）
