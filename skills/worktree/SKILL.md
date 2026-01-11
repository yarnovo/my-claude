---
name: worktree
description: Git Worktree 管理（支持分支名或功能描述）
allowed-tools: Bash, Read, Write
---

请帮我管理 git worktree。

## 核心任务

用户启用此命令并附带一个需求/问题，工作流程如下：
1. **需求澄清** - 了解代码现状，与用户确认目标
2. **创建工作区** - 创建 git worktree（基于当前分支）
3. **创建目标文档** - 写入 WORKTREE_TARGET.md
4. **打开 VSCode** - 在新工作区中打开编辑器
5. **执行初始化** - 运行工作区初始化脚本
6. **创建规划脚本** - 创建 start-planning.sh（用户在 VSCode 中自行执行）

## 参数

$ARGUMENTS

## 意图识别

| 意图 | 触发词示例 |
|------|-----------|
| **列表** | 空参数、`list`、`列表`、`有哪些`、`状态` |
| **删除** | `删除 xxx`、`移除 xxx`、`remove xxx`、`-d xxx`、`干掉 xxx` |
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
3. 如有多个匹配，列出让用户选择
4. **执行清理脚本**（如果存在）：
   ```bash
   if [ -x <path>/.worktree/cleanup.sh ]; then
     cd <path> && ./.worktree/cleanup.sh
   fi
   ```
5. 执行删除：
   ```bash
   git worktree remove <path>
   ```

输出格式：
```
✅ Worktree 已删除！

📁 目录: /path/to/repo-branch（已删除）
🌿 分支: branch-name（保留）
```

### 创建（默认）

**重要：创建 worktree 前必须先和用户确认目标，不能直接执行！**

#### 第一步：目标确认（必须）

收到创建请求后，**先展示当前状态并和用户确认目标**，不要直接创建：

1. 列出当前 worktree 状态（让用户了解现有分支）
2. 根据用户描述，理解并复述你的理解
3. 提出澄清问题（如果描述模糊）：
   - 这个功能的边界是什么？
   - 是独立新特性还是对现有功能的改进？
   - 预计改动范围大吗？
4. 确认分支命名

**确认模板**：
```
📋 当前 Worktree：
[列出现有 worktree]

我理解你想要：[复述用户目标]

建议：
- 基于当前分支 `<current-branch>` 创建新 worktree
- 分支名：`<suggested-name>`

确认这样创建吗？或者你想调整一下目标？
```

**只有用户明确确认后，才进入下一步执行创建。**

#### 第二步：解析参数

用户确认后，开始解析：
- 如果是英文且符合分支命名（小写、数字、`-`、`/`），直接作为分支名
- 如果是中文描述，生成合适的英文分支名（kebab-case）
- 添加日期前缀：`<当前分支>-<分支名>-<YYYYMMDD>`

#### 第三步：执行创建

1. **检查目标分支状态**：
   ```bash
   git show-ref --verify --quiet refs/heads/<branch-name>
   ```

2. **创建 worktree**（基于当前分支）：
   - 目录位置：`../<仓库名>-<分支名>`
   - 分支不存在：`git worktree add -b <branch> <path>`
   - 分支已存在：`git worktree add <path> <branch>`

3. **创建目标文件**：
   - 检查 `.gitignore` 是否包含 `WORKTREE_TARGET.md`，不在则添加
   - 检查 `.gitignore` 是否包含 `WORKTREE_PLAN.md`，不在则添加
   - 检查 `.gitignore` 是否包含 `start-planning.sh`，不在则添加
   - 创建 `WORKTREE_TARGET.md` 文件，内容包含：
     - 标题：用户的功能描述
     - 功能目标：简要说明要实现什么
     - 核心需求：拆解主要任务点
     - 技术要点：可能涉及的技术方向

4. **用 VS Code 打开**：
   ```bash
   code <path> 2>/dev/null || open -a "Visual Studio Code" <path>
   ```

5. **执行初始化脚本**（如果存在）：
   ```bash
   if [ -x <path>/.worktree/init.sh ]; then
     cd <path> && ./.worktree/init.sh
   fi
   ```

6. **创建规划脚本**（不执行，用户在 VSCode 中自行运行）：
   ```bash
   cat > <path>/start-planning.sh << 'EOF'
   #!/bin/bash
   claude --permission-mode plan "请阅读 WORKTREE_TARGET.md 了解开发目标，然后：
   1. 探索代码库，理解现有架构
   2. 设计实现方案
   3. 将详细的实施规划输出到 WORKTREE_PLAN.md

   规划文档格式：
   - 目标概述
   - 技术方案
   - 实施步骤（按优先级排序）
   - 涉及的文件列表
   - 潜在风险点"
   EOF
   chmod +x <path>/start-planning.sh
   ```

输出格式：
```
✅ Worktree 创建成功！

📁 目录: /path/to/repo-branch
🌿 分支: branch-name
📍 基于: current-branch
🎯 目标: WORKTREE_TARGET.md（已创建）

📌 启动服务后可访问：
   🌐 Next.js:    https://<domain>.localhost (pnpm dev)
   📖 Storybook:  https://<domain>-sb.localhost (pnpm storybook)

🚀 下一步：在 VSCode 终端执行 ./start-planning.sh 启动规划 Agent
```

## 错误处理

- 不是 git 仓库 → 提示用户
- 分支已被其他 worktree 使用 → 提示用户
- 目录已存在 → 提示用户
- 删除时有未提交更改 → 询问是否强制删除
- 模糊匹配多个结果 → 列出选项让用户确认

## 使用示例

```
/worktree                           # 列出所有 worktree
/worktree 修复登录bug                # 会先确认目标再创建
/worktree 想做个新功能但不确定       # 会和你讨论确认后再创建
/worktree 删除 loan-main             # 删除指定 worktree
/worktree -d loan-main               # 删除（简写）
```
