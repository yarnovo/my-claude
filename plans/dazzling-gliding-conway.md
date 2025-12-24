# 从 pms-agent 提取移动端聊天 UI 组件到 ai-widget

## 概述

从 pms-agent 项目提取完整的移动端聊天 UI 组件（左侧菜单栏 + 右侧对话区域），通用化后放入 ai-widget 项目中。

## 组件分配

### @ai-widget/ui (基础 UI 组件)
| 组件 | 说明 |
|------|------|
| InputGroup | 输入框分组组件 |
| Command | 命令面板组件 (shadcn/ui) |
| Select | 下拉选择器 (shadcn/ui) |
| Textarea | 多行文本框 (shadcn/ui) |
| HoverCard | 悬浮卡片 (shadcn/ui) |

### @ai-widget/ai-elements (AI 元素组件)
| 组件 | 说明 |
|------|------|
| PromptInput | 消息输入框（含附件、发送按钮等） |
| ModelSelector | AI 模型选择器 |
| Reasoning | AI 推理过程展示 |
| Sources | 来源引用展示 |
| Tool | 工具调用展示 |

### @ai-widget/chat-ui (聊天应用组件)
| 组件 | 说明 |
|------|------|
| MessageList | 消息列表渲染 |
| ChatInterface | 聊天界面（消息列表 + 输入框） |
| ChatPage | 完整聊天页面（侧边栏 + 聊天界面） |

## 关键通用化设计

### ChatPage Props 接口

```typescript
export interface ChatPageProps {
  /** 初始对话 ID（来自路由） */
  initialConversationId?: string | null;
  /** 基础路径（用于 URL 更新） */
  basePath?: string;
  /** 自定义 header 内容 */
  header?: ReactNode;
  /** 自定义 footer 内容 */
  footer?: ReactNode;
  /** 对话切换回调（用于更新 URL） */
  onConversationChange?: (conversationId: string | null) => void;
  /** 新对话创建回调 */
  onNewConversation?: (conversationId: string) => void;
}
```

### 依赖抽象（通过 Context）

| 原始依赖 | 通用化方式 |
|---------|-----------|
| `useParams()` (Next.js) | `initialConversationId` prop |
| `useLocale()` (next-intl) | `useI18n().locale` |
| `useTranslations()` (next-intl) | `useI18n().t()` |
| `useUser()` (Clerk) | `useAuth().user` |
| `useClerk().signOut()` | `useAuth().signOut()` |
| `SUPPORTED_MODELS` 常量 | `useModels()` |

## 实现步骤

### 阶段 1: @ai-widget/ui 添加基础组件

1. 新建 `/packages/ui/src/input-group.tsx`
2. 新建 `/packages/ui/src/command.tsx`
3. 新建 `/packages/ui/src/select.tsx`
4. 新建 `/packages/ui/src/textarea.tsx`
5. 新建 `/packages/ui/src/hover-card.tsx`
6. 更新 `/packages/ui/src/index.ts` 导出
7. 更新 `/packages/ui/package.json` 添加依赖

### 阶段 2: @ai-widget/ai-elements 添加 AI 组件

1. 新建 `/packages/ai-elements/src/prompt-input.tsx`
2. 新建 `/packages/ai-elements/src/model-selector.tsx`
3. 新建 `/packages/ai-elements/src/reasoning.tsx`
4. 新建 `/packages/ai-elements/src/sources.tsx`
5. 新建 `/packages/ai-elements/src/tool.tsx`
6. 更新 `/packages/ai-elements/src/index.ts` 导出
7. 更新 `/packages/ai-elements/package.json` 添加依赖

### 阶段 3: @ai-widget/chat-ui 添加聊天组件

1. 新建 `/packages/chat-ui/src/message-list.tsx`
2. 新建 `/packages/chat-ui/src/chat-interface.tsx`
3. 新建 `/packages/chat-ui/src/chat-page.tsx`
4. 更新 `/packages/chat-ui/src/index.ts` 导出
5. 更新 `/packages/chat-ui/package.json` 添加依赖

### 阶段 4: 测试和文档

1. 为新组件创建 Storybook stories
2. 运行构建和类型检查

## 依赖关系

```
@ai-widget/types
    ↓
@ai-widget/utils
    ↓
@ai-widget/ui (+ InputGroup, Command, Select, Textarea, HoverCard)
    ↓
@ai-widget/ai-elements (+ PromptInput, ModelSelector, Reasoning, Sources, Tool)
    ↓
@ai-widget/chat-store
    ↓
@ai-widget/react
    ↓
@ai-widget/chat-ui (+ MessageList, ChatInterface, ChatPage)
```

## 关键源文件参考

- `pms-agent/web/components/chat/standalone/chat-page.tsx`
- `pms-agent/web/components/chat/standalone/chat-interface.tsx`
- `pms-agent/web/components/chat/shared/message-list.tsx`
- `pms-agent/web/components/ai-elements/prompt-input.tsx`
- `pms-agent/web/components/ai-elements/model-selector.tsx`
- `pms-agent/web/components/ai-elements/reasoning.tsx`
- `pms-agent/web/components/ai-elements/sources.tsx`
- `pms-agent/web/components/ai-elements/tool.tsx`
- `pms-agent/web/components/ui/input-group.tsx`
