# 欧元区利率/央行数据抓取配方（ECB + TradingEconomics）

2026-07 会话实战验证。适用：ECB 决议 brief、HICP/核心通胀、€STR、市场定价等带实时数字的任务。

## 0. 总原则

- **ECB 官网永远直接 curl，不用 r.jina.ai**。r.jina.ai 等 `networkidle`，ECB 页面太重 → 15s 超时（`TimeoutError: page.goto ... networkidle`）。用：
  ```bash
  curl -sL --max-time 60 -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" "<URL>" -o /tmp/x.html
  ```
- TradingEconomics 直接 curl 也不封（无需 r.jina.ai）。
- 页面正文提取：`python3` 剥 `<script>/<style>` 和标签 → `html.unescape` → 折叠空白 → 定位关键字切片。ECB 页面导航噪音极大，直接全文 dump 会淹没正文。

## 1. ECB 货币政策决议

- 决议列表页：`https://www.ecb.europa.eu/press/govcdec/mopo/html/index.en.html`
  - 列表条目**不在 HTML 里**，由 `data-snippets` 属性指向 include 文件（如 `../2026/html/index_include.en.html`）。
  - include 的解析路径：相对 `mopo/html/` 上一级，即
    `https://www.ecb.europa.eu/press/govcdec/mopo/2026/html/index_include.en.html`
    ⚠️ 不是 `mopo/html/2026/html/...`（那个 404）。
- include 文件里 `ecb.mp[0-9]+` 是决议 ID，链接为 hash 形式：
  `https://www.ecb.europa.eu/press/pr/date/2026/html/ecb.mp260723~29f24d99bc.en.html`
  ⚠️ 裸猜 `ecb.mp260723.en.html` 必 404。用正则 `re.findall(r'<a href="([^"]*ecb\.mp[^"]*)"', inc)` 提取。
- 决议正文关键锚点：`Key ECB interest rates`（决策段落，含各利率数字与生效日）、`deposit facility`。决策日≠生效日（例：2026-06-11 决议 +25bp，6-17 生效）。
- 利率历史速查（2026-06 加息后）：DFR 2.25% / MRO 2.40% / MLF 2.65%。

## 2. 拉加德/行长记者会

- 开场陈述（introductory statement，含经济/通胀分析全文）：
  `https://www.ecb.europa.eu/press/press_conference/monetary-policy-statement/YYYY/html/ecb.isYYMMDD~<hash>.en.html`
- 链接可从记者会列表页 `https://www.ecb.europa.eu/press/press_conference/html/index.en.html` 里 grep `ecb.is` 得到。
- 关键段落锚点：`Ladies and gentlemen` / `Good afternoon`（开场）、`Inflation`（通胀段）、`Risk assessment`（风险段）。

## 3. ECB 员工宏观经济预测（staff projections）

- 预测数字通常写进当月决议声明正文（基准情景 headline HICP / 核心 / GDP 各年 + 与上次对比的修订方向 + 风险倾向），先抓当月 `ecb.mp*` 声明即可，无需单独页面。
- 注意：**加息决议的预测段才完整**；按兵不动月份的声明可能不含预测。

## 4. TradingEconomics（HICP / 核心 / 分项）

- URL：`https://tradingeconomics.com/euro-area/inflation-cpi`、`/core-inflation-rate`、`/interest-rate` 等。
- 真实数据位置（按出现顺序）：
  1. 页面顶部 summary 段（标题正下方）：当前值 + 环比变化 + 事件背景（如 "confirmed at 2.8% in June 2026, down from 3.2% in May"）。
  2. `Calendar` 表：`GMT | Reference | Actual | Previous | Consensus | TEForecast`，含 flash/最终值、发布日期、各月数据。
  3. `Components` 表：分项（Energy / Services / Food / Core 等）的 Last/Previous。
  4. 月度序列在 summary 段之后的叙述文字里（如 "energy 10.8%→8.5%，services 3.5%→3.2%"）。
- 抓取后先 `find('Euro Area Inflation Rate')` 定位 summary 段，再 `find('Calendar')` 取历史表。

## 5. 数字核实纪律（用户硬性要求）

- brief 里**每个数字**必须对应一个本次真实抓取过的 URL；做不到就标 `UNVERIFIED`，并在结尾集中列出未验证项。
- 未验证项宁可明说"not fetched this pass"，也不要补推测值。
- 同一轮里无依赖的抓取并行（多 terminal 调用同一块发出），别串行耗轮次。

## 6. Worked example（2026-07-31 会话）

- 23 Jul 2026 决议：按兵不动，DFR 2.25%/MRO 2.40%/MLF 2.65%；声明称能源价格"close to June baseline, well above pre-conflict levels"，"full inflationary impact has yet to play out"。
- 11 Jun 2026 决议：+25bp（6-17 生效），因中东战争能源冲击；"robust across a range of scenarios"。
- Jun 2026 预测：HICP 3.0%(26)/2.3%(27)/2.0%(28)，核心 2.5%/2.5%/2.2%，GDP 0.8%/1.2%/1.5%（26/27 下修）。
- HICP：Jun 2.8%（May 3.2%）；核心 Jun 2.4%（May 2.6%）；能源 8.5%（10.8%）；服务 3.2%（3.5%）。
- 教训：会议日期以 include 文件里的实际 ID 为准（2026 年 6 月会议是 6-11，不是 6-4/6-17）；任务上下文给的日期可能不准。
