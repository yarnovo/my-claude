---
name: archive-project-todo-skill
description: 归档当前任务文件（不创建新任务）
allowed-tools: Bash, Read, Write, Glob
---

归档当前 TODO.md 到 `.todo/` 目录，不创建新任务。

## 参数

- `$ARGUMENTS`（可选）：
  - `done` 或 `完成` - 强制归档到 done/
  - `archive` 或 `暂停` - 强制归档到 archive/
  - 空 - 自动判断

## 执行流程

1. **检查 TODO.md 是否存在**
   不存在则提示用户

2. **读取当前 TODO.md**
   - 获取内容和创建时间
   - 从标题提取主题关键词

3. **确定归档位置**
   - 如果参数指定 → 使用指定位置
   - 如果标记为"✅ 完成"或大部分任务已勾选 → `.todo/done/`
   - 否则 → `.todo/archive/`

4. **执行归档**
   - 重命名格式：`{YYYY-MM-DD}-{主题关键词}.md`
   - 移动到目标目录

## 输出格式

```
✅ 任务已归档！

📁 位置: .todo/done/2025-12-27-model-selector.md
📊 状态: 已完成（8/10 任务勾选）
```
