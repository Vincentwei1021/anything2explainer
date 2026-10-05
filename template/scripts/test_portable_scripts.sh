#!/usr/bin/env bash
# Smoke-check portable script syntax (#16).
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
for s in new_project.sh still.sh render.sh preview.sh; do
  bash -n "$HERE/$s"
done
# Frame list parsing (still.sh core)
FRAMES="1,2, 3"
IFS=',' read -r -a FRAME_LIST <<< "$FRAMES"
got=""
for N in "${FRAME_LIST[@]}"; do
  N=$(echo "$N" | tr -d '[:space:]')
  got+="$N "
done
[ "$got" = "1 2 3 " ] || { echo "frame split failed: '$got'"; exit 1; }
head -1 "$HERE/new_project.sh" | grep -q 'env bash' || { echo "shebang"; exit 1; }
echo ok
