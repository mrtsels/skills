# Visual Slide Reconstruction Patterns

fitz.get_text() misses images and flattens multi-column tables. When the raw text has "Figure N" or "Table" with no data below, rebuild from slide context.

## Pattern 1: Side-by-side comparison (most common)

**Signal**: Slide title is "Comparison between X and Y" or "X vs Y". Raw text has column headers (e.g. "Quote-driven", "Order-driven") but the body is empty or garbled.

**Reconstruction**: The slide has two columns under a shared initial state:

```
                  Initial State: Bid 52.0 × 500, Offer 53.5 × 1,000
  Action          Quote-driven                     Order-driven
  ───────         ─────────────                     ────────────
  Take the offer  Buy at 53.5 from dealer ✓        Market buy order, eats best offer 53.5
  Hit the bid     Sell at 52.0 to dealer ✓         Market sell order, eats best bid 52.0
  Limit order     Negotiate with dealer             Post passive limit order (e.g. sell at 54.0)
  Improve price   Dealer doesn't show inside        Post new sell 53.0 → becomes new best; old 53.5 moves to second tier
```

**Template**:
```markdown
**初始状态（Initial State）：** [bid/ask/sizes]

| 动作 | X-driven | Y-driven |
|------|---------|---------|
| **Action A** | How X handles it | How Y handles it |
| **Action B** | ... | ... |

> **关键区别：** One-paragraph summary of the fundamental difference
```

## Pattern 2: State transition diagrams

**Signal**: "Figure: Overview of..." with a flow chart. Raw text has only labels like "Step 1 → Step 2 → Step 3".

**Reconstruction**: Convert to a numbered list or code-block ASCII flow:

```
1️⃣ First stage
    → what happens
2️⃣ Second stage  
    → what happens
3️⃣ Third stage
```

For circular/feedback diagrams, use a table with relationship arrows.

## Pattern 3: Stock-flow / timeline visuals

**Signal**: "Figure: Temporary market impact properties" or "Figure: Market impact visualized". Raw text has axis labels but no curve data.

**Reconstruction**: Describe the shape verbally + equation:

```markdown
The price spikes up on execution, then decays exponentially back toward the fundamental price:
```
P_k = P_0 + Σ f(x_j)·e^{-γ·(k-j)} + ...
```
Temporary impact peaks at execution, decays with rate γ. Permanent impact persists.
```

## Pattern 4: Institutional architecture diagrams

**Signal**: "Figure: Market structure for different asset classes" or "Figure: Inter-dealer broker network". Raw text has venue names (ECN, MTF, ATS, Dark Pool).

**Reconstruction**: Tree/flow in code block:

```markdown
```
Exchange-traded (CME, NYSE)
  → Central order book, standardized, transparent
OTC (Dealer-client)
  → Bilateral, customized, opaque
Alternative (ECN, Dark Pool)
  → Electronic, anonymous, reduced market impact
```
```

## Pattern 5: Screenshot-based slides

**Signal**: Lecture 11's algorithm descriptions (Iceberg, GetDone, TWAP, VWAP, PVOL, Close) — each slide has a title + "Details will be covered during the lecture" + a screenshot of a brokerage product description.

**Reconstruction**: Write a concise definition table:

```markdown
| Algorithm | 中文 | 核心逻辑 | 适用场景 |
|-----------|------|---------|---------|
| **TWAP** | 时间加权均价 | 按时间均匀拆分 | 实现简单，无需预测 |
| **VWAP** | 成交量加权均价 | 按历史量曲线拆分 | 市场冲击更小 |
| **PVOL** | 成交量百分比 | 按市场实时量固定比例参与 | 动态适应 |
```

## General rules

1. **Always detect "Figure"/"Table" in raw text** — if extract() shows a caption but no data, that's a visual-only slide. Plan reconstruction immediately.
2. **Use the slide title as your primary clue** — it tells you what comparison or concept is being shown.
3. **Draw on adjacent slides** — the preceding and following slides often have the labels/terminology you need.
4. **Add a [Figure X] marker** in the notes so the user can cross-reference with the original PDF if needed.
5. **Err on the side of over-reconstructing** — a complete table with reasonable content is better than a blank section that the user has to flag.
