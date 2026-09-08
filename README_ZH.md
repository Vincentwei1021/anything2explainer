# anything2explainer

[![Claude Code](https://img.shields.io/badge/Claude%20Code-skill-D97757?logo=anthropic&logoColor=white)](https://claude.com/claude-code)
[![Codex](https://img.shields.io/badge/Codex-skill-000000)](https://openai.com/codex)
[![Remotion](https://img.shields.io/badge/Remotion-4.0-0B84F3)](https://remotion.dev)
[![License](https://img.shields.io/badge/license-PolyForm%20Noncommercial-informational)](LICENSE)

[English](README.md) | **简体中文**

给一个主题 → 产出一条**黑底 MG 风格、带配音字幕章节进度条的中文科普讲解视频**（时长你定，常用 3–5 分钟）。
画面全部是代码画的（Remotion + React），不使用任何现有视频的素材。

这是一个 **Claude Code / Codex skill**：仓库里装的不是一个 CLI，而是一整套让 agent 把片子做出来的方法——可编译的模板工程、图元与光效库、配音/分镜/渲染/量化质检工具、风格与动效规范、多 agent 分工协议，以及一条完整样片作为质量标尺。

![样片前 30 秒的帧总表](examples/rag/frames/overview_1.jpg)

样片《RAG 与知识库》：4′35″、44 句解说、44 个镜头，8 个构建 agent 并行 40 分钟 + 两轮 QC。
全套过程文件在 [`examples/rag/`](examples/rag/)（调研 → 解说词 → 分镜表 → 镜头源码 → QC 报告 → 交付说明），成片帧在 [`examples/rag/frames/`](examples/rag/frames/)。

## 成片规格

| | |
|---|---|
| 画幅 / 帧率 | 1280×720 @ 30fps，H.264 |
| 时长 | 由你定（见下表），2–8 分钟都能做 |
| 视觉 | 黑底 + 星点 + 雾底渐变；白线条图形 + 紫色重点；超粗黑体大字 |
| 常驻层 | 44px 白字黑边字幕、底部章节进度条、顶部胶囊 HUD、可选流程轨 |
| 配音 | 中文 edge-tts `zh-CN-YunxiNeural`（云希，男声）/ 英文 kokoro-82m `am_liam`（Liam，男声）；也可用你自己的 TTS 或成品配音 |

时长决定内容丰富程度与全流程规模：

| 时长 | 中文字数 | 句 / 镜头数 | 章节 | 构建 agent | 产出耗时 | 磁盘 |
|---|---|---|---|---|---|---|
| 2–3 分钟 | 700–950 | 24–32 | 3 | 4–6 | ≈1.5 小时 | ≈2GB |
| 3–5 分钟（样片档） | 1200–1500 | 40–50 | 4 | 8 | ≈3 小时 | ≈2GB |
| 5–8 分钟 | 1800–2400 | 60–80 | 5–6 | 10–14 | ≈4–5 小时 | ≈3GB |

## 安装

```bash
git clone https://github.com/Vincentwei1021/anything2explainer.git
ln -s "$PWD/anything2explainer" ~/.claude/skills/anything2explainer   # Claude Code
ln -s "$PWD/anything2explainer" ~/.codex/skills/anything2explainer    # Codex
```

依赖：

```bash
# Node ≥18（模板 npm install 会装 remotion 4.0.507 / react 19）
brew install ffmpeg          # 抽帧 / 转码，必需

python3 -m venv ~/.venvs/a2e && source ~/.venvs/a2e/bin/activate
pip install 'edge-tts==7.2.8' numpy pillow scipy   # 建议固定 edge-tts 版本：它跟着微软端点变，升级常有破坏性

# 只做英文片时再装（kokoro-82m 本地推理）
pip install kokoro soundfile && brew install espeak-ng
```

`scipy` 只给质检脚本 `frame_metrics.py` 用。脚本是 zsh + Python 3，在 macOS 上开发与验证；Linux 应可用，Windows 未测试。

## 用法

在 Claude Code 里直接说要做什么就行，skill 会被触发：

> 讲一下向量数据库，做成一条讲解视频

它会按 `SKILL.md` 的 9 个阶段走：建项目 → 调研（1 个 agent） → 解说词与时间轴 → 分镜 → 覆盖层与图元 → 打样（1 个 agent + 30 秒样片） → 并行构建（其余各组） → 渲染 → QC 与修复 → 交付。

也可以手动跑模板：

```bash
template/scripts/new_project.sh ~/work/my-video myslug
cd ~/work/my-video
# 1. research/调研.md          2. script/narration.txt → python3 scripts/tts_build.py
# 3. script/storyboard_src.md → python3 scripts/render_storyboard.py     4. 改 src/config.ts
# 5. src/shots/G1..Gn          6. scripts/preview.sh 30（前 30 秒样片）
# 7. VER=v1 scripts/render.sh + python3 scripts/frame_metrics.py         8. QC → 修 → v2/v3
```

## 四个确认点

流程会在这四处停下来等你回话，不会闷头做完（细节见 `SKILL.md`）：

1. **时长**——写文案之前。它决定章节数、句数、镜头数和并行 agent 数，也就决定内容能铺多丰富。
2. **解说词定稿**——配音之前。定稿后帧号会被每个镜头硬编码，改一个字全片重对位，这是最便宜的干预点。
3. **配音**——跑 TTS 之前问一句你有没有偏好的 TTS；没有就用默认（中文 edge-tts 云希、英文 kokoro-82m Liam）。也可以直接给成品配音，自己按逐句时间轴填 `timeline.ts`。
4. **前 30 秒样片**——只建完第一个构建组就渲 30 秒给你看风格。在这里改一次是 1 个组的成本，整片渲完再改是全部组。

## 仓库结构

```
SKILL.md                  流程主文档：9 个阶段、四个确认点、质量标尺
reference/                写给主会话与 agent 的规范
  style-guide.md            安全区、调色板、字体、图元目录、版式规律
  motion-vocabulary.md      入场/强调/光效/离场/运镜的公式与帧数
  composition-and-light.md  主体尺寸三档、光跟主角、高光时刻编排、量化判据
  narration-storyboard.md   解说词写法、配音参数、分镜令牌、镜头设计模式表
  research-brief.md         研究员 prompt 与事实规则
  agent-build-rules.md      构建 agent 协议
  agent-qc-rules.md         QC agent 协议
  prompts.md                研究/构建/QC/修复/复验/终检六种 prompt 模板
  lessons.md                三部片子踩过的坑与根因
template/                 可编译的 Remotion 4 项目（用 scripts/new_project.sh 复制）
  src/common/               雾底、星点、glitch、缓动、字幕、进度条、实拍层
  src/ui.tsx  src/fx.tsx    图元与调色板 / 光效·纵深·运镜图元
  src/overlay/              片头、章节卡、HUD、流程轨、片尾
  scripts/                  配音、分镜、still、测渲、前 N 秒样片、整片渲染、量化质检
  public/fonts/             四款字体 + OFL 许可
examples/rag/             样片全套过程文件与成片帧
examples/contrast/        6 组正例/反例帧对照（构图与光的标尺）
```

## 致谢

视觉风格的灵感与标尺来自抖音创作者 **@图灵宇宙** 的科普视频——黑底、白线条配紫色重点、超粗黑体大字这套语言是从他的片子里学来的。本项目所有画面均由代码原创绘制，不使用其任何帧、素材或工程文件；如有不妥请开 issue 告知。

## 原创性

- **画面全部代码绘制**，不使用任何现有视频的帧或片段；可选的实拍 B-roll 只允许免版权来源，并要求登记 MANIFEST（sha256 / 来源 URL / 许可 / 用途）。
- **事实有出处**：画面上出现的每个数字、年份、机构、英文术语都必须能在该片的调研文档里找到来源 URL，没核实的不上画面也不进配音。

## 许可

工具包本身：[PolyForm Noncommercial 1.0.0](LICENSE)——非商业使用免费，商业使用需事先获得作者授权。**用它做出来的视频归你自己**。
模板内四款字体（Noto Sans SC / Orbitron / Exo 2 / Audiowide）按 SIL OFL 1.1 单独授权，版权与许可全文见 [`template/public/fonts/LICENSE.md`](template/public/fonts/LICENSE.md)。
Remotion 自身对公司用户另有授权要求，见 [remotion.dev/license](https://remotion.dev/license)。

## 已知限制

- 中文为主（英文可用 kokoro 配音，但解说词写法与字幕切块规则是按中文调的）；只做这一种视觉风格，换风格要改 `reference/style-guide.md` + `src/ui.tsx`。
- 不适用：复刻某条现有视频、真人口播、以实拍为主的片子。
- 解说词一旦配音定稿就不能改词（镜头代码里硬编码帧号），改词等于全片重对位。
- 并行构建对机器有要求：多个 agent 同时跑 Remotion bundle，建议预留 ≥5GB 磁盘；tmux pane 有上限，超过 12 个要分波派。
