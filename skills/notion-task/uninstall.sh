#!/bin/zsh
# skills/notion-task/uninstall.sh — remove the notion-task skill
# Removes only what install.sh created. Safe to run multiple times.

rm -rf "$HOME/.claude/skills/notion-task"
echo "Removed ~/.claude/skills/notion-task/"

# Clean up legacy path if still present
rm -f "$HOME/.claude/commands/notion-task.md"
