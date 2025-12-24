# 组件重组计划

## 目标
将 `web/components/` 下的 15 个业务组件按功能分类到对应文件夹。

## 新文件夹结构

```
web/components/
├── trading/              # 交易相关 (8个)
├── portfolio/            # 投资组合 (2个)
├── market/               # 市场资讯 (2个)
├── ai/                   # AI助手 (1个)
└── layout/               # 布局导航 (2个)
```

## 文件移动清单

### trading/
| 源文件 | 目标 |
|--------|------|
| allocation-card.tsx | trading/allocation-card.tsx |
| costs-card.tsx | trading/costs-card.tsx |
| execution-method-card.tsx | trading/execution-method-card.tsx |
| fills-blotter.tsx | trading/fills-blotter.tsx |
| market-info-card.tsx | trading/market-info-card.tsx |
| order-blotter.tsx | trading/order-blotter.tsx |
| order-details-card.tsx | trading/order-details-card.tsx |
| orders-table.tsx | trading/orders-table.tsx |
| trading-dashboard.tsx | trading/trading-dashboard.tsx |

### portfolio/
| 源文件 | 目标 |
|--------|------|
| client-portfolio-table.tsx | portfolio/client-portfolio-table.tsx |
| portfolio-chart.tsx | portfolio/portfolio-chart.tsx |

### market/
| 源文件 | 目标 |
|--------|------|
| financial-news.tsx | market/financial-news.tsx |
| product-catalog.tsx | market/product-catalog.tsx |

### ai/
| 源文件 | 目标 |
|--------|------|
| intelligent-assistance.tsx | ai/intelligent-assistance.tsx |

### layout/
| 源文件 | 目标 |
|--------|------|
| navigator.tsx | layout/navigator.tsx |
| locale-switcher.tsx | layout/locale-switcher.tsx |

## 需要更新导入路径的文件

| 文件 | 需更新的导入 |
|------|-------------|
| `web/app/[locale]/pms-admin/dashboard/page.tsx` | 5 个组件路径 |
| `web/app/[locale]/pms-admin/oems/new-order/page.tsx` | trading-dashboard |
| `web/app/[locale]/pms-admin/oems/order-blotter/page.tsx` | order-blotter |
| `web/components/trading/order-blotter.tsx` | navigator, orders-table, fills-blotter |
| `web/components/trading/trading-dashboard.tsx` | 5 个 trading 组件 |
| `web/components/admin/site-header.tsx` | locale-switcher |
| `web/docs/i18n-usage.md` | locale-switcher (文档) |
| `web/docs/i18n-quick-start.md` | locale-switcher (文档) |

## 执行步骤

1. **创建文件夹**: `trading/`, `portfolio/`, `market/`, `ai/`, `layout/`
2. **移动文件**: 使用 git mv 保留历史
3. **更新内部导入**: 修改移动后组件的内部引用
4. **更新外部导入**: 修改页面和其他组件的引用
5. **创建 index.ts**: 每个文件夹创建导出文件便于统一导入
6. **验证**: 运行 TypeScript 检查确保无报错
