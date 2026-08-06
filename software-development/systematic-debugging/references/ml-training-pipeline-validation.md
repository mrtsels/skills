# ML Training Pipeline Validation Checklist

Common bugs that manifest as "model trains but doesn't improve" — loss decreases but metrics flatline, or GNN/transformer underperforms a simple baseline.

## 1. Target Format Mismatch

**Most destructive bug pattern.** Model and loss function silently agree on a wrong interpretation.

### Check

```python
# Hypothesis: model outputs deltas, but targets are absolute values
msg = "model predicts Δcx Δcy Δw Δh"
loss_val = model.compute_loss(predictions, targets)  # MSE(Δ, target)
# If target is raw GT xyxy while model predicts Δcxcywh →
# MSE compares semantically unrelated values → loss drops to a local
# minimum that doesn't correspond to useful learning.
```

### Fix

```python
# target should be: delta = gt_xywh - source_xywh
targets["coord"] = gt_xywh - source_xywh  # model learns the correction
targets["gt_boxes"] = gt_xyxy             # keep raw GT for evaluation
```

### Detection

- Loss starts unexpectedly low (e.g. ~0.15) on epoch 1 — likely comparing small deltas to large absolute values.
- After fix, loss starts much higher (e.g. ~2.0) on epoch 1 — now comparing meaningful values. The apparent "regression" in loss is actually the first correct training signal.
- NoOp baseline beats GNN by 10x+ on position error → suspect target mismatch.

#### Real example (bipartite-gnn-gui, 2026-06-22)

**Before fix** (`targets["coord"] = gt_xyxy` — wrong):
```
Epoch 1: train_loss=0.15  val_loss=0.020  ← suspiciously low start
Epoch 50: train_loss=0.027  val_loss=0.019  ← barely improves
Recall: 0.09  PosError: 0.248  (NoOp: 0.038)
```

**After fix** (`targets["coord"] = gt_xywh - vlm_xywh` — correct):
```
Epoch 1: train_loss=2.05  val_loss=1.63  ← correct high start
Epoch 10: train_loss=0.037  val_loss=0.016  ← meaningful 100x drop
Recall: 0.38  PosError: 0.212  (still beats train_start, needs more data)
```

The fix alone improved val_loss 3x (0.050 → 0.016) and recall 4x (0.09 → 0.38).

## 2. Circular Import in ML Project Layouts

**Common in projects with data/ → graph/ → model/ bidirectional imports.**

### Pattern

```
data/__init__ → graph_dataset → graph/builder → graph/schema → data/vlm_output → data/__init__
                                                            ↻ cycle!
```

### Diagnosis

- Running the script directly works with `--n 10` but hangs with `--n 500` — the import takes different paths depending on which modules get loaded first.
- `python -c "from module import X"` raises `cannot import name X from partially initialized module`.
- Background process shows 100% CPU, 1GB+ memory, but zero output for 60+ seconds — the import cycle deadlocks rather than fails.

### Fix

Move the offending import out of `__init__.py` into a lazy function:

```python
# data/__init__.py — break cycle at the import
def _get_graph_dataset():
    from .graph_dataset import GraphDataset, collate_graph_samples
    return GraphDataset, collate_graph_samples
```

### Prevention

Any `__init__.py` that re-exports from a sibling module (data exports graph_dataset, graph exports schema that imports data) is a cycle candidate. Use `grep -r "from.*bipartite.*import" src/bipartite*/__init__.py` to check for cross-module imports — they should be lazy if they bridge major package boundaries.

## 3. Empty Tensor NaN

Already covered in `pytorch-nan-debugging.md`. Quick reference for training pipelines:

| Context | Check | Fix |
|---------|-------|-----|
| LayerNorm([0, D]) | Batch has 0 constraints/elements | `norm(x) if x.numel() > 0 else x` |
| BCE([], []) | Empty prediction or target | Return 0.0 tensor |
| MSE on empty | Same pattern | Guard before reduction |

## 4. Dataset Split and Data Flow Verification

Verify the training loop actually sees all data:

```python
# Check 1: split sizes match config
assert len(train_set) == int(len(all_graphs) * (1.0 - val_split))
assert len(val_set) == len(all_graphs) - len(train_set)

# Check 2: DataLoader yields correct items
for batch in loader:
    if isinstance(batch, (list, tuple)):
        data, targets = batch
        # Verify shapes match expectations
        assert data["element"].x.shape[0] == targets["coord"].shape[0]

# Check 3: count training steps
num_batches = 0
for _ in loader:
    num_batches += 1
assert num_batches == len(train_set)  # or len//batch_size

# Check 4: verify loss format
# Log first 3 batch's predictions shapes and target keys
for i, batch in enumerate(loader):
    if i >= 3: break
    data, targets = batch
    preds = model(data)
    logger.info("pred keys: %s", list(preds.keys()))
    logger.info("target keys: %s", list(targets.keys()))
```

## 5. Metrics vs Training Target Mismatch

The metric used for evaluation may compute something different from what the loss optimizes:

| Loss | Metric | Mismatch |
|------|--------|----------|
| MSE(Δcxcywh, target_delta) | recall/precision via IoU(xyxy, gt_xyxy) | Loss measures delta accuracy; metric measures final box overlap. Small delta errors → large xyxy errors at IoU threshold boundaries. |
| BCE(existence, 1.0) | recall False Negatives | Augments recall but doesn't improve box precision. |

**Diagnosis:** If loss drops consistently but metrics don't improve, compute an auxiliary metric in the same space as the loss:

```python
# Example: also log MSE between corrected xyxy and GT xyxy
corrected_xyxy = apply_deltas(vlm_boxes, pred_deltas)
box_mse = F.mse_loss(corrected_xyxy, gt_boxes)
logger.info("box_mse=%.6f", box_mse)
```

## 6. VLM-GT Element Count Mismatch (Hungarian Matching)

**Problem:** A real VLM detects a different number of elements than ground truth (e.g. VLM finds 2 elements, GT has 23). Training crashes with:
```
RuntimeError: The size of tensor a (2) must match the size of tensor b (23)
```

### Fix: Hungarian Matching

1. Match VLM predictions → GT elements using IoU-based Hungarian algorithm.
2. Elements below IoU threshold (e.g. 0.3) are excluded from matching.
3. Build three groups:

| Group | VLM box source | Existence target | Coord target |
|-------|---------------|------------------|-------------|
| Matched (M→GT) | Real VLM | 1.0 | gt_xywh - vlm_xywh |
| False Negative (FN) | Unmatched GT | 0.0 (or approximate with noisy GT) | Zero delta (no correction) |
| False Positive (FP) | Unmatched VLM | 0.0 | Zero delta |

```python
# Pseudocode
from scipy.optimize import linear_sum_assignment

iou_matrix = compute_iou(vlm_boxes, gt_boxes)
cost_matrix = 1.0 - iou_matrix
cost_matrix[iou_matrix < iou_threshold] = LARGE_COST  # not 1e9, avoids MPS crash

row_idx, col_idx = linear_sum_assignment(cost_matrix.cpu().numpy())
matched = [(r, c) for r, c in zip(row_idx, col_idx)
           if cost_matrix[r, c] < LARGE_COST]

fp_idx = set(range(len(vlm_boxes))) - {r for r, _ in matched}
fn_idx = set(range(len(gt_boxes))) - {c for _, c in matched}
```

### Pitfalls

- **INF in cost matrix crashes scipy**: Use a large finite value (1e9) instead of `float('inf')`. On MPS/metal devices, crashes manifest as silent hangs rather than Python errors.
- **Variable-length graphs**: After matching, different images have different element counts. Use `batch_size=None` in DataLoader to keep each graph independent (no stacking).
- **Existence targets**: FP elements should appear in the graph (so the GNN sees them) but have existence=0 target. FN GT elements need VLM input approximated (e.g. from GT with added noise) for the model to have something to process.
- **Evaluation must filter by existence**: When computing metrics, exclude FP elements (existence < 0.5) or they pollute recall/precision.

## 7. VLM Quality Baseline Check

Before building a GNN correction pipeline, establish whether the VLM leaves room for improvement:

### Quantify VLM baseline error

```python
noop_metrics = compute_all_metrics(vlm_boxes, gt_boxes)
# Key numbers:
#   noop.position_error ~0.01 → VLM is near-perfect, GNN has no room
#   noop.position_error ~0.10+ → VLM has meaningful error, GNN can help
#   noop.recall < 0.90 → VLM misses elements, GNN can fix omissions
```

**Rule of thumb:** If NoOp position_error < 0.02 (normalized coordinates), the VLM is too accurate for a delta-predicting GNN to beat — the delta target is essentially zero and the GNN can only add noise.

### Three-model benchmark

Test a range of VLM models to find one with the right error profile:

| Model Tier | Size | Error Profile | GNN Potential |
|------------|------|--------------|---------------|
| Qwen3-VL Plus (API) | Large | ~0.013 pos_err | None — too accurate |
| Qwen3-VL Flash (API) | Medium | ~0.0001 pos_err | None — pixel-perfect |
| Moondream (Ollama, 828MB) | Tiny | Few detections, poor coverage | Maybe — but too few elements |
| LLaVA (Ollama, 4.1GB) | Medium | TBD | Best candidate for correction |

### What to compare

| Metric | GNN after fix | NoOp | Qwen3-VL reference | What it tells you |
|--------|--------------|------|-------------------|-------------------|
| Recall | 0.38 | 0.99 | 0.99 | GNN not matching VLM quality |
| Pos Error | 0.21 | 0.04 | 0.013 | Even after fix, delta errors compound |
| F1 | 0.41 | 0.99 | 0.99 | GNN needs more data or different architecture |

### Conclusion patterns

| Finding | Action |
|---------|--------|
| GNN precision > recall | Architecture learns corrections on detected elements but misses undetected ones |
| val_loss stops improving early (epoch 6-10) | Data has reached information ceiling — no more structure to learn |
| All configs converge to same val_loss | Problem is data-limited, not model-capacity-limited |
| GNN can't beat NoOp by 10x+ | Training pipeline bug (see section 1) or VLM too accurate (this section) |
