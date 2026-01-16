# Worktree 开发

请阅读 `WORKTREE_TARGET.md` 了解开发目标，然后按以下流程执行完整开发周期。

---

## 辅助工具：技术调研

**Tools:** `Context7` + `WebSearch` + `WebFetch`

**任何阶段遇到不熟悉的技术时都可调研：**

| 工具 | 用途 | 示例 |
|------|------|------|
| Context7 | 查库/框架文档 | `resolve-library-id` → `query-docs` |
| WebSearch | 搜索最佳实践 | `"<技术> best practices"` |
| WebFetch | 读官方文档 | 官方文档、GitHub README |

**常用 Context7 库 ID：**
`/vercel/next.js` · `/facebook/react` · `/prisma/prisma` · `/tailwindlabs/tailwindcss`

---

## 阶段 1: 头脑风暴与需求澄清

**Skill:** `superpowers:brainstorming`

1. 查看项目当前状态（文件、文档、最近提交）
2. **每次只问一个问题**，优先选择题
3. 提出 2-3 个不同权衡的方案，给出推荐
4. 将设计分段展示（200-300 词/段），每段确认后再继续
5. 设计完成后写入 `docs/plans/YYYY-MM-DD-<topic>-design.md`

**原则：** YAGNI（不做不需要的事）

---

## 阶段 2: 代码库探索

**Agent:** `feature-dev:code-explorer`

1. 启动 2-3 个 explorer agent 并行探索不同方面：
   - 类似功能的实现
   - 架构和抽象层
   - UI 模式、测试方法、扩展点
2. 每个 agent 返回 5-10 个关键文件列表
3. **读取 agent 识别的所有文件**，建立深入理解
4. 汇总发现的模式和约定

---

## 阶段 3: 架构设计

**Agent:** `feature-dev:code-architect`

1. 启动 2-3 个 architect agent，采用不同策略：
   - **最小改动**：最小变更，最大复用
   - **干净架构**：可维护性，优雅抽象
   - **实用平衡**：速度 + 质量
2. 比较各方案权衡
3. **给出推荐并说明理由**
4. **等待用户选择后再继续**

---

## 阶段 4: 编写 Plan

**Skill:** `superpowers:writing-plans`

将选定方案写入 `docs/plans/YYYY-MM-DD-<feature-name>.md`

**Plan 格式要求：**

```markdown
# [Feature Name] Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** [一句话描述]
**Architecture:** [2-3 句话说明方案]
**Tech Stack:** [关键技术/库]

---

### Task N: [Component Name]

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`
- Test: `tests/exact/path/to/test.py`

**Step 1: Write the failing test**
[完整测试代码]

**Step 2: Run test to verify it fails**
Run: `pytest tests/path/test.py::test_name -v`
Expected: FAIL with "function not defined"

**Step 3: Write minimal implementation**
[完整实现代码]

**Step 4: Run test to verify it passes**
Run: `pytest tests/path/test.py::test_name -v`
Expected: PASS

**Step 5: Commit**
`git commit -m "feat: add specific feature"`
```

**每个 Step 是一个原子动作（2-5 分钟）**

---

## 阶段 5: 执行 Plan

**选择一：** `superpowers:subagent-driven-development`（当前会话）

```
每个任务循环：
  1. 派发 implementer subagent
  2. Subagent 实现 + 测试 + 提交 + 自审
  3. 派发 spec-reviewer 检查规格符合性
  4. 派发 code-quality-reviewer 检查代码质量
  5. 如有问题 → implementer 修复 → 重新审查
  6. 标记完成，下一个任务
```

**选择二：** `superpowers:executing-plans`（新会话）

```
批次执行（默认每批 3 个任务）：
  1. 读取 plan，批判性审查
  2. 执行批次中每个任务
  3. 汇报完成情况
  4. 等待反馈
  5. 重复直到全部完成
```

**核心原则：** 遵循 TDD - 红→绿→重构

---

## 阶段 6: TDD 执行细节

**Skill:** `superpowers:test-driven-development`

```
铁律：NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST

RED（写失败测试）
  ↓ 验证确实失败
GREEN（写最小实现）
  ↓ 验证确实通过
REFACTOR（清理代码）
  ↓ 保持绿灯
REPEAT
```

**如果先写了代码？删除它。从测试重新开始。**

---

## 阶段 7: 调试（如遇问题）

**Skill:** `superpowers:systematic-debugging`

```
铁律：NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST

Phase 1: 根因调查
  - 仔细读错误信息
  - 稳定复现
  - 检查最近变更
  - 收集证据

Phase 2: 模式分析
  - 找到能工作的类似代码
  - 对比差异

Phase 3: 假设测试
  - 单一假设
  - 最小改动验证
  - 不行就新假设

Phase 4: 实现修复
  - 先写失败测试
  - 单一修复
  - 验证通过

⚠️ 如果 3+ 次修复失败 → 停下来质疑架构
```

**卡住时的选项：**
- 质疑架构设计
- **技术调研**：用 Context7/WebSearch 查询相关技术文档（见顶部辅助工具）
- 寻求帮助

---

## 阶段 8: 验证完成

**Skill:** `superpowers:verification-before-completion`

```
铁律：NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE

在声称"完成"之前：
  1. 识别：什么命令能证明这个声称？
  2. 运行：执行完整命令
  3. 读取：完整输出，检查退出码
  4. 验证：输出是否确认声称？
  5. 然后才能：声称完成

❌ 禁止：should, probably, seems to
❌ 禁止：未验证就说 "Great!", "Done!"
```

---

## 阶段 9: 代码审查

**Skill:** `superpowers:requesting-code-review` + `/pr-review-toolkit:review-pr`

1. 获取 git SHAs：
   ```bash
   BASE_SHA=$(git rev-parse HEAD~N)  # N = 本次改动的提交数
   HEAD_SHA=$(git rev-parse HEAD)
   ```

2. 派发 `superpowers:code-reviewer` subagent

3. 运行 `/pr-review-toolkit:review-pr`：
   - **comments** - 注释准确性
   - **tests** - 测试覆盖
   - **errors** - 错误处理
   - **types** - 类型设计
   - **code** - 代码质量
   - **simplify** - 简化代码

4. 修复所有 Critical 和 Important 问题

---

## 阶段 10: 提交与 PR

**Command:** `/commit-commands:commit-push-pr`

1. 创建分支（如在 main）
2. 创建提交
3. 推送到远程
4. 创建 Pull Request

---

## 阶段 11: 完成分支

**Skill:** `superpowers:finishing-a-development-branch`

1. **验证测试通过**（必须）
2. 确定基础分支
3. 提供 4 个选项：
   - 本地合并到 base-branch
   - 推送并创建 PR
   - 保持当前状态
   - 放弃这个工作
4. 执行选择
5. 清理 worktree（如适用）

---

## 快速参考

| 阶段 | Plugin/Skill | 触发条件 |
|------|-------------|----------|
| **调研** | `Context7` + `WebSearch` | **任何阶段遇到不熟悉技术时** |
| 头脑风暴 | `superpowers:brainstorming` | 开始任何创造性工作前 |
| 探索 | `feature-dev:code-explorer` | 理解代码库 |
| 设计 | `feature-dev:code-architect` | 设计实现方案 |
| 规划 | `superpowers:writing-plans` | 编写详细执行计划 |
| 执行 | `superpowers:subagent-driven-development` | 当前会话执行 |
| 执行 | `superpowers:executing-plans` | 新会话批次执行 |
| TDD | `superpowers:test-driven-development` | 写任何代码前 |
| 调试 | `superpowers:systematic-debugging` | 遇到 bug/测试失败 |
| 验证 | `superpowers:verification-before-completion` | 声称完成前 |
| 审查 | `superpowers:requesting-code-review` | 完成任务后 |
| 审查 | `/pr-review-toolkit:review-pr` | 全面 PR 审查 |
| 提交 | `/commit-commands:commit-push-pr` | 创建 PR |
| 完成 | `superpowers:finishing-a-development-branch` | 分支工作完成 |

---

## 红旗警告 - 立即停止

看到这些想法时停下来：

| 想法 | 现实 |
|------|------|
| "这个很简单，不需要流程" | 简单的事情也有流程 |
| "先写代码，之后补测试" | 之后的测试证明不了什么 |
| "一次修多个问题更快" | 无法隔离哪个生效，会引入新 bug |
| "应该能用了" | "应该" 不是证据，运行验证 |
| "紧急情况，没时间" | 系统化方法比乱试快 |
| "再试一次修复"（已试 2+ 次） | 3+ 次失败 = 架构问题 |
