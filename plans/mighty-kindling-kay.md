# PMS Admin 聊天面板：新建对话 + 历史对话功能

## 需求概述

在 PMS Admin 右侧聊天面板的 header 上新增两个功能按钮：
1. **+ 图标**：点击创建新对话
2. **时间图标**：点击展示历史对话列表

## 现有架构分析

### 关键文件

| 文件 | 作用 |
|------|------|
| [ai-chat-panel.tsx](web/components/pms-admin/ai-chat-panel.tsx) | 主面板组件，包含 header |
| [chat-interface.tsx](web/components/chat/chat-interface.tsx) | 聊天界面，消息列表 + 输入框 |
| [/api/conversations](web/app/api/conversations/route.ts) | 对话列表/创建 API |
| [/api/conversations/[id]](web/app/api/conversations/[id]/route.ts) | 单个对话管理 API |
| [chat-storage](web/lib/chat-storage/index.ts) | 对话存储 SDK |

### 现有 API

- `GET /api/conversations` - 获取对话列表（支持分页）
- `POST /api/conversations` - 创建新对话
- `GET /api/conversations/:id` - 获取对话详情
- `DELETE /api/conversations/:id` - 删除对话

### 当前状态管理

```typescript
// ai-chat-panel.tsx
const [conversationId] = React.useState(() => nanoid()); // 每次挂载生成新 ID
```

---

## 实施计划

### Step 1: 修改 AiChatPanel 状态管理

**文件**: [web/components/pms-admin/ai-chat-panel.tsx](web/components/pms-admin/ai-chat-panel.tsx)

将 `conversationId` 从一次性状态改为可切换状态：

```typescript
// 改为可变状态
const [conversationId, setConversationId] = React.useState(() => nanoid());

// 新增：历史对话面板状态
const [isHistoryOpen, setIsHistoryOpen] = React.useState(false);
```

### Step 2: 添加 Header 按钮

**文件**: [web/components/pms-admin/ai-chat-panel.tsx](web/components/pms-admin/ai-chat-panel.tsx)

在 header 右侧添加两个图标按钮：

```tsx
import { PlusIcon, HistoryIcon } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';

// 在 header div 内添加右侧按钮组
<div className="flex items-center gap-1">
  <Tooltip>
    <TooltipTrigger asChild>
      <Button variant="ghost" size="icon" className="h-8 w-8" onClick={handleNewConversation}>
        <PlusIcon className="h-4 w-4" />
      </Button>
    </TooltipTrigger>
    <TooltipContent>新建对话</TooltipContent>
  </Tooltip>

  <Tooltip>
    <TooltipTrigger asChild>
      <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => setIsHistoryOpen(true)}>
        <HistoryIcon className="h-4 w-4" />
      </Button>
    </TooltipTrigger>
    <TooltipContent>历史对话</TooltipContent>
  </Tooltip>
</div>
```

### Step 3: 实现新建对话功能

**文件**: [web/components/pms-admin/ai-chat-panel.tsx](web/components/pms-admin/ai-chat-panel.tsx)

```typescript
const handleNewConversation = React.useCallback(() => {
  // 生成新的对话 ID
  const newId = nanoid();
  setConversationId(newId);
  conversationIdRef.current = newId;

  // 重置 useChat 状态（清空消息）
  // 需要调用 useChat 的 setMessages([]) 或重新初始化
}, []);
```

**关键点**：需要重置 `useChat` 的消息状态。方案：
- 将 `useChat` 的返回值中的 `setMessages` 传递进来
- 或者使用 `key` 属性强制重新挂载 `ChatInterface`

### Step 4: 创建历史对话组件

**新文件**: `web/components/pms-admin/conversation-history.tsx`

使用 Sheet 组件展示历史对话列表：

```tsx
'use client';

import * as React from 'react';
import { Sheet, SheetContent, SheetHeader, SheetTitle } from '@/components/ui/sheet';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Button } from '@/components/ui/button';
import { Trash2Icon, MessageSquareIcon } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { zhCN } from 'date-fns/locale';
import type { Conversation } from '@/lib/chat-storage/types';

interface ConversationHistoryProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  currentConversationId?: string;
  onSelectConversation: (conversation: Conversation) => void;
  onDeleteConversation: (id: string) => void;
}

export function ConversationHistory({
  open,
  onOpenChange,
  currentConversationId,
  onSelectConversation,
  onDeleteConversation,
}: ConversationHistoryProps) {
  const [conversations, setConversations] = React.useState<Conversation[]>([]);
  const [isLoading, setIsLoading] = React.useState(false);

  // 加载对话列表
  React.useEffect(() => {
    if (open) {
      fetchConversations();
    }
  }, [open]);

  const fetchConversations = async () => {
    setIsLoading(true);
    try {
      const res = await fetch('/api/conversations?limit=50');
      const data = await res.json();
      setConversations(data.conversations || []);
    } catch (error) {
      console.error('Failed to fetch conversations:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="right" className="w-[320px]">
        <SheetHeader>
          <SheetTitle>历史对话</SheetTitle>
        </SheetHeader>
        <ScrollArea className="h-[calc(100vh-120px)] mt-4">
          {isLoading ? (
            <div className="text-center text-muted-foreground py-8">加载中...</div>
          ) : conversations.length === 0 ? (
            <div className="text-center text-muted-foreground py-8">暂无历史对话</div>
          ) : (
            <div className="space-y-2">
              {conversations.map((conv) => (
                <ConversationItem
                  key={conv.id}
                  conversation={conv}
                  isActive={conv.id === currentConversationId}
                  onSelect={() => onSelectConversation(conv)}
                  onDelete={() => onDeleteConversation(conv.id)}
                />
              ))}
            </div>
          )}
        </ScrollArea>
      </SheetContent>
    </Sheet>
  );
}

// 单个对话项
function ConversationItem({ conversation, isActive, onSelect, onDelete }) {
  return (
    <div
      className={cn(
        'flex items-center justify-between p-3 rounded-lg cursor-pointer hover:bg-accent',
        isActive && 'bg-accent'
      )}
      onClick={onSelect}
    >
      <div className="flex items-center gap-3 min-w-0">
        <MessageSquareIcon className="h-4 w-4 shrink-0 text-muted-foreground" />
        <div className="min-w-0">
          <p className="text-sm font-medium truncate">
            {conversation.title || '新对话'}
          </p>
          <p className="text-xs text-muted-foreground">
            {formatDistanceToNow(new Date(conversation.updatedAt), {
              addSuffix: true,
              locale: zhCN,
            })}
          </p>
        </div>
      </div>
      <Button
        variant="ghost"
        size="icon"
        className="h-8 w-8 shrink-0"
        onClick={(e) => {
          e.stopPropagation();
          onDelete();
        }}
      >
        <Trash2Icon className="h-4 w-4" />
      </Button>
    </div>
  );
}
```

### Step 5: 实现对话切换功能

**文件**: [web/components/pms-admin/ai-chat-panel.tsx](web/components/pms-admin/ai-chat-panel.tsx)

切换对话时需要：
1. 更新 `conversationId`
2. 加载该对话的历史消息
3. 重置 `useChat` 状态

```typescript
const handleSelectConversation = React.useCallback(async (conversation: Conversation) => {
  // 1. 更新对话 ID
  setConversationId(conversation.id);
  conversationIdRef.current = conversation.id;

  // 2. 加载历史消息
  const res = await fetch(`/api/conversations/${conversation.id}/messages`);
  const { messages: historyMessages } = await res.json();

  // 3. 设置消息（需要从 useChat 获取 setMessages）
  setMessages(historyMessages);

  // 4. 关闭历史面板
  setIsHistoryOpen(false);
}, [setMessages]);
```

### Step 6: 实现删除对话功能

```typescript
const handleDeleteConversation = React.useCallback(async (id: string) => {
  try {
    await fetch(`/api/conversations/${id}`, { method: 'DELETE' });

    // 如果删除的是当前对话，创建新对话
    if (id === conversationId) {
      handleNewConversation();
    }
  } catch (error) {
    console.error('Failed to delete conversation:', error);
  }
}, [conversationId, handleNewConversation]);
```

### Step 7: 更新 useChat 集成

需要从 `useChat` 获取 `setMessages` 方法：

```typescript
const { messages, sendMessage, status, setMessages } = useChat({ transport });
```

---

## 文件变更清单

| 文件 | 操作 | 说明 |
|------|------|------|
| [web/components/pms-admin/ai-chat-panel.tsx](web/components/pms-admin/ai-chat-panel.tsx) | 修改 | 添加状态管理、header 按钮、对话切换逻辑 |
| `web/components/pms-admin/conversation-history.tsx` | 新建 | 历史对话 Sheet 组件 |

---

## UI 设计

```
┌─────────────────────────────────────┐
│  PMS 助手  [已连接]     [+] [🕐]    │  ← Header 右侧新增按钮
├─────────────────────────────────────┤
│                                     │
│     (消息列表)                       │
│                                     │
├─────────────────────────────────────┤
│  [输入框...]              [发送]    │
└─────────────────────────────────────┘

点击 🕐 后弹出 Sheet:
┌──────────────────┐
│  历史对话        │
├──────────────────┤
│ 📝 对账差异分析   │
│    2分钟前       │
├──────────────────┤
│ 📝 晨会巡检      │
│    1小时前       │
├──────────────────┤
│ 📝 新对话        │
│    昨天         │
└──────────────────┘
```

---

## 实施顺序

1. **Step 1-2**: 修改 AiChatPanel 添加 header 按钮（视觉可见）
2. **Step 3**: 实现新建对话功能
3. **Step 4**: 创建 ConversationHistory 组件
4. **Step 5-6**: 实现对话切换和删除功能
5. **Step 7**: 集成 useChat 的 setMessages

## 依赖检查

- [x] `lucide-react` - PlusIcon, HistoryIcon ✅
- [x] `@/components/ui/sheet` - Sheet 组件 ✅
- [x] `@/components/ui/tooltip` - Tooltip 组件
- [x] `date-fns` - 时间格式化
- [x] `/api/conversations` - API 已存在 ✅
