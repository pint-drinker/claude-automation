#!/bin/zsh
# skills/notion-task/install.sh — install the notion-task skill
# Safe to run multiple times (idempotent). Also callable standalone.
#
# What this touches outside the repo:
#   ~/.claude/commands/notion-task.md  (rendered copy with resolved paths)

set -e
SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"

# Render skill file with resolved paths into ~/.claude/commands/
mkdir -p "$HOME/.claude/commands"
rm -f "$HOME/.claude/commands/notion-task.md"
sed "s|__SKILL_DIR__|$SKILL_DIR|g" "$SKILL_DIR/notion-task.md" > "$HOME/.claude/commands/notion-task.md"
echo "Installed ~/.claude/commands/notion-task.md"

chmod +x "$SKILL_DIR/add_notion_task.sh" "$SKILL_DIR/notion_task.py"

if [[ ! -f "$SKILL_DIR/.env" ]]; then
  echo ""
  echo "⚠  No .env found. Copy and fill in your credentials:"
  echo "   cp $SKILL_DIR/.env.example $SKILL_DIR/.env"
fi
