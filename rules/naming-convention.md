# Claude Code 命名规范

## 核心规则

| 类型 | 后缀 | 示例 |
|------|------|------|
| Skill | `-skill` | `create-project-todo-skill` |
| Agent | `-agent` | `code-review-agent` |
| Command | 无后缀 | `create-project-todo` |

## 格式

- 使用连字符（kebab-case）
- 全小写
- 语义清晰
- **Command 以动作开头**（如 `create-`、`archive-`、`sync-`）

## 目的

通过后缀区分类型，避免同名冲突：
- `/create-project-todo`（Command）调用 `create-project-todo-skill`（Skill）
- 名称相似但不会冲突
