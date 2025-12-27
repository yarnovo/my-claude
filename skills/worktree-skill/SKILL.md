---
name: worktree
description: Git Worktree 管理（支持分支名或功能描述）
allowed-tools: Bash, Read, Write
---

请帮我管理 git worktree：

## 参数

$ARGUMENTS

## 意图识别

根据参数判断用户意图：

| 意图 | 触发词示例 |
|------|-----------|
| **列表** | 空参数、`list`、`列表`、`有哪些`、`状态` |
| **删除** | `删除 xxx`、`移除 xxx`、`remove xxx`、`-d xxx`、`干掉 xxx` |
| **同步检查** | `检查`、`同步状态`、`落后`、`check` |
| **清理** | `清理`、`prune`、`清理无效` |
| **创建** | 其他情况（分支名或功能描述） |

## 执行步骤

### 列表（无参数或明确请求）

```bash
git worktree list
```

输出格式：
```
📋 当前 Worktree 列表：

| 目录 | 分支 | 状态 |
|------|------|------|
| /path/to/repo | main | ✅ 当前 |
| /path/to/repo-feature | feature | 📁 |
```

### 删除

1. 解析要删除的 worktree（支持：目录名、分支名、模糊匹配）
2. 检查是否有未提交更改
3. 执行删除：
   ```bash
   git worktree remove <path>
   ```
4. 如有多个匹配，列出让用户选择

输出格式：
```
✅ Worktree 已删除！

📁 目录: /path/to/repo-branch（已删除）
🌿 分支: branch-name（保留）
```

### 同步检查

检查所有 worktree 的远程同步状态：

```bash
git fetch --all
# 对每个 worktree 检查 ahead/behind
```

输出格式：
```
📊 Worktree 同步状态：

| 目录 | 分支 | 状态 |
|------|------|------|
| loan | next | ✅ 已同步 |
| loan-main | main | ⚠️ 落后 5 个提交 |
```

### 清理

清理无效的 worktree 引用：

```bash
git worktree prune
```

### 创建（默认）

1. **解析参数**：
   - 如果是英文且符合分支命名（小写、数字、`-`、`/`），直接作为分支名
   - 如果是中文描述，生成合适的英文分支名（kebab-case）
   - 添加日期前缀：`<当前分支>-<分支名>-<YYYYMMDD>`

2. **检查分支状态**：
   ```bash
   git show-ref --verify --quiet refs/heads/<branch-name>
   ```

3. **创建 worktree**：
   - 目录位置：`../<仓库名>-<分支名>`
   - 分支不存在：`git worktree add -b <branch> <path>`
   - 分支已存在：`git worktree add <path> <branch>`

4. **用 VS Code 打开**：
   ```bash
   # 优先使用 code 命令，不可用时 fallback 到 open
   code <path> 2>/dev/null || open -a "Visual Studio Code" <path>
   ```

输出格式：
```
✅ Worktree 创建成功！

📁 目录: /path/to/repo-branch
🌿 分支: branch-name
📍 基于: current-branch

已用 VS Code 打开新目录
```

## 错误处理

- 不是 git 仓库 → 提示用户
- 分支已被其他 worktree 使用 → 提示用户
- 目录已存在 → 提示用户
- 删除时有未提交更改 → 询问是否强制删除
- 模糊匹配多个结果 → 列出选项让用户确认

## 使用示例

```
/worktree                     # 列出所有 worktree
/worktree 修复登录bug          # 创建新 worktree
/worktree 删除 loan-main       # 删除指定 worktree
/worktree 删除那个旧的 v2      # 模糊匹配删除
/worktree 检查同步状态         # 检查远程同步
/worktree 清理                 # 清理无效引用
```
