---
name: create-clerk-user
description: 创建 Clerk 测试用户并保存认证状态。使用 Clerk Backend API 创建用户，然后自动登录保存 cookie。
allowed-tools: Bash, Read
---

# Create Clerk User - 创建测试用户

## 项目约定

| 文件 | 用途 |
|------|------|
| `.claude/config.local.json` | 端口配置 `{ "ports": { "nextjs": 13002 } }` |
| `web/.env` | Clerk 密钥（CLERK_SECRET_KEY） |
| `.auth/user.json` | 普通用户认证状态 |
| `.auth/admin.json` | 管理员用户认证状态 |

## 前置条件

1. `web/.env` 中已配置 `CLERK_SECRET_KEY=sk_test_xxx`
2. 开发服务器运行中

## 执行

```bash
npx tsx ~/.claude/skills/create-clerk-user-skill/scripts/create-user.ts <project-root> [options]
```

### 选项

| 选项 | 说明 | 默认值 |
|------|------|--------|
| `--email` | 用户邮箱 | `test@example.com` |
| `--password` | 用户密码 | `Test123456!` |
| `--first-name` | 名 | `Test` |
| `--last-name` | 姓 | `User` |
| `--type` | 用户类型 (user/admin) | `user` |
| `--save-auth` | 创建后保存认证状态 | `false` |

## 示例

```bash
# 创建默认测试用户
npx tsx ~/.claude/skills/create-clerk-user-skill/scripts/create-user.ts .

# 创建管理员用户
npx tsx ~/.claude/skills/create-clerk-user-skill/scripts/create-user.ts . --type admin --email admin@example.com

# 创建用户并保存认证状态
npx tsx ~/.claude/skills/create-clerk-user-skill/scripts/create-user.ts . --email test@test.com --save-auth

# 使用自定义信息
npx tsx ~/.claude/skills/create-clerk-user-skill/scripts/create-user.ts . \
  --email john@example.com \
  --password MySecure123! \
  --first-name John \
  --last-name Doe
```

## 工作流程

1. **读取配置**：从 `web/.env` 获取 `CLERK_SECRET_KEY`
2. **创建用户**：调用 Clerk Backend API 创建用户
3. **配置环境变量**：将用户邮箱写入 `web/.env.local`
4. **保存认证**（可选）：调用 `save-auth` 脚本登录并保存 cookie

## 输出

```
==================================================
🔐 Create Clerk User
==================================================
   项目: /path/to/project
   用户: test@example.com
   类型: user
==================================================

🔍 检查 Clerk 配置...
   ✅ CLERK_SECRET_KEY 已配置

👤 创建用户...
   ✅ 用户创建成功！
   ID: user_xxx
   Email: test@example.com
   Name: Test User

📝 更新环境变量...
   ✅ E2E_CLERK_USER_USERNAME=test@example.com

🔐 保存认证状态...
   ✅ 已保存: .auth/user.json

==================================================
✅ 用户创建完成！
==================================================
```

## 注意事项

- 如果用户已存在，脚本会提示并跳过创建
- 创建的用户使用邮箱+密码认证方式
- `--save-auth` 需要开发服务器正在运行
