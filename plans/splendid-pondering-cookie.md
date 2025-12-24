# AI Widget 聊天 UI 提取计划

## 目标

将 pms-agent 的聊天 UI 功能（左侧对话列表 + 右侧聊天界面）提取到 ai-widget monorepo，使 loan 项目也能复用。

## 确认的设计决策

- **UI 组件**: 创建独立 `@ai-widget/ui` 包，内置 shadcn/ui 组件
- **API 策略**: 只提供接口定义，消费者自行实现
- **渲染模式**: 仅客户端渲染，无需 SSR 支持
- **React 版本**: 升级到 React 19

---

## 包结构设计

```
ai-widget/
├── packages/
│   ├── types/          # 已有 → 扩展 AI 相关类型
│   ├── utils/          # 已有 → 扩展时间分组等工具
│   ├── core/           # 已有 → 保持不变
│   ├── ui/             # 新增 → shadcn/ui 基础组件
│   ├── ai-elements/    # 新增 → AI 原子组件
│   ├── chat-store/     # 新增 → Zustand 状态管理
│   ├── chat-ui/        # 新增 → 聊天业务组件
│   └── react/          # 新增 → Provider 和 Hooks
```

### 包依赖关系

```
types ─────────────────────────────────────┐
  │                                        │
  ├── utils                                │
  │     │                                  │
  ├── ui ───────────────────┐              │
  │     │                   │              │
  │     └── ai-elements ────┤              │
  │           │             │              │
  ├── chat-store ───────────┤              │
  │           │             │              │
  │           └── chat-ui ──┴── react ─────┘
```

---

## Phase 1: 扩展基础包

### 1.1 扩展 `@ai-widget/types`

**文件**: `packages/types/src/index.ts`

新增类型：
```typescript
// 用户信息
export interface ChatUserInfo {
  id?: string;
  email?: string;
  firstName?: string;
  lastName?: string;
  imageUrl?: string;
  fullName?: string;
}

// 对话摘要
export interface ConversationSummary {
  id: string;
  title: string;
  updatedAt: string;
  createdAt: string;
}

// 工具批准响应
export interface ToolApprovalResponse {
  id: string;
  approved: boolean;
  reason?: string;
}

// Agent 模式
export type AgentMode = 'ask' | 'exec';

// 国际化适配器
export interface I18nAdapter {
  t: (key: string, params?: Record<string, string | number>) => string;
  locale: string;
}

// 认证适配器
export interface AuthAdapter {
  user: ChatUserInfo | null;
  isLoading: boolean;
  signOut: () => void | Promise<void>;
}

// 对话 API 适配器（消费者实现）
export interface ConversationApiAdapter {
  fetchConversations: (params: { limit: number; cursor?: string }) => Promise<{
    conversations: ConversationSummary[];
    hasMore: boolean;
  }>;
  fetchMessages: (conversationId: string) => Promise<{
    messages: UIMessage[];
    title?: string;
  }>;
  deleteConversation: (id: string) => Promise<void>;
}

// 模型配置
export interface ModelConfig {
  id: string;
  name: string;
  provider: string;
  providerSlug: string;
}
```

### 1.2 扩展 `@ai-widget/utils`

**文件**: `packages/utils/src/index.ts`

新增工具函数：
```typescript
// 时间分组（用于对话列表）
export function groupByTime<T>(
  items: T[],
  getDate: (item: T) => Date,
  options: { locale: string }
): Array<{ label: string; items: T[] }>;

// 消息格式转换（UIMessage → MessageType）
export function convertToMessageType(message: UIMessage): MessageType;
```

---

## Phase 2: 创建 `@ai-widget/ui`

**路径**: `packages/ui/`

从 pms-agent 提取 shadcn/ui 组件：

### 核心组件列表

| 组件 | 来源 |
|------|------|
| Button, ButtonGroup | `/web/components/ui/button.tsx` |
| Badge | `/web/components/ui/badge.tsx` |
| Collapsible | `/web/components/ui/collapsible.tsx` |
| DropdownMenu | `/web/components/ui/dropdown-menu.tsx` |
| HoverCard | `/web/components/ui/hover-card.tsx` |
| Input, InputGroup | `/web/components/ui/input.tsx`, `input-group.tsx` |
| Select | `/web/components/ui/select.tsx` |
| Tabs | `/web/components/ui/tabs.tsx` |
| Tooltip | `/web/components/ui/tooltip.tsx` |
| Skeleton | `/web/components/ui/skeleton.tsx` |
| Command | `/web/components/ui/command.tsx` |
| Dialog | `/web/components/ui/dialog.tsx` |
| Avatar | `/web/components/ui/avatar.tsx` |
| Sidebar 全套 | `/web/components/ui/sidebar.tsx` |

### 依赖

```json
{
  "dependencies": {
    "@radix-ui/react-avatar": "^1.1.2",
    "@radix-ui/react-collapsible": "^1.1.2",
    "@radix-ui/react-dialog": "^1.1.4",
    "@radix-ui/react-dropdown-menu": "^2.1.4",
    "@radix-ui/react-hover-card": "^1.1.4",
    "@radix-ui/react-select": "^2.1.4",
    "@radix-ui/react-tabs": "^1.1.2",
    "@radix-ui/react-tooltip": "^1.1.6",
    "@radix-ui/react-slot": "^1.1.1",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.2.0",
    "cmdk": "^1.0.0"
  },
  "peerDependencies": {
    "react": "^19.0.0",
    "react-dom": "^19.0.0"
  }
}
```

### 导出 Tailwind Preset

```typescript
// packages/ui/src/tailwind-preset.ts
export const tailwindPreset = {
  theme: {
    extend: {
      // CSS 变量配置
    }
  }
};
```

---

## Phase 3: 创建 `@ai-widget/ai-elements`

**路径**: `packages/ai-elements/`

从 pms-agent 提取 AI 组件：

### 组件列表

| 组件 | 来源 | 说明 |
|------|------|------|
| Conversation | `conversation.tsx` | 对话容器，自动滚动 |
| Message | `message.tsx` | 消息展示，分支支持 |
| PromptInput | `prompt-input.tsx` | 输入框，附件支持 |
| Tool | `tool.tsx` | 工具调用展示 |
| Reasoning | `reasoning.tsx` | 推理过程 |
| Sources | `sources.tsx` | 来源引用 |
| Suggestion | `suggestion.tsx` | 建议按钮 |
| ModelSelector | `model-selector.tsx` | 模型选择器 |
| CodeBlock | `code-block.tsx` | 代码块 |
| Loader | `loader.tsx` | 加载动画 |
| Shimmer | `shimmer.tsx` | 闪烁效果 |
| Image | `image.tsx` | 图片展示 |

### 依赖

```json
{
  "dependencies": {
    "@ai-widget/ui": "workspace:*",
    "@ai-widget/types": "workspace:*",
    "use-stick-to-bottom": "^1.1.1",
    "streamdown": "^1.6.1",
    "shiki": "^3.15.0",
    "motion": "^12.23.24"
  },
  "peerDependencies": {
    "react": "^19.0.0",
    "lucide-react": "^0.450.0",
    "@ai-sdk/react": "^3.0.0-beta.108"
  }
}
```

---

## Phase 4: 创建 `@ai-widget/chat-store`

**路径**: `packages/chat-store/`

### 核心实现

```typescript
// packages/chat-store/src/store.ts
import { create } from 'zustand';
import type { ConversationApiAdapter, ConversationSummary, AgentMode } from '@ai-widget/types';
import type { UIMessage } from '@ai-sdk/react';

export interface ChatState {
  currentConversationId: string | null;
  currentTitle: string;
  selectedModel: string;
  selectedMode: AgentMode;
  messagesCache: Map<string, UIMessage[]>;
  isLoadingHistory: boolean;
  conversations: ConversationSummary[];
  isLoadingConversations: boolean;
  isLoadingMore: boolean;
  hasMoreConversations: boolean;
  conversationsInitialized: boolean;
}

export interface ChatActions {
  switchConversation: (id: string | null) => void;
  newConversation: () => void;
  setCurrentTitle: (title: string) => void;
  setSelectedModel: (model: string) => void;
  setSelectedMode: (mode: AgentMode) => void;
  cacheMessages: (id: string, messages: UIMessage[]) => void;
  getCachedMessages: (id: string) => UIMessage[] | undefined;
  clearMessagesCache: (id?: string) => void;
  setIsLoadingHistory: (loading: boolean) => void;
  fetchConversations: () => Promise<void>;
  fetchMoreConversations: () => Promise<void>;
  deleteConversation: (id: string) => Promise<void>;
  addConversation: (conv: ConversationSummary) => void;
  updateConversation: (id: string, updates: Partial<ConversationSummary>) => void;
}

export type ChatStore = ChatState & ChatActions;

export function createChatStore(options: {
  defaultModel: string;
  defaultMode?: AgentMode;
  api: ConversationApiAdapter;
}): ReturnType<typeof create<ChatStore>>;
```

### 依赖

```json
{
  "dependencies": {
    "@ai-widget/types": "workspace:*"
  },
  "peerDependencies": {
    "zustand": "^5.0.0",
    "@ai-sdk/react": "^3.0.0-beta.108"
  }
}
```

---

## Phase 5: 创建 `@ai-widget/chat-ui`

**路径**: `packages/chat-ui/`

### 组件列表

| 组件 | 来源 | 说明 |
|------|------|------|
| MessageList | `shared/message-list.tsx` | 消息列表，HITL 支持 |
| ModeSelector | `shared/mode-selector.tsx` | Ask/Exec 模式切换 |
| ChatInterface | `standalone/chat-interface.tsx` | 聊天界面 |
| NavConversations | `standalone/nav-conversations.tsx` | 对话列表 |
| ChatAppSidebar | `standalone/chat-app-sidebar.tsx` | 侧边栏容器 |
| ChatNavUser | `standalone/chat-nav-user.tsx` | 用户菜单 |
| ChatPage | `standalone/chat-page.tsx` | 完整页面 |

### 关键修改

1. **移除 Next.js 依赖**: 使用传入的 props 替代 `useParams`, `useLocale`
2. **移除 Clerk 依赖**: 使用 `AuthAdapter` 接口
3. **移除 next-intl 依赖**: 使用 `I18nAdapter` 接口
4. **移除硬编码配置**: 通过 Context 注入 `models`, `basePath` 等

### 依赖

```json
{
  "dependencies": {
    "@ai-widget/types": "workspace:*",
    "@ai-widget/utils": "workspace:*",
    "@ai-widget/ui": "workspace:*",
    "@ai-widget/ai-elements": "workspace:*",
    "@ai-widget/chat-store": "workspace:*",
    "date-fns": "^4.1.0"
  },
  "peerDependencies": {
    "react": "^19.0.0",
    "lucide-react": "^0.450.0",
    "@ai-sdk/react": "^3.0.0-beta.108",
    "ai": "^6.0.0-beta.108",
    "zustand": "^5.0.0"
  }
}
```

---

## Phase 6: 创建 `@ai-widget/react`

**路径**: `packages/react/`

### Provider 实现

```typescript
// packages/react/src/provider.tsx
import { createContext, useContext } from 'react';
import type { I18nAdapter, AuthAdapter, ConversationApiAdapter, ModelConfig, AgentMode } from '@ai-widget/types';
import { createChatStore } from '@ai-widget/chat-store';

export interface ChatWidgetConfig {
  defaultModel: string;
  defaultMode?: AgentMode;
  models: ModelConfig[];
  basePath?: string;
}

export interface ChatWidgetContextValue {
  i18n: I18nAdapter;
  auth: AuthAdapter;
  api: ConversationApiAdapter;
  config: ChatWidgetConfig;
  store: ReturnType<typeof createChatStore>;
}

const ChatWidgetContext = createContext<ChatWidgetContextValue | null>(null);

export interface ChatWidgetProviderProps {
  children: React.ReactNode;
  i18n: I18nAdapter;
  auth: AuthAdapter;
  api: ConversationApiAdapter;
  config: ChatWidgetConfig;
  logo?: React.ReactNode;
}

export function ChatWidgetProvider(props: ChatWidgetProviderProps): JSX.Element;

// Hooks
export function useChatWidget(): ChatWidgetContextValue;
export function useAuth(): AuthAdapter;
export function useI18n(): I18nAdapter;
export function useModels(): ModelConfig[];
export function useChatConfig(): ChatWidgetConfig;
```

### 适配器工厂（可选）

```typescript
// packages/react/src/adapters.ts

// Clerk 适配器
export function createClerkAdapter(options: {
  useUser: () => { user: any; isLoaded: boolean };
  useClerk: () => { signOut: () => void };
}): AuthAdapter;

// next-intl 适配器
export function createNextIntlAdapter(options: {
  useTranslations: () => (key: string) => string;
  useLocale: () => string;
}): I18nAdapter;

// fetch API 适配器
export function createFetchApiAdapter(options: {
  baseUrl?: string;
  headers?: Record<string, string>;
}): ConversationApiAdapter;
```

---

## 实现顺序

| 阶段 | 任务 | 预估文件数 |
|------|------|-----------|
| **Phase 1** | 扩展 types + utils | ~3 |
| **Phase 2** | 创建 @ai-widget/ui | ~20 |
| **Phase 3** | 创建 @ai-widget/ai-elements | ~15 |
| **Phase 4** | 创建 @ai-widget/chat-store | ~3 |
| **Phase 5** | 创建 @ai-widget/chat-ui | ~10 |
| **Phase 6** | 创建 @ai-widget/react | ~5 |

---

## 关键源文件路径

### pms-agent 源文件

```
/Users/yarnb/tongyu-projects/pms-agent/web/
├── components/
│   ├── chat/
│   │   ├── standalone/
│   │   │   ├── chat-page.tsx
│   │   │   ├── chat-interface.tsx
│   │   │   ├── chat-app-sidebar.tsx
│   │   │   ├── nav-conversations.tsx
│   │   │   └── chat-nav-user.tsx
│   │   └── shared/
│   │       ├── message-list.tsx
│   │       ├── mode-selector.tsx
│   │       └── constants.ts
│   ├── ai-elements/
│   │   ├── conversation.tsx
│   │   ├── message.tsx
│   │   ├── prompt-input.tsx
│   │   ├── tool.tsx
│   │   ├── reasoning.tsx
│   │   ├── sources.tsx
│   │   ├── suggestion.tsx
│   │   ├── model-selector.tsx
│   │   ├── code-block.tsx
│   │   ├── loader.tsx
│   │   └── index.ts
│   └── ui/
│       ├── button.tsx
│       ├── sidebar.tsx
│       ├── dropdown-menu.tsx
│       ├── tabs.tsx
│       └── ... (其他 shadcn 组件)
└── lib/
    └── stores/
        └── chat/
            ├── store.ts
            └── types.ts
```

### ai-widget 目标结构

```
/Users/yarnb/tongyu-projects/ai-widget/
├── packages/
│   ├── types/src/
│   │   └── index.ts          # 扩展
│   ├── utils/src/
│   │   ├── index.ts          # 扩展
│   │   ├── group-by-time.ts  # 新增
│   │   └── message-converter.ts # 新增
│   ├── ui/src/               # 新建
│   │   ├── button.tsx
│   │   ├── sidebar.tsx
│   │   └── ...
│   ├── ai-elements/src/      # 新建
│   │   ├── conversation.tsx
│   │   ├── message.tsx
│   │   └── ...
│   ├── chat-store/src/       # 新建
│   │   ├── store.ts
│   │   └── index.ts
│   ├── chat-ui/src/          # 新建
│   │   ├── message-list.tsx
│   │   ├── chat-interface.tsx
│   │   ├── chat-page.tsx
│   │   └── ...
│   └── react/src/            # 新建
│       ├── provider.tsx
│       ├── hooks.ts
│       ├── adapters.ts
│       └── index.ts
```

---

## 使用示例

### 在 loan 项目中使用

```tsx
// app/providers.tsx
import { ChatWidgetProvider } from '@ai-widget/react';

const i18n = {
  t: (key: string) => translations[key],
  locale: 'zh',
};

const auth = {
  user: currentUser,
  isLoading: false,
  signOut: () => clerk.signOut(),
};

const api = {
  fetchConversations: async ({ limit, cursor }) => {
    const res = await fetch(`/api/conversations?limit=${limit}&cursor=${cursor}`);
    return res.json();
  },
  fetchMessages: async (id) => {
    const res = await fetch(`/api/conversations/${id}/messages`);
    return res.json();
  },
  deleteConversation: async (id) => {
    await fetch(`/api/conversations/${id}`, { method: 'DELETE' });
  },
};

export function Providers({ children }) {
  return (
    <ChatWidgetProvider
      i18n={i18n}
      auth={auth}
      api={api}
      config={{
        defaultModel: 'gpt-4o',
        models: [{ id: 'gpt-4o', name: 'GPT-4o', provider: 'OpenAI', providerSlug: 'openai' }],
        basePath: '/chat',
      }}
    >
      {children}
    </ChatWidgetProvider>
  );
}

// app/chat/page.tsx
import { ChatPage } from '@ai-widget/chat-ui';

export default function ChatRoute() {
  return <ChatPage />;
}
```
