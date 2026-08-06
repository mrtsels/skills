# Checkpoint Investigation Pattern — ML Web Demo

## When to Use

Before committing to a demo design, verify that ALL model heads actually
produce meaningful output on representative data. A checkpoint that loads
and forward-passes without error can still have broken heads.

## Step 0: Verify Architecture Match BEFORE Head Quality

The most dangerous failure is silent: `load_state_dict(strict=False)` skips
shape-mismatched keys and keeps random init — the model still runs, and its
garbage outputs look plausible. Always count matched keys first:

```python
sd = torch.load(path, map_location='cpu')
ms = model.state_dict()
filtered = {k: v for k, v in sd.items() if k in ms and v.shape == ms[k].shape}
print(f"{path}: matched {len(filtered)}/{len(sd)} keys")  # <100% → STOP

# Probe the checkpoint's real architecture (e.g. hidden_dim from conv weight)
hd = sd['encoder.e_to_c_convs.0.lin_l.weight'].shape[0]
```

Real case (bipartite-gnn-gui): `violation_detection/best_model.pt` was
hidden_dim=16, but the eval script loaded it into a hidden_dim=128 model —
only 5/44 (11%) keys matched, so 89% of weights were random. All downstream
"+2.9pp F1" results were meaningless. The script had been re-run with
`strict=False` and never checked the key count. The correct checkpoint
(`violation_detection_joint/best_model.pt`, 44/44 keys) gave a real but far
smaller gain (~+1pp F1 across 200 images).

Related variants:
- Single-head checkpoints (`*_violation_only`) leave other heads untrained:
  proposal boxes come out with x2<=x1 (filtered → zero proposals).
- Visual-fusion checkpoints expect 197-d element features; feeding 5-d
  silently drops `element_proj` (random input layer) → fake results.

## Methodology

### 1. Enumerate All Checkpoints

```python
import glob
for p in sorted(glob.glob('checkpoints/**/*.pt', recursive=True)):
    ckpt = torch.load(p, map_location='cpu')

    # Check format: raw state_dict vs wrapped dict
    if isinstance(ckpt, dict) and 'model' in ckpt:
        sd = ckpt['model']
    elif isinstance(ckpt, (dict, OrderedDict)):
        sd = ckpt
    else:
        continue

    # Detect heads from key names
    has_viol = any('violation' in k or 'vio' in k for k in sd)
    has_prop = any('proposal' in k for k in sd)
    has_exist = any('existence' in k for k in sd)
    has_coord = any('coord' in k for k in sd)

    total_params = sum(sd[k].numel() for k in sd if isinstance(sd[k], torch.Tensor))
```

### 2. Test on Controlled Synthetic Data

Create 3 test cases covering distinct scenarios:

| Test Case | Description | Expected Behavior |
|-----------|-------------|-------------------|
| Clean | Well-aligned elements, natural layout | Low violation, moderate existence |
| With hallucination | Clean + 1 random element in empty space | Low existence on fake element |
| Random | Scattered, no structural relationship | High violation count |

```python
for name, sd in ckpt_data.items():
    m = Model(…)
    m.load_state_dict(sd)
    m.eval()
    with torch.no_grad():
        out = m(graph)

    for head_name in ["existence", "violation", "proposal"]:
        s = out[head_name].squeeze().tolist()
        spread = max(s) - min(s)
        mean_val = sum(s) / len(s)
        # Working: spread > 0.1
        # Broken:  spread < 0.01
        print(f"{name}/{head_name}: mean={mean_val:.4f} spread={spread:.4f}")
```

### 3. Interpret Results

| Pattern | Meaning | Action |
|---------|---------|--------|
| All scores ~0.5, spread < 0.01 | Sigmoid saturated at 0.5 — no learned signal | Head never properly trained or collapsed |
| All scores ~0, spread < 0.01 | Violation/proposal head collapsed to zero | Multi-task training imbalance |
| Spread > 0.3 across test cases | Good discrimination | Use this checkpoint! |
| Spread varies wildly between test cases | Dataset-specific overfitting | Test on more diverse inputs |

### 4. Report Debug-First

When a model head doesn't work, the flow should be:
1. **Investigate**: Check all checkpoints, test systematically
2. **Report**: Show the user the data, explain what's broken and why
3. **Don't hide**: Don't put broken heads in the UI with a note saying "experimental"
   — remove them or be explicit that the component doesn't transfer to real data

## Real Example: Bipartite GNN GUI Project

Four checkpoints existed for a multi-head GNN (violation + proposal + existence + coord):

| Checkpoint | Violation Spread | Existence Spread | Existence on Fake | Verdict |
|------------|:-:|:-:|:-:|:-:|
| violation_only | 0.994 | ~0.03 | ~0.45 | ✅ Violation works |
| screenspot_finetuned | 0.26 | ~0.02 | ~0.45 | ⚠️ Weak |
| joint (viol+proposal) | 0.007 | ~0.01 | ~0.48 | ❌ Collapsed |
| proposal_only | 0.08 | ~0.01 | ~0.47 | ❌ Broken |

Key finding: **Joint training collapsed the violation head** (0.994 → 0.007 spread).
The existence head never worked on any checkpoint because it was trained on
synthetic noise (random jitter), not realistic VLM false positives.
