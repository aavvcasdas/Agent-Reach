# AI 娘 / 模型娘「运营日记」视频项目选型手册

> 用途：给「鲸鱼娘 / Claude 娘 / Grok 娘 / GPT 龙娘……」这类**账号自运营日记**视频找
> **不用视频生成模型**的开源生产路线。对标对象：`aavvcasdas/ai-yunying`
> （分支 `arena/9941452f-ai-yunying`，B 站 `DeepSeek鲸鱼娘在运营` 的抖音重制版）。
>
> 调研日期：2026-11-04。所有 star 数、提交时间均为当日 `gh api` 实测值。
> 本仓库不是视频引擎，本文只是**选型结论 + 落地顺序**；真正出片由 Agent 按下面的仓库组合执行。

---

## 0. 一句话结论

`ai-yunying` 的问题**不是选题**——它的运营排期、评论区收割、文案门禁（`呆萌体检.py` /
`开场体检.py` / `画面红线体检.py`）在同类里已经是很高的水准。它的问题是**心脏换错了**：

```
Day1–Day10：一集一个手写 .mjs 渲染器（@napi-rs/canvas 画 1920×1080）
Day11 起  ：tools/engine/ 统一引擎（仍然是手写 canvas + 逐集 episode.spec.mjs）
```

结果就是：**每集都要重新写几百行绘图代码**，一改台词就要动渲染器，横屏 16:9 为主、
竖屏靠 `export_vertical.mjs` 重排，动作库是不断打补丁的像素骨架 + 生图差分。
它不是「一个引擎 + 很多数据集」，而是「很多个引擎 + 一集数据集」。

**换法**：把渲染心脏换成 **HTML/CSS/GSAP（或 JSON）→ 无头浏览器逐帧 → ffmpeg** 的确定性渲染器，
**改用声明式分集成片**。这样一集 = 一份 JSON/HTML，改一句台词 1 分钟重出，不花视频模型的钱，
也不需要生视频模型。

- **首选主引擎**：`heygen-com/hyperframes`（78.7k★，Apache-2.0，npm 包 `hyperframes`）
- **首选中文成品模板**：`garycaogan/pixel-diary`（19★，MIT，就是这批「AI 接管账号」视频的开源复刻版）
- **首选竖屏替代（无 Chromium 也能跑）**：Pillow + ffmpeg 的确定性卡片渲染（本手册第 4 节，已在本沙箱实测）

---

## 1. 先看清楚：这条赛道已经开源到什么程度

这波「AI 接管账号」在 2026-10 就已经被人拆开复刻并开源了，不用从零造：

| 项目 | ★ | 许可 | 它到底给你什么 |
|---|---:|---|---|
| [`garycaogan/pixel-diary`](https://github.com/garycaogan/pixel-diary) | 19 | MIT | **直接对标 `ai-yunying` 的成品**：像素角色 + 对话框逐字打出 + 打字音 + 8-bit 配乐，一集一个 `episodes/*.json`，引擎算字的时间、生成表情/口型/音效，再用 HyperFrames 逐帧渲染 1080p。附带一份 Claude Code skill（`skill/pixel-diary/SKILL.md`），写清了「怎么拆对标、怎么压像素立绘、怎么写分集 JSON、怎么质检」 |
| [`heygen-com/hyperframes`](https://github.com/heygen-com/hyperframes) | 78.7k | Apache-2.0 | HTML/CSS/GSAP → 逐帧 seek → MP4，**确定性**（同一输入逐像素一致），自带 `check / snapshot / render / preview` 和一套 Agent skill。这是 pixel-diary 的底层渲染器 |
| [`heygen-com/hyperframes-community-skills`](https://github.com/heygen-com/hyperframes-community-skills) | 250 | Apache-2.0 | 社区 skill：角色、吉祥物、剧情短片有单独的 `references/types/character.md` 路线 |
| [`geekjourneyx/hyperframes-motion-director`](https://github.com/geekjourneyx/hyperframes-motion-director) | 477 | AGPL-3.0 | **中文优先**的分镜导演 skill：先把 brief/设计稿给你确认，再生成资产、合成、验收。适合当「导演层」，⚠️ AGPL 注意 |
| [`cclank/lanshu-create-ai-presenter-video`](https://github.com/cclank/lanshu-create-ai-presenter-video) | 2.9k | MIT | 数字人/讲解向的完整流水线（12 种演出风格 + 证据门禁），**presenter 路线要付费生成**，但 **styled explainer 路线只要配音**，可当「周边栏目」用 |
| [`zhuyansen/awesome-claude-video-skills`](https://github.com/zhuyansen/awesome-claude-video-skills) | 1.5k | — | 413 个「给 Agent 做视频」的仓库清单，16 个做了端到端实测（含耗时、是否有声音）。**先查这张表再选型**，别一个个试 |
| [`nexu-io/html-video`](https://github.com/nexu-io/html-video) | 4.8k | Apache-2.0 | 单文件 HTML 视频模板库（21 套直播/数据/标题/片头板式），插进任何渲染器都能用；适合封面、片头、数据卡 |
| [`LBEILC/Multiplane`](https://github.com/LBEILC/Multiplane) | 149 | Apache-2.0 | 中文写的「镜头就是网页」渲染器：`render(t)` 纯时间函数 + 运动模糊/景深 + `lint` 确定性检查 + `verify` 逐像素校验。**给 Agent 用最省心的规范性最好的一个** |
| [`ZhouXiaolin/opencat`](https://github.com/ZhouXiaolin/opencat) | 72 | 无 | JSX + Skia GPU + Rust 渲染，**不用 Chromium**，一命令出 MP4。想在弱机器上跑 HTML 级排版可以看这个 |
| [`motion-canvas/motion-canvas`](https://github.com/motion-canvas/motion-canvas) | 19.7k | MIT | 代码动画（TypeScript），生成器语法做「先这个问题、再那个结果」的讲解型镜头很顺 |
| [`midrender/revideo`](https://github.com/midrender/revideo) | 4.2k | MIT | Motion Canvas 的「可参数化视频」分支，适合批量套模板出一系列同款片 |
| [`SkyeShark/eidoverse-video`](https://github.com/SkyeShark/eidoverse-video) | 117 | AGPL-3.0 | Deno + WebGPU + three.js 的「Agent 电影厂」，含 VRM/口型/镜头/渲染。⚠️ 要真 GPU，本类沙箱跑不动 |
| [`natalia-3nitilab/vita-myth-studio`](https://github.com/natalia-3nitilab/vita-myth-studio) | 0 | MIT | **VRM 角色 + 动作捕捉轨迹**讲长篇故事的引擎（一条十分钟约 $0.86 / 7.4 分钟本机算力）。思路可借：**不做视频生成模型，用 3D 角色 + 合成旁白** |
| ⚠️ [`remotion-dev/remotion`](https://github.com/remotion-dev/remotion) | 70.7k | 自定义（非开源） | React 写视频，**公司规模到线要买 license**。个人可用，但本项目要长期留档，不建议当底座 |

> 已停用/不推荐：`remotion`（许可）、`ChatTTS`（AGPL，且本项目用不着）、任何「一句话生视频」的 SaaS。
> 本手册只收**代码渲染、不调视频生成模型**的路线。

---

## 2. 角色素材：鲸鱼娘 / Claude 娘 / Grok 娘 从哪拿

不用自己画，也不要用生图模型一集一集现生成。现成的、按角色分好的：

| 来源 | ★ | 许可 | 内容 |
|---|---:|---|---|
| [`HABAI182/ai-girls-atlas`](https://github.com/HABAI182/ai-girls-atlas) | 7 | 逐文件 | **模型娘情报总站**：45 个角色（DeepSeek/鲸鱼娘、Claude、Grok、GPT 龙娘、Gemini 猫娘、Kimi、GLM 狐娘、Qwen……），每个角色页列清「作者版本 / 识别点 / 许可 / SHA256」；`videos/` 有 96 条同赛道视频的 23 篇抽帧案例（按 18 个内容品类），`encyclopedia/ready-packages.md` 有 14 组可直接下载的素材包（含 2 组 **Live2D** 模型 + PSD/CMO3 源文件） |
| [`TreapGoGo/deepseek-whale-girl`](https://github.com/TreapGoGo/deepseek-whale-girl) | 734 | MIT | 鲸鱼娘二创资源库：参考图、生成提示词、社区作品、6 份 ComfyUI 工作流 |
| [`JAdpp/dsh-whale-galgame`](https://github.com/JAdpp/dsh-whale-galgame) | 39 | 代码 MIT / 美术 CC BY-NC-SA | **六位模型娘立绘**（鲸鱼娘 / Claude 克洛德 / GPT 小吉 / Gemini 双子 / Kimi 月见 / Grok 洛可）+ 7 张鲸鱼娘表情差分 + 11 行桌宠动画图集。**许可注意：素材非商用**，见 `assets/default/README.md` |
| [`Small-tailqwq/dsh-deep-whale`](https://github.com/Small-tailqwq/dsh-deep-whale) | 3k | 代码 MIT / 美术 CC BY-NC-SA | 鲸鱼娘皮肤系列；署名链 上善 → ZipZipPipe → Small-tailqwq，**用之前读它的 LICENSE-ARTWORK** |
| [`PC2005-cloud/dsh-pet`](https://github.com/PC2005-cloud/dsh-pet) | 5.5k | MIT | **不是出片引擎，但它的「素材链」是这个痛点最完整的解**：10 秒动作提示词配方 → 绿幕批量生成 → `chroma_step02.py` HSV 抠像 → 归一化到统一站立位 → 透明 webm/HEVC-alpha。100+ 段动画首尾无缝衔接。见第 2.1 节 |
| [`Plaguedoctorhere/dsh-pet-character-packs`](https://github.com/Plaguedoctorhere/dsh-pet-character-packs) | 5 | 无许可声明 | 龙娘与 Claude 娘的 dsh-pet 角色扩展包（透明动作 + 安装工具）。**没有许可，只能参考不能商用** |

### 2.1 「要动作，又不能每集生视频」的标准解法（dsh-pet 素材链）

先把边界说清：绿幕/`chroma` 这条路，**第①步仍然是一次性用生成模型做素材**（可灵、Runway、豆包都行），
只是**素材做一次、之后所有集复用**，不是一集生成一集。如果你连这一步都不想碰生成模型，
就直接用 Live2D（`ai-girls-atlas` 里有两组可直接下载的鲸鱼娘 Live2D + PSD/CMO3 源文件）
或纯代码画的立绘/像素图（第 4 节原型那种），跳过 ①–④。

`ai-yunying` 走的是「生图差分 + 像素骨架」，越做越重。更稳的做法是**一次做动作库，之后只渲染**：

```
① 生图/生视频模型（一次性）→ 绿幕 10s 视频，人物位置/大小/首尾帧锁死
② chroma_step02.py        → HSV 抠像，透明 webm（烂的动作走 PR 手工抠像）
③ normalize_step03.py     → 统一站立位 2160×1215 归一化
④ encode_thumbs.py        → 640×360 播放变体 + 预览
⑤ 引擎里按「动作 + 时长 + 权重」播，首尾相接
```

之后每一集**完全不碰模型**：台词、表情、动作都只是 JSON 里的字段。
动作库越用越值钱，而不是每集重新生成一次。

---

## 3. 声音：不要用「克隆配音」兜底，用能出时间轴的 TTS

`ai-yunying` 的时间轴门禁是对的（**cue 必须来自实测音频**：ASR 词级 + RMS 修边），
但它把「克隆声线」当默认，导致每集都要重做 ASR。更省的做法是**用能直接给词级时间戳的 TTS**：

| 方案 | 许可 | 为什么选它 |
|---|---|---|
| [`rany2/edge-tts`](https://github.com/rany2/edge-tts) 12.5k | 开源（读 Edge 在线 TTS） | **免费、有中文多音色、WordBoundary 直接给词级时间戳** → 不用 ASR 就能对齐字幕和口型，一条命令出 mp3 + srt |
| [`RVC-Boss/GPT-SoVITS`](https://github.com/RVC-Boss/GPT-SoVITS) 64.8k | MIT | 一分钟数据克隆固定人设声线，**本地跑、不联网**；适合要「本鲸专属声音」时一次性做好 |
| [`SWivid/F5-TTS`](https://github.com/SWivid/F5-TTS) 15.5k | MIT | 零样本克隆，推理快，适合想试不同语气 |
| [`index-tts/index-tts`](https://github.com/index-tts/index-tts) 24.9k | 见仓库 | 中文自然度目前第一梯队，长句稳 |
| [`m-bain/whisperX`](https://github.com/m-bain/whisperX) 25.1k | BSD-2 | **只在已有录音/外部配音时**做词级对齐；有 edge-tts 时不必每集跑 |

> 硬规矩照抄 `ai-yunying` 的：**没有实测音频，禁止把 plan 轴写成 `measured=true`**；
> 换音源必须重生成 timing / 字幕 / 对齐报告。这条比任何引擎都重要。

---

## 4. 竖屏（9:16）怎么办 —— 本沙箱实测的第三条路

HyperFrames / pixel-diary 的 HTML 渲染都要 **Node 22 + Chromium**。如果目标机器（或本沙箱）
装不上浏览器，用 **Pillow 逐帧画 + ffmpeg 编码**同样能做到确定性、可复现，而且极快：

本仓库已附实测样张与样片（角色是**占位图形**，不是任何人的美术）：

- [`docs/assets/model-moe/vertical-prototype.png`](assets/model-moe/vertical-prototype.png) — 截帧
- [`docs/assets/model-moe/vertical-prototype.mp4`](assets/model-moe/vertical-prototype.mp4) — 7.9 秒样片（236 帧，1080×1920，30fps）
- [`docs/assets/model-moe/vertical-prototype.py`](assets/model-moe/vertical-prototype.py) — 可直接运行的渲染脚本（`pip install pillow imageio-ffmpeg`）

236 帧渲染 **6–8 秒**（≈30× 实时），中文字体用 `NotoSansSC`（OFL-1.1，可商用）。
换成你自己的透明立绘只需要替换 `draw_chibi()` 一个函数——`dsh-pet` 的素材链产出的正是
「统一站立位 + 透明」的 PNG，天然对接。

要点（`ai-yunying` 的抖音复盘直接印证）：

1. **9:16 是原生画布**，不是横屏裁出来。`export_vertical.mjs` 那种「同一场景重排」是对的方向，
   但更好的做法是**一开始就按 1080×1920 设计**，横屏另出一版。
2. **首帧必须有 10–12 字钩子**（`ai-yunying` 实测 2 秒跳出 34–50%）。别用标题卡开场。
3. **片尾说完就停**，不做片尾卡、不写粉丝数/播放量/进度条（它自己的「画面红线」已经证明这点）。
4. **字幕每行 ≤13–15 字**，单句 ≤25 字，>18 字长句占比 ≤12%——这几条它的门禁脚本已经写死了，直接抄。

---

## 5. 建议的落地顺序（不重写运营层，只换心脏）

`ai-yunying` 的运营层（`00_运营总览/`、`DayN/文案`、三个体检脚本、`gate.py`）全部保留，
只做下面四步：

1. **把 `tools/engine/` 换成声明式渲染器。**
   一集一份 `episode.json`（台词 / 说话人 / 表情 / 词点 / 卡片 / 场景类型），
   渲染器只做「读 JSON → 画帧 → 编码」。
   - 能装浏览器 → 抄 `pixel-diary` 的 `scenes.py + template.html` 结构（11 种场景：标题卡、交接、状态卡、
     规则卡、大字、配图+进度、账本盖章、聊天记录、视频画框、评论区点菜、片尾），换皮不换骨。
     具体字段照 `episodes/demo/day0.json`：`cast` 里一个角色一个对象（`sprite/color/blip`），
     `scenes[]` 每条 `{id, type, ...}`，台词写 `lines: [{t, cues, after}]`，`cues` 负责「说到哪个词
     时弹哪张卡 / 哪条规则高亮」——这就是它一改台词重出一条只要一分钟的原因。
   - 装不上浏览器 → 用第 4 节的 Pillow 路线，把同样的 11 种场景画一遍。
2. **一集一个目录，产物只增不改。** `episodes/dayN/{script.md, episode.json, audio/, stills/, out.mp4, REVIEW.md}`。
   保留它现有的「先估时 → 再分镜 → 先试剪 → 后整片」流程（`agent.md` 第 17 条），
   但把「手写 render_dayN.mjs」这条彻底废掉。
3. **动作库和形象库独立于集数。** 用 2.1 的素材链做一次动作库（待机/挥手/吃饭/护碗/哭/冲刺……），
   之后所有集共用；角色差分只做表情，不做新骨骼。
4. **门禁脚本改成查 JSON，不查 .mjs。**
   `画面红线体检.py` / `呆萌体检.py` / `开场体检.py` 的规则不变，把扫描对象从渲染器源码换成
   `episode.json` 的字段（数字、进度条、片尾卡、第一句字数、长句占比）。这样规则和实现解耦，
   换引擎不用重写检查。

做完这四步，单集制作从「一天」压到「一集 JSON + 一次渲染」，并且**换角色 = 换 cast 目录**，
鲸鱼娘、Claude 娘、Grok 娘可以跑同一套引擎出系列。

---

## 6. 最小可运行组合（推荐直接开跑）

```bash
# 1) 渲染器 + 中文成品模板
git clone https://github.com/garycaogan/pixel-diary.git
cd pixel-diary && python3 -m venv .venv && .venv/bin/pip install -e .

# 2) 中文字体（OFL-1.1）
curl -L -o fonts/NotoSansSC-VF.ttf \
  "https://github.com/google/fonts/raw/main/ofl/notosanssc/NotoSansSC%5Bwght%5D.ttf"

# 3) 先用 demo 出片，确认 1–2 分钟一条
.venv/bin/python -m pixel_diary check episodes/demo/day0.json
.venv/bin/python -m pixel_diary build episodes/demo/day0.json --out work/demo --render out/demo.mp4

# 4) 要更强的镜头语言 / 竖屏 / 注册表组件，再单装 HyperFrames
npx hyperframes init my-video --skip-skills
npx hyperframes render
```

> HyperFrames 单独用时要求 **Node ≥22 + ffmpeg**；Agent 第一次跑要先 `npx hyperframes check --json`
> 再 `render`，别看代码就宣布通过——这是它官方 skill 里写死的循环。

---

## 7. 避坑清单（都是这批项目踩过的）

- **不要用 Remotion 当底座**：许可不是 MIT，量起来要付费。
- **不要生一集视频**：绿幕动作库一次做、长期用；每集只换 JSON，这是 `pixel-diary` 与 `dsh-pet` 的共同结论。
- **不要把「克隆配音」当每集默认**：能出词级时间戳的 TTS（edge-tts）能省掉整条 ASR 链。
- **不要横屏做完再裁竖屏**：`ai-yunying` 的完播率 3.31% 就是横屏 82 秒的直接代价。
- **不要写死数字**：粉丝数、播放量、进度条一律不上屏；片尾说完就停。
- **不要镜像当侧脸、不要正脸图当 3D 运镜**：它 `agent.md` 第 20 条已经吃过这个亏。
- **美术许可要分清**：鲸鱼娘形象链是 上善 → ZipZipPipe → Small-tailqwq，多数派生图是 **CC BY-NC-SA（非商用）**；
  商用前必须逐个查 `assets/default/README.md` 或 `LICENSE-ARTWORK`。代码 MIT ≠ 美术 MIT。

---

## 8. 来源

- `ai-yunying`（`arena/9941452f-ai-yunying`）：`agent.md`、`00_运营总览/*`、`tools/engine/README.md`、`tools/day9制作/README.md`、`tools/剧本/画面红线体检.py`
- pixel-diary：README、`skill/pixel-diary/SKILL.md`、`pixel_diary/build.py`、`episodes/demo/day0.json`
- HyperFrames：README、`skills/hyperframes/SKILL.md`、`skills/hyperframes-cli/SKILL.md`、npm `hyperframes@0.9.12`
- dsh-pet：README、`MAKE-YOUR-OWN-PET.md`、`prompts/桌面宠物 10 秒动作提示词.md`、`scripts/*.py`
- ai-girls-atlas：`characters/*/README.md`、`videos/README.md`、`encyclopedia/ready-packages.md`
- dsh-whale-galgame：README、`assets/default/README.md`
- awesome-claude-video-skills：16 个 skill 的端到端实测表
- 竖屏原型：本仓库 `docs/assets/model-moe/vertical-prototype.{py,png,mp4}`，Pillow 13.0.0 + imageio-ffmpeg 9.0.2 实测（236 帧 / 6–8 秒）
