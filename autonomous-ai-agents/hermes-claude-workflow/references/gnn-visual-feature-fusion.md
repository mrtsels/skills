# Visual Feature Fusion for GNN Nodes

When a GNN only has spatial/structural features (bbox, type, confidence) and you want to add visual information:

## Architecture Options

| Approach | Detail | Params | Impact |
|----------|--------|:------:|:------:|
| **Simple concat** | Pre-compute visual features, append to node features | +5.7M (vit_tiny) | +25pp violation acc, +14pp type acc |
| **Cross-attention fusion** | struct→MLP, visual→MLP, MultiheadAttention(visual Q × struct KV) | +33K | +?pp (being tested) |

## Pre-computation Pattern

```python
import timm, torch
model = timm.create_model('vit_tiny_patch16_224', pretrained=True).eval()
# For each element, crop (x1-5, y1-5, x2+5, y2+5) from screenshot
# Resize to (224,224), normalize, batch encode
with torch.no_grad():
    out = model.forward_features(batch)  # (N, 197, 192)
    feat = out[:, 1:, :].mean(dim=1)     # (N, 192) — pool patches, skip CLS
# Cache to disk as .pt files
```

## Key Decisions

- **Pre-fusion (before GNN encoder)** vs **Post-fusion (after encoder, before heads)**: Pre-fusion is preferred — visual semantics should guide constraint↔element message passing.
- **Vision model choice**: vit_tiny (5.7M params) is enough for proof of concept. DINOv2/SigLIP/ResNet18 may give small further gains.
- **Backward compatibility**: when visual features absent, fall back to structural MLP projection alone.

## Vision Model Comparison (bipartite-gnn-gui, 500 RICO)

| Config | Params | Feat Dim | Violation Acc | Type Acc | Proposal MSE | Precomp Time |
|--------|:------:|:--------:|:-------------:|:--------:|:------------:|:------------:|
| Pure structural | 0 | 5 | 0.593 | 0.312 | 0.088 | — |
| + vit_tiny concat | 5.7M | 192 | **0.847** | **0.450** | **0.079** | 30s |
| + DINOv2-base concat | 86M | 768 | 0.854 | 0.403 | 0.085 | 173s |
| + Cross-attention fusion (vit_tiny) | 5.7M+33K | 64 | 0.850±0.031 | 0.440±0.016 | **0.062** | 30s+training |

## Key Negative Result: DINOv2

**DINOv2-base (86M params, 768-dim) provides no meaningful improvement over vit_tiny (5.7M params, 192-dim).** Despite:
- 15× more model parameters
- 4× richer features
- 6× precomputation cost (173s vs 30s)

All three metrics are essentially identical across both encoders. **The task's bottleneck is NOT visual feature quality** — vit_tiny already captures sufficient visual information for effective element classification and proposal generation. Do not spend time upgrading the visual encoder without evidence that feature quality is the limiting factor.

## Cross-Attention Fusion: Mixed Results

Cross-attention fusion (via `CrossAttentionFusion` + `SplitAndFuse` in `attention.py`) replaces simple concatenation with learned attention between structural and visual modalities:

**Architecture:** struct (5-d) → MLP → Q, visual (192-d) → MLP → KV, MultiheadAttention → residual + LayerNorm → encoder.

**3-seed results (mean ± std):**

| Metric | Simple Concat | Cross-Attention | Δ |
|--------|:-------------:|:---------------:|:-:|
| Violation Acc | 0.847 ± 0.001 | 0.850 ± 0.031 | +0.003 |
| Proposal MSE | 0.081 ± 0.004 | **0.062 ± 0.004** | **−0.018** |
| Type Acc | 0.447 ± 0.008 | 0.440 ± 0.016 | −0.007 |

Proposal MSE consistently improves (−23%) across all seeds — the attention mechanism helps localize missing elements. But violation and type metrics are essentially tied, and variance increases. **Simple concatenation remains recommended** for most use cases unless proposal quality is the primary concern.

## Dependencies

```bash
pip install timm open-clip-torch torchvision pillow
```
