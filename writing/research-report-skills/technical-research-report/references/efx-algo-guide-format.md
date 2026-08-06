# eFX Global Algo Strategy Guide — Reference Format

Documents of this type provide algorithm definitions in a 5-column table:

| Algo | Description | When to use | Parameter | Parameter description |
|------|-------------|-------------|-----------|-----------------------|

## Algorithms Typically Documented

| Algorithm | Type | Key Parameters |
|-----------|------|----------------|
| **Whisper** | Pegging — skews client price stream | Urgency (0% near side → 50% mid), If Limit (Pause/Expedite), TP Price, Include External Liquidity |
| **Decipher** | Dynamic POV — adapts participation | Urgency (Low 15%, Normal 25%, High 45%) |
| **TWAP** | Time-weighted average | Liquidity, Start/End Time, Urgency, Include Bank Liquidity, Allow Random, Attempt Passive |
| **VWAP** | Volume-weighted average | Liquidity, Start/End Time |
| **Iceberg** | Expose portion, replenish on fill | Liquidity, Limit Price, Exposed %, Include Bank Liquidity |
| **GetDone** | Take from top of book at limit | Liquidity, Limit Price, Include Bank Liquidity |
| **Tracker** | Floating Iceberg with anti-gaming | Liquidity, Follow Exchange, Exposed %, Pips Adjust, Max Move, Stay/Reaction/Replenish Time |
| **Critical Mass** | Market-sweeping + optional Iceberg balance | Liquidity, Limit Price, Work the Balance, Exposed % |
| **Access** | Full exposure on chosen venues | Liquidity, Limit Price |

## Writing Rules

When the task references this guide:
- **Use exact definitions** — do not paraphrase algorithms as something they aren't
- **Include the parameters table** — the specific parameter names and values (0%, 50%, Low 15%) are the deliverable
- **Matching rules for each algo** come from the Description column
- **Use case** comes from the "When to use" column
