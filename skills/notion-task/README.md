# notion-task skill

Adds a task to your Notion database from natural language — via Claude Code (`/notion-task`) or a macOS Shortcut.

## What it does

1. **Claude Code trigger**: type `/notion-task` in Claude Code, describe your task, and Claude calls `notion_task.py` to create it in Notion.
2. **macOS Shortcut trigger**: a Shortcut runs `add_notion_task.sh`, which shows an input dialog, sends the text to `claude -p`, and displays a notification with the created task title.

## Required environment variables

Set these in `~/.claude_env`:

| Variable | Description |
|---|---|
| `NOTION_TOKEN` | Notion integration token (`ntn_...`) |
| `NOTION_DATABASE_ID` | ID of your Notion task database |

## Files

| File | Purpose |
|---|---|
| `notion-task.md` | Claude skill definition — symlinked to `~/.claude/commands/` |
| `add_notion_task.sh` | macOS Shortcuts trigger — symlinked to `~/code/scripts/` |
| `notion_task.py` | Notion API client (schema, search-project, create) — symlinked to `~/code/scripts/` |
| `install.sh` | Installs this skill (creates symlinks, sets permissions) |

## Install

From the repo root:
```bash
./install.sh          # installs all skills
```

Or install only this skill:
```bash
./skills/notion-task/install.sh
```

## Test

```bash
python3 ~/code/scripts/notion_task.py schema
```
