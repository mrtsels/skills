# GNN Research Validation Patterns

> Reusable patterns for validating GNN research hypotheses with minimal
> architectural investment.  Captures the approach from the *structural
> completeness* experiment in the bipartite-gnn-gui project.

## The "Reuse Existing Heads" Pattern

**Situation**: You have a hypothesis about what a GNN could learn, but
building a new head / loss / decoder is expensive. You want the fastest
possible signal: *"can this GNN learn this task at all?"*

**Pattern**: Pick an **existing prediction head** whose output semantics
are closest to your new task.  Change only the **data pipeline** (what
goes in, what labels come out).  Keep the model architecture frozen.

### Case Study: Structural Completeness

| Component | Original task | Validation spike |
|---|---|---|
| Head | `violation_head` (binary: violated/valid constraint) | Same head |
| Original targets | GT constraint violations | **New:** synthetically-vsiolated constraints from random element removal |
| Architecture | encoder + 3 heads | 100% unchanged |
| Data | VLM→GT matching | GT layouts, randomly drop elements, recompute violation labels |

Result: **91% accuracy** on detecting structural incompleteness, achieved
in a single afternoon with zero new model code.

## Extension: From Classification to Regression

Once the existing-head spike validates feasibility (violation detection at
95 %), the **same encoded constraint embeddings** can drive a proposal
head that predicts missing-element bounding boxes.  No architecture change
was needed beyond adding a small MLP on top of the existing encoder output.

### Extension Pattern: Constraint Embedding → Proposal Head

```
Violated constraint embedding (hidden_dim)
    → 2-layer MLP + Sigmoid
    → (x1, y1, x2, y2) [0, 1]  ← missing-element bbox proposal
```

The element-proposal head operates on **constraint embeddings**, not element
embeddings.  This is only possible because the bipartite encoder already
produces rich constraint-node representations that aggregate information
from all participating (surviving) elements via two-hop message passing.

### Joint Training Result

| Head | Task | Epoch 1 | Epoch 33 | Final |
|---|---|---|---|---|
| `violation_head` | Detect broken constraints | 68.8% acc | **94.1% acc** | 94.1% |
| `proposal_head` | Predict missing bbox | MSE 0.073 | **MSE 0.044** | 0.044 |

Both heads trained simultaneously (2000 samples, 60% drop ratio, 33 epochs).
No task interference — the encoder learns representations useful for both
discriminative (violation detection) and generative (bbox proposal) tasks.

## When to Use This

- You have a hypothesis about **what the GNN could learn from structure**
- Your model already has a relevant head (violation, existence, regression)
- Building a custom decoder would take more time than spiking the idea

## When NOT to Use This

- The hypothesis requires fundamentally different output semantics
- The existing head's architecture constraints would distort the task
- You need precise quantitative comparison with a new method

## Practical Steps

1. **Identify the closest existing head** — what does it predict, and
   what's the closest analog to your new task?

2. **Design a synthetic data pipeline** — create labeled examples by
   corrupting or transforming ground-truth data.  Synthetic data gives
   you unlimited samples and clean ground truth.

3. **Zero out irrelevant losses** — set `coord_weight=0`,
   `existence_weight=0` etc. in the `CombinedLoss` so only the relevant
   head's parameters receive gradients.

4. **Run a small experiment first** — 200-500 samples, 30-50 epochs.
   If the training loss drops consistently and val metrics are above
   random baseline, the hypothesis is validated.

5. **Escalate when validated** — once the spike confirms feasibility,
   build the proper head/architecture for the production task.

## Common Pitfalls

- **Masking instead of removing**: Masking element features (setting to
  -1 or 0) while keeping the element node in the graph gives the model
  a "ghost node" with visible edges — this leaks structural information
  about the element's original position through edge features.  Actual
  removal of elements is a harder and more realistic test.

- **Too high a masking ratio**: With 60%+ masking, neighboring elements
  are also masked, leaving no signal for message propagation.  The model
  can only guess.  Start with 30-40% removal and work up.

- **Forgetting to check edge feature propagation**: Most SAGEConv
  instances don't use `edge_attr` unless explicitly configured with
  `edge_dim`.  If the graph carries edge features but the conv layers
  ignore them, message passing is less informative than expected.
