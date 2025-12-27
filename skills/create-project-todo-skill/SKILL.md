---
name: create-project-todo-skill
description: 创建新任务文件（自动归档旧任务）
allowed-tools: Bash, Read, Write, Glob
---

创建新的 TODO.md 任务文件，自动归档当前任务。

## 参数

- `$ARGUMENTS`: 新任务的标题/主题（必填）

## 目录结构

```
.todo/
├── done/      # 已完成的任务
├── archive/   # 未完成但暂停的任务
└── README.md  # 目录说明
```

## 执行流程

1. **检查并初始化目录**
   如果 `.todo/` 不存在，创建目录结构

2. **归档当前 TODO.md**（如存在）
   - 读取内容，从标题提取主题关键词
   - 如果标记为"✅ 完成"或大部分任务已勾选 → `.todo/done/`
   - 否则 → `.todo/archive/`
   - 重命名格式：`{YYYY-MM-DD}-{主题关键词}.md`

3. **创建新 TODO.md**
   使用以下模板：

```markdown
# {标题}

## 功能目标

{简述目标}

## 当前状态: 🚧 规划中

---

## 需求详情

### 1. {需求1}

- [ ] {任务}

### 2. {需求2}

- [ ] {任务}

---

## 技术方案

{待补充}

---

## 实现步骤

### Phase 1: {阶段1}

- [ ] {任务}

---

## 历史任务

归档在 `.todo/` 目录。
```

4. **列出历史任务链接**
   在底部列出 `.todo/done/` 和 `.todo/archive/` 中的文件

## 目录初始化

```bash
mkdir -p .todo/done .todo/archive
```

创建 `.todo/README.md`：

```markdown
# 任务归档

## 目录说明

- `done/` - 已完成的任务
- `archive/` - 暂停/搁置的任务

## 命名规则

`{YYYY-MM-DD}-{主题关键词}.md`
```
