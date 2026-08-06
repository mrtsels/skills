# Checkpoint Loading & Inference Hardening — Verified Recipe

From the bipartite-gnn-gui demo rebuild (backend agent task: `api/pipeline.py`
+ `api/main.py`). All code below ran successfully against the real joint
checkpoint; test transcripts are from the actual session.

## 1. Why the loader must fail loudly

The joint checkpoint (`checkpoints/violation_detection_joint/best_model.pt`)
is the ONLY trustworthy one in this project:

| Checkpoint | Loaded | Reality |
|---|---|---|
| `violation_detection/best_model.pt` | 5/44 (11%) | hd=16 — wrong arch |
| `violation_detection_violation_only/best_model.pt` | 44/44 | proposal head untrained |
| `violation_detection/visual_fusion_model.pt` | partial | needs 197-d visual input |
| **`violation_detection_joint/best_model.pt`** | **44/44** | **the only valid one** |

`strict=False` silently drops mismatched keys → random weights → plausible-
looking garbage. The loader below turns "wrong checkpoint" into a startup
crash instead.

## 2. Verified loader implementation

```python
def _detect_hidden_dim(self, checkpoint_path: str) -> int:
    """Infer hidden_dim from the checkpoint's first-layer weight shape."""
    state = torch_load(checkpoint_path)          # torch_load: weights_only=True
    if isinstance(state, dict) and "model" in state:
        state = state["model"]
    if isinstance(state, dict):
        for key in ("encoder.element_proj.weight",
                    "encoder.e_to_c_convs.0.lin_l.weight"):
            if key in state:
                return int(state[key].shape[0])  # (hidden_dim, element_dim)
    raise RuntimeError(f"Cannot detect hidden_dim from checkpoint: {checkpoint_path}")

def _safe_load_state(self, ckpt: Any) -> int:
    """Shape-filtered load + sanity checks. Returns number of matched keys."""
    state = ckpt
    if isinstance(state, dict) and "model" in state:
        state = state["model"]
    if isinstance(state, dict) and "state_dict" in state:
        state = state["state_dict"]
    if not isinstance(state, dict):
        raise RuntimeError(f"Unsupported checkpoint format: {type(ckpt)}")
    if any(k.startswith("model.") for k in state):       # strip prefix
        state = {k[len("model."):]: v for k, v in state.items()}

    model_state = self.model.state_dict()
    matched = {k: v for k, v in state.items()
               if k in model_state and v.shape == model_state[k].shape}
    n_matched, n_total = len(matched), len(state)
    if n_matched < 30:                                    # floor: 44 keys total
        raise RuntimeError(
            f"Checkpoint mismatch: only {n_matched}/{n_total} keys matched. "
            f"Expected hidden_dim={self.hidden_dim}.")
    critical = ["encoder.element_proj.weight",
                "violation_head.network.3.weight",
                "proposal_head.network.3.weight"]
    for ck in critical:
        if ck not in matched:
            raise RuntimeError(f"Critical layer missing from checkpoint: {ck}")
    self.model.load_state_dict(matched, strict=False)
    logger.info("Loaded %d/%d keys (critical layers OK)", n_matched, n_total)
    return n_matched
```

Model construction: `BipartiteGNNCorrector(element_dim=5, constraint_dim=11,
hidden_dim=self.hidden_dim, num_layers=2, dropout=0.0)` — inference only, so
dropout=0; the checkpoint's hd drives the architecture.

## 3. Real test transcript

```
# joint ckpt (default path): 44 keys, hd=128
element_proj.weight shape: (128, 5)
matched keys: 44 / 44
OK 220439
health: {'params': 220439, 'hidden_dim': 128, 'violation_threshold': 0.6, ...}

# hd=16 checkpoint loads fine (compat path)
hd16 OK: 16 4279

# visual_fusion checkpoint must be REJECTED, loudly
RuntimeError raised OK: Critical layer missing from checkpoint: encoder.element_proj.weight
```

## 4. Bbox output-format bug (xywh vs xyxy)

The proposal head (`ElementProposalHead.forward`) returns
`torch.cat([raw[:, :4].sigmoid(), type_logits], dim=1)` — i.e. `[x1,y1,x2,y2]`
already, NOT center-xywh. The old pipeline fed it through `_xywh_to_xyxy()`,
corrupting every proposal. Rule: read the head source before writing the
post-processor. And since the four sigmoids are independent, invalid boxes
(x1>x2 or y1>y2) are common → filter:

```python
bbox_xyxy = proposal[i].tolist()
bbox_xyxy = [max(0.0, min(1.0, v)) for v in bbox_xyxy]
if bbox_xyxy[2] <= bbox_xyxy[0] or bbox_xyxy[3] <= bbox_xyxy[1]:
    continue   # skip invalid proposal
```

## 5. Monkeypatch-forward validation (filter logic test)

Synthetic aligned grids never trigger the violation head, so to test the
invalid-bbox filter deterministically, stub the model:

```python
def fake_forward(graph):
    return {
        'existence': torch.tensor([[0.9]] * 9),
        'violation': torch.tensor([[0.95], [0.95], [0.2]]),
        'proposal': torch.tensor([[0.8, 0.1, 0.3, 0.9],   # invalid x1>x2
                                  [0.1, 0.1, 0.9, 0.9],   # valid
                                  [0.2, 0.2, 0.4, 0.4]]), # below threshold
        'proposal_type': torch.zeros(3, 8),
    }
p.model.forward = fake_forward
r = p.gnn_analyse(grid_elements, img_w=120, img_h=120)
assert len(r['proposals']) == 1 and r['proposals'][0]['bbox'][2] > r['proposals'][0]['bbox'][0]
```

Result: `proposals kept: 1` (invalid filtered, below-threshold filtered,
violated-count still reports 2 — filtering only affects the proposals list).

## 6. Degenerate-input fallbacks

Return early with a `fallback` field instead of crashing or emitting empty
results that look like errors:

- 0 valid elements → `"fallback": "no_elements"`
- <3 elements → `"fallback": "no_elements"` (2 same-size elements CAN form a
  `same_size` constraint, so don't rely on constraint extraction alone)
- 3+ elements but 0 constraints → `"fallback": "no_constraints"`

Frontend shows a hint ("元素太少,无法构建约束图") instead of a blank panel.

## 7. API-contract notes (bipartite-gnn demo)

- `/api/cases` → summaries `[{id, name, metrics}]`; `cases.json` missing →
  `[]` with 200 + a logged warning (never 500).
- `/api/case/{id}` → full case; unknown id → 404 `{"error": ...}`.
- `/api/screenshot/{id}` → FileResponse; honor case's `screenshot` field,
  then fall back through `{id}.jpg/.png/.jpeg`.
- `/api/predict` response: hero-case schema (`id="upload"`, `img_w/h`,
  `vlm_elements` normalized to [0,1], `proposals`, `metrics: null`,
  `vlm_time_ms`, `gnn_time_ms`, `fallback`) + backward-compat fields
  (`vlm`, `gnn`, `corrected_json`, `overlay_b64`). No `image_b64`.
- Removing a `Form` param (`vlm_model`) is safe — FastAPI ignores undeclared
  form fields, so the old frontend that still posts it keeps working.
- `pillow_heif` import wrapped in try/except (server starts without it).
