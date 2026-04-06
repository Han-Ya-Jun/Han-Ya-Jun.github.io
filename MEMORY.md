# MEMORY.md - 长期记忆库

## 🚨🚨🚨 CRITICAL：系统保护规则（最高优先级）🚨🚨🚨

### 绝对禁止的操作

1. **禁止删除或修改以下文件**（已设置 chattr +i 不可变属性）：
   - `/root/.openclaw/openclaw.json` — 核心配置文件
   - `/root/.openclaw/cron/jobs.json` — 定时任务配置
   - `/root/.acpx/config.json` — ACP 代理映射配置（chmod 444）

2. **禁止删除以下 skill 核心文件**（量化分析系统，2026-03-09 因误删重建）：
   - `skills/stock-analysis-lianghua-integrated/quant_analysis.py` — 量化分析引擎
   - `skills/stock-analysis-lianghua-integrated/chinese_chart_generator.py` — 图表生成器
   - `skills/stock-analysis-lianghua-integrated/main.py` — 主入口
   - `skills/stock-analysis-lianghua-integrated/longbridge_query.py` — 长桥数据查询
   - `skills/stock-analysis-lianghua-integrated/news_fetcher.py` — 新闻获取
   - 这些文件**只能修改，不能删除**。如需重构，先备份再改写。

3. **禁止通过 `exec` 运行任何 claude 命令**：
   - ❌ `exec({ command: "claude ..." })` / `npx @anthropic-ai/claude-code ...` 等
   - 原因：exec 有超时限制，复杂任务会被 SIGTERM 杀掉

4. **禁止修改系统 crontab 中的 OpenClaw 定时任务**
   - OpenClaw 有自己的内部定时任务系统（`/root/.openclaw/cron/jobs.json`）

---

## PREF-2026-02-01-01：Agent 身份与用户偏好

**type**: preference | **date**: 2026-02-01 | **updated**: 2026-03-10

### Agent 身份
- 名称：hanbot 🦊（聪明、机智的狐狸）

### 用户信息
- 用户：handry（QQ 昵称：朗月清风）
- 语言：中文
- 时区：北京时间 (UTC+8)
- 位置：深圳市龙华区
- 主渠道：QQ Bot (c2c)

---

## PREF-2026-04-03-01：股票分析报告模板

**type**: preference | **date**: 2026-04-03

股票量化分析报告统一使用以下模板：
- **模板文件**: `/root/.openclaw/workspace/report-template-final.html`
- **特点**: 渐变背景 + 玻璃态卡片效果
- **截图工具**: Playwright (chromium)
- **输出格式**: PNG 长图

禁止直接使用 Pillow 绘制报告（效果差）。

流程：
1. 读取模板 → 替换占位符 → 保存 HTML
2. Playwright 打开 HTML → 截图生成 PNG
3. 通过 `<qqimg>` 发送

---

## DEC-2026-03-02-01：记忆与备份体系

**type**: decision | **date**: 2026-03-02 | **importance**: high

### 三层记忆架构
1. **会话记忆**（RAM）— 短期，自动压缩
2. **每日日志**（`memory/YYYY-MM-DD.md`）— 工作记录
3. **长期记忆**（`MEMORY.md`）— 重要决策与偏好

### 使用规则
- ID前缀：DEC（决策）、PREF（偏好）、FACT（事实）、POLICY（规则）、ARCH（架构）

### 备份系统
| 时间 | 任务 |
|------|------|
| 02:00 每天 | 本地备份 (cron-backup skill) |
| 02:30 每天 | 腾讯云 COS 同步 (`cron-backup-cos-with-memory.sh`) |
| 03:00 每天 | 清理旧备份 (30天) |
| 12:00 每天 | 记忆文件整理 (`cleanup-memory.sh`) |
| 04:00 每周日 | Workspace 清理 (workspace-cleaner skill) |

---

## FACT-2026-03-10-01：系统架构总览

**type**: fact | **date**: 2026-03-10 | **importance**: critical

### 双 AI 助手架构

| 服务 | 管理方式 | 端口 | 说明 |
|------|----------|------|------|
| OpenClaw Gateway | systemd user 服务 | 18789 | 主 AI 助手（Node.js） |
| PicoClaw Gateway | systemd 系统服务 (`picoclaw.service`) | 18790 | 轻量 AI 助手（Go v0.2.2，运维专用） |
| 量化引擎 | supervisord | 19001 | Go 版量化交易 |

### OpenClaw QQBot
- 插件：`@tencent-connect/openclaw-qqbot@1.5.7`（插件ID: `openclaw-qqbot`），路径：`/root/.openclaw/extensions/openclaw-qqbot/`
- AppID：`102921772`
- Token 格式：`appId:clientSecret`
- 消息模式：Markdown（msg_type=2），换行用 `\n\n`
- 主动消息 API：`sendProactiveC2CMessage`（每月限制）
- 已知用户数据：`/root/.openclaw/qqbot/data/known-users.json`
- Target：`qqbot:c2c:E81F367BE00DFCDC7DD603BA86E69F7C`

### PicoClaw（2026-03-10 部署）
- 端口 18790，systemd 系统服务 `picoclaw.service`，当前版本 v0.2.2
- 配置：`/root/.picoclaw/config.json`，默认模型 `ark-code-latest`
- QQ Bot AppID：`102923388`
- 双向运维 Skill：OpenClaw 侧 `picoclaw-ops`、PicoClaw 侧 `openclaw-ops`

---

## FACT-2026-03-10-02：模型与 API 配置

**type**: fact | **date**: 2026-03-10 | **importance**: high

### 当前模型配置

#### OpenClaw 主模型
- **当前**: `xchai/claude-opus-4-6`
- **配置位置**: `openclaw.json` → `agents.defaults.model.primary`

#### ACP Claude Code（编程助手）
- **当前**: xchai.xyz / `claude-opus-4-6`
- **环境变量**（`~/.bashrc`）:
  - `ANTHROPIC_BASE_URL="https://xchai.xyz"`（注意：不是 `ANTHROPIC_API_URL`）
  - `ANTHROPIC_API_KEY="sk-M3Y8..."`
  - `ANTHROPIC_MODEL="claude-opus-4-6"`

#### 图片识别
- **当前**: `xchai/claude-opus-4-6`
- **QQ Bot 图片路径**: `/root/.openclaw/qqbot/downloads` → 符号链接到 `/root/.openclaw/media/qqbot-downloads`

#### ⚠️ ACP 调用规则
- `agentId` 必须使用 `"claude"`（不要用 `"claude-code"`）
- 正确: `sessions_spawn({ "runtime": "acp", "agentId": "claude", "mode": "run", "task": "..." })`
- ACP 权限模式：`approve-all`
- ACP 失败时，自己直接写代码，不要尝试 exec 运行 claude CLI

### 可用 Provider

| Provider | Base URL | 协议 | 模型 |
|----------|----------|------|------|
| xchai | `https://xchai.xyz` | anthropic-messages | claude-opus-4-6, claude-sonnet-4-6 |
| arkcode | `https://ark.cn-beijing.volces.com/api/coding` | anthropic-messages | ark-code-latest, doubao-seed-2.0-code, glm-4.7, deepseek-v3.2, kimi-k2.5 |
| qcloudlkeap | `https://api.lkeap.cloud.tencent.com/v1` | openai-completions | deepseek-v3.2 |
| moonshot | `https://api.moonshot.cn/v1` | openai-completions | kimi-k2.5, kimi-k2-thinking, moonshot-v1-128k |

### PicoClaw 模型注意事项（2026-03-10 踩坑）
- xchai 代理 API：`api_base` 必须是 `https://xchai.xyz/v1`（不能省略 `/v1`，否则返回 HTML）
- ARK Code 在 PicoClaw 中：用 `anthropic/` 前缀 + `api_base: https://ark.cn-beijing.volces.com/api/coding/v1`
- 腾讯云 DeepSeek：用 `openai/` 前缀，兼容性最好
- Anthropic 代理偶发 `content_chars=0`（空回复），可能是协议兼容问题

### 切换方法
- **切主模型**: 改 `openclaw.json` 的 `agents.defaults.model.primary`
- **切 ACP Claude Code**: 改 `~/.bashrc` 的环境变量
- **切图片识别**: 改 `openclaw.json` 的 `agents.defaults.imageModel`
- **生效**: `openclaw gateway start` 重启网关

---

## PREF-2026-03-07-01：新闻推送偏好

**type**: preference | **date**: 2026-03-07 | **importance**: high

| 时间 | 名称 | 风格 |
|------|------|------|
| 09:00 | 🌅 AI+金融早报 | 综合早报，涵盖隔夜动态 |
| 12:00 | ☀️ AI+金融午间快讯 | 聚焦上午重要事件 |
| 19:00 | 🌙 AI+金融晚间总结 | 全天回顾+明日展望 |

- **领域**: AI + 金融投资（含加密货币）
- **来源**: RSS订阅 + 搜索补充
- **格式**: emoji 装饰，每条一行标题+摘要，6-8条
- **工具**: `rss-ai-reader/` + `config_finance_ai.yaml`

---

## DEC-2026-03-07-01：定时任务

**type**: decision | **date**: 2026-03-07

### OpenClaw 内部 Cron (`cron/jobs.json`)

| 任务 | 时间 | 说明 |
|------|------|------|
| rss-morning-09 | 09:00 每天 | AI+金融早报 |
| rss-noon-12 | 12:00 每天 | AI+金融午间快讯 |
| rss-evening-19 | 19:00 每天 | AI+金融晚间总结 |
| stock-daily-report | 08:30 工作日 | 股票日报分析（长桥 API） |

由 OpenClaw Gateway 自动调度，配置在 `/root/.openclaw/cron/jobs.json`。

---

## DEC-2026-03-07-02：搜索技能

**type**: decision | **date**: 2026-03-07 | **importance**: high

### 搜索策略优先级
1. **search-layer**（首选）— 多源聚合（Exa/Tavily/Brave/Grok）
2. **Exa MCP**: `mcporter call exa.web_search_exa(...)` — AI 优化结果
3. **DuckDuckGo**: `web_fetch("https://lite.duckduckgo.com/lite/?q=...")` — 无需 API
4. **multi-search-engine** — 17 引擎 URL 参考

### MCP 配置
- `exa` → `https://mcp.exa.ai/mcp`（基础 2 工具）
- `exa-full` → 含高级工具（深度研究、公司调研等 8 工具）

---

## POLICY-2026-03-07-01：Skill 安装安全规则

**type**: policy | **date**: 2026-03-07 | **updated**: 2026-03-09 | **importance**: critical

**🚨 强制要求：每次安装 skill 前必须先用 `skill-vetter` 检查安全性 🚨**

**流程（不可跳过）：**
1. 发现新 skill → **立即停止，先 vetter**
2. 读取 `skill-vetter` SKILL.md，按流程审查代码
3. 生成 VETTING REPORT，通过后再安装

**触发关键词**：`skillhub install`、`clawhub install`、`git clone` skill、"装个 XXX"

**违规记录**：2026-03-09 安装 my-system-info-skill 时忘记先扫描（第N次）

---

## PREF-2026-03-07-02：股票分析报告格式

**type**: preference | **date**: 2026-03-07 | **importance**: high

**标准输出模板:**
```
📊 股票名称 (代码) 深度分析报告
📅 分析时间

💹 实时行情 → 现价、涨跌幅、成交量、成交额
🎯 量化评分: XX/100 → 四因子（趋势/动量/波动率/成交量）+ 交易建议
🎯 关键价位 → 支撑位、阻力位
⚠️ 风险指标 → 年化波动率、最大回撤、夏普比率
📰 重磅消息面 → 地缘政治/机构评级/业务进展/财报
💡 综合研判 → 利好✅ / 风险⚠️ / 操作建议
⚠️ 免责声明
<qqimg>图表路径</qqimg>
```

**核心原则：严禁编造新闻。搜索全部失败时标注"暂时不可用"。**

**完整分析流程（必须按顺序执行）：**
1. `longbridge_query.py` + `quant_analysis.py` → 行情/技术指标/多因子评分
2. `chinese_chart_generator.py` → K线+均线+布林带+MACD+RSI 图表
3. `news_fetcher.py`（调用 search-layer）→ 新闻搜索
4. AI 整合 → 完整分析报告

---

## FACT-2026-03-06-01：长桥 API

**type**: fact | **date**: 2026-03-06

- 环境变量已配置到 systemd 服务（`openclaw-gateway.service`）
- `config.yaml` 已配到 openclaw-trade 目录，已加入 .gitignore
- SDK: longbridge v0.2.77 (Python)
- MCP: `/usr/local/bin/longport-mcp`
- MCP 需同时配置在：`~/.mcporter/mcporter.json`、`/root/.openclaw/config/mcporter.json`、`/root/.openclaw/workspace/config/mcporter.json`

### 股票数据源
- **弃用**: yfinance（限速）、Finnhub（限额低）
- **当前**: 长桥 OpenAPI

### 监控列表
- 港股: 700.HK, 9988.HK, 3690.HK, 9618.HK, 1810.HK, 9888.HK, 2318.HK, 1211.HK
- 美股: AAPL.US, MSFT.US, NVDA.US, GOOGL.US, AMZN.US, META.US, TSLA.US, TSM.US
- A股: 600519.SH, 000858.SZ, 300750.SZ, 601318.SH, 000001.SZ, 600036.SH, 002594.SZ, 603259.SH

---

## FACT-2026-03-08-01：部署信息

**type**: fact | **date**: 2026-03-08

- GitHub Pages: `https://hanyajun.com/static-pages/`
- 静态文件路径: `/root/.openclaw/workspace/static-pages/`
- RSS AI Reader: `/root/.openclaw/workspace/rss-ai-reader/`
- RSS 主配置: `config_finance_ai.yaml`（不存在时用 `config_optimized.yaml`）

---

## ARCH-2026-03-09-01：量化交易系统

**type**: architecture | **date**: 2026-03-09 | **importance**: critical

- Go 项目 `openclaw-trade`，路径 `/root/.openclaw/workspace/openclaw-trade`
- 进程管理：supervisord（端口 19001），3 个策略进程（quant-all / quant-0dte-qqq / quant-0dte-spy）
- 信号推送：Go notify → `/hooks/agent` → OpenClaw Gateway → QQBot
- Hooks token: `34369261bec67cb2fd1a830ca346e063`
- 策略详情、进程管理命令、持仓对应表见 `skills/quant-ops/`

---

## DEC-2026-03-10-01：PicoClaw 部署

**type**: decision | **date**: 2026-03-10 | **importance**: high

- 用途：OpenClaw 备用助手 + 运维诊断，独立 QQ Bot
- 踩坑：xchai 必须加 `/v1`；ARK Code 用 `anthropic/` 前缀；Anthropic 代理偶发空回复可换 OpenAI 协议模型
- 详细操作记录见 `memory/2026-03-10.md`，运维细节见 `skills/picoclaw-ops/`

---

## DEC-2026-03-25-01：妖股扫描策略优化

**type**: decision | **date**: 2026-03-25

- **问题**：`meme_loop_scan.sh` 每 10 分钟无限循环扫描，盘前/盘后反复触发
- **改为**：每个时段只扫描 3 次（间隔 5 分钟）确认候选，之后只运行妖股策略不再扫描
- **状态文件**：`runtime/meme-scan-state-{session}-{date}.json` 跟踪扫描次数
- 脚本路径：`openclaw-trade/scripts/meme_loop_scan.sh`
- **⚠️ 工作日限定**：2026-03-29 handry 确认，妖股扫描只在工作日运行，周末跳过（非交易日无意义）

---

## DEC-2026-03-25-02：QQQ 0DTE 网格策略优化

**type**: decision | **date**: 2026-03-25

### 问题
- `grid_spacing` $1.0 太小，QQQ 窄幅震荡时每 2-3 分钟触发一次
- 同一档位 call 13 分钟内反复买卖 4 次，扣手续费几乎无利润
- 网格以当前价为中心对称设，不参考近期价格区间

### 修改
| 参数 | 旧值 | 新值 |
|------|------|------|
| `grid_spacing` | $1.0 | **$2.0** |
| `minHoldMinutes` | 无 | **5 分钟** |
| `lookbackBars` | 无 | **30 根 1m bar** |
| 网格上下限 | 价格 ± 间距×N | **近期 K 线高低点** |

- 网格基于最近 30 分钟 K 线最高/最低价设定上下限
- 档位在区间内均匀分布（非等间距对称）
- 文件：`internal/strategy/qqq_0dte_grid.go`

---

## FACT-2026-03-25-01：IMA 技能安装

**type**: fact | **date**: 2026-03-25

- IMA OpenAPI 技能（笔记 + 知识库管理）
- 路径：`skills/ima-skill/`
- 凭证：`~/.config/ima/client_id` + `~/.config/ima/api_key`
- API 验证通过（ima.qq.com）
- 来源：`https://app-dl.ima.qq.com/skills/ima-skills-1.1.2.zip`

---

## 已废弃（归档）

- `monitor-signals.sh`、`openclaw-signal-push.service`、`monitor-quant-signals.py` — 旧日志轮询方案，已被 Go notify 模块替代
- yfinance、Finnhub — 已被长桥 OpenAPI 替代
- perplexity、tavily-search skill — 无 API key，已移除
- Python 旧量化系统 — 已被 Go 版 openclaw-trade 替代
