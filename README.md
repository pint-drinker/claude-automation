# claude-automation

Automation scripts and Claude skill definitions for personal productivity workflows.
Currently: add tasks to Notion via a keyboard shortcut (macOS Shortcuts) or directly from Claude Code.

## Repo structure

```
claude-automation/
├── skills/
│   └── notion-task/
│       ├── notion-task.md        # Claude skill definition (has __SKILL_DIR__ placeholders)
│       ├── add_notion_task.sh    # macOS Shortcuts trigger
│       ├── notion_task.py        # Notion API client
│       ├── .env.example          # Credential template — copy to .env
│       ├── install.sh            # Renders skill file, installs to ~/.claude/commands/
│       ├── uninstall.sh          # Removes installed skill file
│       └── README.md
├── install.sh                    # Runs each skill's install.sh
└── README.md
```

## New machine setup

```bash
git clone <this-repo>
cd claude-automation
cp skills/notion-task/.env.example skills/notion-task/.env
# Fill in your real credentials in .env
./install.sh
```

## Credentials

Each skill keeps its own `.env` file (git-ignored) with the secrets it needs. See each skill's `.env.example` for the required variables.

## How to add a new skill

1. Create `skills/<skill-name>/` with at minimum:
   - `<skill-name>.md` — the Claude skill prompt (use `__SKILL_DIR__` for paths)
   - `install.sh` — renders the skill file into `~/.claude/commands/`
   - `uninstall.sh` — removes it
   - `README.md`
2. Run `./install.sh` (or `./skills/<skill-name>/install.sh` standalone).
3. Use it in Claude Code with `/<skill-name>`.
