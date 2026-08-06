# Synthetic vs Real Metric Collapse — Re-verification Recipe

Session: bipartite-gnn-gui demo (2026-07). The user asked to showcase the
report's two best results (confidence scoring AUROC 0.989, structure
completion +40~56% IoU). Both collapsed on real VLM data. This file records
the exact re-verification so a future session re-runs it instead of trusting
the report.

## Why the report numbers were misleading

| Claimed (report) | Test condition | Real-data result |
|---|---|---|
| Confidence AUROC 0.989 | Random imposters injected into GT (synthetic) | joint existence head **0.489** (≈random); dedicated confidence_scoring model **0.603** |
| Completion IoU 0.123 vs NN 0.088 (+40–56%) | Synthetic element-dropping (drop 60–80% of GT) | GNN proposals 0.198 vs NN baseline 0.212 — **GNN NOT better** |

Root reason: synthetic tasks are easy. Randomly-placed imposters are
structurally separable (real VLM FPs look like genuine elements); dropped
elements leave an interpolation shortcut that real VLM misses do not.

## Re-verification scripts (run against the real eval set)

### 1. Existence-head AUROC on real VLM data

Use the SAME loading path as production (shape-filtered, Pitfall 15), the
same builder/constraint extraction as `prepare_demo_cases.run_gnn`, and
Hungarian center-distance ≤ 0.1 as the TP/FP label. **Do NOT use
`builder.build(elems)` alone** — this project's builder requires
`constraints` (TypeError). Use `extract_all_constraints(elems)` first.

```python
from sklearn.metrics import roc_auc_score
# ... load model (shape-filtered), builder, VLM_DIR, RICO_DIR ...
for f in glob(f'{VLM_DIR}/*.json'):
    vlm_elems, _, _ = load_vlm_elements(Path(f))
    gt_elems = load_gt_elements(RICO_DIR / f'{img_id}.json')
    if len(vlm_elems) < 3: continue
    constraints = extract_all_constraints(vlm_elems)
    data = builder.build(vlm_elems, constraints)
    matched, _, _ = hungarian_match(vlm_elems, gt_elems, 0.1)
    matched_set = {i for i, _ in matched}
    exist = model(data.to(DEVICE))['existence'].squeeze(-1).tolist()
    for i, s in enumerate(exist):
        scores.append(s); labels.append(1 if i in matched_set else 0)
print(roc_auc_score(labels, scores))
# joint hd=128: 0.4889 over 185 images / 2918 elements (TP 1582, FP 1336)
# confidence_scoring hd=16 (44/44 keys): 0.6033
```

Test multiple checkpoints (joint + dedicated + per-head) on the same data —
"which model" matters as much as "does it work".

### 2. Proposal IoU vs NN baseline on real misses

NN baseline: for each violated constraint, propose the mean bbox of its
participant elements (source + target indices), then NMS. Compare only
proposals whose center lands within 0.1 of a GT element (matched), by IoU.

```python
# GNN path: violation > threshold → proposal head xyxy → clamp → NMS
# NN path:  per violated constraint, mean of participant bboxes → NMS
# Result (2026-07): GNN 527 props / 175 matched / IoU 0.1979
#                   NN  447 props / 162 matched / IoU 0.2119
```

## Decision pattern for the user conversation

1. Re-verify FIRST, silently, against real data.
2. If the data contradicts the report, present the table immediately:
   synthetic number → real number, with test conditions spelled out.
3. Propose the honest ranking (what survives real data) and let the user
   choose the demo scope. Do not build a fake showcase, do not refuse flatly.

## Project-specific notes

- `checkpoints/completion/best_model.pt` is a WRAPPED dict
  (`{'model_state': ..., 'config': ...}`), 40 keys, hd=128, NO proposal head
  — not usable for completion demo without unwrapping.
- `checkpoints/confidence_scoring/best_model.pt` is hd=16, 44 keys.
- VLM dir: `data/vlm_predictions/rico_qwen_flash/*.json` (200 files).
