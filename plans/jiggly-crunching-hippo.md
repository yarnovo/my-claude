# DeepEval 教程设计计划

## 用户选择

- **语言**：中文
- **学习范围**：全面学习（从基础到高级）
- **迁移策略**：最后提供一份迁移建议文档（不实际改造项目）

## 目标

在项目根目录创建 `tutorials/deepeval/` 教程文件夹，设计一套渐进式学习 DeepEval 框架的中文教程。

## 背景信息

### DeepEval 是什么

- 开源 LLM 评估框架（[GitHub](https://github.com/confident-ai/deepeval)）
- 类似 Pytest 但专门用于测试 LLM 输出
- 30+ 内置评估指标（GEval、RAG、Agent、Safety 等）
- 支持 LLM-as-Judge 评估方法
- 可与 Confident AI 云平台集成

### 核心概念

| 概念 | 说明 |
|------|------|
| LLMTestCase | 单轮对话测试用例（input, actual_output, expected_output） |
| ConversationalTestCase | 多轮对话测试用例 |
| Metrics | 评估指标（GEval, AnswerRelevancy, Faithfulness 等） |
| assert_test | 断言函数，验证测试是否通过 |

### 项目现状

当前项目已有自定义评估系统：
- 位置：`evals/`
- 测试用例：JSON 格式（25+ 个）
- 执行器：`evaluate.py`（LLM-as-Judge）
- 已安装 DeepEval：`evals/.venv/bin/deepeval`

---

## 教程结构设计

```
tutorials/
└── deepeval/
    ├── README.md                    # 教程概览和学习路线
    ├── 01-getting-started/          # 入门篇
    │   ├── 01-installation.md       # 安装配置
    │   ├── 02-first-test.md         # 第一个测试
    │   └── 03-run-tests.md          # 运行测试
    ├── 02-core-concepts/            # 核心概念
    │   ├── 01-test-cases.md         # 测试用例
    │   ├── 02-metrics-overview.md   # 指标概览
    │   └── 03-scoring.md            # 评分机制
    ├── 03-builtin-metrics/          # 内置指标
    │   ├── 01-geval.md              # G-Eval（自定义标准）
    │   ├── 02-answer-relevancy.md   # 答案相关性
    │   ├── 03-faithfulness.md       # 忠实度（幻觉检测）
    │   ├── 04-rag-metrics.md        # RAG 指标
    │   └── 05-agent-metrics.md      # Agent 指标
    ├── 04-advanced/                 # 进阶篇
    │   ├── 01-custom-metrics.md     # 自定义指标
    │   ├── 02-conversational.md     # 多轮对话评估
    │   ├── 03-async-evaluation.md   # 异步评估
    │   └── 04-component-level.md    # 组件级评估
    ├── 05-integration/              # 集成篇
    │   ├── 01-pytest-integration.md # Pytest 集成
    │   ├── 02-ci-cd.md              # CI/CD 集成
    │   └── 03-confident-ai.md       # Confident AI 云平台
    ├── 06-migration-guide.md        # 迁移建议文档
    └── examples/                    # 示例代码
        ├── basic_test.py            # 基础测试
        ├── geval_custom.py          # GEval 示例
        ├── rag_evaluation.py        # RAG 评估
        ├── agent_evaluation.py      # Agent 评估
        └── conversational_test.py   # 多轮对话
```

---

## 每章详细内容

### 01 入门篇

**01-installation.md**
- 创建虚拟环境
- pip install deepeval
- 配置 OPENAI_API_KEY
- deepeval login（可选）
- 验证安装

**02-first-test.md**
- 最小测试示例
- LLMTestCase 结构
- GEval 基础用法
- assert_test 断言

**03-run-tests.md**
- deepeval test run 命令
- 查看测试报告
- 常见问题排查

### 02 核心概念

**01-test-cases.md**
- LLMTestCase 属性详解
- ConversationalTestCase
- context 和 retrieval_context
- expected_output 使用

**02-metrics-overview.md**
- 指标分类（Custom, RAG, Agent, Safety）
- threshold 阈值设置
- 评分 0-1 标准化

**03-scoring.md**
- LLM-as-Judge 原理
- QAG（问答生成）
- G-Eval 技术

### 03 内置指标

**01-geval.md**
- GEval 自定义评估标准
- criteria 和 evaluation_steps
- 实用案例：正确性、语气、完整性

**02-answer-relevancy.md**
- 答案与问题相关性
- 使用场景

**03-faithfulness.md**
- 检测幻觉
- context 验证

**04-rag-metrics.md**
- Contextual Relevancy
- Contextual Precision
- Contextual Recall

**05-agent-metrics.md**
- Task Completion
- Tool Correctness
- Plan Adherence

### 04 进阶篇

**01-custom-metrics.md**
- 继承 BaseMetric
- 实现 measure 方法
- 自定义评分逻辑

**02-conversational.md**
- 多轮对话测试
- 知识保留检测
- 角色一致性

**03-async-evaluation.md**
- async_mode=True
- a_measure() 异步方法
- 并发评估

**04-component-level.md**
- @observe 装饰器
- 组件级追踪
- 白盒测试

### 05 集成篇

**01-pytest-integration.md**
- pytest + deepeval
- conftest.py 配置
- 测试组织

**02-ci-cd.md**
- GitHub Actions 集成
- 评估报告上传
- 失败阈值设置

**03-confident-ai.md**
- Confident AI 平台
- 回归测试
- 生产监控

### 06 迁移建议

**migration-guide.md**（单独一份迁移建议文档）
- 现有 evals/ 系统分析
- DeepEval 迁移路线图
- JSON 测试到 DeepEval 的映射方案
- 迁移步骤与注意事项
- 成本与收益分析
- 最佳实践建议

---

## 实施步骤

1. **创建目录结构**
   ```bash
   mkdir -p tutorials/deepeval/{01-getting-started,02-core-concepts,03-builtin-metrics,04-advanced,05-integration,06-project-practice,examples}
   ```

2. **编写 README.md**（教程概览）

3. **按顺序编写各章节**
   - 从 01-getting-started 开始
   - 每章包含理论 + 实践代码
   - 示例代码放入 examples/

4. **创建可运行示例**
   - examples/*.py 均可独立运行
   - 使用项目现有的 evals/.venv

5. **链接项目实践**
   - 展示如何评估 /api/chat
   - 复用现有测试用例格式

---

## 创建文件清单

按顺序创建以下文件：

### 第一阶段：基础结构
```
tutorials/deepeval/README.md                    # 教程总览
tutorials/deepeval/01-getting-started/README.md # 入门指南
tutorials/deepeval/01-getting-started/01-installation.md
tutorials/deepeval/01-getting-started/02-first-test.md
tutorials/deepeval/01-getting-started/03-run-tests.md
```

### 第二阶段：核心概念
```
tutorials/deepeval/02-core-concepts/README.md
tutorials/deepeval/02-core-concepts/01-test-cases.md
tutorials/deepeval/02-core-concepts/02-metrics-overview.md
tutorials/deepeval/02-core-concepts/03-scoring.md
```

### 第三阶段：内置指标
```
tutorials/deepeval/03-builtin-metrics/README.md
tutorials/deepeval/03-builtin-metrics/01-geval.md
tutorials/deepeval/03-builtin-metrics/02-answer-relevancy.md
tutorials/deepeval/03-builtin-metrics/03-faithfulness.md
tutorials/deepeval/03-builtin-metrics/04-rag-metrics.md
tutorials/deepeval/03-builtin-metrics/05-agent-metrics.md
```

### 第四阶段：进阶内容
```
tutorials/deepeval/04-advanced/README.md
tutorials/deepeval/04-advanced/01-custom-metrics.md
tutorials/deepeval/04-advanced/02-conversational.md
tutorials/deepeval/04-advanced/03-async-evaluation.md
tutorials/deepeval/04-advanced/04-component-level.md
```

### 第五阶段：集成与实践
```
tutorials/deepeval/05-integration/README.md
tutorials/deepeval/05-integration/01-pytest-integration.md
tutorials/deepeval/05-integration/02-ci-cd.md
tutorials/deepeval/05-integration/03-confident-ai.md
```

### 第六阶段：迁移建议
```
tutorials/deepeval/06-migration-guide.md            # 迁移建议文档（独立成章）
```

### 示例代码
```
tutorials/deepeval/examples/basic_test.py           # 基础测试
tutorials/deepeval/examples/geval_custom.py         # GEval 自定义
tutorials/deepeval/examples/rag_evaluation.py       # RAG 评估
tutorials/deepeval/examples/agent_evaluation.py     # Agent 评估
tutorials/deepeval/examples/conversational_test.py  # 多轮对话
```

---

## 参考资源

- [DeepEval 官方文档](https://deepeval.com/docs/getting-started)
- [DeepEval GitHub](https://github.com/confident-ai/deepeval)
- [DataCamp DeepEval 教程](https://www.datacamp.com/tutorial/deepeval)
- [Analytics Vidhya 指南](https://www.analyticsvidhya.com/blog/2025/01/llm-assessment-with-deepeval/)
