#!/bin/zsh
# 出 still：still.sh <Comp: Video|Overlay|G1..G8> <帧号列表 1 起,逗号分隔> <输出目录(绝对路径)> [tag]
# ⚠ 每个构建组只用一个 tag（如 g3），不要每次换新 tag（每个 bundle ≈40MB）；改代码会自动重建，FORCE_BUNDLE=1 强制。
set -e
ROOT=$(cd "$(dirname "$0")/.." && pwd); cd "$ROOT"
COMP=$1; FRAMES=$2; OUT=$3; TAG=${4:-$COMP}
[ -n "$COMP" ] && [ -n "$FRAMES" ] && [ -n "$OUT" ] || { echo "usage: still.sh <Comp> <frames> <out_dir_abs> [tag]"; exit 1; }
B=build_dev_$TAG
if [ "${FORCE_BUNDLE:-0}" = 1 ] || [ ! -d "$B" ] || [ -n "$(find src -newer "$B" -name '*.tsx' -o -newer "$B" -name '*.ts' 2>/dev/null | head -1)" ]; then
  rm -rf "$B"
  npx remotion bundle src/index.ts --out-dir "$B" --log=error
fi
mkdir -p "$OUT"
for N in ${(s:,:)FRAMES}; do
  npx remotion still "$B" "$COMP" "$OUT/f_$(printf %04d $N).png" --frame=$((N-1)) --timeout=${RTIMEOUT:-300000} --log=error
done
# 清理 4 小时以上没动过的 remotion 临时 bundle（只清明显已死的：这台机器上可能有别的
# remotion 项目/agent 正在渲染，短阈值会删掉别人正在用的 bundle）。CLEAN_TMP=0 可关闭。
[ "${CLEAN_TMP:-1}" = 1 ] && find "${TMPDIR:-/tmp}" -maxdepth 1 -name 'remotion-webpack-bundle-*' -mmin +240 -exec rm -rf {} + 2>/dev/null
ls "$OUT" | wc -l
