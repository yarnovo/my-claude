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
| **创建** | 其他情况（分支名或功能描述），支持 `--from <分支>` 或 `从 <分支> 创建` |

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
3. 如有多个匹配，列出让用户选择
4. **读取域名配置**（删除前）：
   ```bash
   cat <path>/.claude/worktree.json  # 获取 domain 字段
   ```
5. **清理 Caddy 配置**：
   ```bash
   # 从 ~/.config/caddy/worktrees.caddy 删除对应域名配置块
   # 匹配注释行 "# <branch-name>" 到下一个空行之间的内容
   sed -i '' '/^# <branch-name>$/,/^$/d' ~/.config/caddy/worktrees.caddy

   # 重载 Caddy
   caddy reload --config /opt/homebrew/etc/Caddyfile
   ```
6. 执行删除：
   ```bash
   git worktree remove <path>
   ```

输出格式：
```
✅ Worktree 已删除！

📁 目录: /path/to/repo-branch（已删除）
🌿 分支: branch-name（保留）
🌐 Caddy 配置已清理
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
   - **解析基础分支**（可选）：
     - `--from <分支>` 或 `-f <分支>`：指定基础分支
     - `从 <分支> 创建 xxx`：中文语法
     - `基于 <分支> xxx`：中文语法
     - 未指定时默认使用当前分支
   - 如果是英文且符合分支命名（小写、数字、`-`、`/`），直接作为分支名
   - 如果是中文描述，生成合适的英文分支名（kebab-case）
   - 添加日期前缀：`<基础分支>-<分支名>-<YYYYMMDD>`

2. **验证基础分支**（如果指定了）：
   ```bash
   git show-ref --verify --quiet refs/heads/<base-branch>
   # 或检查远程分支
   git show-ref --verify --quiet refs/remotes/origin/<base-branch>
   ```
   - 如果基础分支不存在，提示用户并列出可用分支

3. **检查目标分支状态**：
   ```bash
   git show-ref --verify --quiet refs/heads/<branch-name>
   ```

4. **创建 worktree**：
   - 目录位置：`../<仓库名>-<分支名>`
   - 分支不存在且指定基础分支：`git worktree add -b <branch> <path> <base-branch>`
   - 分支不存在且使用当前分支：`git worktree add -b <branch> <path>`
   - 分支已存在：`git worktree add <path> <branch>`

5. **执行初始化脚本**（如果存在）：
   ```bash
   # 检查新 worktree 目录下是否有初始化脚本
   if [ -x <path>/.claude/worktree-init.sh ]; then
     cd <path> && ./.claude/worktree-init.sh
   fi
   ```

6. **读取生成的端口配置**：
   ```bash
   # 从初始化脚本生成的配置中读取端口
   cat <path>/.claude/worktree.json
   ```

7. **用 VS Code 打开**：
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

🔧 初始化完成，服务已启动：
🌐 Next.js:    https://<domain-name>.localhost
📖 Storybook:  https://<domain-name>-sb.localhost

已用 VS Code 打开新目录
```

注意：域名从分支名提取（去掉前缀和日期后缀），例如 `main-loan-consulting-agent-20260102` -> `loan-consulting-agent`

## 错误处理

- 不是 git 仓库 → 提示用户
- 指定的基础分支不存在 → 提示用户并列出可用分支
- 分支已被其他 worktree 使用 → 提示用户
- 目录已存在 → 提示用户
- 删除时有未提交更改 → 询问是否强制删除
- 模糊匹配多个结果 → 列出选项让用户确认

## 使用示例

```
/worktree                           # 列出所有 worktree
/worktree 修复登录bug                # 基于当前分支创建
/worktree 新功能 --from develop      # 基于 develop 创建
/worktree 新功能 -f main             # 基于 main 创建（简写）
/worktree 从 develop 创建 新功能     # 中文语法
/worktree 基于 main 修复bug          # 中文语法
/worktree 删除 loan-main             # 删除指定 worktree
/worktree 删除那个旧的 v2            # 模糊匹配删除
/worktree 检查同步状态               # 检查远程同步
/worktree 清理                       # 清理无效引用
```
