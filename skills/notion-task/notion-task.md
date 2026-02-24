Create a task in my Notion database from natural language.

**Model preference:** This is a simple, structured task. Use the fastest available model (e.g., Haiku) if the caller supports model selection.

Env file: __SKILL_DIR__/.env (set NOTION_TOKEN and NOTION_DATABASE_ID)

## Database fields that matter
- **Task** — title (required)
- **Kanban** — select: Waiting, Someday, Backlog, Next week, This week, Tomorrow, Today, In progress
- **Project** — relation to Projects database (optional, set via ID from search-project)

## Steps

1. **Get Kanban options** (1 API call):
   ```bash
   source __SKILL_DIR__/.env && python3 __SKILL_DIR__/notion_task.py schema
   ```
   Use this to confirm valid Kanban values. Skip if the user's intent maps obviously to one of the known options above.

2. **Find the project** — only if the user mentions a project (3 API calls):
   ```bash
   source __SKILL_DIR__/.env && python3 __SKILL_DIR__/notion_task.py search-project "query term"
   ```
   Returns a JSON array of `{id, title}` matches. Use the best matching entry's `id` as the Project value.
   If no match is found, create the task without a Project and mention it.

3. **Create the task** (2 API calls):
   ```bash
   source __SKILL_DIR__/.env && python3 __SKILL_DIR__/notion_task.py create '<json>'
   ```
   JSON shape — include only fields you have values for:
   ```json
   {
     "Task": "Get groceries",
     "Kanban": "Today",
     "Project": ["<project-page-id>"]
   }
   ```

4. Confirm success: show the task title and the Notion URL from the result.

## Guidelines
- Always set **Task** and **Kanban** — these are the minimum required fields.
- Kanban reflects urgency/timing: map "today", "now", "urgent" → "Today"; "tomorrow" → "Tomorrow"; "this week" → "This week"; no time context → "Backlog".
- Skip schema fetch if Kanban intent is unambiguous.
- Never pre-fetch all relation entries — use search-project only when needed.
- If env vars are missing, remind the user to add NOTION_TOKEN and NOTION_DATABASE_ID to __SKILL_DIR__/.env (copy from .env.example).
