# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A collection of Claude Code skills and automation scripts for personal productivity. Each skill lives in its own directory under `skills/` and is installed into `~/.claude/commands/` so Claude Code discovers it as a slash command.

## Architecture

- **`skills/<name>/`** — self-contained skill directories. Each has:
  - `SKILL.md` — skill prompt template with YAML frontmatter and `__SKILL_DIR__` placeholders (resolved at install time via `sed`)
  - `install.sh` — renders `SKILL.md` into `~/.claude/skills/<name>/SKILL.md` with absolute paths
  - `uninstall.sh` — removes the rendered skill from `~/.claude/skills/<name>/`
  - `scripts/` — supporting scripts (e.g. Python helpers, shell entry points)
  - `.env` / `.env.example` — per-skill credentials (git-ignored)
- **`install.sh`** (root) — loops through all `skills/*/install.sh` files; idempotent

The `__SKILL_DIR__` placeholder pattern is the key convention: skill prompts reference local scripts via this placeholder, and `install.sh` replaces it with the absolute path at install time.

## Commands

```bash
# Install all skills (idempotent)
./install.sh

# Install/uninstall a single skill
./skills/notion-task/install.sh
./skills/notion-task/uninstall.sh

# Test the Notion API connection
source skills/notion-task/.env && python3 skills/notion-task/scripts/notion_task.py schema
```

## Adding a new skill

1. Create `skills/<skill-name>/` with `SKILL.md`, `install.sh`, `uninstall.sh`, `README.md`, and a `scripts/` subdirectory for supporting scripts
2. Add YAML frontmatter to `SKILL.md` (`name`, `description`, `disable-model-invocation`, `allowed-tools`)
3. Use `__SKILL_DIR__` in `SKILL.md` anywhere you need an absolute path to the skill directory
4. The `install.sh` must render `SKILL.md` via `sed "s|__SKILL_DIR__|$SKILL_DIR|g"` into `~/.claude/skills/<skill-name>/SKILL.md`
4. Keep credentials in a per-skill `.env` file with a committed `.env.example` template

## Conventions

- All shell scripts use `#!/bin/zsh` and `set -e`
- Python scripts use only stdlib (no pip dependencies) — `notion_task.py` uses `urllib.request` directly
- Skills are designed to work both interactively (via `/skill-name` in Claude Code) and headlessly (via `claude -p` from macOS Shortcuts)
