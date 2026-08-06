---
name: research-visit-memo
description: "Write Chinese research visit memos (调研纪要) for FOF due diligence — following the 同温层 template format with overview-first conclusions and explicit placeholders."
version: 1.0.0
author: Hermes Agent
tags: [writing, due-diligence, fof, research-visit, memo, chinese]
---

# Research Visit Memo (调研纪要) — FOF Due Diligence

Write structured research visit memos for private fund manager on-site visits during FOF due diligence. Output is used internally by the trust's equity investment department.

## Format (match 同温层 template exactly)

```
公司全称
调研纪要

日期：【待补充或具体日期】
地点：【待补充或具体地址】
参加人员:
粤财信托：姓名、姓名
对方机构：姓名（职位）、姓名（职位）

主要结论
首段：公司股权结构/实控人/治理情况概述（首句无数字，数字在首句后展开）
第二段：投研团队/人员规模概述（首句定性，后续展开）
第三段：管理规模/策略特征概述（首句定性，后续展开）
第四段：财务状况概述（首句定性，后续展开）
第五段：与粤财合作情况概述（首句定性，后续展开）

Q&A
问题1？
A：答案。【待补充】留无法确认的细节

问题2？
A：答案。【待补充】

调研照片

权益投资部
日期
```

## Writing rules (strict)

### 主要结论段落
- Every paragraph's **first sentence** is the **bold-formatted headline conclusion** (定性判断) — this is the reader-facing takeaway
- Hard numbers (AUM, percentages, revenue, NAV, dates, team counts) appear **after** the first sentence, as supporting evidence
- Each paragraph covers ONE distinct topic dimension: equity → team → strategy/performance → capital/channel → financial
- Use the format `XXX（以下简称"公司"）` at the very start of the first paragraph

### Q&A section
- `Q&A` label on its own line (no markdown heading)
- Question is a `###` subheading (bold plain text on its own line)
- Answer is written as **full flowing paragraphs (自然段)** — no bullet points, no numbered lists, no structured tables. Merge related data points into coherent narrative text
- Answer starts with a judgment/takeaway sentence, then supports with data. Pattern: claim → evidence → nuance
- If the source document doesn't contain the answer → do NOT include the question at all. Only list questions with available answers

### Placeholder rule
- Every `【待补充】` marks info that must come from the actual visit
- NEVER invent data, quotes, or facts not present in the source document
- Cross-check: if a detail comes from a reference template (e.g. 同温层's Wuhan/武大华科), do NOT carry it to a different manager
- For unknowns, provide a descriptive placeholder — not just `【待补充】` but `【待补充：具体提示内容】` so the colleague knows what to fill

### Source extraction pattern
1. Read the DD report (docx extraction via read_file) for company info
2. Read the template memo for format reference ONLY
3. Cross-check: every fact in the memo must trace to a specific line in the DD report
4. Leave unknowns as `【待补充】` — do NOT infer, guess, or borrow
5. **During ongoing meetings**: if the manager gives permission ("尽调报告里的内容也能用"), immediately cross-reference the DD questionnaire (0–尽调问卷.docx) to fill answerable gaps. The DD questionnaire contains factual data (AUM, financials, team, strategy details) even if not yet confirmed verbally

### Q&A Answer Voice — Concrete Examples

**Data-dump (WRONG):**
> A：2023-2025年公司营业收入从607万元增长至1.17亿元（2025年同比增长2,425%），净利润从亏损498万元转为盈利3,311万元。2025年末资产总额3,906万元，所有者权益3,231万元，资产负债率17.27%。

**Conversational (RIGHT):**
> A：整体挺健康的，没什么问题。公司过去几年在搭建团队和系统上投入比较大，早期基本盈亏平衡，2025年管理规模起来之后业绩报酬兑现了，利润才真正出来。负债率不到20%，没有外部融资压力。

The difference: the right version starts with a JUDGMENT ("整体挺健康的"), then uses numbers to support it. The wrong version just dumps a table.

### Standard Question Scope

| Question | When to include | Answer source |
|----------|----------------|---------------|
| 公司目前的整体情况？团队、规模 | Always | DD: headcount & AUM sections |
| 投研团队架构和分工 | Always | DD: management table |
| 策略核心逻辑和竞争优势 | Always | DD: investment philosophy |
| 收益来源和风险控制 | Always | DD: risk management |
| 策略迭代/其他策略储备 | Always | DD: strategy development notes |
| 策略容量/未来规模规划 | If DD mentions it | DD: scale/capacity notes; otherwise `【待补充】` |
| 与粤财合作情况及未来计划 | If cooperation exists | DD: cooperation history; future plans `【待补充】` |
| 产品线和策略线布局 | If product details exist | DD: product table; else combine with strategy Q |
| 财务状况 | ❌ NOT a standalone Q&A — cover in 主要结论 only | Covered in 主要结论 paragraph 3 |

**Avoid overlapping questions** — `产品线和策略线布局` and `量化策略核心逻辑` ask similar things. Scope them distinctly:
- 核心逻辑 → how the strategy works, edge, methodology
- 产品线布局 → which products exist, their dates/codes/parameters

If both are needed, put product details first (it's factual), then strategy logic (it's explanatory).

### Financial Data Positioning

Financial metrics belong in 主要结论 paragraph 3, formatted with the overview-first rule:
```
公司财务状况较为稳健，2025年营收和利润大幅提升。全年实现营业收入1.17亿元，净利润3,311万元，资产负债率17.27%。
```

Do NOT add a standalone "财务状况" Q&A question — it's not a topic you'd naturally ask in a visit. The Excel-style line-item answer ("2023-2025年营业收入从607万增长至1.17亿...") sounds like a spreadsheet, not a conversation. If the user explicitly asks for it, write it conversationally with the opinion-first pattern.

## Common pitfalls
- ❌ Putting hard numbers (AUM, %, dates) in the first sentence of 主要结论 paragraphs — first sentence must be a bold-formatted headline conclusion only
- ❌ Writing Q&A answers as bullet points or numbered lists — must be flowing 自然段 (natural paragraphs)
- ❌ Including questions with `【待补充】` or `——待补充` in the Q&A section during ongoing meetings — only list questions with available answers
- ❌ Waiting for user to say "commit" — after every file change, auto commit+push
- ❌ Copying details from the reference template's DIFFERENT manager into the target memo (e.g. 同温层 is Wuhan-based → don't transfer 武大华科 to Shenzhen-based manager)
- ❌ Writing Q&A in bullet-point formal style — must be conversational paragraph per the template
- ❌ Fabricating future plans / marketing strategy when the source document has no such info
- ❌ Adding a standalone "财务状况" Q&A question — financial data belongs in 主要结论 paragraph 3, not in Q&A. It's not a natural visit topic.
- ❌ Two questions with overlapping scope — e.g. "产品线和策略线布局" and "量化策略核心逻辑" overlap. Scope them distinctly or merge.
- ❌ Blindly copying template content into a different manager's memo — docx草稿可能包含从其他管理人模板复制的段落（如"市场中性策略与信托公司非标产品存在替代性"对主观多头管理人无效）。**检查每句话是否匹配目标管理人的实际策略。**
- ❌ Treating docx meeting notes as authoritative over NAV system data — 用户从行情系统粘贴的净值/回撤/夏普数据优先级高于 docx 中的估算值

## Verification
Before finalizing, diff-check against the template format:
1. Title format matches? (公司名+调研纪要, no markdown headers)
2. 主要结论 first sentences all bold-formatted headline conclusions?
3. Q&A answers are flowing 自然段 (no bullet lists, no numbered lists)?
4. During ongoing meetings: Q&A only includes questions with available answers (no 待补充 questions listed)?
5. No hallucinated content from a different manager's file?
6. No "财务状况" standalone Q&A question unless user explicitly asked?
7. No two Q&A questions asking the same thing with different wording?
8. Every Q&A answer passes the "does this sound like a person talking?" test — read aloud

## Ongoing meeting pattern

当调研会议还在进行中、只有部分信息时：

- 文件名用 `调研纪要（续）` 后缀，标记为进行中状态
- 先写 主要结论（4段），覆盖已确认的核心信息
- **Q&A 只放有答案的问题**——不要列出带「——待补充」的问题。没有答案的问题等会议结束后再补，不提前占位
- 用户每轮提供新信息 → 增量填充后自动 commit+push（不等用户说）
- 关键信息行内标注来源（如 `Q1曾破5亿` 来自 draft 笔记）
- 尽调问卷（0–尽调问卷.docx）在会议中也可参考——当对方说"尽调报告里的内容也能用"时，立即填入
- 会议全部完成后移除"（续）"后缀，清理全部 待补充

### Data source priority (ongoing meetings)

当多个来源数据冲突时，按以下优先级裁决：
1. **NAV系统数据**（净值页面截图/系统查询结果）> **docx会议纪要** > **尽调问卷** > **draft笔记** > 估算值

典型场景：
- draft 笔记写安心一号最大回撤"~2%"，用户提供净值页面显示 6.16% → **用 6.16%**（系统数据推翻会议口头估算）
- docx 写"团队共18人"，尽调问卷明细列出 14人（投研9/风控2/营销2/行政1）→ **用尽调问卷**（明细>概括，且问卷含编制表佐证）
- docx 主要结论与 Q&A 自相矛盾 → 标记矛盾，优先采信可验证的源头（问卷/系统），同时保留说明

### Docx meeting notes processing

当用户提供的是 docx 文件而非传统尽调问卷时，此 docx 可能是**本次调研会议的纪要草稿**（按同温层模板写的结论+Q&A）。处理步骤：
1. **先识别 docx 类型**：打开看首行。如果首行是公司名+调研纪要，则是**会议纪要草稿**而非尽调问卷。如果首行是尽调问卷标题，则是问卷。
2. **同步**：将 docx 中的结论和 Q&A 内容同步到 md 文件。但系统 NAV 数据（用户粘贴的净值行情）对绩效数据拥有最高优先级。
3. **矛盾处理**：docx 中"主要结论"和"Q&A"对同一事实数据不一致时（如主要结论写"14人"、Q&A写"18人"），优先采信尽调问卷/系统等可验证来源，并在 md 中标注。
4. **模板复用注意**：docx 中的某些段落可能直接复制自同温层模板（如"市场中性策略与信托公司原有的非标产品存在一定的替代性"）。不要盲从——检查该说法是否匹配目标管理人的策略特征（臻远是主观多头，不存在市场中性策略）。**不把模板内容当真理。**
5. **命名**：docx 统一重命名为 `zhenyuan.docx`（拼音+英文），与 md 文件名一致。
