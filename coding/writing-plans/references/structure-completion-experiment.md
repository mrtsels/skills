# Structural Completion Experiment Pattern (GNN)

A reusable experimental paradigm for GNN-based **element completion** on graphs.

## Core Idea

Given a bipartite graph where some elements are removed, train a GNN to:
1. **Detect violated constraints** (constraints that lost participants)
2. **Propose missing elements** (predict their position from constraint embeddings)

This is a **self-supervised** task: complete GT data is available, so randomly
dropping nodes creates unlimited training pairs.

## Pipeline

```
GT Elements ─┬─→ Full Constraints ──┐
              │                      │
              ▼                      ▼
       Random Drop (60%)      For each constraint:
              │                 check survivors count
              ▼                      │
       Survivors + Kept Constraints  ▼
              │              label: violated (0/1)
              │              target: missing element bbox
              ▼
       GNN encodes:
         - element embeddings
         - constraint embeddings
              │
              ├── ViolationHead → per-constraint: is this incomplete?
              └── ProposalHead  → per-constraint: where is the missing bbox?
```

## Key Design Decisions

### 1. Data Generation (`build_violation_graph`)

```python
def build_violation_graph(
    gt_elements: list[ElementNode],
    drop_ratio: float = 0.4
) -> tuple[HeteroData, dict]:
    # Extract constraints from full GT layout
    # Randomly drop elements
    # For each constraint, check surviving participants
    # If < 2 survivors → violated (label=1)
    # Compute proposal target: average GT bbox of removed participants
```

### 2. Heads

- **ViolationHead**: BCE on constraint embeddings → per-constraint violation
- **ProposalHead**: 2-layer MLP + Sigmoid → (4,) bbox [x1,y1,x2,y2] in [0,1]

### 3. Loss

```python
total = violation_weight * BCE(violation_pred, violation_label)
total += proposal_weight * MSE(proposal_pred[mask], proposal_target[mask])
```

Only compute proposal loss on violated constraints (use `mask`).

### 4. Evaluation Protocol

| Drop Ratio | What It Tests |
|---|---|
| 0.2 | Sparse missing; nearest-neighbor is competitive |
| 0.4 | Moderate; GNN starts to close gap |
| 0.6 | GNN > NN; structural signal dominates |
| 0.8 | Extreme sparsity; GNN still works |

**Baselines:**
- Nearest-neighbor: copy closest survivor's bbox
- Center: always predict layout center (degenerate)
- Random: uniform random in [0,1]

## Results Template

| drop | GNN Acc | GNN MSE | GNN IoU | NN MSE | NN IoU | ΔIoU |
|---|---|---|---|---|---|---|
| 0.2 | acc | mse | iou | nn_mse | nn_iou | gnn - nn |
| 0.6 | acc | mse | iou | nn_mse | nn_iou | gnn - nn |

GNN beats NN when drop ≥ 0.6 (IoU +30-40%).

## Pitfalls

- **MSE without Sigmoid**: output layer must be bounded ([0,1]) or MSE explodes
- **Drop ratio too low (< 0.3)**: nearest-neighbor beats structural reasoning
- **Loss imbalance**: violation loss dominates proposal loss; weight them
- **Constraint-only proposal**: multiple constraints may point to the same missing element; aggregation (e.g., mean constraint embeddings per missing element) can improve accuracy
- **Center baseline bug**: must use normalized coordinates; pixel-coordinate baselines produce ~10^6 MSE and are meaningless
