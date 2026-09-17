#!/usr/bin/env bash
# Build hugo-src and sync the public files to the repository root
# (GitHub Pages serves the username.github.io root).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SRC="$ROOT/hugo-src"
TMP="$ROOT/.public-tmp"

if ! command -v hugo >/dev/null 2>&1; then
  echo "hugo is required" >&2
  exit 1
fi

rm -rf "$TMP"
hugo --minify -s "$SRC" -d "$TMP"

# Keep source / git metadata; replace generated site files.
find "$ROOT" -mindepth 1 -maxdepth 1 \
  ! -name '.git' \
  ! -name '.github' \
  ! -name '.gitmodules' \
  ! -name '.gitignore' \
  ! -name 'hugo-src' \
  ! -name 'README.md' \
  ! -name '.public-tmp' \
  -exec rm -rf {} +

cp -a "$TMP"/. "$ROOT"/
rm -rf "$TMP"

echo "Published Hugo site to $ROOT"
