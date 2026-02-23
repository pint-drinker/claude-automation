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

# ── 2. Install each skill ─────────────────────────────────────────────────────
for skill_installer in "$REPO_DIR/skills/"*/install.sh; do
  echo ""
  echo "── Installing $(basename "$(dirname "$skill_installer")") ──"
  source "$skill_installer"
done

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
echo "Done. Next steps:"
echo "  1. Edit ~/.claude_env and add your real NOTION_TOKEN and NOTION_DATABASE_ID."
echo "  2. Ensure \$HOME/.local/bin/claude is installed (brew install claude or equivalent)."
echo "  3. Test: python3 ~/code/scripts/notion_task.py schema"
