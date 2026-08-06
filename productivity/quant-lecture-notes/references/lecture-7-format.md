# Lecture 7 Notes.md — Full Template Anatomy

This file captures the exact structural blueprint from Lecture 7 Notes.md (772 lines, 40K chars). Use as a concrete reference when creating notes for new lectures.

## Header

```markdown
# Lecture 7 — Foundation Finance I（金融基础 I）

> 讲师：Henry Chan | Asia Quant Academy
> 拓展笔记（基于课堂内容 + 补充知识）

---
```

## Section skeleton (repeated per major topic)

```markdown
## 一、Chinese Section Title（English Section Title）

### Subtopic（中文翻译）

#### Term Table

| English（英文） | 中文 | 解说 |
|---------|------|------|
| **Term** | 翻译 | 1-2 sentence explanation |

#### Formula (display math)

$$ ... $$

#### Blockquote

> **Bold header for the insight**
> 
> Detail lines...
```

## All Section Headers from Lecture 7

```
一、Introduction to Financial Market（金融市场导论）
  - Brief History（简要历史）
  - Functions, Role Players & Market Types（功能、参与者与市场类型）
  - Key Properties（市场关键属性）
  - Four Risk Management Techniques（四种风险管理方式）
  - Market-Specific Risks（各市场特有风险）
  - Elements of Financial Markets（金融市场要素）

二、Time Value of Money（货币时间价值）
  - Core Concept（核心概念）
  - Present Value Operator（现值算子）
  - Time Value of Money（货币时间价值）
  - 例题详解
  - Compounding（复利）
  - Inflation（通货膨胀）
  - Annuities & Perpetuities（年金与永续年金）

三、Bond（债券）
  - Key Terms（关键术语）
  - Bond Quoting（债券报价）
  - Accrued Interest（应计利息）
  - Day Count Conventions（计息天数惯例）
  - Yield-to-Maturity / YTM（到期收益率）
  - Discount Factors（折现因子）
  - Bootstrapping（自举法）
  - Spot Rate（即期利率）
  - Macaulay Duration（麦考利久期）
  - Convexity（凸性）
```

## Formula style

All formulas were plain ASCII in Lecture 7 (written before user's LaTeX correction). Lecture 8 style is the current standard: **always LaTeX**.

## Summary table

```markdown
---

## Summary — Quick Reference（快速对照表）

| 英文 | 中文 | 一句话核心 |
|------|------|-----------|
| **Term** | 翻译 | One-liner |
```

Every term from the body appears here. ~20-25 rows typical.

## Key conventions

1. Tables use pipe syntax with alignment dashes
2. Bold only on the English term column
3. Chinese translations in parentheses after English: `Term（术语）`
4. Blockquotes (`>`) for: supplementary knowledge, financial intuition, deeper explanations, worked examples
5. Code fences (` ``` `) only for: non-formula demonstrations (numeric worked examples, bootstrap steps, how-to lists)
6. Horizontal rules (`---`) between major sections
7. Sections are numbered, subsections are not (just ### headings)

---

## Section Headers from Lecture 9 (Market Microstructure)

```
一、Exchange, Broker, Dealer（交易所、经纪商、交易商）
  - Electronic Trading
  - Core Execution Methods (Agency vs Principal)
  - Risk of Execution Methods
  - Type of Funds & Institutions (Pension/Quant/HFT/StatArb)
  - Type of Tradings

二、Market Microstructure（市场微观结构）
  - Types of Markets (Quote-driven vs Order-driven vs Hybrid)
  - Order Types (Market, Limit, Conditional, Stop, Iceberg)
  - Sample Order Book
  - Market Rules (Precedence, Tick Size, Halts, After-hours)
  - Trading Process (Price Formation → Discovery → Settlement)
  - Price Discovery Mechanisms (Bilateral, Continuous Auction, Call Auction)

三、World Market（全球市场）
  - Market Structure Evolution (single dealer → multi → inter-dealer)
  - Alternative Markets (ECN, MTF, ATS, Dark Pool)
  - Global Market Trends (Electronic, Transparency, Accessibility)
  - Centralization vs Fragmentation
```

## Section Headers from Lecture 10 (TCA & Market Impact)

```
一、Transaction Cost Analysis / TCA（交易成本分析）
  - Definition: cost measure vs cost forecast
  - Nature of TCA (components, standard error)

二、Implementation Shortfall / IS（实施缺口）
  - Paper Return vs Actual Return
  - Complete Execution (all shares traded)
  - Opportunity Cost (unexecuted portion)
  - Expanded IS (Delay + Trading + Opportunity Cost + fees)

三、Benchmark Performance（基准表现）
  - Benchmark Price Performance
  - VWAP Benchmark (Full Day / Interval / End of Day)
  - PWP Benchmark (Participation Weighted Price)
  - Algorithm Comparison & Statistical Tests (Paired/Independent non-parametric)

四、Market Impact（市场冲击）
  - Temporary vs Permanent Impact
  - Temporary Decay Model (Pk = P₀ + Σ f(xⱼ)·e^{-γ·(k−j)})
  - Random Walk with Market Impact (drift + temp + perm + noise)
```

## Section Headers from Lecture 11 (Algorithmic Trading)

```
一、Trading 101（交易基础）
  - Order Information (ticker, side, qty, type, TIF)
  - Order Book & Consolidated Order Book
  - Auction Sessions (HKEX Open/Close)

二、Introduction to Trading Algorithms（算法交易概述）
  - What is an Execution Algorithm (not a trading strategy)
  - Classification: Single-order vs List-based; Schedule-based vs Dynamic
  - Sub-components: Smart Router, Display, Pricing, Scheduling
  - Trading Cost (Explicit: commissions/tax; Implicit: spread/impact/leakage/opp cost)
  - Execution Risk (Asset Risk, Trading Risk, Risk Aversion tradeoff)
  - Agency Brokers ≠ Alpha Trading (9 reasons)

三、Mechanical and Advanced Trading Algorithms
  - Mechanical: Iceberg, GetDone
  - Advanced: TWAP, VWAP, PVOL, Close

四、Practical Considerations（实践考量）
  - Edge Cases (invalid params, bad behaviors)
  - Price Limit & Catch Up Logic
  - Volume Constraints (large order, illiquid stock, volume spike)
```

## Section Headers from Lecture 12 (Order Book & Volume Curve)

```
一、Order Book Modeling（订单簿建模）
  - Limit Order Book (mathematical definition: price grid, state vector X(t))
  - Order Book Dynamics (6 event types as state transitions: x → x^{p±1})
  - Stochastic Model (Poisson arrivals, power law λ(i) = k / i^α)
  - Parameter Estimation (Nl(i), Nm, least-squares fit)

二、Volume Curve Modeling（成交量曲线建模）
  - Definition (v_n: volume, V_n: cumulative, p_n: percentage, P_n: cumulative%)
  - Performance Metrics (TE, MAE, MAPE, MSE — with volume spike caveat)
  - Historical Curve (median per bin, then normalize)
  - Real Time Adjustment (coefficient θ_n = p^a_n / p^h_n, anti-runaway bounds)
```
