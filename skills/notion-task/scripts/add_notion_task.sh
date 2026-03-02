#!/bin/zsh

# Get input: stdin if piped (e.g. from Dictate Text in Shortcuts), otherwise prompt with dialog
if [[ ! -t 0 ]]; then
  INPUT="$(cat)"
else
  INPUT=$(osascript -e 'text returned of (display dialog "What do you want to add to Notion?" default answer "" with title "Add Notion Task" buttons {"Cancel", "Add"} default button "Add")' 2>/dev/null)
  [[ $? -ne 0 || -z "$INPUT" ]] && exit 0
fi

INPUT="${INPUT## }"
INPUT="${INPUT%% }"
[[ -z "$INPUT" ]] && exit 0

# Load credentials from repo-local env file; set -a exports all vars so they
# cascade through to claude's subprocess and its bash tool calls (notion_task.py)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
set -a
source "$SCRIPT_DIR/../.env"
set +a

# Build prompt from skill file (strip YAML frontmatter before passing to claude -p)
SKILL=$(python3 -c "
import sys, pathlib
text = pathlib.Path(sys.argv[1]).read_text()
if text.startswith('---'):
    end = text.index('---', 3)
    text = text[end+3:].lstrip()
print(text, end='')
" "$HOME/.claude/skills/notion-task/SKILL.md")
PROMPT="$SKILL

User request: $INPUT"

# Run claude non-interactively; --dangerously-skip-permissions allows bash tool
# calls (e.g. python3 notion_task.py) to execute without interactive approval prompts
RESULT=$($HOME/.local/bin/claude -p --dangerously-skip-permissions --model haiku "$PROMPT" 2>&1)

# Extract Notion URL from result (notion_task.py returns it in its JSON output)
NOTION_URL=$(python3 -c "
import sys, re
text = sys.stdin.read()
m = re.search(r'https://www\.notion\.so/[\w/-]+', text)
if m:
    print(m.group())
" <<< "$RESULT" 2>/dev/null)

# Notify with full result output; use heredoc to avoid AppleScript quoting issues
osascript <<APPLESCRIPT
display notification "$(echo "$RESULT" | tr -d '\"\\' | head -c 300)" with title "Added to Notion"
APPLESCRIPT

echo "$RESULT"
