---
name: resume-zh-bullet-style
description: Write Chinese resume bullets for finance/AM roles.
version: 0.1.0
author: Hermes
---

# Chinese Resume Bullet Style (Finance / AM / FoF)

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
