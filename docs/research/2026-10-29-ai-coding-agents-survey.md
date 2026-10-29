# 近 90 天（2026-07-29 → 2026-10-29）AI 编程 Agent / 改代码工具 / 低成本用法 调研

> 调研执行时间：2026-10-29（UTC）
> 时间窗：只把 **2026-07-29 之后** 发布或重大更新的东西当作"新"，更早的只作为方法论参考并明确标注。
> 执行方式：用 Agent Reach 的渠道思路（Exa 式全网检索 + YouTube 搜索页 + B站搜索页 + GitHub API）做了 **11 轮** 检索，检索式见文末「附录 A」。

---

## 0. 一句话结论

1. **"改代码"这件事在 2026 年 9–10 月被重做了一遍**：不再是"聊天框里贴代码"，而是 **模型 + harness（编辑工具格式）** 的组合竞赛。同一个模型换一种编辑格式，成功率能从 6.7% 变 68.3%，输出 token 还能降 61%。
2. **新模型三个月内换代三轮**：Claude Opus 5.5（9/22）→ GPT-6.1 Sol（9/29）/ Terra（10/26）→ Gemini 4 Argon（10/13）/ **Carbon（10/28–29，当前榜单第一但还没开放）**；xAI 的 Grok 4.7 在 9/21 主打"便宜"。
3. **便宜不是选最便宜的模型，而是控制"输入 token + 缓存 + effort"**：Opus 5.5 的缓存读取价 $0.20/M 是输入价的 1/20，缓存一断成本直接 ×12.5；同模型不同 effort 实测成本差 **11.9 倍**。
4. **最省钱的四条路**（都在 3 个月内被验证过）：① 用国产 Coding Plan 当"油"（GLM Lite $18/月起，比 Claude Pro 还便宜，可接 Claude Code）；② 官方 $20 档 + 模型路由（magpie / cc-switch / CLIProxyAPI 等）；③ 免费额度（Grok Build 免费档、Antigravity、Gemini API 免费层）；④ 上下文压缩（context-mode 号称砍 98% 工具输出）。
5. **便宜模型 + 免费额度的隐性代价**：Grok 4.7 完成同任务更费 token（$3.74/任务 vs GPT-5.6 Sol $1.99）；智谱 ZCode 被曝静默上传工作区与 Git 历史（9/18），Grok Build 被曝把整个仓库传到云（9/16）。

---

## 1. 三个月时间线（可核对）

| 日期 | 事件 | 为什么和你有关 |
|---|---|---|
| 08-12 | xAI Grok 4.6 | 长任务 agent 方向 |
| 09-01 | Anthropic **Fable 5.1 / Mythos 5.1** | 当前最强档，Opus 5.5 对标它 |
| 09-16 | 曝 **Grok Build 把整个 Git 仓库上传到云**，隐私开关没拦住 | 用 agent 前先看隐私开关 |
| 09-18 | 曝 **智谱 ZCode 静默上传整个工作区及 Git 历史** | 国内低价 agent 的合规风险 |
| 09-19 | **Grok Build 开源**（`xai-org/grok-build`，27.6k★，Rust TUI） | 可自审、可换模型（Composer 2.5 / OpenAI 兼容 / Anthropic Messages） |
| 09-21 | **Grok 4.7** 发布，$2/$6 per MTok，500K 上下文，AA Coding Agent Index 47→56 | 便宜档里最能打的编程模型之一 |
| 09-22 | **Claude Opus 5.5**，$4/$20，缓存读 $0.20，1M 上下文，默认 effort=medium | Claude Code v2.1.280 起 **默认模型变 Opus**（Pro/Team Standard 也从 Sonnet 切过来） |
| 09-22 | GPT-6 Sol / Luna 进 Codex | 分层用量 |
| 09-28 | **Claude Sonnet 5.5**（性价比档） | 日常改代码主力 |
| 09-29 | **GPT-6.1 Sol**（DevDay），"接近 Astra 但更便宜" | Codex 新默认 |
| 10-06 | Codex **auto-review 对 ChatGPT 登录用户免费**（不再吃额度） | 白拿一层代码审查 |
| 10-07 | Codex CLI **0.161.0 把默认模型切成 GPT-6.1 Sol**；Bedrock 多 agent；MCP 登录 | 没设 model 的人已静默切换 |
| 10-08 | GPT-6.1 Sol **Ultrafast** 档 + Codex 托管 worktree / Code Mode 工具搜索 | 并行改多个分支 |
| 10-11 | Codex 里 GPT-6.1 Sol 默认上下文 272K → **500K**（可开到 1M） | 长仓库整包读 |
| 10-13 | **Gemini 4 Argon** 全面开放：`gemini-4-argon`，1,048,576 上下文，DeepSWE v1.1 **77.9%**，Antigravity 内置 | 唯一"全模态 + 1M + 便宜"三件套 |
| 10-14 | GPT-5.5 从 Codex（ChatGPT 登录）下线；API key 不受影响 | 老脚本要改 model id |
| 10-24 | **Antigravity preview 09-2026**：原生代码搜索 + **行区间编辑（line-range editing）** + 更好 prompt caching | "改代码"工具层的关键更新 |
| 10-26 | **GPT-6.1 Terra**：$1 输入 / $0.05 缓存输入 / $5 输出，强视觉 + 电脑操作 | 目前最便宜的"能看屏幕改代码" |
| 10-28 | **Gemini 4 Carbon**：AA Intelligence Index v5 = **59（第一）**；AA Coding Agent Index 59（第二，落后 Claude Code+Opus 5.5 的 62）；Terminal-Bench 4.0 65.2% | 榜单第一 ≠ 编程 agent 第一 |
| 10-29 | Carbon 仍是 **Fairwind 定向 / 限量**，没全面开放；定价过渡期 $4/$20 | 现在别把它当生产依赖 |

---

## 2. 编译器 / IDE / Agent 工具体（3 个月内）

### 2.1 官方三大家（都在 3 个月内换过血）

| 工具 | 形态 | 当前默认模型 | 3 个月内的关键变化 |
|---|---|---|---|
| **Claude Code**（v2.1.280 → 2.1.311） | 终端 / VS Code / JetBrains / Web | Opus 5.5（Pro 及以上全档） | 默认模型改 Opus；effort 改成 per-model（新模型从 medium 起）；checkpoint 式审查；Skills 按需加载；子代理 MCP 修复 |
| **Codex**（CLI 0.159 → 0.165） | CLI / 桌面 / 云 / IDE | GPT-6.1 Sol（0.161 起） | 默认模型静默切换；500K 上下文；Ultrafast；`/presets` 10 个常用提示槽；Code Mode 工具搜索；托管 worktree；Vertex AI provider；auto-review 免费 |
| **Google Antigravity** | Agent-first IDE / CLI / macOS Gemini App 内嵌 | Gemini 4 Argon | 4 Argon 全量接入；preview-09-2026 加 **原生代码搜索 + 行区间编辑 + prompt caching**；直接把"老代码现代化"（40 年科学计算 → Rust）做成官方 demo |

### 2.2 新出现的"改代码"类工具（GitHub 数据抓取于 2026-10-29）

| 项目 | ★ | 建仓 | 一句话 | 对你的用处 |
|---|---|---|---|---|
| `farion1231/cc-switch` | 149.9k | 2025-08 | 跨平台一键切换 Claude Code / Codex / OpenCode / OpenClaw / **Grok Build** 的配置 | 多套餐/多中转切换的事实标准 |
| `anomalyco/opencode` | 222.9k | 2025-04 | 开源 coding agent，编辑工具带 **9 级回退匹配** | 自建最稳的编辑层 |
| `router-for-me/CLIProxyAPI` | 56.8k | 2025-07 | 把 Antigravity / Codex / Claude Code / Grok Build / Muse Code 包成 OpenAI/Gemini/Claude 兼容端点 | 一个网关喂所有客户端 |
| `decolua/9router` | 31.6k | 2026-01 | "Unlimited FREE AI coding"，把 Claude Code/Codex/Cursor/Cline/Copilot/Antigravity 接到免费模型 | 纯白嫖路线（注意 ToS） |
| `mksglu/context-mode` | 32.8k | 2026-02 | 沙箱化工具输出（号称 −98%）、持久化会话 | 便宜的第一杠杆 |
| `xai-org/grok-build` | 27.6k | 2026-07-14 | xAI 官方 TUI harness，可换模型 | 想用 Grok 4.7 又不想被锁 |
| **`yetone/magpie`** | **25.1k** | **2026-09-23** | 菜单栏里给每个 agent 换模型："Codex on DeepSeek，Claude Code on Kimi" | **3 个月内最值得装的省钱工具** |
| **`zai-org/ZCode`** | **8.4k** | **2026-09-20** | 智谱的 coding harness，免费档 | 便宜，但有 9/18 的上传争议 |
| **`omnirush-ai/omnirush-gui`** | **4.3k** | **2026-09-21** | 桌面 coding agent，"免费访问前沿模型" | 观察中，第三方免费额度有跑路风险 |
| **`HarnessRouter/harnessrouter`** | **3.8k** | **2026-08-09** | 自托管统一接口，跑 Codex / Claude Code / Hermes / PI / DSH | 团队内统一 harness |
| `zqiren/Orbital` | 969 | 2026-03 | 多 agent 共用一份上下文，随时换 agent | 切模型不丢上下文 |
| `Supercompress/Supercompress` | 138 | 2026-07-31 | query-aware 上下文压缩，砍 ~65% 输入 token | 长会话省钱 |

> B站 10/24 有期「我用过的最好的 Agent IDE（Orca）」[BV1XeHK6fEkz](https://www.bilibili.com/video/BV1XeHK6fEkz/)，Orca 属于 3 个月内新冒出来的 agent-native IDE，但 GitHub 上还只有零散插件/对比仓库，**生产可用性待验证**。

---

## 3. "改代码的方法"：2026 年真正的技术分歧

这一节是三个月内最值钱的部分——**同样的模型，换编辑格式成绩天差地别**。

### 3.1 五种主流编辑协议

| 协议 | 代表 | 模型看到什么 | 优点 | 坑 |
|---|---|---|---|---|
| **`apply_patch` / V4A** | Codex CLI、GPT 系 | `*** Begin Patch` / `*** Update File:` / `@@` 上下文 + `+/-` 行 | token 最省（只发改动行）；一个 patch 可多文件 + 重命名；训练对齐过 | **强模型绑定**：给 Grok 4 用失败率 50.7%；行数对不上直接废 |
| **SEARCH/REPLACE 块** | Aider、Cline、RooCode、Mistral Vibe | `<<<<<<< SEARCH / ======= / >>>>>>> REPLACE` | 意图清晰，社区工具最多 | 需一字不差复现空白 |
| **`old_string`/`new_string`（str_replace）** | Claude Code、Gemini CLI | 工具参数里两个字符串 | 心智模型最简单，无格式学习成本 | 必须唯一匹配；缩进差一格就失败 |
| **line-range 行区间替换** | Grok TextEditorTool（`replaceLines`/`insert`）、**Antigravity preview-09-2026** | 行号区间 + 新内容 | 大文件局部改动极省 token；配合"原生长代码搜索"定位 | 多次编辑后行号漂移，必须每次重读 |
| **hash 锚点（hashline）** | 新一类 harness 实验 | 用代码块哈希定位，不复制原文 | 不要求完美复现空白；文件被改过会**先拒绝再报错**，不会写坏 | 生态还小 |

### 3.2 关键实证数字（可直接用来选型）

- **编辑格式换一个，成功率 10 倍**：Grok Code Fast 在真实改代码任务上从 **6.7% → 68.3%**，模型没变、训练没变，只改了编辑工具格式；同时弱模型输出 token **−61%**（不再疯狂重试）。
- **AST 锚定的 SEARCH/REPLACE 应用成功率 99.3%**，整文件重写 78.2%（还带 `// ... 其余不变` 式的偷懒删代码），**带行号 unified diff 只有 64.5%**（模型数不清 `@@ -142,7 +142,9 @@`）— 2026-10-17 的架构文。
- **OpenCode 的 9 级回退**（精确 → 行 trim → 块锚点 → 空白归一 → 缩进弹性 → 转义归一 → 边界 trim → 上下文相似 50% → 多命中 replaceAll）：思路是"不要求模型精确，用工具补偿不精确"。
- **Aider 的 5 级模糊匹配**：精确 → 空白归一 → 相对缩进 → git cherry-pick → diff-match-patch。文章里那条经验仍然成立：*不同模型擅长不同格式，让格式去适配模型*。
- **Codex 的 V4A 有 4 级模糊**（精确 → 右 trim → trim → Unicode 归一），但**结构错就救不回来**。

### 3.3 落地建议（你可以照着改自己的流程）

1. **模型 × 格式要对齐**：GPT 系用 `apply_patch`/V4A；Claude 系用 `old_string/new_string` 或 SEARCH/REPLACE；Gemini 系用 search/replace + 行区间；开源小模型（GLM/DeepSeek）优先走 **9 级回退** 的实现（OpenCode 风格），别硬上 V4A。
2. **禁止整文件重写、禁止带行号 diff**，只允许"唯一命中"的锚定块；命中 0 次或 >1 次立刻返回带上下文的 40-token 诊断，让模型自己修。
3. **改完必须有验证闭环**：跑编译/测试/LSP 诊断，失败原样回灌。没有验证的 agent 只是在"生成看起来对的代码"。
4. **先索引再改**：Tree-sitter / LSP 符号图取"1 跳影响面"比向量切片准；视频侧的对应实践是 CodeGraph 索引（YouTube 上那期"省 90% token"的核心就是它）。
5. **上下文纪律**：精确 `@文件:行` 引用、任务切片、`/compact`、`/clear`、`.claudeignore`、别在会话中途换模型（会破缓存）。

---

## 4. 低成本使用：价格表 + 四个杠杆

### 4.1 先看单价（官方价，2026-10）

| 模型 | 输入 / 输出（每 1M token） | 缓存读 | 备注 |
|---|---|---|---|
| Claude Opus 5.5 | **$4 / $20** | **$0.20**（写 $5） | 比 Opus 5 便宜约 40%/任务；Fast 档 $8/$40 |
| Claude Sonnet 5.5 | 更低价（Opus 的零头） | — | 日常主力 |
| GPT-6.1 Sol | 与 6 Sol 同价 | — | Codex 默认；Ultrafast 另计价 |
| **GPT-6.1 Terra** | **$1 / $5** | **$0.05** | 10/26 上线，最便宜的多模态"看屏幕改代码" |
| Grok 4.7 | **$2 / $6** | — | 但同等任务更费 token（$3.74/任务） |
| Gemini 4 Argon / Carbon | 混合约 **$8/MTok**；Carbon 过渡期后 $4/$20 | — | Argon 不在免费层 |
| GLM-5.3（智谱） | ~**$1.40 / $4.40** | — | 最便宜的"能干活"档 |
| DeepSeek V4 Pro / Flash | 最低档 | — | 适合当"执行者"不吃推理 |

### 4.2 订阅档（月度）

| 方案 | 价格 | 含什么 | 适合 |
|---|---|---|---|
| Claude Pro | $20（年付 ≈$17） | Opus 5.5 + Sonnet + Claude Code；5 小时窗 + 周上限 | 轻度到中度 |
| ChatGPT Plus（Codex） | $20 | GPT-6.1 Sol + GPT-6 Luna；5 小时消息 + 周上限 | 中度，不封号 |
| **Grok Build** | **免费档** / $30 SuperGrok / $100 / $300 | Grok 4.7；开源 Rust TUI；可换第三方模型 | 最低门槛试 4.7 |
| **Google Antigravity** | 免费 / $20 / $100 / $200 | Gemini 3.5 Flash / 3.1 Pro / Argon（Ultra 档） | 免费额度党 |
| **GLM Coding Plan** | **Lite $18（年付 $12.6）/ Pro $72（年付 $56）/ Max $160** | 可接 **Claude Code**、Cline、OpenCode、Cursor 等 20+ 客户端；每周 credits；off-peak 半价 | 预算敏感 + 想留 Claude Code 手感 |
| Cursor Pro | $20 | Claude/GPT/Gemini 多模型 | IDE 党 |

### 4.3 四个真正省钱的杠杆（按性价比排序）

**① 缓存（最大杠杆，立刻见效）**
- Opus 5.5 缓存读 $0.20/M = 输入的 5%。**缓存一断，成本 ×12.5**（B站 9/6 实测）。
- 断缓存的常见动作：换仓库、频繁重启会话、会话中途切模型、改 system prompt / CLAUDE.md。
- 官方建议：稳定前缀（CLAUDE.md 放最前不动）、别来回切模型、长任务别开新会话。

**② effort / 模型分层**
- Opus 5.5 默认 effort **medium**（Opus 5 是 high）；同一模型不同 effort 实测成本差 **11.9 倍**。
- 探索/读代码 → Haiku 5.5 或 GLM Lite；实现 → Sonnet 5.5 / Sol；架构、疑难 → Opus 5.5 / Astra；跑终端自动化 → Terra（$1/$5）。

**③ 上下文瘦身**
- `.claudeignore`（node_modules / dist / lock / .git / coverage）实测输入 15 万 → 6 万 token。
- 好的 `CLAUDE.md` 减少"探索式 cat/find/grep"（占总输入 70–85%）。
- `context-mode`（工具输出沙箱化，−98%）/ `Supercompress`（−65%）/ CodeGraph 索引。
- 子代理不是万能：B站 10 月实测「子代理分工到底省不省？跑 12 遍，最省的是不分工」——分工前先测。

**④ 换"油"不换车**
- **magpie**（25k★，9/23）：菜单栏一键把 Codex 接到 DeepSeek、Claude Code 接到 Kimi。
- **cc-switch**（150k★）：多账号/多中转/多 harness 配置切换，支持 Grok Build。
- **CLIProxyAPI**（57k★）：一个本地网关，把 5 家 harness 包装成统一 API。
- **GLM Coding Plan** 直接接 Claude Code，等于"用 Claude Code 的界面跑 $1.4/$4.4 的模型"。
- 不用订阅、纯按量：有实测估算约 **$110/月**（B站 10/14），比 Max 5x 便宜但更费心。

### 4.4 三档推荐组合

| 预算 | 组合 | 月成本 | 说明 |
|---|---|---|---|
| **零成本** | Grok Build 免费档 + Antigravity 免费档 + Gemini API 免费层 + Ollama 本地 | $0 | 够验证想法；别接商业代码 |
| **≤$20** | Claude Pro $20（主力 Opus 5.5）+ GLM Lite $18（跑量的任务）→ 或只留一个 | $18–38 | 画质/性价比平衡最好 |
| **$40–80** | Codex Plus $20（Sol）+ Claude Pro $20 + GLM Lite $18 | $58 | 双栈互查：一个写、一个 review（Codex auto-review 免费） |
| **重度** | Claude Max 5x $100 或 Codex Pro $100 + GLM Pro $56 | $100–156 | 别用按量跑整天 |

---

## 5. 三个月内的视频/文章清单（按时间倒序，均为 3 个月内）

### B站（中文，实操向）
- [Gemini 4 Carbon 登顶｜Argon 对比](https://www.bilibili.com/video/BV1gqso6rEJY/) — 10/29
- [谷歌发布 Gemini 4 Carbon，AA 超 Opus 5.5（依旧只能看不能用）](https://www.bilibili.com/video/BV1yCsR6ZE9V/) — 10/29
- [Gemini 4 Argon 更新！免费测试教程](https://www.bilibili.com/video/BV16dso6tEPL/) — 10/29
- [国内怎么用上 Gemini 4｜Google AI Pro 开通教程](https://www.bilibili.com/video/BV1bpx367ELb/) — 10/27
- [AI 游戏开发日报 10.27｜Claude Code 2.1.311 修子代理 MCP、Codex 上线 GPT-6.1 Terra](https://www.bilibili.com/video/BV1eNxT6VEFs/) — 10/27
- [斯坦福 CS146S：如何用约 200 行代码实现 Claude Code](https://www.bilibili.com/video/BV1WWH56zEQt/) — 10/25
- [我用过的最好的 Agent IDE（Orca）](https://www.bilibili.com/video/BV1XeHK6fEkz/) — 10/24
- [多个 AI 编程代理来回切换，Orbital 让它们共用一份上下文](https://www.bilibili.com/video/BV1bmnm6MEWu/) — 10/22
- [实测 DeepSeek 新 Flash：家用跑 Claude 级代理有多贵](https://www.bilibili.com/video/BV1F8nK6zEwA/) — 10/20
- [实测：Claude Code 子代理分工到底省不省？跑 12 遍，最省的是不分工](https://www.bilibili.com/video/BV1jZnN6hEqj/) — 10 月
- [开着缓存 TOMC 还省钱吗？6 轮真实计费实测少花 55%](https://www.bilibili.com/video/BV15KJi6CEjY/) — 10/17
- [不订阅用 Claude Code，一个月约 $110？按量付费估算](https://www.bilibili.com/video/BV1pzpS6uE6f/) — 10/14
- [同一模型成本差 11.9 倍！Claude Code 官方成本表 + 子代理 effort 省钱指南](https://www.bilibili.com/video/BV1CEpt6VE74/) — 10/09
- [Claude Code 太烧钱？用 OmniRoute 省 90% AI 成本](https://www.bilibili.com/video/BV15Hap6uErM/) — 09/29
- [Codex 到底怎么用更省钱（模型定价/渠道/上下文/缓存/会话管理/思考强度）](https://www.bilibili.com/video/BV1h4a36KED9/) — 09/28 ← 31 万播放，最系统
- [Grok 4.7 来了！接入 Codex 和 Grok Build 完整教程](https://www.bilibili.com/video/BV1Ncht6NEUd/) — 09/23
- [cc-switch 使用指南第七期：Grok Build 接入配置](https://www.bilibili.com/video/BV1q1hJ6wEBn/) — 09/22
- [智谱 ZCode 偷传代码风波升级，企业发函追责](https://www.bilibili.com/video/BV1KEhB6YETM/) — 09/21 ← 必看风险
- [Grok Build 把整个 Git 仓库上传到云，隐私开关为什么没拦住](https://www.bilibili.com/video/BV1Fies6sEFv/) — 09/16
- [26K Star 的 Grok Build：和 Codex、Claude Code 差在哪](https://www.bilibili.com/video/BV1n8YT6rEJH/) — 09/10
- [缓存从 5 分钟锁到 1 小时！v2.1.265 的 3 个省钱开关](https://www.bilibili.com/video/BV18SYt6EEuJ/) — 09/09
- [缓存一断贵 12.5 倍！Claude Code 新功能告诉你在哪漏钱](https://www.bilibili.com/video/BV13Wbw6iEyb/) — 09/06
- [官方 6 招：提示缓存直接省 90%](https://www.bilibili.com/video/BV12H8p6HEEr/) — 08/22
- [DeepSeek V4 Pro 接入 Codex 还能解析图片｜CC Switch + Codex++ 双方案](https://www.bilibili.com/video/BV1t58n6EEwN/) — 08/19
- [GLM 5.3 最省钱用法：ZCode 免费档与最佳配置](https://www.bilibili.com/video/BV14w8G6sEGM/) — 08/18

### YouTube（英文，含官方）
- [OpenAI：GPT-6.1 Terra is now in orbit](https://www.youtube.com/watch?v=tTuk4pGnT0A) — 10/27
- [Gemini 4 Argon: Modernizing 40 year code（Google Antigravity 官方）](https://www.youtube.com/watch?v=biOWEPYyS5c) — 10 月
- [I TESTED Gemini 4 Argon Against Claude Opus 5.5 & GPT 6.1 Sol](https://www.youtube.com/watch?v=sjczVV-9Pn8) — 10 月
- [Vibe Coding Showdown: Claude Opus 5.5 vs Codex 6.1 Sol](https://www.youtube.com/watch?v=94NP3WfJqRg) — 10 月
- [Give Me 14 Mins and I'll Save You Millions of Claude Tokens](https://www.youtube.com/watch?v=peZyP4UC88U) — 10/19
- [Gemini 4 Argon Full Tutorial for Beginners](https://www.youtube.com/watch?v=SBYCw-oHjlQ) — 10/19
- [Grok 4.7 + Grok Bot Is CHEATING (Only $20 NOW!)](https://www.youtube.com/watch?v=OPThXcTW9Rk) — 10 月
- [Grok 4.7 Is Cheap. Can It Actually Build?（Cursor 内 16 个视觉编程基准）](https://www.youtube.com/watch?v=JRgjMRUXfqE) — 09 月
- [I Tested NEW Grok 4.7 on Coding: Another Over-Hyped LLM?](https://www.youtube.com/watch?v=VPOwJjRAm3I) — 09 月
- [How To Save 90% of Claude Code Token Usage（CodeGraph / RTK / Caveman / 会话管理）](https://www.youtube.com/watch?v=UslVzxAkiZ0) — 6 月（超出窗口，但方法论仍是参照）

### 文章/官方文档
- Google AI：Antigravity preview 09-2026（行区间编辑、原生代码搜索） https://ai.google.dev/gemini-api/docs/models/antigravity-preview-09-2026
- ChatGPT & Codex changelog（10/26 Terra、10/23 presets、10/14 GPT-5.5 退役） https://learn.chatgpt.com/docs/changelog
- Claude Opus 5.5 规格与价格 https://claudelog.com/faqs/what-is-claude-opus-5-5/
- Fable 5.1 / 5.5 家族与 Claude Code 默认模型变化 https://claude-world.com/articles/claude-fable-5-1-and-claude-5-5-family/
- Grok 4.7 发布与基准 https://www.unite.ai/spacexai-releases-grok-4-7-for-coding-and-knowledge-work/
- Gemini 4 Carbon 基准与开放状态 https://saascity.io/blog/gemini-4-carbon-benchmarks-pricing-availability-2026
- 编辑工具格式横评（apply_patch / V4A / SEARCH-REPLACE）https://charlesazam.com/blog/deepdive-benchmark/ · https://codex.danielvaughan.com/2026/03/31/codex-cli-apply-patch-v4a-diff-format/
- hashline 锚点编辑（Grok Code Fast 6.7%→68.3%）https://dev.to/alexchen31337/the-harness-problem-is-real-and-the-edit-tool-is-where-it-starts-nff
- AST 锚定 SEARCH/REPLACE 99.3% 应用率（10/17）https://falconiclab.com/blog/building-autonomous-code-agents-that-ship-working-software
- Coding Plan 对比（10/12，Claude vs Codex vs Antigravity vs GLM）https://explainx.ai/blog/claude-code-vs-codex-vs-gemini-cli-vs-glm-5-2-2026

---

## 6. 风险与坑（三个月内真实发生）

1. **ZCode 静默上传工作区 + Git 历史**（9/18，企业发函）→ 公司仓库别用来源不明的 harness；至少先看 egress 流量。
2. **Grok Build 把整个 Git 仓库传到云，隐私开关没拦住**（9/16）→ 先 `git remote -v` 和 `.env` 自查，再开 agent。
3. **第三方"免费/中转"网关**（9router、omnirush、各种 everyapi 类）：便宜是真的，但 key 与代码都过第三方；用专用小号 + 只喂公开代码。
4. **账号风险**：Cookie/共享账号/代充都有封号与合规风险；官方 $20 档通常是最省心的下限。
5. **"便宜模型更贵"陷阱**：Grok 4.7 单位价便宜但输出 token 翻倍，任务成本反而高；Gemini 4 Carbon 榜单第一但 coding agent 榜第二且尚未开放。
6. **模型过时很快**：Sonnet 4.5 将于 2026-11-30 退役；GPT-5.5 已于 10/14 从 Codex（ChatGPT 登录）下线。脚本里写死 model id 会突然坏。

---

## 7. 我建议你接下来做的三件事

1. **这周**：`npm i -g @anthropic-ai/claude-code` / `codex` 保持最新；装 **cc-switch** 或 **magpie** 做配置与模型路由；在项目里放 `.claudeignore` + 精简 `CLAUDE.md`（10 分钟，立刻省 40–60% 输入）。
2. **这个月**：拿同一个真实的"改代码"任务（跨 3 个文件、有测试）在 **Opus 5.5 / GPT-6.1 Sol / Grok 4.7 / GLM-5.3 / Gemini 4 Argon** 上各跑一遍，记录 **任务总成本**（不是单价）和 **首次通过率**——按你的仓库选，不要按榜单选。
3. **长期**：把"编辑格式"当成可配置项。你的 harness 若自研，优先抄 **OpenCode 的 9 级回退** + **AST 锚定 SEARCH/REPLACE**，并强制"改完跑测试"。

---

## 附录 A：本次检索记录（11 轮）

**全网检索（Exa 式语义搜索，`web_search`）**
1. `Claude Code 低成本使用 教程 2026` → 免费/中转/国产模型三条路
2. `最新模型 GPT-5.x Claude Opus 4.x 2026年10月 编程能力 对比` → 选型矩阵
3. `Grok 4.7 coding agent code editing 2026` → 4.7 发布、Grok Build、AA 指数
4. `Gemini 4 coding agent release September 2026 Antigravity` → Argon 10/13 GA
5. `Claude Opus 5.5 release date Claude Code default model October 2026` → 9/22 + v2.1.280
6. `Codex CLI GPT-6.1 Sol Terra release October 2026` → 0.161/0.164/0.165 changelog
7. `2026年10月 低成本 使用 Claude Code Codex 方案 glm coding plan 价格 中转 对比` → 套餐价格表
8. `coding agent code editing technique 2026 apply_patch search replace line range edit format` → 编辑协议流派 + 成功率数据
9. `Gemini 4 Carbon release Google October 29 2026 benchmarks coding` → 10/28 榜单与开放状态

**视频平台**
10. YouTube：`claude code cost save` / `gemini 4 coding agent` / `grok 4.7 coding` / `codex gpt-6.1 coding`（各取近 1 个月排序）
11. B站：`AI编程代理` / `Claude Code 省钱` / `Grok Build` / `Gemini 4 Argon`（`order=pubdate` 按发布时间排序）

**代码/仓库**
- GitHub Data API：`search/repositories?q=coding agent created:>2026-07-29`、`claude-code`、`codex`、`grok build`、`9router`、`orca agent ide`、`orbital agents`
- 逐个读取 star / 建仓时间 / 最近 push：`yetone/magpie`、`farion1231/cc-switch`、`xai-org/grok-build`、`zai-org/ZCode`、`omnirush-ai/omnirush-gui`、`HarnessRouter/harnessrouter`、`decolua/9router`、`mksglu/context-mode`、`router-for-me/CLIProxyAPI`

**渠道说明（如实交代）**
- 本次沙箱的出网白名单只有 GitHub / npm / PyPI，`yt-dlp`、`r.jina.ai`、B站 API 直连均被网络层挡住（`SSL_ERROR_SYSCALL`）；因此 YouTube 与 B站 采用**公开搜索结果页的文本抓取**（能拿到标题、UP 主、相对时间、播放量），**没有拉取字幕/评论**。真实环境里用 `yt-dlp --write-auto-sub` + `agent-reach doctor` 可以补齐字幕与评论，命令见下。
- B站 `api.bilibili.com` 直连返回 **412 风控**，`search.bilibili.com` 页面抓取可用——这也印证了 README 里"B站不要用 yt-dlp"的判断。

**下次在正常网络里复跑**
```bash
agent-reach doctor --json
yt-dlp --write-auto-sub --skip-download -o "/tmp/%(id)s" "https://www.youtube.com/watch?v=VIDEO_ID"
bili search "Claude Code 省钱" --type video -n 10
gh search repos "coding agent" --created ">2026-07-29" --sort stars --limit 20
```
