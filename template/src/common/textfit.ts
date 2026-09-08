/**
 * 文本宽度估算与自适应字号——纯函数，不测 DOM，所以渲染是确定性的（同一帧在任何机器上一样）。
 *
 * em 宽取自随模板附带的字体实测平均值（fontTools 量 wght 700–900）：
 *   Noto Sans SC：小写 .566 大写 .668 数字 .590 空格 .227 半角标点 .325 汉字 1.000
 *   Audiowide 大写 .788 / Orbitron 大写 .815 / Exo 2 大写 .606  → 用 EM_* 系数换算
 * 用途：中文一块字幕 ≤16 字（≈704px）本来就装得下，但英文一块 8 个词就可能 1300px 出画，
 * 所以字幕、进度条章名、章节卡标题都过一遍 fitSize 兜底。真正的约束仍在文案侧（见 narration-storyboard.md）。
 */
export const EM_HEAVY = 1;      // Noto Sans SC（正文 / 字幕 / 标题）
export const EM_WIDE = 1.18;    // Audiowide（片名、大写缩写）
export const EM_ORB = 1.2;      // Orbitron（数字 / 章序号）
export const EM_TECH = 0.92;    // Exo 2（英文技术词，斜体窄）

/** 估算一段文字的宽度，单位 em（1em = fontSize px） */
export const textEm = (s: string, emScale = 1): number => {
  let em = 0;
  for (const ch of s) {
    const c = ch.codePointAt(0) ?? 32;
    if (c >= 0x2e80) em += 1;                              // CJK、全角标点
    else if (ch === ' ') em += 0.227;
    else if (ch >= 'A' && ch <= 'Z') em += 0.668;
    else if (ch >= '0' && ch <= '9') em += 0.59;
    else if (ch >= 'a' && ch <= 'z') em += 0.566;
    else em += 0.325;                                      // 半角标点
  }
  return em * emScale;
};

/** 估算宽度（px） */
export const textW = (s: string, size: number, emScale = 1): number => textEm(s, emScale) * size;

/**
 * 超宽就等比缩字号，最低到 minSize（默认 78%）。返回值保留 1 位小数，避免亚像素抖动。
 * 缩到 minSize 仍然超宽 → 说明文案违反了每块长度预算，改文案，不要指望这里。
 */
export const fitSize = (s: string, maxW: number, size: number, minSize = size * 0.78, emScale = 1): number => {
  const w = textW(s, size, emScale);
  if (w <= maxW) return size;
  return Math.max(minSize, Math.round(((size * maxW) / w) * 10) / 10);
};
