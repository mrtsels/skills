# Task 2 sources and structure notes

Session produced: research report on US stock exchanges (Nasdaq & NYSE) and algorithmic trading, as a Virtual Internship deliverable.

## Source documents
- `task 2 Exchange and Algorithmic Trading – Part 1 Understand the Market.pdf` — task instructions (image-based, 2 pages)
- `efx_algo_guide_final (2).pdf` — eFX Global Algo Strategy Guide reference (2 pages)

## Report structure
```
01 — Market Details
    A. Trading Hours
    B. Open & Close Auctions
    C. Pre-Market & After-Hours Rules
    D. Order Types & Matching Rules

02 — Alternative Venues & Trading Systems
    A. Dark Pools
    B. Smart Order Routing

03 — Agency Trading algorithms
    i. Whisper — Pegging Algorithm
    ii. TWAP
    iii. VWAP
    iv. Decipher — Dynamic POV Algorithm
    v. Iceberg

04
    Broker implementation differences (table)
    Evaluation metrics (table)
```

## Key format choices
- Time ranges: `9:30 AM – 4:00 PM ET` (spaces around en-dash)
- Parameter lists: dot list with `—` separator
- Broker differences: `维度 | Side A | 后果 | Side B | 后果` table
- Each algorithm: Definition → Use case → Parameters → Mermaid → Python → Edge cases
- Edge cases always: Order incompletion, Inadequate liquidity, Open & close auctions
- Python uses dataclasses + explicit run() method
