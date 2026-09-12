#!/usr/bin/env bash
# Symlink the skills in this repo into the Claude Code AND Codex skills directories so they
# are available from any working directory, in either tool. Re-running is safe (idempotent),
# and it prunes links left behind when a skill is renamed.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$REPO_DIR/skills"

# Override either destination to install elsewhere; set one to "" to skip that tool.
CLAUDE_SKILLS_DIR="${CLAUDE_SKILLS_DIR-$HOME/.claude/skills}"
CODEX_SKILLS_DIR="${CODEX_SKILLS_DIR-$HOME/.codex/skills}"

install_into() {
  dest="$1"
  [ -n "$dest" ] || return 0
  mkdir -p "$dest"

  # Drop symlinks that point into this repo but no longer resolve (renamed or deleted skill).
  for link in "$dest"/*; do
    [ -L "$link" ] || continue
    case "$(readlink "$link")" in
      "$SRC"/*) [ -e "$link" ] || { rm -f "$link"; echo "pruned stale $(basename "$link") in $dest"; } ;;
    esac
  done

  for skill in "$SRC"/*/; do
    name="$(basename "$skill")"
    link="$dest/$name"
    # Remove an existing symlink or empty stub before relinking.
    if [ -L "$link" ] || [ -e "$link" ]; then
      rm -rf "$link"
    fi
    ln -s "$skill" "$link"
    echo "linked $name -> $link"
  done
  echo "Done. Skills installed to $dest"
}

install_into "$CLAUDE_SKILLS_DIR"
install_into "$CODEX_SKILLS_DIR"
