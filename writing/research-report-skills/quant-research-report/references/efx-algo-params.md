# eFX Global Algo Strategy Guide — Parameter Reference

Extracted from the official eFX Global Algo Strategy Guide document. Use these exact parameters when documenting algorithms.

## Whisper (Pegging Algorithm)

| Parameter | Details |
|-----------|---------|
| **Urgency** | 0% = near side bid/offer, 50% = mid in internal matching engine |
| **If Limit** | Pause: never trade beyond limit. Expedite: increase urgency as market approaches limit, fills may be worse than limit |
| **TP Price** | Take profit or convert to buy/sell limit order at this price |
| **Include External Liquidity** | Route to external venues to supplement internal liquidity |

## Decipher (Dynamic POV Algorithm)

| Parameter | Details |
|-----------|---------|
| **Urgency** | Low = 15%, Normal = 25%, High = 45% participation rate |

## TWAP

| Parameter | Details |
|-----------|---------|
| **Liquidity** | Intelligent = route to venues with highest execution probability |
| **Start Time / End Time** | Order start and end times |
| **Urgency** | How much spread to pay in passive phases |
| **Include Bank Liquidity** | Interact with franchise internal matching engine |
| **Allow Random** | Randomizes time for moving passive -> mid -> crossing spread |
| **Attempt Passive** | First place passive bid/offer before crossing spread |

## VWAP

| Parameter | Details |
|-----------|---------|
| **Liquidity** | Intelligent = route to venues with highest execution probability at competitive price |
| **Start Time / End Time** | Order start and end times |

## Iceberg

| Parameter | Details |
|-----------|---------|
| **Liquidity** | Intelligent = route to venues with highest execution probability |
| **Limit Price** | Will trade up to, but not beyond, limit price |
| **Exposed %** | Percentage/currency amount of original order to expose |
| **Include Bank Liquidity** | Interact with franchise internal matching engine |

## Other Algorithms (reference)

| Algorithm | Description |
|-----------|-------------|
| **GetDone** | Takes from top of book at limit price, without exposing interest |
| **Tracker** | Floating Iceberg that pegs to market using anti-gaming logic |
| **Critical Mass** | Market-sweeping algorithm, option to work balance via Iceberg |
| **Access** | Shows interest on chosen trading venues |
