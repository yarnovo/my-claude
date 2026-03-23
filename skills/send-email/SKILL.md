---
name: send-email
description: 发送邮件通知。当用户说"发邮件"、"send email"、"邮件通知"、"notify"等时调用。
allowed-tools: Bash, Read, Glob, Grep, Write, WebFetch
---

通过 AgentMail API 发送邮件。可在任何 Claude Code 项目中复用。

## 配置

需要环境变量（在 .env 或 shell 中设置）：

| 变量 | 必需 | 说明 |
|------|------|------|
| `AGENTMAIL_API_KEY` | 是 | AgentMail API 密钥 |
| `AGENTMAIL_INBOX` | 是 | 发件箱地址（如 `xxx@agentmail.to`） |
| `NOTIFY_EMAIL` | 是 | 默认收件人邮箱 |

## 操作流程

### 1. 确定邮件内容

从用户指令中提取：
- **收件人**：用户指定，或使用 `$NOTIFY_EMAIL`
- **主题**：用户指定
- **正文**：三种来源（按优先级）：
  1. 用户直接给出文本
  2. 用户指定文件路径 → 读取文件内容作为正文
  3. 用户要求生成（如"总结今天的工作发邮件"）→ 先生成内容再发送

### 2. 发送邮件

先将正文写入临时文件，用 jq 构造 JSON 避免转义问题：

```bash
# 加载环境变量
source .env 2>/dev/null || true

# 将正文写入临时文件
BODY_FILE=$(mktemp)
cat > "$BODY_FILE" << 'BODY_EOF'
<正文内容>
BODY_EOF

# 用 jq 构造 JSON（安全处理特殊字符）
PAYLOAD=$(jq -n \
  --arg to "$NOTIFY_EMAIL" \
  --arg subject "<主题>" \
  --arg text "$(cat "$BODY_FILE")" \
  '{to: $to, subject: $subject, text: $text}')

# 发送
curl -s -X POST \
  "https://api.agentmail.to/v0/inboxes/$AGENTMAIL_INBOX/messages/send" \
  -H "Authorization: Bearer $AGENTMAIL_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD"

rm -f "$BODY_FILE"
```

如果需要发送 HTML 格式，把 `text` 换成 `html` 或同时提供两者。

### 3. 报告结果

- 成功：简短告知"已发送到 xxx"
- 失败：显示错误详情

## API 参考

```
POST https://api.agentmail.to/v0/inboxes/{inbox_id}/messages/send
Authorization: Bearer $AGENTMAIL_API_KEY
Content-Type: application/json

请求体:
{
  "to": "收件人@example.com",
  "subject": "邮件主题",
  "text": "纯文本正文",
  "html": "<p>可选 HTML 正文</p>"
}

响应:
{
  "message_id": "msg_xxx",
  "thread_id": "thread_xxx"
}
```

## 注意事项

- 如果当前项目有 `.env` 文件包含 `AGENTMAIL_API_KEY`，优先使用
- 如果没有 `.env`，检查 shell 环境变量
- 长正文务必用临时文件 + jq 构造 JSON，避免 shell 转义问题
