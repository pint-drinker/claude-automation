#!/bin/zsh
# install.sh — bootstrap claude-automation on a new machine
# Safe to run multiple times (idempotent).

set -e
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

# ── 1. Credentials file ───────────────────────────────────────────────────────
if [[ ! -f "$HOME/.claude_env" ]]; then
  cp "$REPO_DIR/.env.example" "$HOME/.claude_env"
  echo "Created ~/.claude_env from .env.example — fill in your real credentials."
else
  echo "~/.claude_env already exists — skipping."
fi

# ── 2. Claude commands (skill definitions) ───────────────────────────────────
mkdir -p "$HOME/.claude/commands"
for src in "$REPO_DIR/claude-commands/"*.md; do
  name="$(basename "$src")"
  dest="$HOME/.claude/commands/$name"
  ln -sf "$src" "$dest"
  echo "Linked ~/.claude/commands/$name → $src"
done

# ── 3. Scripts (preserve ~/code/scripts path used by macOS Shortcuts) ────────
mkdir -p "$HOME/code/scripts"
for src in "$REPO_DIR/scripts/"*; do
  name="$(basename "$src")"
  dest="$HOME/code/scripts/$name"
  ln -sf "$src" "$dest"
  chmod +x "$src"
  echo "Linked ~/code/scripts/$name → $src"
done

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
echo "Done. Next steps:"
echo "  1. Edit ~/.claude_env and add your real NOTION_TOKEN and NOTION_DATABASE_ID."
echo "  2. Ensure \$HOME/.local/bin/claude is installed (brew install claude or equivalent)."
echo "  3. Test: python3 ~/code/scripts/notion_task.py schema"
