# Real VLM Completion Pipeline — Methodology & Findings

## When To Use This
Evaluating a GNN's real-world impact requires running on **actual VLM predictions**, not synthetic element dropping. The synthetic paradigm (randomly drop 60% of elements) does NOT replicate VLM error patterns.

## How To Build The Pipeline

### 1. Data Requirements
- VLM predictions on real screenshots (e.g., Qwen3-VL Flash)
- Ground-truth element annotations (e.g., RICO view hierarchy)
- One-to-one mapping between VLM output files and GT files (by filename)

### 2. Matching Strategy
Use center-distance Hungarian matching (threshold=0.1 = ~144px on 1440px screen):
- **True Positive (TP)**: VLM element matched to a GT element
- **False Positive (FP)**: VLM element with no GT match  
- **False Negative (FN)**: GT element with no VLM match

### 3. GNN Correction Pipeline

For each image's VLM elements:
1. Build constraint graph via BipartiteGraphBuilder + extract_all_constraints
2. Run model inference:
   - Confidence filtering: elements with sigmoid(existence) < 0.5 → remove
   - Violation detection: constraints with sigmoid(violation) > 0.5 → mark missing
   - Element proposal: for violated constraints, propose new elements at proposal coords
3. NMS deduplication on proposed elements
4. Corrected set = surviving VLM elements + proposed elements
5. Match corrected set → GT for After metrics

### Key Findings

| Metric | Before (VLM) | After (VLM+GNN) | Δ |
|--------|:-----------:|:---------------:|:-:|
| Precision | 0.382 | 0.369 | -1.4pp |
| Recall | 0.235 | 0.282 | +4.7pp |
| F1 | 0.291 | 0.320 | +2.9pp |

- 721 proposals → 226 additional TPs (31% proposal→TP rate)
- Main bottleneck: VLM recall 23.5%. GNN can't fix what it can't see.
- Only train_violation.py's default checkpoint works for real proposals
- Cross-domain (RICO→ScreenSpot): AUROC drops 0.703→0.554
- Type prediction caps at 62% even with clean single-element removal targets
