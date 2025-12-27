# 项目目录结构规范

## 三大内容目录

| 目录 | 用途 | 内容类型 |
|------|------|----------|
| `input/` | 原始输入 | 外部文档、会议记录、竞品材料 |
| `knowledge/` | 研究知识 | 分析报告、术语表、教程 |
| `docs/` | 项目文档 | 设计、需求、验收、运维 |

---

## input/ - 原始输入文档

外部输入的原始材料，待处理或参考。

```
input/
├── 产品文档/          # 产品规格、价格表
├── 会议记录/          # 会议录音和总结
├── 测试反馈/          # 用户测试反馈
├── 竞品宣传/          # 竞品分析材料
└── examples/          # 示例文件
```

---

## knowledge/ - 研究知识库

内部研究、分析和学习材料。

```
knowledge/
├── research/          # 研究分析报告
├── notes/             # 工作笔记
└── tutorials/         # 教程指南
```

---

## docs/ - 项目文档

项目管理和技术文档。

```
docs/
├── design/            # 设计文档
│   ├── architecture/  # 架构设计
│   ├── components/    # 组件设计
│   ├── ui/            # 界面设计
│   ├── api/           # API 设计
│   ├── acceptance/    # 验收标准
│   └── BDD/           # 行为驱动开发
├── requirements/      # 需求文档（PRD、URD）
├── analysis/          # 产品分析
├── records/           # 变更记录
├── reports/           # 项目报告
└── operations/        # 运维文档
```

---

## 查找指南

| 需要找... | 去哪里 |
|-----------|--------|
| 原始输入材料 | `input/` |
| 研究分析报告 | `knowledge/research/` |
| 架构设计 | `docs/design/architecture/` |
| 组件设计 | `docs/design/components/` |
| 界面设计 | `docs/design/ui/` |
| API 设计文档 | `docs/design/api/` |
| 用户需求 | `docs/requirements/` |
| BDD 测试场景 | `docs/design/BDD/` |
| 验收标准 | `docs/design/acceptance/` |
