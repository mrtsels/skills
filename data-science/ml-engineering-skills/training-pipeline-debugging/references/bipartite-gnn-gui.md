# bipartite-gnn-gui Training Pipeline Reference

## Project Structure

```
bipartite-gnn-gui/
├── scripts/run_experiment.py      # Standardized experiment runner (CLI + library)
├── scripts/e2e_smoke_test.py      # Quick end-to-end verification
├── experiments/sweep.py            # Hyperparameter sweep (6 configs)
├── experiments/results.json        # Sweep results (append-only)
├── configs/experiment.yaml         # Default experiment config
├── src/bipartite_gnn_gui/
│   ├── data/
│   │   ├── graph_dataset.py        # GraphDataset (GUIDataset→HeteroData bridge)
│   │   ├── dataset.py              # GUIDataset, GUIDataModule
│   │   ├── rico_loader.py          # RICO View Hierarchy parser
│   │   └── ground_truth.py         # GT loading (ScreenSpot, RICO)
│   ├── graph/
│   │   ├── builder.py              # BipartiteGraphBuilder → HeteroData
│   │   ├── constraints.py          # extract_all_constraints
│   │   └── schema.py               # ElementNode (xyxy+confidence)
│   ├── model/
│   │   ├── model.py                # BipartiteGNNCorrector
│   │   ├── trainer.py              # Trainer.fit()
│   │   ├── encoder.py              # BipartiteGraphSAGE
│   │   └── losses.py               # CombinedLoss
│   └── eval/
│       ├── metrics.py              # compute_all_metrics
│       ├── evaluator.py            # Evaluator (per-category breakdown)
│       ├── baselines.py            # NoOp, Identity, RandomJitter
│       └── qualitative.py          # plotting (correction comparison, heatmap)
```

## Data Flow

```
RICO JSON (View Hierarchy)
  → parse_rico_vh() → extract_elements() → ElementNode[]
  → make_noisy_vlm() → VLM ElementNode[] (simulated predictions)
  → extract_all_constraints() → ConstraintNode[]
  → BipartiteGraphBuilder.build(VLM_elements, constraints) → HeteroData
  → targets = {"coord": delta, "gt_boxes": raw_gt, "existence": ..., "violation": ...}
  → Trainer.fit(hetero_data, targets)
  → evaluate_model() → (GNN_metrics, NoOp_metrics)
```

## Critical Fix (June 2026)

`targets["coord"]` must be `(gt_xywh - vlm_xywh)` in cxcywh format, NOT raw xyxy GT boxes.
Raw GT boxes go into `targets["gt_boxes"]` for evaluation.

**Both** GraphDataset.__getitem__ AND build_graph() in run_experiment.py need this fix.

## Known Limitations

### 1. Simulated Gaussian noise has no structural patterns

The GNN can never outperform NoOp on Gaussian noise because there is no pattern to learn. Every element's noise is independent and zero-mean. The optimal strategy is Δ=0. Real VLM predictions have structured errors (icon drift vs text drift, adjacent-element correlations, systematic misalignments) that the GNN CAN exploit.

**Signal:** All hyperparameter sweep configs converge to same val_loss (~0.054) regardless of hidden_dim (64/128/256). Model capacity is not the bottleneck — the noise model is.

### 2. ScreenSpot is too sparse for GNN training

- 610 images, 1272 annotations
- avg 2.1 elements/image (max 6)
- Only 415 images have ≥2 elements (minimum for constraint extraction)
- With avg ~2 elements, constraints are trivial — no useful graph structure learned

RICO (66K images, avg 24±18 elements, 50±49 constraints) is the primary training source.

### 3. CPU training limits scale

RICO has 66K images. At ~0.3s per epoch per 100 graphs on CPU, training on 1000+ samples becomes a multi-minute affair. Full-scale training (10K+ samples, 100+ epochs) realistically needs GPU.

## Sweep Results (June 2026)

6 configs × 200 samples × 50 epochs:

| Config | best_val | recall | precision | pos_err |
|---|---|---|---|---|
| hd64_small-noise (0.08) | 0.056 | 0.150 | 0.531 | 0.244 |
| hd128_small-noise (0.08) | 0.055 | 0.201 | 0.540 | 0.248 |
| hd64_big-noise (0.20) | 0.056 | 0.201 | 0.534 | 0.245 |
| hd128_big-noise (0.20) | **0.054** | 0.204 | 0.534 | 0.249 |
| hd128_low-lr (5e-4) | 0.055 | 0.202 | 0.529 | 0.246 |
| hd256 (lr=1e-3) | 0.054 | 0.201 | 0.539 | 0.249 |

**Key insight:** hidden_dim makes almost no difference. All configs converge to ~0.054.

## Training Commands

```bash
# Quick test (100 samples, 10-15 epochs)
.venv/bin/python -u scripts/run_experiment.py --n 100 --epochs 10

# Full sweep
.venv/bin/python -u experiments/sweep.py

# All tests
.venv/bin/python -m pytest tests/ -v --tb=no -q
```

## Data Locations

- RICO: `/Users/minimx/bipartite-gnn-gui/data/rico_local/combined/` (66K JSON + JPG)
- ScreenSpot: SMB mount at `data/raw/screenspot/`
- Use ABSOLUTE paths when running from worktrees (`/Users/minimx/bipartite-gnn-gui/data/rico_local/combined/`)

## VLM Predictions

See `references/vlm-inference.md` for Qwen3-VL API setup, batch stats, and training integration.
