#!/bin/zsh
# install.sh — bootstrap claude-automation on a new machine
# Safe to run multiple times (idempotent).

set -e
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

# ── Install each skill ─────────────────────────────────────────────────────
for skill_installer in "$REPO_DIR/skills/"*/install.sh; do
  echo ""
  echo "── Installing $(basename "$(dirname "$skill_installer")") ──"
  source "$skill_installer"
done

echo ""
echo "Done."
