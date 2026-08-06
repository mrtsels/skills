# Model Layer Implementation Prompt (2026-06-22)

**Context:** Bipartite GNN for GUI Correction. Replace 6 stub files with real implementations.
**Model:** `deepseek-v4-pro`
**Worktree:** Independent git worktree for isolation

## Prompt Structure

```
TASK: Implement the Model Layer (Phase 4.4) — replace all stubs in src/bipartite_gnn_gui/model/.

CONTEXT:
You are in a WORKTREE at /tmp/bgg-worktree/feat/model-layer/

Read ALL these files:
- CLAUDE.md
- src/bipartite_gnn_gui/model/encoder.py (current stub — 51 lines)
- src/bipartite_gnn_gui/model/heads.py (stub — 45 lines)
- src/bipartite_gnn_gui/model/losses.py (stub — 49 lines)
- src/bipartite_gnn_gui/model/model.py (stub — 37 lines)
- src/bipartite_gnn_gui/model/trainer.py (stub — 25 lines, no-op)
- src/bipartite_gnn_gui/model/inference.py (stub — 11 lines)
- src/bipartite_gnn_gui/model/__init__.py (exports)
- src/bipartite_gnn_gui/graph/schema.py
- src/bipartite_gnn_gui/graph/builder.py
- src/bipartite_gnn_gui/utils/config.py
- configs/default.yaml
- docs/design/detailed.md
- docs/algorithm.md

The .venv is at /Users/minimx/bipartite-gnn-gui/.venv/

ARCHITECTURE:
Two-layer message passing: element → constraint → element
Three prediction heads on element embeddings
Combined loss with 4 components

WHAT YOU NEED TO IMPLEMENT:
[detailed per-module instructions for encoder, heads, losses, model, trainer, inference]

VERIFY:
- Each new test file passes individually
- All existing tests still pass
- .venv/bin/python -m pytest tests/ -v

GIT WORKFLOW:
[sequential commits per module, then push + PR]
```

## Key Architecture Decisions

1. **HeteroGraphSAGE with PyG** — Use `torch_geometric.nn.SAGEConv` with `HeteroData`. Two-layer message passing: element→constraint→element.
2. **Heads** — Simple MLPs with dropout, no residual connections needed for this task.
3. **CombinedLoss** — 4 components: coord (MSE), violation (BCE), existence (BCE), alignment consistency (penalizes constraint violations after delta).
4. **Trainer** — Standard PyTorch loop. AdamW + cosine + warmup. AMP support. Early stopping on val loss.
5. **Inference** — VLM JSON → HeteroData → model → apply deltas → clamp → corrected JSON.

## Risks

| Risk | Mitigation |
|------|------------|
| torch-geometric may not be installed | Include `pip install torch-geometric` in prompt |
| HeteroData from builder might differ from encoder expects | Prompt says to read builder.py and match its output schema |
| Trainer depends on real HeteroData batches | Use synthetic HeteroData in tests |
