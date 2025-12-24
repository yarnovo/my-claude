# Agent 响应等待时间测量系统

## 核心指标

**用户等待时间 = 点击发送 → 看到第一个回复字符**

这是用户体验最直接感知的指标。

---

## 测量点

```
用户点击发送 (sendTime)
      ↓
网络请求发出
      ↓
服务端处理
      ↓
第一个字符返回 (firstResponseTime)
      ↓
等待时间 = firstResponseTime - sendTime
```

---

## 1. 前端测量实现

**文件**: `web/app/[locale]/chat/[id]/page.tsx`

### 1.1 添加时间追踪状态

```typescript
// 等待时间追踪
const [waitingStartTime, setWaitingStartTime] = useState<number | null>(null);
const [lastWaitTime, setLastWaitTime] = useState<number | null>(null);
```

### 1.2 在发送时记录开始时间

```typescript
const handleSubmit = useCallback((message: PromptInputMessage) => {
  setWaitingStartTime(Date.now()); // 记录发送时间
  sendMessage({
    text: message.text || '',
    files: message.files,
  });
}, [sendMessage]);
```

### 1.3 监听 messages 变化，计算等待时间

```typescript
useEffect(() => {
  // 当有新的 assistant 消息出现时
  if (waitingStartTime && messages.length > 0) {
    const lastMessage = messages[messages.length - 1];
    if (lastMessage.role === 'assistant') {
      const waitTime = Date.now() - waitingStartTime;
      setLastWaitTime(waitTime);
      setWaitingStartTime(null);

      // 上报到服务端
      reportWaitTime(conversationId, waitTime);
    }
  }
}, [messages, waitingStartTime, conversationId]);
```

### 1.4 上报函数

```typescript
async function reportWaitTime(conversationId: string, waitTimeMs: number) {
  try {
    await fetch('/api/admin/performance', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        conversationId,
        waitTimeMs,
        timestamp: new Date().toISOString(),
      }),
    });
  } catch (e) {
    // 静默失败，不影响用户体验
  }
}
```

---

## 2. 数据库设计

**文件**: `web/db/schema.ts`

```typescript
export const waitTimeMetrics = pgTable(
  'wait_time_metrics',
  {
    id: text('id').primaryKey(),
    conversationId: text('conversation_id').references(() => conversations.id),
    waitTimeMs: integer('wait_time_ms').notNull(),  // 等待时间（毫秒）
    createdAt: timestamp('created_at', { withTimezone: true }).defaultNow(),
  },
  (table) => [
    index('idx_wait_time_created_at').on(table.createdAt),
    index('idx_wait_time_conversation').on(table.conversationId),
  ]
);
```

简化设计：只存储**等待时间**这一个核心指标。

---

## 3. 性能 API

**新文件**: `web/app/api/admin/performance/route.ts`

### POST - 记录等待时间

```typescript
export async function POST(request: Request) {
  const { conversationId, waitTimeMs } = await request.json();

  await db.insert(waitTimeMetrics).values({
    id: nanoid(),
    conversationId,
    waitTimeMs,
  });

  return NextResponse.json({ success: true });
}
```

### GET - 查询统计

```typescript
export async function GET(request: Request) {
  const url = new URL(request.url);
  const days = parseInt(url.searchParams.get('days') || '7');

  // 查询最近 N 天的数据
  const metrics = await db.select()
    .from(waitTimeMetrics)
    .where(gte(waitTimeMetrics.createdAt, subDays(new Date(), days)))
    .orderBy(desc(waitTimeMetrics.createdAt));

  // 计算统计值
  const waitTimes = metrics.map(m => m.waitTimeMs);

  return NextResponse.json({
    count: waitTimes.length,
    avg: average(waitTimes),
    min: Math.min(...waitTimes),
    max: Math.max(...waitTimes),
    p50: percentile(waitTimes, 50),
    p90: percentile(waitTimes, 90),
    p95: percentile(waitTimes, 95),
    recent: metrics.slice(0, 20), // 最近 20 条
  });
}
```

---

## 4. Admin Dashboard 展示

**新文件**: `web/app/[locale]/admin/performance/page.tsx`

### 展示内容

1. **核心指标卡片**
   - 平均等待时间
   - P90 等待时间（90% 的请求在这个时间内响应）
   - 最慢响应
   - 样本数量

2. **最近请求列表**
   - 时间
   - 等待时间（毫秒）
   - 对话 ID（可点击查看）

3. **简单分布**
   - <2s: 优秀
   - 2-5s: 良好
   - 5-10s: 较慢
   - >10s: 需优化

---

## 5. 文件清单

| 文件 | 操作 | 说明 |
|-----|------|------|
| `web/db/schema.ts` | 修改 | 添加 waitTimeMetrics 表 |
| `web/app/[locale]/chat/[id]/page.tsx` | 修改 | 添加等待时间测量和上报 |
| `web/app/api/admin/performance/route.ts` | 新增 | 等待时间 API |
| `web/app/[locale]/admin/performance/page.tsx` | 新增 | 性能监控页面 |
| `web/app/[locale]/admin/layout.tsx` | 修改 | 添加导航链接 |

---

## 6. 实施步骤

### Step 1: 数据库
1. 在 `schema.ts` 添加 `waitTimeMetrics` 表
2. 运行 `npm run db:push`

### Step 2: 前端测量
1. 修改 `page.tsx` 添加时间追踪
2. 添加上报函数

### Step 3: 后端 API
1. 创建 `/api/admin/performance` 端点
2. 实现 POST（记录）和 GET（查询）

### Step 4: Dashboard
1. 创建性能监控页面
2. 展示统计数据

### Step 5: 测试验证
1. 发送测试消息
2. 确认数据被记录
3. 查看 Dashboard 展示

---

## 7. 可选：UI 实时显示

在聊天界面底部显示上次等待时间（调试用）：

```typescript
{lastWaitTime && (
  <div className="text-xs text-gray-400 text-center">
    等待时间: {(lastWaitTime / 1000).toFixed(1)}s
  </div>
)}
```

---

## 8. 优化目标参考

| 等级 | 等待时间 | 用户感受 |
|-----|---------|---------|
| 优秀 | <2s | 流畅 |
| 良好 | 2-5s | 可接受 |
| 较慢 | 5-10s | 需等待 |
| 差 | >10s | 需优化 |

---

## 不修改的内容

- 不改服务端逻辑
- 不改 AI 配置
- 不做任何优化
- 只做测量和展示
