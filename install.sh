#!/usr/bin/env bash
# Symlink the skills in this repo into your Claude Code skills directory so they
# are available from any working directory. Re-running is safe (idempotent).
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$REPO_DIR/skills"
DEST="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"

mkdir -p "$DEST"

for skill in "$SRC"/*/; do
  name="$(basename "$skill")"
  link="$DEST/$name"
  # Remove an existing symlink or empty stub before relinking.
  if [ -L "$link" ] || [ -e "$link" ]; then
    rm -rf "$link"
  fi
  ln -s "$skill" "$link"
  echo "linked $name -> $link"
done

echo "Done. Skills installed to $DEST"
