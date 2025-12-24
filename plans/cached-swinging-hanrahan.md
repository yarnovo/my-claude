# 评估用例生成系统设计方案

## 用户需求确认

| 决策项 | 选择 |
|--------|------|
| 输入源 | **多源输入**（BDD、PRD、产品 Wiki） |
| 用例格式 | **JSON 为主**，需要时转换为 Python |
| 更新策略 | **智能合并**（比对差异，保留自定义内容） |
| 自动验证 | **是**（格式检查 + 基本逻辑验证） |

## 背景分析

### 当前状态
1. **现有 agent**: `bdd-to-evals` - 从 BDD 生成 JSON 格式评估用例
2. **现有 skill**: `bdd-to-evals` - 调用上述 agent 的入口
3. **评估框架**: `evals/` - 基于 DeepEval 的 LLM-as-Judge 评估
4. **测试分类**: capabilities（能力）, e2e（端到端）, edge_cases（边界）

### 问题与机会
1. 现有的 `conversation.py` 是**手工维护**的 23 个场景，与 JSON 格式不统一
2. 缺乏从 JSON 到 Python 代码的转换能力
3. 缺乏评估用例的验证机制
4. 输入源单一（仅 BDD），未考虑其他文档类型

---

## 设计方案：分层评估用例生成系统

### 架构总览

```
┌─────────────────────────────────────────────────────────────────┐
│                     用户入口层 (Skills)                          │
├─────────────────┬─────────────────┬─────────────────────────────┤
│  /eval-generate │  /eval-validate │  /eval-sync                 │
│  生成评估用例    │  验证用例质量    │  同步到框架                  │
└────────┬────────┴────────┬────────┴──────────┬──────────────────┘
         │                 │                   │
         ▼                 ▼                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                     编排层 (Coordinator Agent)                   │
│                     eval-coordinator                             │
│  - 分析输入源类型（BDD/PRD/产品文档）                              │
│  - 调度对应的专家 agent                                           │
│  - 聚合和验证结果                                                 │
└────────┬────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     专家层 (Specialist Agents)                   │
├─────────────────┬─────────────────┬─────────────────────────────┤
│  bdd-to-evals   │  prd-to-evals   │  eval-validator             │
│  BDD 场景解析    │  PRD 用例提取    │  用例质量检查                │
├─────────────────┼─────────────────┼─────────────────────────────┤
│  eval-to-code   │  eval-coverage  │  eval-runner                │
│  JSON 转 Python │  覆盖率分析      │  用例执行验证                 │
└─────────────────┴─────────────────┴─────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     输出层                                       │
├─────────────────┬─────────────────┬─────────────────────────────┤
│  evals/tests/   │  evals/utils/   │  evals/reports/             │
│  JSON 用例文件   │  conversation.py │  覆盖率报告                  │
└─────────────────┴─────────────────┴─────────────────────────────┘
```

---

## 核心组件设计

### 1. Skill 层（用户入口）

#### Skill 1: `/eval-generate` - 生成评估用例

```yaml
name: eval-generate
description: 从多种文档源生成评估用例。支持 BDD、PRD、产品 Wiki 作为输入。
allowed-tools: Task, Read, Write, Glob, Grep
```

**触发场景：**
- "生成评估用例"
- "从 BDD 创建测试"
- "添加 FICO 边界测试"

#### Skill 2: `/eval-validate` - 验证用例质量

```yaml
name: eval-validate
description: 验证评估用例的格式、覆盖率和质量。
allowed-tools: Task, Read, Bash
```

**触发场景：**
- "验证评估用例"
- "检查测试覆盖率"
- "用例格式正确吗"

#### Skill 3: `/eval-sync` - 同步到框架

```yaml
name: eval-sync
description: 将 JSON 用例同步到 Python 评估框架（conversation.py）。
allowed-tools: Task, Read, Write
```

**触发场景：**
- "同步用例到 Python"
- "更新 conversation.py"
- "集成新测试到框架"

---

### 2. Agent 层（核心逻辑）

#### Agent 1: `eval-coordinator` - 评估编排器

**职责：** 分析输入、调度专家、聚合结果

```markdown
---
name: eval-coordinator
description: 评估用例生成的编排 Agent。分析输入源类型，调度专家 Agent，聚合和验证结果。
model: sonnet
---

## Mission
协调评估用例的完整生成流程。

## Input Source Detection
根据用户请求和文件路径识别输入类型：
- `docs/BDD/` → bdd-to-evals agent
- `docs/PRD/` → prd-to-evals agent
- `web/lib/agent/prompts/wiki/` → wiki-to-evals agent

## Workflow
1. 分析用户请求，确定输入源
2. 调用对应的专家 agent
3. 收集生成的 JSON 用例
4. 调用 eval-validator 验证
5. 如需要，调用 eval-to-code 同步到 Python
6. 输出覆盖率报告
```

#### Agent 2: `bdd-to-evals` - BDD 解析器（已存在，可复用）

**增强点：**
- 输出统一的 JSON Schema
- 支持增量更新
- 保留 BDD 场景追溯链接

#### Agent 3: `prd-to-evals` - PRD 解析器（新增）

```markdown
---
name: prd-to-evals
description: 从 PRD 文档提取可测试场景，生成评估用例。
model: sonnet
---

## Mission
从 `docs/PRD/` 读取产品需求文档，提取可验证的用户故事和验收标准，转换为评估用例。

## Extraction Rules
1. 用户故事 → e2e 测试场景
2. 验收标准 → capabilities 测试
3. 边界条件 → edge_cases 测试
```

#### Agent 4: `eval-validator` - 用例验证器（新增）

```markdown
---
name: eval-validator
description: 验证评估用例的格式正确性、完整性和可执行性。
model: haiku
---

## Validation Rules
1. JSON Schema 校验
2. expectations 字段完整性
3. toolCalls 与工具定义一致性
4. contains/notContains 合理性
5. BDD 覆盖率检查
```

#### Agent 5: `eval-to-code` - 代码生成器（新增）

```markdown
---
name: eval-to-code
description: 将 JSON 评估用例转换为 Python 代码（conversation.py 格式）。
model: sonnet
---

## Mission
读取 `evals/tests/**/*.json`，生成/更新 `evals/utils/conversation.py`。

## Output Format
按照现有 conversation.py 的数据结构：
- Turn(user, expected_output, description)
- Conversation(name, description, turns, tags, priority, bdd_source)
```

---

### 3. 数据流设计

```
输入文档
    │
    ├─ docs/BDD/agent/*.feature ──────┐
    │                                 │
    ├─ docs/PRD/*.md ─────────────────┼──▶ eval-coordinator
    │                                 │       │
    └─ web/lib/agent/prompts/wiki/*.md┘       │
                                              ▼
                                     ┌───────────────────┐
                                     │  专家 Agent 并行   │
                                     ├───────────────────┤
                                     │ bdd-to-evals      │
                                     │ prd-to-evals      │
                                     └─────────┬─────────┘
                                               │
                                               ▼
                                     ┌───────────────────┐
                                     │ JSON 评估用例      │
                                     │ evals/tests/      │
                                     └─────────┬─────────┘
                                               │
                                               ▼
                                     ┌───────────────────┐
                                     │ eval-validator    │
                                     │ 格式/覆盖率检查     │
                                     └─────────┬─────────┘
                                               │
                                               ▼
                                     ┌───────────────────┐
                                     │ eval-to-code      │
                                     │ 生成 Python 代码   │
                                     └─────────┬─────────┘
                                               │
                                               ▼
                                     ┌───────────────────┐
                                     │ conversation.py   │
                                     │ (评估框架集成)     │
                                     └───────────────────┘
```

---

## JSON 评估用例 Schema（统一格式）

```typescript
interface EvalTest {
  version: "1.0";
  category: "capabilities" | "e2e" | "edge_cases";
  id: string;                    // unique-id
  name: string;                  // 测试名称
  description: string;           // 测试描述
  source: {
    type: "bdd" | "prd" | "wiki";
    file: string;                // 源文件路径
    scenario?: string;           // BDD 场景名
  };
  tags: string[];                // 标签
  priority: "P0" | "P1" | "P2";  // 优先级

  // 单轮测试（capabilities, edge_cases）
  tests?: Array<{
    id: string;
    name: string;
    input: string;
    expectations: Expectation;
  }>;

  // 多轮对话测试（e2e）
  conversation?: Array<{
    turn: number;
    user: string;
    expectations: Expectation;
  }>;

  finalExpectations?: {
    approved?: boolean;
    hasLoanOptions?: boolean;
    toolsCalled?: string[];
  };
}

interface Expectation {
  // 工具调用验证
  toolCalls?: string[];
  toolParams?: Record<string, any>;
  noToolCalls?: string[];

  // 响应内容验证
  contains?: string[];
  notContains?: string[];
  matchesPattern?: string;

  // 业务规则验证
  rateAdjustment?: number;
  ltvPenalty?: number;
  dtiLimit?: number;
}
```

---

## 实施计划

### Phase 1: 基础设施（JSON Schema + 验证器）
**目标**：建立统一的用例格式和验证能力

1. **创建 JSON Schema 定义** `evals/schemas/eval-test.schema.json`
   - 统一 capabilities、e2e、edge_cases 三类格式
   - 支持 source 追溯（BDD/PRD/Wiki）

2. **创建 `eval-validator` agent** `.claude/agents/eval-validator.md`
   - JSON Schema 校验
   - 工具名一致性检查（与 tools.md 对比）
   - 期望值逻辑验证

3. **创建 `/eval-validate` skill** `.claude/skills/eval-validate/SKILL.md`
   - 验证所有 JSON 用例
   - 输出验证报告

### Phase 2: 增强 BDD 转换
**目标**：完善现有 bdd-to-evals 的智能合并能力

1. **增强 `bdd-to-evals` agent**
   - 添加智能合并逻辑（读取现有文件 → 比对 → 合并）
   - 保留 `// CUSTOM` 标记的自定义内容
   - 生成 diff 报告

2. **更新 bdd-to-evals skill**
   - 添加 `--merge` / `--overwrite` 参数
   - 生成后自动调用 validator

### Phase 3: 扩展输入源
**目标**：支持 PRD 和 Wiki 作为输入

1. **创建 `prd-to-evals` agent** `.claude/agents/prd-to-evals.md`
   - 解析 `docs/PRD/*.md`
   - 提取验收标准 → capabilities
   - 提取用户故事 → e2e

2. **创建 `wiki-to-evals` agent** `.claude/agents/wiki-to-evals.md`
   - 解析 `web/lib/agent/prompts/wiki/*.md`
   - 提取业务规则 → edge_cases

3. **创建 `eval-coordinator` agent** `.claude/agents/eval-coordinator.md`
   - 自动识别输入源类型
   - 调度对应的专家 agent
   - 聚合结果 + 去重

4. **创建 `/eval-generate` skill** `.claude/skills/eval-generate/SKILL.md`
   - 统一入口
   - 支持 `--source bdd|prd|wiki|all`

### Phase 4: Python 代码同步
**目标**：JSON 与 conversation.py 双向同步

1. **创建 `eval-to-code` agent** `.claude/agents/eval-to-code.md`
   - 读取 `evals/tests/**/*.json`
   - 生成 `evals/utils/conversations/` 目录
   - 保持 conversation.py 向后兼容

2. **创建 `/eval-sync` skill** `.claude/skills/eval-sync/SKILL.md`
   - JSON → Python 转换
   - Python → JSON 反向提取（可选）

### Phase 5: 工具链完善
**目标**：集成到开发流程

1. **覆盖率报告生成**
   - BDD 场景覆盖率
   - 按标签统计

2. **Makefile 集成**
   ```makefile
   eval-gen:     # 生成用例
   eval-val:     # 验证用例
   eval-sync:    # 同步到 Python
   eval-run:     # 运行评估
   ```

---

## 关键文件清单

### 新增文件（共 10 个）

| 文件路径 | 用途 |
|----------|------|
| `evals/schemas/eval-test.schema.json` | JSON Schema 定义 |
| `.claude/agents/eval-coordinator.md` | 编排器 Agent |
| `.claude/agents/eval-validator.md` | 验证器 Agent |
| `.claude/agents/eval-to-code.md` | JSON → Python Agent |
| `.claude/agents/prd-to-evals.md` | PRD 解析 Agent |
| `.claude/agents/wiki-to-evals.md` | Wiki 解析 Agent |
| `.claude/skills/eval-generate/SKILL.md` | 统一生成入口 |
| `.claude/skills/eval-validate/SKILL.md` | 验证入口 |
| `.claude/skills/eval-sync/SKILL.md` | 同步入口 |
| `evals/utils/conversations/` | 分模块的 Python 用例 |

### 修改文件（共 3 个）

| 文件路径 | 变更内容 |
|----------|----------|
| `.claude/agents/bdd-to-evals.md` | 添加智能合并逻辑 |
| `.claude/skills/bdd-to-evals/SKILL.md` | 添加参数支持 |
| `evals/Makefile` | 添加新命令 |

---

## 智能合并策略设计

### 标记语法

JSON 文件中使用注释标记自定义内容：

```json
{
  "tests": [
    // AUTO-GENERATED from 03-资格评估.feature
    { "id": "fico-pass", "input": "..." },

    // CUSTOM - 手工添加的特殊场景
    { "id": "fico-special", "input": "...", "_custom": true }
  ]
}
```

### 合并算法

```
1. 读取现有 JSON 文件
2. 解析并标记：
   - AUTO-GENERATED: 来自源文档
   - CUSTOM (_custom: true): 手工添加
3. 从源文档重新生成 AUTO-GENERATED 部分
4. 保留所有 CUSTOM 项
5. 按 id 去重，保留最新版本
6. 写入文件，添加时间戳和来源标记
```

---

## 验证规则清单

### 格式验证
- [ ] JSON 语法正确
- [ ] 符合 eval-test.schema.json
- [ ] id 全局唯一

### 内容验证
- [ ] toolCalls 中的工具名存在于 tools.md
- [ ] contains 不与 notContains 冲突
- [ ] source.file 指向真实文件

### 覆盖验证
- [ ] 每个 BDD @positive 场景有对应测试
- [ ] 每个 BDD @boundary 场景有边界测试
- [ ] 所有工具至少有一个用例覆盖
