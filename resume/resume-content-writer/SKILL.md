---
name: resume-content-writer
description: "Write and structure resume content — style rules (EN/ZH), bullet formula, metrics quantification, section templates, formatting, and tailoring. Covers finance/AM bullets in Chinese."
---

# Resume Content Writer

Governs the voice, grammar, and word-choice rules for ALL resume bullet content. These rules override standard English grammar — they are non-negotiable once final output is produced. Use alongside `resume-bullet-writer` (structure and metrics) and `project-to-resume` (content extraction).

## When to Use

- Writing new resume bullet points from scratch.
- Reviewing/rewriting existing bullets for voice consistency.
- Generating content from a project directory via `project-to-resume` — apply these rules to the output.
- Tailoring a resume for a specific job via `resume-tailor` — re-check voice after keyword insertion.

## Quick Reference

| Rule | Wrong | Right |
|------|-------|-------|
| No articles a/an/the (unless unavoidable) | Developed a system that reduced the latency | Developed system reducing latency |
| Past-tense action verb, no subject | Was responsible for backend; He built the API | Designed RESTful API |
| No passive voice | Was involved in testing; Was hired to lead | Led QA team of 5 |
| Replace be/have with strong verbs | Was the lead engineer; Had responsibility for | Architected microservices pipeline |
| Nouns over gerunds | Helped in reducing latency | Reduced latency by 40% |
| No filler words: various, several, multiple, significant, very | Processed various data sources | Processed 15+ data sources |

## Procedure

When writing or reviewing bullet content, apply in this order:

### Step 1 — Delete filler words

Strip: `various`, `several`, `multiple`, `significant`, `very`, `extremely`, `quite`, `really`. If the metric is unknown, frame scope (`10+ clients`) instead of using filler.

### Step 2 — Delete articles

Strike every `a`, `an`, `the` unless removing it makes the sentence ungrammatical (e.g., "the S&P 500" — keep "the"). Test: read the sentence aloud without the article — if it still parses, cut it.

### Step 3 — Convert passive to active

Find every `was/were/has been/have been` + past participle and rewrite to a single past-tense verb. If the subject is missing ("was responsible for"), pick an appropriate verb and lead with it.

### Step 4 — Replace weak verbs

Scan for: `was`, `had`, `has`, `did`, `made`, `got`, `helped`, `participated in`, `involved in`, `responsible for`, `tasked with`, `worked on`.

Replace with one of:
`Designed`, `Implemented`, `Optimized`, `Reduced`, `Architected`, `Built`, `Developed`, `Led`, `Deployed`, `Automated`, `Engineered`, `Delivered`, `Secured`, `Generated`, `Established`, `Authored`, `Benchmarked`, `Proposed`, `Conducted`, `Analyzed`, `Structured`, `Produced`, `Constructed`, `Integrated`, `Configured`, `Orchestrated`, `Standardized`, `Streamlined`, `Consolidated`, `Accelerated`.

### Step 5 — Convert gerunds to nouns

Find `-ing` verbs acting as nouns (`Helped in reducing`, `Contributed to building`, `Assisted in developing`). Replace with the bare past-tense form: `Reduced`, `Built`, `Developed`.

### Step 6 — Verify length

Each bullet must be 1-2 lines in the final PDF (10pt, 1.5em leftmargin, 504pt line width). Run the `latex-bullet-fill-optimizer` check after typesetting.

## Pitfalls

- **Don't sacrifice scannability** — technical terms (GPT-o3-mini, LoRA, PDE) are correct even if they contain articles. The rules apply to prose, not proper nouns.
- **Don't strip articles from fixed phrases** — "the S&P 500", "the University of Hong Kong", "a priori" keep their articles.
- **Don't apply during first draft** — write for completeness first, then apply style rules. The voice pass is a separate editing step.
- **Don't skip verification** — a grammatically correct passive sentence can slip through. Run the output through the quick-reference table as a final check.
- **When in doubt, shorter wins** — "Led team of 5" beats "Was the lead person of a team of about 5 engineers."

## Verification

Pick any 3 bullets from the output and check each against the 6 rules. Log results as:

```
Rule 1 (articles): PASS/FAIL
Rule 2 (no passive): PASS/FAIL
Rule 3 (strong verb): PASS/FAIL
Rule 4 (past tense): PASS/FAIL
Rule 5 (nouns > gerunds): PASS/FAIL
Rule 6 (filler): PASS/FAIL
Rule 7 (length): PASS/FAIL
```

## Templates for Equity Research / AM / PE Bullets

For research-oriented roles, bullets should follow:

```
Action Verb + Research Scope + Methodology/Tools + Deliverable + Quantified Impact
```

See `references/bullet-templates.md` for 10 template formulas (industry research, company/equity, competitive benchmarking, financial modeling, data analysis, policy research, competitive landscape, expert interviews, report output, investment recommendation) with examples.

### Daily Market Briefing + Trade Execution (AM/Trust)

For asset management roles combining analysis and trading, structure as:

```
[Market analysis method] + [analysis scope] + [trading method] + [volume/scope]
```

- **Analysis first**: Lead with the market review/outlook, follow with execution.
- **Name the methods**: Index breadth ratios, sector capital flow rankings, moving averages, RSI, VaR, factor attribution for style rotation signals — avoid vague "market analysis".
- **Intern roles**: Use "Completed" / "Delivered" / "Executed", NOT "Orchestrated" / "Led" / "Managed" (overstates junior authority).

**Example**: *Delivered daily market briefings using index breadth ratios, sector capital flow rankings, and technical indicators (moving averages, RSI, VaR) with factor model attribution for style rotation signals; executed 30+ daily bond repo and reverse repo orders (GC001-GC014) on [platform] with ¥800M+ daily turnover across exchange and interbank markets*

### Post-Investment / Fund Monitoring

For portfolio monitoring and compliance reporting, follow the **analysis → screening → reporting** sequence:

```
[Completed holdings analysis with methods] + [monitoring method] + [produced report with contents]
```

- **Methods to name**: Concentration ratios, sector exposure, NAV trend comparison, financial news platform search.
- **Report contents must be explicit**: "authored post-investment reports covering market review, holdings analysis, and sub-advisor assessments", not just "authored reports".

**Example**: *Completed Q2 portfolio holdings analysis (concentration, sector exposure, NAV trends) for 10+ FoF products and monitored sub-advisor negative news via financial news platforms and web searches; authored post-investment reports covering market review, holdings analysis, and sub-advisor assessments across dozens of partner fund managers (¥10B+ total AUM)*

## Verb Groups (by category)

| Category | Verbs |
|----------|-------|
| Research | Conducted, Performed, Investigated, Examined, Evaluated, Assessed, Reviewed |
| Financial | Modeled, Forecasted, Projected, Estimated, Valued, Benchmarked |
| Data | Collected, Compiled, Analyzed, Processed, Synthesized, Visualized |
| Deliverables | Produced, Presented, Delivered, Recommended, Identified, Generated |

## Bullet Diagnosis Checklist

When reviewing existing bullets, check:

1. **Categorization** — does it cover one function? Or mix unrelated work?
2. **Quantification** — does it have a number? If not, add one (company count, volume, %, entities). If exact data unavailable, ask user or estimate (this user explicitly permits fabricated metrics where scope is known).
3. **Impact** — does it say who used the work or what decision it supported?
4. **Verb strength** — is the first word a strong past-tense action verb?
5. **Conciseness** — does it fit 2 lines after compilation?

## ATS Keywords

For equity research / AM / PE roles, naturally include: Equity Research, Fundamental Analysis, Financial Statement Analysis, Financial Modeling, DCF Valuation, Comparable Company Analysis, Sensitivity Analysis, Investment Thesis, Bloomberg, Wind, Capital IQ, FactSet.

---

## Bullet Writing Formula

## When to Use

Use when the user needs to improve resume bullet points, make them more achievement-focused, or add metrics.

## Core Capabilities

- Transform weak bullets into achievement statements
- Add metrics and quantifiable results
- Focus on impact rather than responsibilities
- Follow STAR method (Situation, Task, Action, Result)
- Maintain truthfulness while maximizing impact

## The Formula

Good bullet = Action Verb + What You Did + How You Did It + Measurable Result

Structure:
- Action Verb (past tense) + Task/Project + Method/Tool + Metric/Outcome

## Common Mistakes to Fix

- Starting with "Responsible for" (weak)
- Listing duties without results
- No numbers or metrics
- Passive voice (was responsible, was involved)
- Vague language (various, several, multiple)
- Too long (>2 lines) or too short (< half line)

## Bullet Strength Scale

| Level | Example | Score |
|-------|---------|-------|
| Weak | Responsible for managing team | 1/5 |
| Better | Led team of 5 engineers | 3/5 |
| Strong | Led team of 5 engineers to ship 3 products, increasing revenue by $2M | 5/5 |

## Implementation

When improving bullets, for each existing bullet:
1. Identify what was done (core action)
2. Identify the result or impact
3. Add metrics (real or estimated ranges)
4. Apply the formula
5. Keep each bullet to 1-2 lines

---

## Quantifying Impact

Use when the user needs to add metrics to resume bullets but does not have exact data.

## Metric Types to Add

- **Scale**: users served, revenue handled, team size
- **Efficiency**: time saved, cost reduced, process improved
- **Impact**: revenue generated, adoption rate, satisfaction score
- **Scope**: projects managed, regions covered, budget size

## Estimation Guidelines

- Use ranges when exact numbers unknown (10-15 people, $500K-$1M)
- Use approximate indicators (over, nearly, approximately)
- Be conservative — better to understate than overstate
- Never fabricate specific numbers
- Use industry benchmarks when available
- Flag estimates clearly

## Where to Add Metrics

- Leadership: team size, budget, project count
- Engineering: system scale, performance gains, uptime
- Sales/BD: revenue targets, deal size, quota attainment
- Product: users impacted, feature adoption, NPS
- Operations: cost savings, efficiency gains, error reduction

---

## Section Templates

Use when the user needs to create or restructure specific sections of their resume.

## Section Templates

### Professional Summary
- Experienced hire: [Title] with [X] years in [industry], specializing in [key skill]
- Entry level: [Degree] graduate with experience in [area], passionate about [field]
- Career changer: [Previous role] transitioning to [new field], bringing [key transferable skill]

### Skills Section
- Technical: languages, frameworks, tools, platforms
- Soft skills: leadership, communication, collaboration
- Domain: industry-specific knowledge
- Certifications: relevant credentials

### Experience Section Order
- Most recent first
- Group by company, then role
- 3-6 bullets per role
- Most impressive achievement first per role

### Education Section
- Degree, institution, year
- GPA (if 3.5+ or recent grad)
- Honors, relevant coursework
- Thesis (if applicable)

---

## Formatting Rules

Use when the user needs help formatting their resume for readability and ATS compatibility.

## Core Rules

- Single column layout
- Standard fonts only (Arial, Calibri, Georgia, Times New Roman)
- 10-12pt body, 14-16pt headers
- Consistent spacing throughout
- No tables, text boxes, or columns
- No graphics, images, or charts
- Bullet points for experience items
- Reverse chronological order

## Format Checklist

- Margins: 0.5-1 inch all around
- Line spacing: 1.0-1.15
- Section headers: bold, consistent style
- Contact info at top (not in header)
- File name: FirstName_LastName_Resume.pdf or .docx
- Page breaks: no orphan headings
- No colored text (black only)
- PDF must be text-searchable

---

## Tailoring to a Job Posting

Use when the user wants to customize their resume for a specific job application.

## Process

1. Analyze job description requirements
2. Compare against master resume
3. Prioritize relevant experience (reorder bullets, emphasize matching projects)
4. Add missing keywords naturally
5. Remove or de-emphasize irrelevant content
6. Adjust professional summary for the role
7. Maintain truthfulness — never fabricate experience

## Rules
- Never add experience that does not exist
- One resume version per application
- Track changes against master resume
- Keep format ATS-compatible

---

## Chinese Bullets (Finance / AM / FoF)

Rules for writing Chinese resume bullets for intern-level finance roles (asset management, FoF, trust). Complements the EN-focused `resume-writing-style` and `resume-bullet-writer` skills with Chinese-specific conventions.

## When to Use

- Writing/rewriting Chinese bullets for a resume
- User corrects verb choice as "too grand for intern"
- Adding market analysis or post-investment descriptions
- User asks to include specific technical methods or numbers

## Core Rules

### 1. Verb Strength — Don't Overreach

Intern roles use execution-level verbs, not management-level:

| Avoid (too grand) | Use instead |
|-------------------|-------------|
| 统筹 | 完成、参与、执行 |
| 管理全流程 | 完成X、Y、Z |
| 产出 | 编制、撰写、完成 |
| 负责 | 参与、协助、执行 |

Right: `完成十余只FoF产品二季度持仓分析…覆盖数十家合作基金公司、总规模超百亿`
Wrong: `统筹公司FoF产品投后全流程`

### 2. Always Include Scope Numbers

Every bullet needs quantifiable scope:
- Product count: `十余只FoF产品`, `30+笔`
- Entity count: `数十家合作基金公司`, `30+家公司`
- Scale: `总规模超百亿`, `日均成交超8亿元`, `50亿元资产配置`

### 3. Market Analysis Must Include Methods

Generic "分析市场行情" is too vague. Include specific techniques:

```
指数涨跌比          → index breadth ratios
板块资金流向排名     → sector capital flow rankings
技术指标（均线、RSI） → moving averages, RSI, VaR
因子归因             → factor model attribution
```

Order: analysis/outlook first, then execution/trading.

### 4. Post-Investment Bullet Structure (FoF/Trust)

Three-part structure:
1. **Holdings analysis** — `个股集中度、行业暴露、净值变化`
2. **Negative news monitoring** — `通过网络及财经资讯平台检索投顾负面舆情`
3. **Report** — `编制含市场复盘与持仓分析的投后管理报告`

Wrap with scope: `覆盖N家合作基金公司、总规模超¥X`

### 5. LaTeX-Specific Pitfalls

- `%` must be escaped in all bullet text: `60\%`, `94\%`
- `\textendash` for date ranges: `2026/07\textendash 2026/08`
- `\ResumeUrl{URL}{text}` works inside `[]` subtitle parameters for professor links
- Linespread set ONLY in cls file, never duplicated in main `.tex`

## Quick Reference

```
完成[数量]FoF产品二季度持仓分析（个股集中度、行业暴露、净值变化），
通过网络及财经资讯平台检索投顾负面舆情；
编制含市场复盘与持仓分析的投后管理报告，
覆盖[数量]家合作基金公司、总规模超¥[数字]亿
```

```
每日复盘市场行情，运用指数涨跌比、板块资金流向排名及技术指标（均线、RSI），
结合因子归因识别轮动信号；
在xQuant OMS执行[数量]笔日频债券回购与逆回购，日均成交超¥[数字]亿元
```

## Verification

Check every new ZH bullet against:
1. No `统筹`, `管理全流程`, `产出` — replace with level-appropriate verbs
2. At least one scope number present
3. Market bullets include specific method names
4. Order: analysis before execution
5. All `%` properly escaped as `\%`
