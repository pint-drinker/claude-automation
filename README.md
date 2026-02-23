# claude-automation

Automation scripts and Claude skill definitions for personal productivity workflows.
Currently: add tasks to Notion via a keyboard shortcut (macOS Shortcuts) or directly from Claude Code.

## Repo structure

```
claude-automation/
├── skills/
│   └── notion-task/
│       ├── notion-task.md        # Claude skill definition (symlinked to ~/.claude/commands/)
│       ├── add_notion_task.sh    # macOS Shortcuts trigger (symlinked to ~/code/scripts/)
│       ├── notion_task.py        # Notion API client (symlinked to ~/code/scripts/)
│       ├── install.sh            # installs only this skill
│       └── README.md             # explains this skill
├── .env.example                  # Placeholder credentials — safe to commit
├── .gitignore
├── install.sh                    # install-all: env setup + calls each skill's install.sh
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
- Run each `skills/*/install.sh` to create symlinks and set permissions

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

## How to add a new skill

1. Create `skills/<skill-name>/` with at minimum:
   - `<skill-name>.md` — the Claude skill prompt
   - `install.sh` — creates symlinks and sets permissions
   - `README.md` — explains what the skill does
2. Run `./install.sh` (or `./skills/<skill-name>/install.sh` standalone).
3. Use it in Claude Code with `/<skill-name>`.
