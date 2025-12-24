# 迁移聊天入口组件到 ai-widget

## 目标

将 loan 项目中的聊天入口页面组件抽取为可复用组件，放到 ai-widget 项目中暴露出去。

## 组件分布

| 组件 | 目标包 | 说明 |
|------|--------|------|
| PromptInput 系列 | `@ai-widget/ai-elements` | 输入框核心组件 |
| ChatEntry | `@ai-widget/chat-ui` | 首页入口容器组件 |
| InputGroup 等 UI 组件 | `@ai-widget/ui` | 基础 UI 依赖 |

## 实施步骤

### 阶段 1: 迁移基础 UI 组件到 @ai-widget/ui

**需要迁移的文件:**
- `loan/web/components/ui/textarea.tsx` → `ai-widget/packages/ui/src/textarea.tsx`
- `loan/web/components/ui/input-group.tsx` → `ai-widget/packages/ui/src/input-group.tsx`

**步骤:**
1. 复制 Textarea 组件
2. 复制 InputGroup 组件 (依赖 Button, Input, Textarea)
3. 调整 import 路径为 `@ai-widget/ui` 内部引用
4. 更新 `packages/ui/src/index.ts` 导出

### 阶段 2: 迁移 PromptInput 到 @ai-widget/ai-elements

**源文件:** `/Users/yarnb/tongyu-projects/loan/web/components/ai-elements/prompt-input.tsx` (1378 行)

**目标结构:**
```
packages/ai-elements/src/
├── prompt-input/
│   ├── index.ts           # 导出入口
│   ├── prompt-input.tsx   # 核心组件 + Context
│   ├── attachments.tsx    # 附件相关子组件
│   └── types.ts           # 类型定义
```

**步骤:**
1. 创建 `prompt-input/` 目录
2. 迁移并拆分代码（按功能模块）
3. 修改 import 路径：
   - `@/components/ui/*` → `@ai-widget/ui`
   - `@/lib/utils` → `@ai-widget/ui` 的 cn
4. 去除业务耦合：
   - 移除 `import type { ChatStatus } from "ai"`，定义本地类型
   - 所有文本通过 props 传入，设置合理默认值
5. 添加 `nanoid` 依赖到 ai-elements 包
6. 更新 `packages/ai-elements/src/index.ts` 导出

**导出的组件:**
```typescript
// 核心
PromptInput, PromptInputBody, PromptInputHeader, PromptInputFooter
PromptInputTextarea, PromptInputTools, PromptInputButton, PromptInputSubmit

// 附件
PromptInputAttachments, PromptInputAttachment
PromptInputActionMenu, PromptInputActionMenuTrigger, PromptInputActionMenuContent
PromptInputActionAddAttachments

// Provider (可选)
PromptInputProvider, usePromptInputController

// 类型
type PromptInputMessage, type PromptInputProps
```

### 阶段 3: 创建 ChatEntry 组件到 @ai-widget/chat-ui

**新建文件:** `packages/chat-ui/src/chat-entry.tsx`

**Props 设计:**
```typescript
export type ChatEntryTexts = {
  title?: string
  subtitle?: string
  description?: string
  inputPlaceholder?: string
  footer?: string
}

export type ChatEntryProps = HTMLAttributes<HTMLDivElement> & {
  texts?: ChatEntryTexts
  onSubmit: (message: { text: string; files: FileUIPart[] }) => void | Promise<void>
  headerSlot?: ReactNode  // 可选的顶部插槽（如用户头像、语言切换）
}
```

**步骤:**
1. 创建 ChatEntry 组件，组合 PromptInput
2. 实现响应式布局（居中、全屏高度）
3. 更新 `packages/chat-ui/src/index.ts` 导出

### 阶段 4: Storybook 和测试

1. 创建 `packages/ai-elements/stories/prompt-input.stories.tsx`
2. 创建 `packages/chat-ui/stories/chat-entry.stories.tsx`
3. 运行 `pnpm build` 确保构建通过
4. 运行 `pnpm typecheck` 确保类型正确

## 关键文件

**源文件 (loan):**
- `/Users/yarnb/tongyu-projects/loan/web/app/[locale]/page.tsx`
- `/Users/yarnb/tongyu-projects/loan/web/components/ai-elements/prompt-input.tsx`
- `/Users/yarnb/tongyu-projects/loan/web/components/ui/input-group.tsx`
- `/Users/yarnb/tongyu-projects/loan/web/components/ui/textarea.tsx`

**目标文件 (ai-widget):**
- `/Users/yarnb/tongyu-projects/ai-widget/packages/ui/src/textarea.tsx` (新建)
- `/Users/yarnb/tongyu-projects/ai-widget/packages/ui/src/input-group.tsx` (新建)
- `/Users/yarnb/tongyu-projects/ai-widget/packages/ui/src/index.ts` (修改)
- `/Users/yarnb/tongyu-projects/ai-widget/packages/ai-elements/src/prompt-input/` (新建目录)
- `/Users/yarnb/tongyu-projects/ai-widget/packages/ai-elements/src/index.ts` (修改)
- `/Users/yarnb/tongyu-projects/ai-widget/packages/chat-ui/src/chat-entry.tsx` (新建)
- `/Users/yarnb/tongyu-projects/ai-widget/packages/chat-ui/src/index.ts` (修改)

## 使用示例

```tsx
import { ChatEntry } from '@ai-widget/chat-ui'

function HomePage() {
  const handleSubmit = async (message) => {
    const conversationId = nanoid()
    router.push(`/chat/${conversationId}?initialMessage=${message.text}`)
  }

  return (
    <ChatEntry
      texts={{
        title: "GMCC 顾问",
        subtitle: "Non-QM 贷款智能评估专家",
        inputPlaceholder: "描述您的贷款需求...",
      }}
      onSubmit={handleSubmit}
      headerSlot={<UserButton />}
    />
  )
}
```
