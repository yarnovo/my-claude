---
description: 自动总结 staged 内容并提交（遵循 Conventional Commits 完整规范）
allowed-arguments: ["-add"]
---

请帮我创建一个 git commit：

## 参数说明
- 无参数：只提交已 staged 的内容
- `-add`：先执行 `git add .` 暂存所有改动，再提交

## 步骤
1. 如果参数包含 `-add`，先运行 `git add .`
2. 运行 `git status` 查看 staged 的文件
3. 运行 `git diff --staged` 查看 staged 的改动内容
4. 根据改动内容，按照 Conventional Commits 完整规范生成提交消息
5. 使用 `git commit -m "消息"` 或 `git commit -m "标题" -m "内容体" -m "footer"` 提交

## Conventional Commits 完整格式

```
<type>[optional scope][optional !]: <description>

[optional body]

[optional footer(s)]
```

### 标题行（必需）
- 格式：`<type>(<scope>): <中文描述>` 或 `<type>: <中文描述>`
- type（必需）：feat, fix, docs, style, refactor, perf, test, chore, build, ci
- scope（可选）：改动的范围，如 api, ui, parser 等
- !（可选）：表示 BREAKING CHANGE
- 描述：简洁的中文描述

### 内容体（可选）
- 空一行后的详细说明
- 用中文解释改动的动机、背景或实现细节
- 适用于复杂改动

### Footer（可选）
- `BREAKING CHANGE: <说明>` - 不兼容的重大变更
- `Closes #123` - 关闭的 issue
- `Refs #456` - 相关的 issue

## 示例

简单提交：
```
feat: 添加用户登录功能
```

带 scope：
```
fix(api): 修复数据查询超时问题
```

重大变更（方式1）：
```
feat!: 重构认证系统

使用 JWT 替代 Session 认证机制

BREAKING CHANGE: 所有 /auth 接口需要在 header 中携带 Bearer token
```

重大变更（方式2）：
```
feat(api)!: 更改 API 响应格式

BREAKING CHANGE: API 响应从 {data} 改为 {code, data, message}
Closes #234
```

## 要求
- 描述和内容体必须使用中文
- type、scope 使用英文小写
- 根据改动复杂度决定是否需要 body
- 如有不兼容变更，必须标记 BREAKING CHANGE
- 不要添加 "Generated with Claude Code" 等额外内容
