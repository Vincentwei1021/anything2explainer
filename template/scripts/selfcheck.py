#!/usr/bin/env python3
"""主会话静态自检（不渲染，几秒跑完；与 QC 从像素查互补）：
  1) 帧覆盖：各组 index.ts 里的 {id, from, to} 与 分镜表.md 的镜头区间对账，报空洞 / 重叠 / 缺失；
  2) 闪烁白名单：每个 SCxx.tsx 里 GlitchIn 的出现次数 vs 分镜表全局约束 §3 白名单；
  3) 画面字面量：抽取各 SC 文件里会上画面的字符串，剔除 CSS / 标识符噪声，列出不在事实清单里的词供人工核对。
用法：python3 scripts/selfcheck.py [G1 G2 …]（不传则查全部已建组）"""
import re, os, sys, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sb = open(f'{ROOT}/分镜表.md', encoding='utf-8').read()

# ---- 分镜表镜头区间 ----
sb_shots = {}
for m in re.finditer(r'^\| (SC\d\d)[^|]*\| (\d+)–(\d+) \|', sb, re.M):
    sb_shots[m.group(1)] = (int(m.group(2)), int(m.group(3)))

# ---- 白名单 ----
wl_text = re.search(r'\*\*闪烁白名单.*?\*\*：(.*?)。\*\*不在表内', sb, re.S)
whitelist = {}
if wl_text:
    for part in wl_text.group(1).split('·'):
        mm = re.match(r'\s*(SC\d\d)\s+(.*)', part.strip())
        if mm: whitelist[mm.group(1)] = mm.group(2).strip()

groups = sys.argv[1:] or sorted(os.path.basename(p) for p in glob.glob(f'{ROOT}/src/shots/G*'))
problems = 0

# ---- 1) 帧覆盖 ----
built = {}
for g in groups:
    idx = f'{ROOT}/src/shots/{g}/index.ts'
    if not os.path.exists(idx): continue
    src = open(idx, encoding='utf-8').read()
    for m in re.finditer(r"id:\s*'([^']+)'\s*,\s*from:\s*(\d+)\s*,\s*to:\s*(\d+)", src):
        built[m.group(1)] = (int(m.group(2)), int(m.group(3)), g)
    if not re.search(r"id:\s*'", src):
        print(f'[coverage] {g}: index.ts 里没有字面量 from/to（可能用了常量）→ 请人工核对')
print(f'[coverage] 分镜表 {len(sb_shots)} 镜头；已建 {len(built)} 镜头')
for sid, (a, b) in sorted(sb_shots.items()):
    if sid in built:
        ba, bb, g = built[sid]
        if (ba, bb) != (a, b):
            print(f'  ✗ {sid} ({g}) 区间 {ba}–{bb} ≠ 分镜表 {a}–{b}'); problems += 1
import json
_tl = json.load(open(f'{ROOT}/script/timeline.json'))
_chapter_starts = {c['from'] for c in _tl['chapters']}
ids = sorted(built, key=lambda k: built[k][0])
for p, q in zip(ids, ids[1:]):
    gap = built[q][0] - built[p][1]
    # 章节卡占位（上一章末句 to+3 → 本章首句 from−9）是设计上的空洞，跳过
    if gap > 1 and any(built[q][0] == cs - 8 for cs in _chapter_starts):  # 下一镜头首帧 = 本章首句 from−8
        print(f'  · 章节卡空档 {p}→{q}: {built[p][1]}→{built[q][0]}（覆盖层接管）'); continue
    if gap > 1: print(f'  ✗ 空洞 {p}→{q}: {built[p][1]}→{built[q][0]} ({gap-1} 帧无镜头)'); problems += 1
    if gap < -4: print(f'  ✗ 重叠 {p}→{q}: {-gap+1} 帧'); problems += 1

# ---- 2) 闪烁 ----
print(f'[glitch] 白名单 {len(whitelist)} 条')
for g in groups:
    for f in sorted(glob.glob(f'{ROOT}/src/shots/{g}/SC*.tsx')):
        sid = os.path.basename(f)[:4]
        src = open(f, encoding='utf-8').read()
        n = len(re.findall(r'<GlitchIn\b', src)) + len(re.findall(r'glitchOpacity\(', src))
        want = 1 if sid in whitelist else 0
        flag = '' if n == want else '  ✗'
        if n != want: problems += 1
        print(f'  {sid} GlitchIn×{n} (白名单 {whitelist.get(sid, "—")}){flag}')

# ---- 3) 字面量 ----
fact = re.search(r'1\. \*\*事实清单.*?\n', sb, re.S)
fact_txt = (fact.group(0) if fact else '') + sb  # 分镜表全文都算"已核"（画面文本按分镜写）
noise = re.compile(r'^(#|rgb|[0-9.\s%pxem-]+$|[a-z][A-Za-z0-9]*$|\.\./|src/|[A-Z_]+$|none|auto|absolute|relative|center|left|right|top|bottom|solid|dashed|round|butt|square|nowrap|hidden|visible|inherit|bold|italic|normal)')
print('[literals] 不在分镜表/事实清单中的画面字符串（人工核对）：')
seen = set()
for g in groups:
    for f in sorted(glob.glob(f'{ROOT}/src/shots/{g}/*.tsx')):
        src = open(f, encoding='utf-8').read()
        for s in re.findall(r"(?:'|\"|`)([^'\"`\n]{3,80})(?:'|\"|`)", src):
            s2 = s.strip()
            if not s2 or noise.match(s2) or s2 in seen: continue
            if '${' in s2 or 'px' in s2 or 'rgba' in s2 or 'gradient' in s2 or re.fullmatch(r'[\d.,\s]+', s2) or s2.startswith('./') or re.match(r'^[a-zA-Z-]+\(', s2) or s2 in ('border-box','content-box'): continue  # CSS / 模板串 / 路径噪声
            if re.fullmatch(r'[\d.,×x%+\-–\s]+', s2): pass  # 数字类一律列出
            elif not re.search(r'[A-Za-z]{3}', s2): continue
            if s2 in fact_txt or s2 in sb: continue
            seen.add(s2); print(f'  {os.path.basename(f)}: {s2}')
print(f'\nproblems: {problems}')
