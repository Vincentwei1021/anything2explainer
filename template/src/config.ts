/**
 * 片子级配置（唯一需要按主题改的文件之一；另一个是 script/narration.txt）。
 * 句 id（S01…）来自 scripts/tts_build.py 生成的 timeline.ts；章节数与标题来自 narration.txt 的 `# CHAPTER n 标题` 行。
 */
export type HudEntry = {fromS: string; toS: string; text: string; tech?: string; fromOffset?: number; toOffset?: number; w?: number};
export type RailSpec = {steps: string[]; switchS: string[]; fromS: string; toS: string};
export const VIDEO = {
  slug: 'demo', // 素材目录 public/assets/<slug>/（配音 audio.wav 由 tts_build.py 写到这里）
  /**
   * 片子语言：'zh' 中文（默认）｜'en' 英文。
   * 影响 → 配音引擎（tts_build.py 的 TTS_ENGINE=auto 也会自己按解说词判语言）、标题/章节卡是否压窄（拉丁不压）、
   * 居中文字的基线补偿（CJK −2 / 拉丁 0）、文案与字幕块长度预算（见 reference/narration-storyboard.md §5）。
   */
  lang: 'zh' as 'zh' | 'en',
  /**
   * 幕底：'stars' 星点 + 雾底渐变（默认，样片风格）｜'dots' 点阵波（video-talkcraft dot-field-wave 移植，`common/DotFieldBg.tsx`）。
   * 两者互斥；镜头里的 BG_Gn 覆写（`stars:'none'` 关幕底）对两种方案都生效。frame_metrics.py 会按这里的值抠掉幕底再统计。
   */
  bg: 'stars' as 'stars' | 'dots',
  /**
   * 片头。中文片：big 用 Audiowide 宽体（缩写/英文词），rest 用 Noto 900（中文部分），en 是英文全称，tagline 一句话钩子。
   * 英文片：rest 留空 ''（不显示），big 放主词/缩写，en 放全称或副标，tagline 一句话钩子。
   */
  title: {big: 'RAG', rest: '与知识库', en: 'Retrieval-Augmented Generation', tagline: '让大模型开卷考试'},
  /** 章节英文副标（顺序对应 narration 的 CHAPTER 1..n；章节卡从第 2 章起显示） */
  chapterTech: ['Why RAG', 'Indexing', 'Retrieval & Generation', 'Evaluation & Advanced RAG'],
  /** 顶部 HUD 胶囊（当前小节名）：按句 id 区间；相邻条目之间自动无空档；跨章节卡自动淡出。 */
  hud: [
    {fromS: 'S01', toS: 'S05', text: '大模型的短板'},
    {fromS: 'S06', toS: 'S07', text: '开卷考试'},
    {fromS: 'S08', toS: 'S10', text: 'RAG', tech: 'Retrieval-Augmented Generation'},
  ] as HudEntry[],
  /** 流程轨（可选，一章最多一条，五步以内）：y118–162，当前步紫、已过灰底、未到灰边；有轨的章内容主区 y175–620 */
  rails: [
    {steps: ['解析', '切块', '向量化', '建索引', '更新'], switchS: ['S12', 'S13', 'S16', 'S18', 'S20'], fromS: 'S12', toS: 'S20'},
  ] as RailSpec[],
  /** 片头帧数（tts_build 的 LEAD+CHAPTER_GAP 决定，通常 85）与片尾压黑 */
  endingFade: 30,
};
