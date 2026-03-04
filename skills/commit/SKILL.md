---
name: commit
description: 提交代码改动。当用户说"提交"、"commit"、"帮我提交"等时调用。
allowed-tools: Bash, Read, Glob, Grep
---

代码提交技能——分析当前改动，生成 Conventional Commits 格式的提交信息并提交。

## 操作流程

### 1. 分析改动
- `git status` 查看改动文件
- `git diff` 查看具体变更内容
- `git log --oneline -5` 了解最近的提交风格

### 2. 生成提交信息
- 根据改动内容生成符合 Conventional Commits 规范的提交信息
- 格式：`type(scope): description`
- 常用 type：feat、fix、chore、refactor、docs、test、style
- 展示提交信息供用户确认

### 3. 提交
- 按文件名暂存相关文件（不要用 `git add -A`）
- 创建提交

## 注意事项
- 不要暂存 .env、credentials 等敏感文件
- 提交信息用英文，简洁描述 "why" 而非 "what"
- 提交前展示信息让用户确认
