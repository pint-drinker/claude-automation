#!/bin/zsh
# skills/notion-task/install.sh — install the notion-task skill
# Safe to run multiple times (idempotent). Also callable standalone.

set -e
SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"

mkdir -p "$HOME/.claude/commands" "$HOME/code/scripts"

ln -sf "$SKILL_DIR/notion-task.md" "$HOME/.claude/commands/notion-task.md"
echo "Linked ~/.claude/commands/notion-task.md → $SKILL_DIR/notion-task.md"

ln -sf "$SKILL_DIR/add_notion_task.sh" "$HOME/code/scripts/add_notion_task.sh"
echo "Linked ~/code/scripts/add_notion_task.sh → $SKILL_DIR/add_notion_task.sh"

ln -sf "$SKILL_DIR/notion_task.py" "$HOME/code/scripts/notion_task.py"
echo "Linked ~/code/scripts/notion_task.py → $SKILL_DIR/notion_task.py"

chmod +x "$SKILL_DIR/add_notion_task.sh" "$SKILL_DIR/notion_task.py"
