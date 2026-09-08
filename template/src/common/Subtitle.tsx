import React from 'react';
import {AbsoluteFill, Sequence} from 'remotion';
import {SUBS} from './subs';
import {fitSize, textW} from './textfit';

/**
 * 字幕：白 #FFF Noto Sans SC 700 44px、居中 x=640、CSS top 637（墨迹 y644–684）、黑描边 4px（16+8+4 方向 text-shadow 环，避免 -webkit-text-stroke 的尖角刺）、
 * 无底框（靠雾底衬托）、进出单帧硬切。条目由 scripts/tts_build.py 从配音词边界生成（每块 ≤16 字）。
 */
export const SUB_STYLE = {fontSize: 44, weight: 700, top: 637, color: '#FFFFFF', stroke: 4, strokeColor: '#000000'};
export const SUB_MAX_W = 1160; // 安全区 x60–1220；超宽自动缩到 34px 兜底（中文 ≤16 字 / 英文 ≤48 字符本来就装得下）
const ring = (r: number, k: number, col: string) => Array.from({length: k}, (_, i) => {
  const a = (i / k) * Math.PI * 2;
  return `${(Math.cos(a) * r).toFixed(2)}px ${(Math.sin(a) * r).toFixed(2)}px 0 ${col}`;
});
export const strokeShadow = (w = SUB_STYLE.stroke, col = SUB_STYLE.strokeColor) => [...ring(w, 16, col), ...ring(w * 0.6, 8, col), ...ring(w * 0.3, 4, col)].join(', ');

export const SubtitleLine: React.FC<{text: string; top?: number; left?: number; color?: string; stroke?: number}> = ({text, top = SUB_STYLE.top, left = 640, color = SUB_STYLE.color, stroke = SUB_STYLE.stroke}) => {
  // 一块字幕默认单行（字幕带只有 53px 高）：超宽先缩字号到 34px。
  // 连 34px 都装不下（英文一块 >70 字符）→ 折成两行向上生长：会压进内容区，但比两头被裁掉可读。
  // 这是兜底不是设计，tts_build.py 生成时已按 SUB_BUDGET 打过 ⚠，正确做法是用 | 再切一刀。
  const size = fitSize(text, SUB_MAX_W, SUB_STYLE.fontSize, 34);
  const wrap = textW(text, size) > SUB_MAX_W;
  const lh = 1.2;
  return (
    <div
      style={{
        position: 'absolute', left, top: wrap ? top - Math.round(size * lh) : top, transform: 'translateX(-50%)',
        width: wrap ? SUB_MAX_W : undefined, textAlign: wrap ? 'center' : undefined, whiteSpace: wrap ? 'normal' : 'nowrap',
        fontFamily: `'Noto Sans SC', 'PingFang SC', sans-serif`, fontWeight: SUB_STYLE.weight, fontSize: size, lineHeight: lh, color, textShadow: strokeShadow(stroke),
      }}
    >
      {text}
    </div>
  );
};
export const Subtitles: React.FC = () => (
  <AbsoluteFill style={{pointerEvents: 'none'}}>
    {SUBS.map((s, k) => (
      <Sequence key={k} from={s.from - 1} durationInFrames={Math.max(1, s.to - s.from + 1)}>
        <SubtitleLine text={s.text} />
      </Sequence>
    ))}
  </AbsoluteFill>
);
