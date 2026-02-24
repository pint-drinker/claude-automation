#!/bin/zsh
# skills/notion-task/uninstall.sh — remove the notion-task skill
# Removes only what install.sh created. Safe to run multiple times.

rm -f "$HOME/.claude/commands/notion-task.md"
echo "Removed ~/.claude/commands/notion-task.md"
