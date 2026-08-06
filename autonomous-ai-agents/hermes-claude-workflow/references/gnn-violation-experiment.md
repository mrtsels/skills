# GNN Violation Detection Experiment Methodology

## Core Pattern: Build Constraints from Full Element Set, Then Filter

### ✅ Correct
```python
# 1. Extract constraints from ALL elements (before removal)
full_cons = extract_all_constraints(all_elements)

# 2. Randomly select survivors
survivor_mask = torch.rand(N) >= drop_ratio
survivors = [all_elements[i] for i in torch.where(survivor_mask)[0]]

# 3. Filter constraints: keep those with at least 1 surviving participant
kept = [c for c in full_cons
        if set(c.source_indices + c.target_indices) & set(survivor_indices)]

# 4. Remap participant indices to survivors list
old_to_new = {old: new for new, old in enumerate(survivor_indices)}
for c in kept:
    src = [old_to_new[s] for s in c.source_indices if s in old_to_new]
    tgt = [old_to_new[t] for t in c.target_indices if t in old_to_new]

# 5. Violation label: constraint has ≥1 removed participant
v = 1.0 if set(c.source_indices + c.target_indices) & set(removed_indices) else 0.0
```

### ❌ Wrong (what got 100% acc by mistake)
```python
# Building constraints from survivors only = impossible for any constraint
# to reference a removed element → no violations → model just predicts 0
survivor_cons = extract_all_constraints(survivors)  # WRONG
```

## Reporting Requirements

Always report alongside model accuracy:
- **Majority baseline**: what % would always-predict-the-majority-class achieve?
  - This catches cases where the task is imbalanced (e.g. 86% violated at drop=0.6)
- **Training set size** and **validation set size**
  - Affects whether 100% acc is meaningful (with 15 val graphs it's not)

## CONTAINMENT-Only Findings

| Config | Majority Baseline | GNN Acc | Delta | Train Graphs |
|--------|:---:|:-------:|:-----:|:----:|
| Full (10 types) | 86.1% | 85.3% | -0.8pp | 388 |
| CONTAINMENT-only | 72.0% | 79.5% | +7.5pp | 196 |

- Full GNN's accuracy is an illusion from high baseline
- CONTAINMENT-only provides real signal (+7.5pp over baseline) with half the data
- Alignment types (58% of all constraints) are noise

## Controlled Experiments (Phase 9)

### 9.1: Single-Head vs Joint (5 seeds)

| Config | mean ± std |
|--------|:----------:|
| Full × joint | **0.876 ± 0.020** |
| Full × violation-only | **0.898 ± 0.018** (+2.2pp) |
| Full × proposal-only | **0.489 ± 0.071** |

**Multi-task training genuinely hurts violation detection**: isolating the violation head with full constraint types still beats the joint model. The effect is NOT just about CONTAINMENT constraints being easier — the reviewer's suspicion was wrong on this point.

### 9.3: Type Prediction with Single-Element Removal

**Critical finding**: the original training target is incoherent — when multiple elements are removed from one constraint, the proposal target averages all missing bboxes but takes only the *first* missing type. No single element satisfies both targets.

Fix: `--single-element-removal` flag ensures at most 1 element is dropped per graph. Results:

| Metric | type_weight=0.5 | type_weight=2.0 |
|--------|:---------------:|:---------------:|
| Type Acc | **61.8%** | **61.8%** |
| Prop MSE | 0.087 | 0.087 |

Type accuracy caps at **62%** regardless of loss weight. Constraint context alone doesn't encode semantic type information — this is an architectural limitation, not a training problem.

## Real VLM Evaluation

### RICO (mobile apps — 200 images)

Raw VLM (Qwen3-VL Flash) quality:
| Metric | Value |
|--------|-------|
| VLM Precision | 0.382 |
| VLM Recall | **0.235** — 76.5% of GT elements undetected |
| VLM F1 | 0.291 |
| GNN Existence AUROC | 0.703 |

The GNN can filter some FPs but the recall gap is so large that precision gains come at heavy recall cost.

### ScreenSpot (PC/web — 610 images)

| Metric | Value |
|--------|-------|
| VLM Precision | **0.028** — massive over-detection |
| VLM Recall | 0.383 |
| VLM F1 | 0.052 |
| GNN Existence AUROC | **0.489** — no separation |

Cross-domain evaluation is severely confounded by distribution differences:
- ScreenSpot avg **2.1 elements/image** vs RICO avg **25**
- VLM produces **17,000 detections for 1,200 GT** (17:1 FP ratio)
- GNN gives both TP and FP ≈0.90 confidence — useless

### Key Takeaway

The GNN's strongest results (98-99% violation acc, 0.058 proposal MSE) are from **synthetic element dropping**, which does NOT replicate real VLM error patterns. On real VLM data:
- RICO: moderate utility (AUROC 0.703)
- ScreenSpot: useless (AUROC 0.489)

## Visual Feature Fusion (ViT Tiny) — Biggest Breakthrough

### Rationale
GNN only sees spatial relationships (containment, alignment) — it has ZERO access to what elements look like. This is why type prediction capped at 62% and cross-domain failed.

### Approach
- Use timm `vit_tiny_patch16_224` (5.7M params) to encode each element's crop region
- Crop extended 5px for context, resize to 224×224
- Extract features via `model.forward_features()` → mean-pool patches → 192-dim vector
- Concatenate to existing node features (bbox + type embed + confidence)
- Total element feature dim: 197 (was 5)

### Results (500 RICO, hidden=128, drop=0.4)

| Metric | Without Visual | With Visual | Δ |
|--------|:-------------:|:-----------:|:-:|
| Violation Acc | 0.593 | **0.847** | **+25.4pp** |
| Proposal MSE | 0.088 | **0.079** | −0.009 |
| Type Acc | 0.312 | **0.450** | **+13.9pp** |

### What This Means
- **Violation detection +25pp**: the GNN can now see whether a predicted element "looks wrong" (blurry crop = FP), not just "is in the wrong place"
- **Type prediction +14pp (31%→45%)**: visual features directly close the semantic gap — the model can distinguish buttons from text by appearance
- viT tiny (5.7M params, 192-dim) is sufficient; no need for heavy models
- Pre-computed features cached to disk, no inference-time overhead after pre-computation

### Implementation
- Precompute: `scripts/precompute_visual_features.py` → `data/rico_local/visual_features/<uid>.pt`
- Builder modified to accept `visual_feat` optional per-element array in `_build_node_features()`
- When visual feats present: feature dim=197, else 5 (backward compatible)
- Training: `experiments/train_with_visual.py`
