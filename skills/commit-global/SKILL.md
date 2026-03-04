---
name: commit-global
description: 提交全局 Claude 配置。当用户说"提交全局 claude"、"commit global claude"等时调用。
allowed-tools: Bash, Read
---

提交 `~/.claude` 仓库的改动。

## 操作流程

### 1. 分析改动
- `cd ~/.claude && git status` 查看改动文件
- `cd ~/.claude && git diff` 查看具体变更内容
- `cd ~/.claude && git log --oneline -5` 了解最近的提交风格

### 2. 生成提交信息
- 根据改动内容生成 Conventional Commits 格式的提交信息
- 格式：`type(scope): description`
- 展示提交信息供用户确认

### 3. 提交
- 按文件名暂存相关文件（不要用 `git add -A`）
- `cd ~/.claude && git add <files> && git commit -m "..."`
- 所有 git 命令都在 `~/.claude` 目录下执行

## 注意事项
- 仓库路径固定为 `~/.claude`
- 不要暂存 .env、credentials 等敏感文件
- 提交信息用英文，简洁描述改动
