# notion-task skill

Adds a task to your Notion database from natural language — via Claude Code (`/notion-task`) or a macOS Shortcut.

## What it does

1. **Claude Code trigger**: type `/notion-task` in Claude Code, describe your task, and Claude calls `notion_task.py` to create it in Notion.
2. **Command line trigger**: echo "add task to kelsey project to call her today" | ./add_notion_task.sh
3. **macOS Shortcut**: a Shortcut runs `add_notion_task.sh`, which accepts dictated text via stdin (voice) or shows an input dialog (keyboard), then sends the text to `claude -p` and displays a notification with the created task title.

## Credentials

Copy `.env.example` to `.env` in this directory and fill in your values (git-ignored, never committed):

```bash
cp skills/notion-task/.env.example skills/notion-task/.env
```

| Variable | Description |
|---|---|
| `NOTION_TOKEN` | Notion integration token (`ntn_...`) |
| `NOTION_DATABASE_ID` | ID of your Notion task database |

## Files

| File | Purpose |
|---|---|
| `notion-task.md` | Skill prompt with `__SKILL_DIR__` placeholders — rendered at install time |
| `add_notion_task.sh` | Shortcut trigger — reads stdin if piped (voice), otherwise shows an input dialog |
| `notion_task.py` | Notion API client (schema, search-project, create) |
| `.env.example` | Template for credentials — copy to `.env` and fill in |
| `install.sh` | Renders skill file into `~/.claude/commands/`, sets permissions |
| `uninstall.sh` | Removes the installed skill file — leaves nothing behind |

## Install

```bash
./skills/notion-task/install.sh
```

**What it touches outside this directory:**
- `~/.claude/commands/notion-task.md` — 1 rendered copy (required for Claude Code to discover the skill)

## Uninstall

```bash
./skills/notion-task/uninstall.sh
```

Removes `~/.claude/commands/notion-task.md`. Nothing else is left behind.

## Setting up the macOS Shortcut

The same script handles both voice (piped stdin) and dialog (keyboard) input.

### Dialog (keyboard) Shortcut

1. Open **Shortcuts** app → click **+** to create a new shortcut.
2. Add a **Run Shell Script** action:
   - Shell: `/bin/zsh`
   - Input: none
   - Script body:
     ```
     /bin/zsh /path/to/claude-automation/skills/notion-task/add_notion_task.sh
     ```
3. Name the shortcut (e.g. "Add Notion Task") and assign a global keyboard shortcut (e.g. `⌃⌥N`).

### Voice Shortcut

1. Open **Shortcuts** app → click **+** to create a new shortcut.
2. Add a **Dictate Text** action.
3. Add a **Run Shell Script** action:
   - Shell: `/bin/zsh`
   - Input: **Shortcut Input** (passes the dictated text via stdin)
   - Script body:
     ```
     /bin/zsh /path/to/claude-automation/skills/notion-task/add_notion_task.sh
     ```
4. Name the shortcut (e.g. "Add Notion Task by Voice") and assign a global keyboard shortcut.

> **Note:** macOS may prompt for accessibility/automation permissions the first time. Allow Shortcuts to control Script Editor / System Events when asked.

## Test

```bash
python3 /path/to/claude-automation/skills/notion-task/notion_task.py schema
```
