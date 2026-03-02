---
name: notion-task
description: Create a task in my Notion database from natural language. Use when the user wants to add, capture, or track something in Notion.
disable-model-invocation: true
allowed-tools: Bash
---

Create a task in my Notion database from natural language.

Env file: __SKILL_DIR__/.env (set NOTION_TOKEN and NOTION_DATABASE_ID)

## Database fields
- **Task** — title (required)
- **Kanban** — select, one of: Waiting, Someday, Backlog, Next week, This week, Tomorrow, Today, In progress (required)
- **ProjectName** — plain string; resolved to a Project relation internally (optional)

## Kanban mapping
- "today", "now", "urgent" → Today
- "tomorrow" → Tomorrow
- "this week", "soon" → This week
- "next week" → Next week
- no time context → This week

## Steps

1. **Parse** the user's request: extract Task name, Kanban value, and optional project name.

2. **Create the task** in one call:
   ```bash
   set -a && source __SKILL_DIR__/.env && set +a && python3 __SKILL_DIR__/scripts/notion_task.py smart-create '<json>'
   ```
   JSON shape — include only fields you have values for:
   ```json
   {
     "Task": "Get groceries",
     "Kanban": "Today",
     "ProjectName": "Home projects"
   }
   ```
   The result JSON includes `url`, `title`, and `project_matched` (the resolved project name, or null).

3. **Confirm**: show the task title, Notion URL, resolved project name (if any), and time taken.

## Guidelines
- Always set **Task** and **Kanban** — these are required.
- If `project_matched` is null but the user named a project, say you couldn't find a matching project.
- If env vars are missing, remind the user to add NOTION_TOKEN and NOTION_DATABASE_ID to __SKILL_DIR__/.env.

## Diagnostics (debug only)
```bash
# Inspect schema / Kanban options
set -a && source __SKILL_DIR__/.env && set +a && python3 __SKILL_DIR__/scripts/notion_task.py schema

# Search projects manually
set -a && source __SKILL_DIR__/.env && set +a && python3 __SKILL_DIR__/scripts/notion_task.py search-project "query"
```
