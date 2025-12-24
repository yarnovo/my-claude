# PMS Agent 工具实现计划

## 目标

实现**适配层机制**：同一个业务工具，根据入口点不同，执行方式不同：
- **Embedded**：操作前端 GUI（导航到页面、打开弹窗、填充表单、等待用户确认）
- **Standalone**：直接调用 API + HITL 确认消息

当前业务范围：**基金主数据管理**（系统管理员角色）

---

## 当前状态

### 已有基础设施

| 模块 | 状态 | 关键文件 |
|------|------|---------|
| 工具框架 | ✅ | `web/lib/agent/tools/index.ts` |
| UI 状态工具 | ✅ | `web/lib/agent/tools/ui-state.ts`（13 个通用 UI 工具） |
| PartyKit 通信 | ✅ | `web/party/ui-state.ts` |
| PMS SDK | ✅ | `web/lib/sdk/pms/`（自动生成） |
| 基金 API | ✅ | `web/lib/services/pms-admin/fund/api.ts` |
| 基金页面 | ✅ | `web/app/[locale]/pms-admin/master-data/fund/page.tsx` |

### 基金模块现有实现

**数据模型 (FundDto)**：
```typescript
{
  id: number;
  version?: number;      // 乐观锁
  fundName?: string;     // 基金名称
  activeStatus?: 'ENABLE' | 'DISABLE';
  remarks?: string;
}
```

**API 接口**：
- `POST /pms-service/fund/list-paged` - 分页查询
- `POST /pms-service/fund/calc` - 数据验证
- `POST /pms-service/fund/batch-upsert` - 批量创建/更新
- `POST /pms-service/fund/delete/{id}` - 删除

**页面 UI 状态**：
- `formOpen` / `setFormOpen` - 表单弹窗开关
- `formMode` - 'create' | 'edit'
- `editingFund` - 编辑中的基金
- `deleteOpen` / `deletingFund` - 删除确认弹窗

---

## 架构设计

### 核心理念

```
┌─────────────────────────────────────────────────────────────┐
│                    Agent 调用业务工具                        │
│                                                             │
│   create_fund({ fundName: "Alpha", remarks: "测试" })       │
│                                                             │
└─────────────────────────────────┬───────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────┐
│                      工具工厂                                │
│                                                             │
│   根据 entryPoint 选择适配器                                 │
│                                                             │
└──────────────┬──────────────────────────┬───────────────────┘
               │                          │
               ▼                          ▼
┌──────────────────────────┐  ┌───────────────────────────────┐
│     Standalone 适配器     │  │      Embedded 适配器          │
│                          │  │                               │
│  1. 调用 PMS API         │  │  1. navigate('/master-data/   │
│  2. 返回确认消息          │  │     fund')                    │
│     "即将创建基金 Alpha， │  │  2. 打开创建弹窗              │
│      请确认"              │  │  3. 填充表单                  │
│  3. 等待用户确认          │  │  4. 返回 pending_confirmation │
│  4. 执行创建              │  │  5. 用户点击确认后执行        │
│                          │  │                               │
└──────────────────────────┘  └───────────────────────────────┘
```

### 工具分类

| 分类 | 说明 | Standalone | Embedded |
|------|------|-----------|----------|
| **query** | 只读查询 | 直接调 API | 直接调 API（无需 UI） |
| **action** | 写入操作 | API + HITL 确认 | UI 操作 + 用户确认 |

---

## 基金业务工具设计

### 工具列表（6 个）

| 工具名 | 分类 | 业务描述 | 典型问法 |
|--------|------|---------|---------|
| `list_funds` | query | 查询基金列表 | "有哪些基金？" |
| `get_fund_detail` | query | 获取基金详情 | "Alpha 基金的详情" |
| `create_fund` | action | 创建新基金 | "创建一个叫 Alpha 的基金" |
| `update_fund` | action | 修改基金信息 | "把 Alpha 基金的备注改成 xxx" |
| `enable_fund` | action | 启用基金 | "启用 Alpha 基金" |
| `disable_fund` | action | 停用基金 | "停用 Alpha 基金" |

> 注意：不提供 `delete_fund`，用 `disable_fund` 软删除

### 工具参数定义

```typescript
// list_funds
z.object({
  fundName: z.string().optional().describe('按名称模糊搜索'),
  activeOnly: z.boolean().optional().describe('只显示启用的基金'),
})

// get_fund_detail
z.object({
  fundId: z.number().describe('基金 ID'),
})

// create_fund
z.object({
  fundName: z.string().describe('基金名称（必填）'),
  remarks: z.string().optional().describe('备注'),
})

// update_fund
z.object({
  fundId: z.number().describe('基金 ID'),
  fundName: z.string().optional().describe('新的基金名称'),
  remarks: z.string().optional().describe('新的备注'),
})

// enable_fund / disable_fund
z.object({
  fundId: z.number().describe('基金 ID'),
})
```

---

## 文件结构

```
web/lib/agent/tools/
├── index.ts                    # 工具工厂（修改）
├── types.ts                    # 类型定义（扩展）
├── ui-state.ts                 # 通用 UI 工具（保留）
│
├── definitions/                # 新增：工具定义（纯定义，无实现）
│   ├── index.ts
│   └── fund.ts                 # 基金工具定义
│
├── adapters/                   # 新增：适配器
│   ├── index.ts
│   ├── types.ts                # 适配器类型
│   ├── standalone.ts           # Standalone 适配器
│   └── embedded.ts             # Embedded 适配器
│
└── fund/                       # 新增：基金业务工具
    ├── index.ts                # 导出
    ├── queries.ts              # Query 工具（list_funds, get_fund_detail）
    └── actions.ts              # Action 工具（create/update/enable/disable）
```

---

## 实现步骤

### Step 1：扩展类型定义

**文件**: `web/lib/agent/tools/types.ts`

```typescript
// 工具执行结果
export type ToolResult =
  | { status: 'success'; data: unknown }
  | { status: 'pending_confirmation'; message: string; formData?: unknown }
  | { status: 'error'; error: string };

// 双语描述
export interface BilingualText {
  zh: string;
  en: string;
}

// 工具定义（纯定义）
export interface ToolDefinition<T extends z.ZodType = z.ZodType> {
  name: string;
  category: 'query' | 'action';
  description: BilingualText;
  parameters: T;
}

// 适配器接口
export interface ToolAdapter {
  executeQuery: <T>(
    toolName: string,
    params: Record<string, unknown>
  ) => Promise<ToolResult>;

  executeAction: <T>(
    toolName: string,
    params: Record<string, unknown>,
    uiConfig?: UIActionConfig
  ) => Promise<ToolResult>;
}

// UI Action 配置
export interface UIActionConfig {
  navigate: string;              // 目标页面路径
  openModal?: string;            // 打开的弹窗 ID
  formFields: Record<string, string>;  // 参数到表单字段的映射
}
```

### Step 2：创建工具定义

**文件**: `web/lib/agent/tools/definitions/fund.ts`

```typescript
import { z } from 'zod';
import type { ToolDefinition } from '../types';

export const fundToolDefinitions = {
  list_funds: {
    name: 'list_funds',
    category: 'query',
    description: {
      zh: '查询基金列表，可按名称筛选',
      en: 'List funds, optionally filter by name',
    },
    parameters: z.object({
      fundName: z.string().optional().describe('按名称模糊搜索'),
      activeOnly: z.boolean().optional().describe('只显示启用的基金'),
    }),
  } satisfies ToolDefinition,

  get_fund_detail: {
    name: 'get_fund_detail',
    category: 'query',
    description: {
      zh: '获取指定基金的详细信息',
      en: 'Get details of a specific fund',
    },
    parameters: z.object({
      fundId: z.number().describe('基金 ID'),
    }),
  } satisfies ToolDefinition,

  create_fund: {
    name: 'create_fund',
    category: 'action',
    description: {
      zh: '创建新基金',
      en: 'Create a new fund',
    },
    parameters: z.object({
      fundName: z.string().describe('基金名称'),
      remarks: z.string().optional().describe('备注'),
    }),
    uiConfig: {
      navigate: '/pms-admin/master-data/fund',
      openModal: 'fund-form',
      formFields: {
        fundName: 'fundName',
        remarks: 'remarks',
      },
    },
  } satisfies ToolDefinition,

  update_fund: {
    name: 'update_fund',
    category: 'action',
    description: {
      zh: '更新基金信息',
      en: 'Update fund information',
    },
    parameters: z.object({
      fundId: z.number().describe('基金 ID'),
      fundName: z.string().optional().describe('新的基金名称'),
      remarks: z.string().optional().describe('新的备注'),
    }),
    uiConfig: {
      navigate: '/pms-admin/master-data/fund',
      openModal: 'fund-form',
      formFields: {
        fundId: 'fundId',
        fundName: 'fundName',
        remarks: 'remarks',
      },
    },
  } satisfies ToolDefinition,

  enable_fund: {
    name: 'enable_fund',
    category: 'action',
    description: {
      zh: '启用基金',
      en: 'Enable a fund',
    },
    parameters: z.object({
      fundId: z.number().describe('基金 ID'),
    }),
  } satisfies ToolDefinition,

  disable_fund: {
    name: 'disable_fund',
    category: 'action',
    description: {
      zh: '停用基金（软删除）',
      en: 'Disable a fund (soft delete)',
    },
    parameters: z.object({
      fundId: z.number().describe('基金 ID'),
    }),
  } satisfies ToolDefinition,
};
```

### Step 3：实现 Standalone 适配器

**文件**: `web/lib/agent/tools/adapters/standalone.ts`

```typescript
import { getPmsSdkClient, pmsPost } from '@/lib/pms-auth/context';
import type { ToolAdapter, ToolResult } from '../types';

export function createStandaloneAdapter(): ToolAdapter {
  return {
    executeQuery: async (toolName, params) => {
      // Query 直接调用 API
      switch (toolName) {
        case 'list_funds':
          return await listFundsApi(params);
        case 'get_fund_detail':
          return await getFundDetailApi(params);
        default:
          return { status: 'error', error: `Unknown query: ${toolName}` };
      }
    },

    executeAction: async (toolName, params) => {
      // Action 返回确认消息，等待用户确认后执行
      switch (toolName) {
        case 'create_fund':
          return {
            status: 'pending_confirmation',
            message: `即将创建基金「${params.fundName}」，请确认是否继续？`,
            formData: params,
          };
        case 'update_fund':
          return {
            status: 'pending_confirmation',
            message: `即将更新基金 #${params.fundId}，请确认是否继续？`,
            formData: params,
          };
        // ... 其他 action
      }
    },
  };
}

// API 实现
async function listFundsApi(params: { fundName?: string; activeOnly?: boolean }) {
  const criteria: Record<string, unknown> = {};
  if (params.fundName) {
    criteria.fundName = { like: `%${params.fundName}%` };
  }
  if (params.activeOnly) {
    criteria.activeStatus = { eq: 'ENABLE' };
  }

  const result = await pmsPost('/pms-service/fund/list-paged', {
    page: 0,
    pageSize: 100,
    criteria,
  });

  return { status: 'success', data: result };
}
```

### Step 4：实现 Embedded 适配器

**文件**: `web/lib/agent/tools/adapters/embedded.ts`

```typescript
import type { ToolAdapter, ToolResult, UIActionConfig } from '../types';

export function createEmbeddedAdapter(
  sendUIAction: (action: UIAction) => Promise<unknown>
): ToolAdapter {
  return {
    executeQuery: async (toolName, params) => {
      // Query 同样直接调 API（不需要 UI 操作）
      // 复用 standalone 的逻辑
      return standaloneAdapter.executeQuery(toolName, params);
    },

    executeAction: async (toolName, params, uiConfig) => {
      if (!uiConfig) {
        return { status: 'error', error: 'Missing UI config for embedded mode' };
      }

      // 1. 导航到目标页面
      await sendUIAction({ type: 'navigate', path: uiConfig.navigate });

      // 2. 打开弹窗
      if (uiConfig.openModal) {
        await sendUIAction({ type: 'openModal', modalId: uiConfig.openModal });
      }

      // 3. 填充表单
      const formValues: Record<string, unknown> = {};
      for (const [paramKey, fieldKey] of Object.entries(uiConfig.formFields)) {
        if (params[paramKey] !== undefined) {
          formValues[fieldKey] = params[paramKey];
        }
      }
      await sendUIAction({ type: 'fillForm', fields: formValues });

      // 4. 返回等待确认状态
      return {
        status: 'pending_confirmation',
        message: '表单已预填，请确认后点击提交按钮',
        formData: params,
      };
    },
  };
}
```

### Step 5：更新工具工厂

**文件**: `web/lib/agent/tools/index.ts`

```typescript
export function createAgentTools(options: ToolFactoryOptions): ToolSet {
  const { locale, entryPoint, mode } = options;

  // 1. 选择适配器
  const adapter = entryPoint === 'standalone'
    ? createStandaloneAdapter()
    : createEmbeddedAdapter(sendUIAction);

  // 2. 创建业务工具
  const fundTools = createFundTools(locale, adapter);

  // 3. 合并所有工具
  let allTools = {
    ...createUIStateTools(locale, options),  // 通用 UI 工具
    ...fundTools,                             // 基金业务工具
  };

  // 4. 根据模式过滤
  return filterToolsByMode(allTools, mode);
}
```

### Step 6：更新前端页面支持 Agent 操作

**文件**: `web/app/[locale]/pms-admin/master-data/fund/page.tsx`

需要：
1. 监听 PartyKit 的 UI 指令
2. 支持 Agent 打开弹窗、填充表单
3. 暴露表单状态给 Agent 读取

---

## 关键修改文件

| 文件 | 操作 | 说明 |
|------|------|------|
| `web/lib/agent/tools/types.ts` | 修改 | 添加适配器类型 |
| `web/lib/agent/tools/definitions/fund.ts` | 新增 | 基金工具定义 |
| `web/lib/agent/tools/adapters/standalone.ts` | 新增 | Standalone 适配器 |
| `web/lib/agent/tools/adapters/embedded.ts` | 新增 | Embedded 适配器 |
| `web/lib/agent/tools/fund/index.ts` | 新增 | 基金工具组装 |
| `web/lib/agent/tools/index.ts` | 修改 | 整合适配器和新工具 |
| `web/app/[locale]/pms-admin/master-data/fund/page.tsx` | 修改 | 支持 Agent UI 操作 |

---

## 验证场景

### Standalone 模式

```
用户: 帮我创建一个叫 Alpha 的基金
Agent: 调用 create_fund({ fundName: "Alpha" })
       返回: { status: 'pending_confirmation', message: '即将创建基金「Alpha」...' }
Agent: 我将为您创建基金「Alpha」，请确认是否继续？
用户: 确认
Agent: 调用 API 创建
Agent: 基金「Alpha」创建成功，ID 为 123
```

### Embedded 模式

```
用户: 帮我创建一个叫 Alpha 的基金
Agent: 调用 create_fund({ fundName: "Alpha" })
       → 导航到 /pms-admin/master-data/fund
       → 打开创建弹窗
       → 填充 fundName = "Alpha"
       返回: { status: 'pending_confirmation', message: '表单已预填...' }
Agent: 已打开创建基金表单并填入名称「Alpha」，请确认后点击创建按钮
用户: (在 UI 上点击创建)
前端: 发送确认事件
Agent: 基金「Alpha」创建成功
```
