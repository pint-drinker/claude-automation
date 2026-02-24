# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A collection of Claude Code skills and automation scripts for personal productivity. Each skill lives in its own directory under `skills/` and is installed into `~/.claude/commands/` so Claude Code discovers it as a slash command.

## Architecture

- **`skills/<name>/`** — self-contained skill directories. Each has:
  - `<name>.md` — skill prompt template using `__SKILL_DIR__` placeholders (resolved at install time via `sed`)
  - `install.sh` — renders the `.md` into `~/.claude/commands/<name>.md` with absolute paths
  - `uninstall.sh` — removes the rendered file from `~/.claude/commands/`
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
source skills/notion-task/.env && python3 skills/notion-task/notion_task.py schema
```

## Adding a new skill

1. Create `skills/<skill-name>/` with `<skill-name>.md`, `install.sh`, `uninstall.sh`, and `README.md`
2. Use `__SKILL_DIR__` in the `.md` file anywhere you need an absolute path to the skill directory
3. The `install.sh` must render the `.md` via `sed "s|__SKILL_DIR__|$SKILL_DIR|g"` into `~/.claude/commands/`
4. Keep credentials in a per-skill `.env` file with a committed `.env.example` template

## Conventions

- All shell scripts use `#!/bin/zsh` and `set -e`
- Python scripts use only stdlib (no pip dependencies) — `notion_task.py` uses `urllib.request` directly
- Skills are designed to work both interactively (via `/skill-name` in Claude Code) and headlessly (via `claude -p` from macOS Shortcuts)
