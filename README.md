# claude-automation

Automation scripts and Claude skill definitions for personal productivity workflows.
Currently: add tasks to Notion via a keyboard shortcut (macOS Shortcuts) or directly from Claude Code.

## Repo structure

```
claude-automation/
├── scripts/
│   ├── add_notion_task.sh   # Shell wrapper: dialog → Claude → Notion (macOS Shortcuts trigger)
│   └── notion_task.py       # Notion API client (schema, search-project, create)
├── claude-commands/
│   └── notion-task.md       # Claude skill: create a Notion task from natural language
├── .env.example             # Placeholder credentials — safe to commit
├── .gitignore
├── install.sh               # Bootstrap script for new machines
└── README.md
```

## New machine setup

```bash
git clone <this-repo> ~/code/claude-automation
cd ~/code/claude-automation
./install.sh
```

`install.sh` will:
- Copy `.env.example` → `~/.claude_env` (if not already present)
- Symlink each `claude-commands/*.md` → `~/.claude/commands/`
- Symlink each `scripts/*` → `~/code/scripts/`

Then edit `~/.claude_env` and fill in your real credentials.

## Credentials / security

- Real credentials live in `~/.claude_env` — never committed to git.
- `.env.example` contains placeholder values only and is safe to commit.
- `~/.claude_env` is sourced by `add_notion_task.sh` at runtime and optionally by your shell's rc file.

Required environment variables:
| Variable | Description |
|---|---|
| `NOTION_TOKEN` | Notion integration token (`ntn_...`) |
| `NOTION_DATABASE_ID` | ID of your Notion task database |

## How to add a new Claude skill

1. Create `claude-commands/<skill-name>.md` with the skill prompt.
2. Run `./install.sh` to symlink it into `~/.claude/commands/`.
3. Use it in Claude Code with `/skill-name`.

## How to add a new script

1. Add the script to `scripts/`.
2. Run `./install.sh` to symlink it into `~/code/scripts/` and mark it executable.
