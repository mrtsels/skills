# Honest Demo Asset Generation — Confidence & Completion Panels

Session: bipartite-gnn-gui (2026-07). After the synthetic-vs-real re-verification
(see `synthetic-vs-real-metric-collapse.md`), the user chose the honest demo
("A" plan): Tab 2 = confidence scoring capability validation (synthetic
condition, labeled), Tab 3 = completion evaluation curve (all runs, honest).
This file records the two traps hit while generating those assets.

## Trap 1: Binary-head scores biased high → 0.5 threshold labels everything real

The dedicated `confidence_scoring` model (hd=16) on real GT + injected
imposters produced scores with a HIGH bias: real mean 0.693, imposter mean
0.543, and **every element > 0.5**. A naive `score > 0.5` classification
gave tn=0 fn=0 (acc 0.667, "model is broken" reading) — but the ordering was
fine: AUROC 0.984–0.999 per image.

Fix: compute the per-image optimal threshold from the same labels via
Youden's J (maximize TPR − FPR over a coarse grid), then classify with that:

```python
best_t, best_j = 0.5, -1.0
for t in [v / 100 for v in range(10, 96, 5)]:
    tp = sum(lab > 0.5 and sc > t for lab, sc in zip(labels, scores))
    fp = sum(lab < 0.5 and sc > t for lab, sc in zip(labels, scores))
    fn = sum(lab > 0.5 and sc <= t for lab, sc in zip(labels, scores))
    tn = sum(lab < 0.5 and sc <= t for lab, sc in zip(labels, scores))
    j = tp / max(tp + fn, 1) - fp / max(fp + tn, 1)
    if j > best_j: best_j, best_t = j, t
```

Result: thr=0.55 → acc 0.944–0.990 across the 3 demo images, AUROC unchanged.
**Rule: when a calibrated-looking sigmoid head is uniformly biased, report
AUROC + Youden threshold, never a fixed 0.5 cutoff.** Also report AUROC per
image, not just pooled — per-image AUROC is the honest "model discriminates"
claim.

## Trap 2: Benchmark JSON exists but model weights were NOT persisted → no single-image demo

`experiments/completion_results.json` has 8 runs (drop_ratio × 2 seeds, GNN
IoU vs NN baseline) — but the completion model was trained per-run inside
`evaluate_completion.py` and never saved. `checkpoints/completion/best_model.pt`
is a different artifact: wrapped dict, 40 keys, mask-task head set, **no
proposal head**.

Substituting the joint checkpoint for the single-image drop demo is WRONG:
joint's proposal head is trained for violation-driven proposals, not masked
completion. Measured on the drop-60% demo: GNN IoU **0.000** vs NN 0.411 —
it would actively mislead (and in the OTHER direction from the real eval).

**Rule: if the benchmark's weights weren't persisted, show the evaluation
curve only (from the results JSON); never fake a single-image demo with a
different checkpoint.** Aggregate curves are fine — they're the honest record.

## Curve presentation: show ALL runs, including the negatives

`completion_results.json` aggregated honestly (don't cherry-pick the good
drop ratios):

| drop | GNN IoU mean (runs) | NN IoU mean (runs) | Δ |
|---|---|---|---|
| 0.2 | 0.0473 (0.041, 0.054) | 0.0573 (0.035, 0.079) | GNN −17% |
| 0.4 | 0.0786 (0.069, 0.088) | 0.1097 (0.101, 0.119) | GNN −28% |
| 0.6 | 0.1225 (0.064, 0.180) | 0.0881 (0.096, 0.080) | GNN +39% |
| 0.8 | 0.0974 (0.064, 0.130) | 0.0622 (0.071, 0.053) | GNN +57% |

The narrative is honest AND interesting: GNN only beats NN when the layout is
severely depleted — a genuine structural-prior claim, told by showing the
full curve. Per-run values belong in the JSON so the UI can show variance.

## Asset layout produced

```
demo_data/confidence/{img}.json   — per-element {bbox, label, is_imposter, score} + auroc + threshold
demo_data/confidence/{img}.png    — blue=real, red=imposter, score labels
demo_data/confidence/summary.json
demo_data/completion/curve.json   — all 8 runs, aggregated by drop_ratio
```

Prep scripts: `scripts/prepare_confidence_demo.py`,
`scripts/prepare_completion_demo.py` (run with the conda python that has
torch + sklearn; `builder.build` needs `constraints` — call
`extract_all_constraints(elems)` first).
