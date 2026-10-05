#!/usr/bin/env bash
# Create a project from the template: new_project.sh <dest_dir> <slug>
set -euo pipefail
HERE=$(cd "$(dirname "$0")/.." && pwd)
DEST=${1:-}; SLUG=${2:-video}
[ -n "$DEST" ] || { echo "usage: $0 <dest_dir> <slug>"; exit 1; }
[ -f "$HERE/src/config.ts" ] && [ -d "$HERE/src/common" ] || {
  echo "找不到模板（$HERE 不像 template/），请从 template/scripts/ 里运行本脚本"
  exit 1
}
case "$SLUG" in
  ''|*[!A-Za-z0-9_-]*) echo "slug 只能用字母/数字/-/_，收到：$SLUG"; exit 1;;
esac
mkdir -p "$DEST"
# Prefer rsync when present; fall back to cp for Git Bash / Windows without rsync (#16).
if command -v rsync >/dev/null 2>&1; then
  rsync -a --exclude node_modules --exclude 'build*' --exclude renders --exclude fin_frames \
    --exclude stills --exclude 'audio/cache' "$HERE/" "$DEST/"
else
  # cp -a is not portable; -R preserves structure. Exclude heavy dirs after copy.
  cp -R "$HERE/." "$DEST/"
  rm -rf "$DEST/node_modules" "$DEST"/build* "$DEST/renders" "$DEST/fin_frames" \
    "$DEST/stills" "$DEST/audio/cache" 2>/dev/null || true
fi
# portable in-place edit: `-i.bak` + rm works on both BSD/macOS and GNU/Linux sed
sed -i.bak "s/slug: 'demo'/slug: '$SLUG'/" "$DEST/src/config.ts" && rm -f "$DEST/src/config.ts.bak"
mkdir -p "$DEST/public/assets/$SLUG" "$DEST/script" "$DEST/research" "$DEST/qc" "$DEST/stills" "$DEST/renders"
cd "$DEST" && npm install --silent && npx tsc --noEmit && echo "project ready: $DEST (slug=$SLUG)"
