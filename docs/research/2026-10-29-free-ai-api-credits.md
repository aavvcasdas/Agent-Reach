# 免费 / 注册送额度：能调到 GPT、Claude、Grok、Gemini 改代码 的渠道清单

> 复核时间：**2026-10-29**
> 上一版调研跑偏了（写成了"付费方案对比"），这一版只做一件事：**哪些地方不花钱或少花钱就能拿到 key / 额度，并且能接进 Claude Code、Codex、Cline 这类改代码工具。**
> 标注规则：
> - ✅ **官方已核实** = 我直接读了厂商定价/文档页
> - 🟡 **第三方口径** = 聚合站/博客/视频，方向可信但数字会变，用前请自己在控制台看一眼
> - ⚠️ **存疑或已过期** = 网上还在传，但实际已经关了

---

## 0. 先分清三种"免费"

| 类型 | 长什么样 | 能不能长期用 | 例子 |
|---|---|---|---|
| **A. 永久免费层** | 不花钱、不要卡，但限速 | 能，日常挂机 | Gemini Flash 免费层、GitHub Models、NVIDIA NIM、Cloudflare Workers AI、GLM-4.7-Flash |
| **B. 注册送额度** | 一次性给 $5 / 2000 万 token | 用完即止，通常 14–180 天 | Anthropic $5、智谱 2000 万、硅基流动 16 元券、AWS $200 |
| **C. 订阅/活动白给** | 免费档里带编程 agent | 能，但有月上限 | Grok Build 免费档、Antigravity 免费档、Trae 国内版、Copilot Free、Kiro 50 次 |

**关键结论：现在"免费"能给到旗舰模型（Opus 5.5 / GPT-6.1 / Grok 4.7 / Gemini 4 Argon）的只有 B 类的一次性额度 + C 类工具内的自带额度；A 类永久免费层基本只给开源/Flash 级模型。**

---

## 1. 四大厂：官方到底送不送

### 1.1 Anthropic（Claude）✅ 送，但很少

| 项目 | 内容 | 备注 |
|---|---|---|
| 新账号额度 | **约 $5**，手机短信验证后控制台横幅点 Claim | **不需要信用卡**；VoIP / Google Voice / 座机不收 |
| 有效期 | **点 Claim 之后 14 天**（不是注册后 14 天） | 所以别提前领，要用的时候再点 |
| 能买多少 | Haiku 级约几百万 token、Opus 级约 100 万输入 token | 够跑十几次 Claude Code 会话 |
| 限速 | 新号约 5 RPM | 免费层慢是正常的 |
| 可覆盖范围 | API、Console Workbench、**Claude Code 都能花这 $5** | 这是免卡跑 Claude Code 唯一官方路径 |
| 大额路径 | Claude Startups（约 $1,000 API credits，6 个月）、Claude for Open Source、学生计划 | 要申请/资格 |

🟡 社区口径把有效期写成"3 个月"的也有，以控制台横幅为准。
⚠️ 网上还有"$25,000 免费 Claude 额度"——那是 Menlo Ventures 的 Anthology Fund 特定伙伴项目，不是通用额度。

### 1.2 OpenAI（GPT）⚠️ 新号基本不送了，但有两条"暗门"

| 路径 | 内容 | 门槛 |
|---|---|---|
| 新账号 | **已无自动赠送**，最低要先充 $5 🟡 | 想白嫖的可以放弃这条 |
| **Data Sharing 每日免费 token** | 开启数据共享后**每天**给：旗舰模型 25 万–100 万 token/天，小模型 250 万–1000 万 token/天（按 usage tier） | **账户余额必须为正（充 $1 也行）**，只有组织 owner 能开；不含 gpt-6-astra |
| Codex for Students | **$100 ChatGPT 额度给 Codex** | 仅美/加认证学生 |
| Codex for Open Source | API 额度 + 6 个月 ChatGPT Pro + Codex Security | 主流开源项目维护者 |
| Microsoft for Startups | Azure 额度 **$1,000 + 无投资人再加 $4,000**，可付 Azure OpenAI | 未到 C 轮的创业公司 |
| Researcher Access / 网络安全 grant | 最高 $1,000 / 分批 $10,000 | 申请制 |

> 想"纯免费"用 GPT 改代码，实际最顺的是 **GitHub Models**（见 2.3）和 **Vercel AI Gateway 的 $5/月**（见 2.2），而不是 OpenAI 自己。

### 1.3 xAI（Grok）✅ 不送 API，但送"Grok Build"免费档

| 路径 | 内容 | 关键点 |
|---|---|---|
| **Grok API** | **明确没有免费层**，新号 0 额度，官方文档只写"先充值再调用" | 网上流传的"注册送 $25 + 每月 $150"是 **2024 年公测活动，已于 2024-12-31 结束** ⚠️ |
| **X Subscription Free（$0 档）** | 含**有限量的 Grok Build**（xAI 的终端编程 agent）+ 有限 Chat / 生图；从 10/12 起取代 SuperGrok 作为购买入口 | **这是目前合法免费用 Grok 4.7 改代码的最直接路径** |
| Grok Build 本体 | 2026-09-19 开源（`xai-org/grok-build`，27.6k★，Rust），可自带第三方 API | 免费档额度有限，重度要上 $30 档 |
| 第三方 "Grok $5" 站点（如 Grokified） | 注册送 $5，但**要首次付款才解锁**，且 grok-4.7 需 Basic 计划 | 别当免费额度 |

### 1.4 Google（Gemini）✅ 有免费层，但旗舰被排除

我直接读了官方定价页（2026-10-29）：

| 模型 | Free Tier |
|---|---|
| **Gemini 4 Argon** | **Free Tier 列 = "Not available"**，官方原文：*"Gemini 4 Argon is not available on the Free tier or on the Google AI Pro plan"* |
| Gemini 3.8 Flash / 3.6 Flash | **Free of charge**（输入输出都免费） |
| Gemini 3.5 Flash-Lite / 3.1 Flash-Lite | Free of charge |
| Gemini 3.1 Pro Preview | Not available |
| Gemma 4 | Free of charge |

- 免卡、只要 Google 账号：`aistudio.google.com/apikey`
- 限速：🟡 社区跟踪约 **10–15 RPM / 1,000–1,500 RPD**（Google 不再公布统一表，实际看 `aistudio.google.com/rate-limit`）
- 免费层**你的内容会被用于改进产品**，别喂公司代码
- **学生**：🟡 美国在读高校生可领 **12 个月 Google AI Pro 免费**（原价 $19.99/月），140+ 其他市场给 12 个月 AI Plus 免费；**2026-12-31 前领取**，SheerID 认证，到期自动续费要自己取消；加拿大/香港/澳门/阿尔巴尼亚/玻利维亚/突尼斯不参加
- **Argon 的免费路径只有两个**：10,000 名科学家 6 个月 Antigravity 最高档（申请制）、Fairwind 安全计划（定向）
- **Antigravity 免费档**：🟡 约 20 requests/day（曾有过 250，被砍）

---

## 2. 聚合网关：一次注册，多个模型一起用（最推荐）

### 2.1 OpenRouter ✅ 官方文档已核实

| 项目 | 数值 |
|---|---|
| 免费模型 | 25+ 个（ID 带 `:free` 后缀），免卡注册 |
| **RPM** | **20 次/分钟**（任何账户都不变） |
| **RPD** | **50 次/天**（从没买过 credits）→ **1,000 次/天**（历史累计买过 ≥$10，买完余额归零也保留） |
| 额外坑 | 余额为负时**连免费模型也返回 402**；失败的请求也计入每日额度；免费端点优先级最低，高峰会排队/掉线 |
| 官方自检 | `GET https://openrouter.ai/api/v1/key` → `free_model_daily_requests` 字段直接告诉你今天还剩多少 |

> 这 $10 是整个生态里性价比最高的一次性投入：不是订阅，credits 不会过期，永久把免费额度从 50 提到 1,000。
> 免费模型清单每月轮换，**不要写死 model id**，用 fallback 数组。

### 2.2 Vercel AI Gateway ✅ 每月 $5，零加价

- 每个 Vercel team 每月 **$5 免费 credit**，30 天刷新，**不用绑卡**
- 走网关时 **token 按厂商原价，不加价**；Claude / GPT / Gemini / Grok 都能调
- ⚠️ 一旦你**买过** credits 就转成 paid，每月 $5 停止发放（所以别乱充值）
- 适合当"临时要用 Opus 5.5 / GPT-6.1 干一票"的接口

### 2.3 GitHub Models ✅ 免卡、能调 GPT / Claude / Grok，但额度很小

| 档位 | RPM | RPD | 单请求上限 |
|---|---|---|---|
| Low 档（小模型） | 15 | 150 | 8K 输入 / 4K 输出 |
| High 档（GPT-4o、o3 这类） | 10 | **50** | 8K 输入 / 4K 输出 |

- 用一个 **GitHub PAT** 就能调，OpenAI 兼容端点，不用另外注册 AI 厂商
- 优点：这是**不用 OpenAI 账号就能碰 GPT 系**的少数正规口子
- 缺点：8K 输入对"读一个仓库改代码"来说太小，只适合单文件、问答题

### 2.4 NVIDIA NIM ✅ 1000 credits/月，免卡，开源模型最多

- `build.nvidia.com` 注册 NVIDIA Developer 账号（免费、无卡），拿 `nvapi-` key
- **每月 1,000 credits**（≈1,000 次标准请求），可申请提到 5,000；约 40 RPM
- 目录里有 **DeepSeek-V4 Pro/Flash（1M 上下文）、Nemotron 3、GLM-5.1、Qwen 3.5、Kimi K2.5、Llama 4**
- OpenAI 兼容端点：`https://integrate.api.nvidia.com/v1`
- ⚠️ **免费端点的输入输出会被记录用于训练**，别喂私有代码

### 2.5 其他真·永久免费层

| 平台 | 免费额度 | 免卡 | 适合 |
|---|---|---|---|
| **Cloudflare Workers AI** | **10,000 neurons/天** | 是 | 开源模型；`https://api.cloudflare.com/client/v4/accounts/{id}/ai/v1`；免费层有 8K 上下文限制 |
| **Cerebras** | **100 万 tokens/天**（约 30 RPM，免费层上下文 8,192） | 是 | 速度最快（2600+ tok/s），适合跑批量重构 |
| **Groq** | 每模型不同，如 gpt-oss-120b：30 RPM / 8,000 TPM / 1,000 RPD / 20 万 tokens 天 | 是 | 低延迟交互 |
| **Together AI** | 🟡 $1 试用 | 是 | 小规模 |
| **Mistral** | 🟡 免费层限速很低 | 是 | 欧洲合规 |

> 这些平台**都只给开源权重模型**，没有 GPT / Claude / Gemini 旗舰。它们的价值是：**把"跑量、跑批、跑测试"的活免费消化掉，把贵的旗舰模型留给真正难的改动。**

---

## 3. 国内平台：中文用户注册送得最多的就在这

| 平台 | 注册送 / 永久免费 | 能干什么 | 备注 |
|---|---|---|---|
| **智谱 BigModel** ✅ | **2000 万 tokens 体验包** + 120 次图像/视频；**GLM-4.7-Flash 长期免费** | GLM-5.3（1M 上下文）、GLM-5.3-Flash（320B-A18B，原生多模态） | 官方 coding 页写明新用户专享 2000 万；有"从 Claude API 搬家"活动，改 URL 即可 |
| **硅基流动 SiliconFlow** 🟡 | 实名送 **16 元券**（活动到 2026-12-31）+ **小参数模型永久 0 元** + 邀请叠加无上限 | DeepSeek-V4、GLM-5.2、Kimi-K2.7 等 | OpenAI 兼容，base_url 一改就能接 |
| **火山方舟（字节）** 🟡 | **每个模型 50 万 tokens 永久免费**；另有"每天 200 万 tokens"口径（存疑，两说） | 豆包 Seed-2.0、DeepSeek-V4、GLM-5.2 | **学生认证最高 1 亿 tokens**；有"安心体验模式"防超量扣费 |
| **阿里云百炼** 🟡 | 新用户 5000 万 tokens（另一说 7000 万/1M each 90 天） | Qwen 全系 | 口径不统一，注册后看实际到账 |
| **百度千帆** 🟡 | ERNIE-Lite / Speed 长期免费（限 QPS） | ERNIE 系 | 中文场景兜底 |
| **智谱 ZCode** 🟡 | 自家 coding harness，有免费档 | 编程 agent | ⚠️ **2026-09-18 被曝静默上传工作区与 Git 历史，企业发函**，商用慎用 |

### ⚠️ 已经完全关闭，别再找了

- **Qwen Code 的免费 OAuth 额度（每天 2000 次）**：2026-04-15 **正式停止**，官方 README 已写明；后续要接百炼 API Key / OpenRouter / 本地模型。网上 2025 年的教程还在传 2000 次/天，别信。
- **xAI 每月 $150 公测额度**：2024-12-31 结束。
- **Google Cloud $300 试用金抵 Gemini API**：2026-03 起不适用了（Vertex AI 另说）。
- **Gemini Pro 系列免费层**：2026-04-01 起移除，只剩 Flash / Flash-Lite。

---

## 4. 不注册就拿额度的"野路子"：能用，但要看清代价

| 方式 | 原理 | 风险 | 我的建议 |
|---|---|---|---|
| **Puter.js**（"User-Pays"） | 你的前端调 `puter.ai.chat()`，账单记在**使用者自己的 Puter 账号**上，开发者 0 成本；官方教程已支持 Claude 5.5 全家、GPT 系 | 只在**浏览器端**跑，CLI 改代码用不了；不是"无限"而是"用户各自有 starter credit" | 做 demo/网页应用可以；别指望它跑 Claude Code |
| **中转站注册送**（CatRouter 600 万 token、诗云 GitHub 登录送 50 元、Chintao 送 10 元、DawCode 送 4 元…） | 第三方聚合，注册即送余额，国内直连 Claude/GPT | **跑路、掺水（用便宜模型冒充）、代码与 key 全过第三方、封号**；这些数字来自 2026-05 的聚合文，**当前是否还活着我没法验证**（沙箱出网受限） | 只当"试一下"用：一次性小号 + 只喂公开 demo 代码 + 绝不接公司仓库 |
| **"免费 API key" GitHub 仓库** | 公开贴别人的 key | **已吊销或钓鱼**，Anthropic 明确说这类 key 很快被封 | 直接跳过 |
| **共享/代充账号** | 多人共用一个 Pro/Max | 封号、合规、钱打水漂 | 不如用 Anthropic $5 + 学生计划 |

---

## 5. 把免费 key 接进你现在的改代码工具（可直接抄）

### 5.1 Claude Code × 任意 Anthropic 兼容端点（智谱 / Kimi / 部分中转）
```bash
# 以智谱为例（它提供 Anthropic 兼容入口，官方有"Claude API 搬家"活动）
export ANTHROPIC_BASE_URL="https://open.bigmodel.cn/api/anthropic"
export ANTHROPIC_AUTH_TOKEN="你的key"
export ANTHROPIC_MODEL="glm-5.3"          # 或 glm-5.3-flash 省钱
claude
```
> 换成 Moonshot / 其他家同理，只要它给 Anthropic 兼容的 base_url。

### 5.2 Claude Code × OpenAI 兼容端点（OpenRouter / NIM / Cerebras / 硅基流动）
Claude Code 只认 Anthropic 协议，所以要加一层转换：
```bash
npm i -g claude-code-router        # 或装 magpie（9/23 新出，菜单栏切换）
# 配置里把 provider 指到 OpenAI 兼容 base_url，例如：
#   https://openrouter.ai/api/v1        模型 openrouter/...
#   https://integrate.api.nvidia.com/v1  模型 deepseek-ai/deepseek-v4-pro
#   https://api.cerebras.ai/v1          模型 qwen-3.8-27b
ccr code    # 用 router 启动 claude
```

### 5.3 Codex CLI × 任意 OpenAI 兼容端点
`~/.codex/config.toml`：
```toml
model = "glm-5.3-flash"
model_provider = "zhipu"

[model_providers.zhipu]
name = "Zhipu"
base_url = "https://open.bigmodel.cn/api/paas/v4"
env_key = "ZHIPU_API_KEY"
```
```bash
export ZHIPU_API_KEY="..."
codex
```
> 同理可填 OpenRouter / NIM / Cloudflare / 硅基流动。**注意：Codex 的 `apply_patch`(V4A) 格式是给 GPT 系训练过的，换国产模型失败率会明显升高**，建议配 `opencode` 那种 9 级模糊匹配的 harness。

### 5.4 Gemini 系
```bash
export GEMINI_API_KEY="..."     # AI Studio 免费层 key（只有 Flash 系）
# Gemini CLI 已不再服务消费者账号，改用 antigravity CLI
```

---

## 6. 我建议的 $0 启动方案（按优先级领）

**第 1 天（30 分钟内能拿到全部）**
1. **Anthropic $5**（console.anthropic.com，手机验证后点 Claim）→ 免卡跑 Claude Code 十几次真实会话
2. **Gemini API key**（AI Studio，免卡）→ Flash 系无限量跑读代码/写测试
3. **GitHub Models**（用现有 GitHub PAT）→ 不用 OpenAI 账号就能对比 GPT 系
4. **OpenRouter 免费模型**（免卡）→ 25+ 模型混着用
5. **智谱 2000 万 tokens**（实名）→ 中文场景 + 1M 上下文的长仓库
6. **NVIDIA NIM 1000 credits/月**（免卡）→ DeepSeek-V4 / Qwen / Kimi 跑批

**第 2 天（换手感）**
7. **Grok Build 免费档**（X Subscription $0 档）→ 体验 Grok 4.7 改代码
8. **Antigravity 免费档**（约 20 次/天）→ 体验 Gemini agent IDE
9. **Kiro Free**（50 次/月，Claude Sonnet 4.5）→ 体验 spec-driven
10. **Copilot Free**（2,000 补全 + 50 chat/月）→ 补全兜底
11. **Trae 国内版**（免费不限量，豆包/DeepSeek/Kimi）→ 国内不翻墙的日常 IDE

**唯一值得花的钱（想长期跑）**
- **OpenRouter 一次性 $10** → 免费模型从 50 次/天变 1,000 次/天，永久生效，credits 不过期
- 想稳定用 Claude Code 又不想 $20/月：**GLM Coding Plan Lite $18（年付 $12.6）**，直接接 Claude Code

---

## 7. 坑清单（这三个月真实发生的）

1. **免费层都会盯你的数据**：Gemini 免费层、NVIDIA NIM、OpenAI Data Sharing、Cloudflare 免费层，条款都写了会用你的输入输出改进模型 → **公司仓库、客户代码、密钥一律不要走免费层**。
2. **免费额度会突然关**：Qwen Code 2000 次/天（4/15 关）、Gemini Pro 免费层（4/1 移）、xAI $150/月（2024 关）、Google $300 抵 Gemini（3 月停）。**任何"永久免费"都要按季度复核。**
3. **RPD 会被失败请求吃掉**：OpenRouter 明确写了失败也计数，重试循环会瞬间烧光当天额度 → 必须做指数退避 + 上限。
4. **余额为负连免费模型都 402**（OpenRouter）→ 别让余额掉到负数。
5. **免费端点优先级最低**：高峰排队、超时，agent 跑到一半断掉 → 长任务留 fallback model。
6. **免费额度 ≠ 能给 agent 用**：8K 上下文（GitHub Models、Cerebras 免费层）装不下一整个文件树，硬上会疯狂失败重试，反而更慢。
7. **第三方中转**：跑路、掺水、封号三件套，别接生产。

---

## 8. 这次检索怎么做的（12 轮）

**官方页直读（✅ 可信度最高）**
- `ai.google.dev/gemini-api/docs/pricing` — 逐个模型核对 Free Tier 列（Argon = Not available / 3.8 Flash = Free）
- `openrouter.ai/docs/api_reference/limits` — 20 RPM、50→1,000 RPD、`free_model_daily_requests` 字段、402/429 语义

**全网检索（`web_search`，按主题分轮）**
1. 2026 年 10 月 免费 API 额度 / 注册送 Claude GPT Gemini Grok
2. Gemini API free tier rate limits 2026
3. Anthropic API free credits new account 2026
4. xAI Grok API free credits 2026
5. OpenRouter free models daily limit / $10 解锁
6. GitHub Copilot free plan 2026
7. Qwen Code free 2000 requests/day（→ 发现已于 4/15 关闭）
8. Cerebras / Groq free tier 2026
9. Google Antigravity free tier 2026
10. Trae / Windsurf / Cursor 免费额度 2026
11. 硅基流动 / 火山方舟 / 智谱 免费额度
12. AWS free tier $200 Bedrock、GitHub Models、NVIDIA NIM、Vercel AI Gateway、学生免费计划、Puter.js

**没能验证的（沙箱只有 GitHub/npm/PyPI 出网）**
- 各"中转站"是否还活着、送的额度是否真实 → 全部标了 🟡，别按我写的数字当承诺
- Anthropic $5 的当前有效期（14 天 vs 3 个月两种说法）→ 领的时候看横幅原文
- 火山方舟"每天 200 万"与"每模型 50 万永久"两个口径 → 注册后看控制台账单

**下次自己在正常网络里复核**
```bash
# 1) 官方额度
curl -s https://openrouter.ai/api/v1/key -H "Authorization: Bearer $OR_KEY" | jq .data.free_model_daily_requests
# 2) Gemini 免费层
open https://aistudio.google.com/rate-limit
# 3) 各平台到账
#    智谱 open.bigmodel.cn/console  |  硅基流动 cloud.siliconflow.cn  |  火山方舟 console.volcengine.com/ark
```
