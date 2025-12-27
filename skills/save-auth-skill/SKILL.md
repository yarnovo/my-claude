---
name: save-auth
description: 保存 Playwright 认证状态（Clerk Testing 自动认证）。全自动 headless 模式，无需手动操作。
allowed-tools: Bash, Read
---

# Save Auth - Clerk Testing 自动认证

## 项目约定

| 文件 | 用途 |
|------|------|
| `.claude/config.local.json` | 端口配置 `{ "ports": { "nextjs": 13002 } }` |
| `web/.env.local` | 用户配置 + CLERK_SECRET_KEY |
| `.auth/<role>.json` | 各角色认证状态 |

## 环境变量格式

```bash
# 格式: role:email;role:email
E2E_CLERK_USERS=user:test@example.com;admin:admin@example.com;trader:trader@example.com

# Clerk 密钥
CLERK_SECRET_KEY=sk_test_xxx
```

## 前置条件

1. 在 Clerk Dashboard 创建测试用户
2. 在 `web/.env.local` 配置 `E2E_CLERK_USERS` 和 `CLERK_SECRET_KEY`
3. 开发服务器运行中

## 执行

```bash
npx tsx ~/.claude/skills/save-auth-skill/scripts/save-auth.ts <project-root> [role]
```

参数说明：
- `project-root`: 项目根目录
- `role`: 可选，指定角色
  - `all`（默认）: 处理所有配置的用户
  - `user`: 仅处理 user 角色
  - `admin`: 仅处理 admin 角色
  - 其他自定义角色名

## 示例

```bash
# 保存所有用户认证（默认）
npx tsx ~/.claude/skills/save-auth-skill/scripts/save-auth.ts .

# 仅保存 user 角色
npx tsx ~/.claude/skills/save-auth-skill/scripts/save-auth.ts . user

# 仅保存 admin 角色
npx tsx ~/.claude/skills/save-auth-skill/scripts/save-auth.ts . admin

# 保存自定义角色（如 trader）
npx tsx ~/.claude/skills/save-auth-skill/scripts/save-auth.ts . trader
```

## 输出

```
==================================================
🔐 Save Auth - Clerk Testing 自动认证
==================================================
   项目: /path/to/project
   端口: 13002
   用户: 3 个
         - user: test@example.com
         - admin: admin@example.com
         - trader: trader@example.com
==================================================

🚀 启动浏览器...

────────────────────────────────────────
👤 user: test@example.com
────────────────────────────────────────
   🔐 正在登录...
   ✅ signIn 完成
   📍 验证登录状态...
   ✅ 登录成功！
   📁 已保存: /path/to/project/.auth/user.json (11KB)

────────────────────────────────────────
👤 admin: admin@example.com
────────────────────────────────────────
   🔐 正在登录...
   ✅ signIn 完成
   📍 验证登录状态...
   ✅ 登录成功！
   📁 已保存: /path/to/project/.auth/admin.json (11KB)

==================================================
📊 认证保存结果:

   ✅ user
   ✅ admin
   ✅ trader
==================================================

✅ 所有用户认证状态已保存！
```

## 输出文件

认证状态保存到 `.auth/<role>.json`：
- `E2E_CLERK_USERS=user:xxx` → `.auth/user.json`
- `E2E_CLERK_USERS=admin:xxx` → `.auth/admin.json`
- `E2E_CLERK_USERS=trader:xxx` → `.auth/trader.json`
