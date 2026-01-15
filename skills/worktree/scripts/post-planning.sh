#!/bin/bash
# 规划完成后执行的脚本
# 用法: post-planning.sh [plan_file_path]
# 检查 plan 文件是否在 .gitignore 中

PLAN_FILE="${1:-WORKTREE_PLAN.md}"

if [ -f "$PLAN_FILE" ]; then
  # 检查 .gitignore 是否包含 plan 文件
  if ! grep -qF "$PLAN_FILE" .gitignore 2>/dev/null; then
    echo "$PLAN_FILE" >> .gitignore
    echo "✅ 已添加 $PLAN_FILE 到 .gitignore"
  else
    echo "✅ $PLAN_FILE 已在 .gitignore 中"
  fi
else
  echo "⚠️  未找到 $PLAN_FILE"
fi
