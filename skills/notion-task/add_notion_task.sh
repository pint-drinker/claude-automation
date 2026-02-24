#!/bin/zsh

# Show input dialog
INPUT=$(osascript -e 'text returned of (display dialog "What do you want to add to Notion?" default answer "" with title "Add Notion Task" buttons {"Cancel", "Add"} default button "Add")' 2>/dev/null)
[[ $? -ne 0 || -z "$INPUT" ]] && exit 0

# Load credentials from repo-local env file
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/.env"

# Build prompt from skill file and user input
SKILL=$(cat ~/.claude/commands/notion-task.md)
PROMPT="$SKILL

User request: $INPUT"

# Run claude non-interactively
RESULT=$($HOME/.local/bin/claude -p --model Haiku "$PROMPT" 2>&1)

# Parse JSON result safely with python3
TITLE=$(python3 -c "
import sys, json
try:
    d = json.loads(sys.stdin.read())
    print(d.get('title', 'Task added'))
except:
    print('Task added')
" <<< "$RESULT" 2>/dev/null)

[[ -z "$TITLE" ]] && TITLE="Task added"

# Sanitize for AppleScript: replace double quotes with single quotes
SAFE_TITLE="${TITLE//\"/\'}"

osascript -e "display notification \"$SAFE_TITLE\" with title \"Added to Notion\""
