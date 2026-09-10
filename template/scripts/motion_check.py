#!/usr/bin/env python3
"""动效密度自测（§9 动词驱动的持续动作）：渲染某组（或成片）低分辨率抽帧，量内容区逐帧变化，按分镜表镜头区间统计"静止帧"占比与最长静止。
用法：python3 scripts/motion_check.py G3            → 渲 G3 预览合成（含覆盖层）该组帧区间，每 3 帧一张、0.25 倍
     python3 scripts/motion_check.py --frames fin_frames   → 对成片逐帧目录（QC 用；每 3 帧取一张）
判据：静止帧（内容区 320×180 灰度平均变化 <0.35）占比 ≤40%，最长静止 ≤1.0 s。
注意：组级（低分辨率渲染）读数偏松，成片 fin_frames 复测才是最终判据；--frames 模式额外给出最长静止段的全分辨率变化像素数（真静 <800 / 小面积动作 <2500）。"""
import sys, os, re, glob, subprocess, tempfile, shutil
import numpy as np
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THR = 0.35
sb = open(f'{ROOT}/分镜表.md', encoding='utf-8').read()
shots = [(m.group(1), int(m.group(2)), int(m.group(3))) for m in re.finditer(r'^\| (SC\d\d)[^|]*\| (\d+)–(\d+) \|', sb, re.M)]

def load(path):
    im = Image.open(path).convert('L').resize((320, 180))
    return np.asarray(im).astype(int)[28:158, :]   # 去掉 HUD（y<110）与字幕/进度条（y>630）

if sys.argv[1] == '--frames':
    d = sys.argv[2]; files = sorted(glob.glob(f'{d}/f_*.jpg'))[::3]
    frames = [(int(re.search(r'f_(\d+)', f).group(1)), load(f)) for f in files]
    step = 3
else:
    comp = sys.argv[1]
    gs = [s for s in shots if True]
    # 组的镜头区间：从分镜表该组表格取（表头 "## Gn（"）
    m = re.search(r'## ' + comp + r'（.*?\n(.*?)(?=\n## |\n---)', sb, re.S)
    ids = re.findall(r'^\| (SC\d\d)', m.group(1), re.M) if m else []
    rng = [(a, b) for (i, a, b) in shots if i in ids]
    a, b = min(x[0] for x in rng), max(x[1] for x in rng)
    step = 3
    # 每次重新 bundle（代码在变、多组并发），用进程独占目录，跑完删除
    bundle = f'{ROOT}/build_dev_mc_{os.getpid()}'
    subprocess.run(['npx', 'remotion', 'bundle', 'src/index.ts', '--out-dir', bundle, '--log=error'], cwd=ROOT, check=True)
    out = tempfile.mkdtemp(prefix='motion_check_')
    subprocess.run(['npx', 'remotion', 'render', bundle, comp, out, '--sequence', '--image-format=jpeg', '--jpeg-quality=80', '--scale=0.5', f'--every-nth-frame={step}', f'--frames={a-1}-{b-1}', '--concurrency=4', '--log=error'], cwd=ROOT, check=True)
    files = sorted(glob.glob(f'{out}/*.jpeg') + glob.glob(f'{out}/*.jpg'))
    frames = [(a + i * step, load(f)) for i, f in enumerate(files)]
    shutil.rmtree(out, ignore_errors=True)
    shutil.rmtree(bundle, ignore_errors=True)

diffs = [(frames[i + 1][0], np.abs(frames[i + 1][1] - frames[i][1]).mean()) for i in range(len(frames) - 1)]
# 次级读数（只在 --frames 模式）：最长静止段内全分辨率"变化像素数"（>25 灰阶 / 3 帧）中位数——区分「真静」(<800) 与「小面积持续动作」(800–2500，如数据包 / 游标)
FULL = sys.argv[1] == '--frames'
def full_changed(s, e):
    d = sys.argv[2]
    imgs = [np.asarray(Image.open(f'{d}/f_{n:04d}.jpg').convert('L')).astype(int)[110:630, :] for n in range(s, e + 1, step)]
    ch = [int((np.abs(imgs[i + 1] - imgs[i]) > 25).sum()) for i in range(len(imgs) - 1)]
    return int(np.median(ch)) if ch else 0
print(f'{"shot":6s} {"len":>5s} {"still%":>7s} {"longest":>8s}  verdict' + ('   longest-run  fullres-changed-px  class' if FULL else ''))
bad = 0
for sid, a, b in shots:
    dd = [(f, v) for (f, v) in diffs if a <= f <= b]
    d = [v for (_, v) in dd]
    if len(d) < 3: continue
    still = sum(v < THR for v in d) / len(d) * 100
    run = best = 0; end = 0
    for i, v in enumerate(d):
        run = run + 1 if v < THR else 0
        if run > best: best = run; end = i
    longest = best * step / 30
    verdict = 'OK' if still <= 40 and longest <= 1.0 else ('✗ still>40%' if still > 40 else '') + (' ✗ hold>1s' if longest > 1.0 else '')
    if verdict != 'OK': bad += 1
    extra = ''
    if FULL and verdict != 'OK' and best > 0:
        s_ = dd[end - best + 1][0] - step; e_ = dd[end][0]
        cp = full_changed(max(a, s_), e_)
        cls = '真静' if cp < 800 else ('小面积动作' if cp < 2500 else '有动作')
        extra = f'   {max(a, s_)}-{e_}  {cp:6d}  {cls}'
    print(f'{sid:6s} {(b-a+1)/30:4.1f}s {still:6.0f}% {longest:7.1f}s  {verdict}{extra}')
print(f'shots failing: {bad}')
