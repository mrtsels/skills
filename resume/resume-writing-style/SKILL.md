---
name: resume-writing-style
description: >-
  Enforce resume voice: active verbs, no articles, no
  filler.
version: 0.1.0
author: Hermes
metadata:
  hermes:
    tags: [Resume, Style-Guide, Voice]
---

# Resume Writing Style

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
