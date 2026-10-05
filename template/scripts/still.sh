#!/usr/bin/env bash
# still.sh <Comp: Video|Overlay|G1..G8> <frames 1-based, comma-separated> <out_dir_abs> [tag]
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd); cd "$ROOT"
COMP=${1:-}; FRAMES=${2:-}; OUT=${3:-}; TAG=${4:-$COMP}
[ -n "$COMP" ] && [ -n "$FRAMES" ] && [ -n "$OUT" ] || {
  echo "usage: still.sh <Comp> <frames> <out_dir_abs> [tag]"; exit 1
}
B=build_dev_$TAG
[ -d "$B" ] || npx remotion bundle src/index.ts --out-dir "$B" --log=error
mkdir -p "$OUT"
IFS=',' read -r -a FRAME_LIST <<< "$FRAMES"
for N in "${FRAME_LIST[@]}"; do
  N=$(echo "$N" | tr -d '[:space:]')
  [ -n "$N" ] || continue
  npx remotion still "$B" "$COMP" "$OUT/f_$(printf %04d "$N").png" --frame=$((N-1)) --log=error
done
[ "${CLEAN_TMP:-1}" = 1 ] && find "${TMPDIR:-/tmp}" -maxdepth 1 -name 'remotion-webpack-bundle-*' -mmin +240 -exec rm -rf {} + 2>/dev/null || true
ls "$OUT" | wc -l
