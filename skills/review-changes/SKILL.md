---
name: review-changes
description: 生成本地 Git 修改的详细自述文档，方便提交前审查
allowed-tools: Bash, Read, Write
---

请帮我生成当前 Git 本地修改的详细自述文档。

## 步骤

1. **获取 Git 状态和 Diff**
   ```bash
   git status
   git diff          # 未暂存的修改
   git diff --staged # 已暂存的修改
   ```

2. **生成变更文档**
   在项目根目录创建 `CHANGES_REVIEW.md`，包含以下内容：

   ```markdown
   # 本地修改审查

   > 生成时间: {当前时间}
   > 分支: {当前分支}

   ## 修改概要

   {简要总结本次修改的目的和范围}

   ## 文件变更列表

   | 状态 | 文件路径 | 说明 |
   |------|----------|------|
   | M/A/D | path/to/file | 简要说明 |

   ## 详细变更

   ### `path/to/file1`

   **变更类型**: 修改/新增/删除

   **变更说明**: {详细描述这个文件的修改内容和原因}

   **关键代码变更**:
   ```diff
   {关键的 diff 片段}
   ```

   ### `path/to/file2`
   ...

   ## 潜在影响

   {分析本次修改可能带来的影响}

   ## 建议的提交消息

   ```
   {根据 Conventional Commits 格式建议的提交消息}
   ```
   ```

3. **确保文件被 Git 忽略**
   检查 `.gitignore` 是否包含 `CHANGES_REVIEW.md`：
   - 如果没有，在 `.gitignore` 末尾添加一行 `CHANGES_REVIEW.md`
   - 如果文件不存在，创建 `.gitignore` 并添加该条目

## 要求

- 使用中文撰写文档
- 对每个修改的文件给出清晰的说明
- 提取关键的 diff 片段展示（不要完整复制大段代码）
- 分析修改的目的和潜在影响
- 建议的提交消息遵循 Conventional Commits 规范
