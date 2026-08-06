# ML Project Planning with Feasibility Verification

> When the user asks for a plan with feasibility verification ("验证可行性", "/plan and verify"), do NOT just read docs and write a plan. Actually load the model, run inference, check dimensions, and document findings before writing the plan.

---

## Why verify first

ML projects have hidden failure modes that documentation alone won't reveal:

- Checkpoint format mismatch (raw state_dict vs wrapped dict with 'model' key)
- Model architecture mismatch (different element_dim/hidden_dim than expected)
- Missing dependencies (timm, transformers, specific PyG version)
- Inference failures on synthetic data (existence head collapse, NaN outputs)
- Device compatibility (MPS vs CUDA vs CPU)

Surfacing these during planning avoids discovering them mid-implementation.

## Verification checklist

Before writing a plan for any ML/DS project that involves checkpoint loading or model inference, run these checks:

### 1. Checkpoint dimension inspection

```python
ckpt = torch.load(ckpt_path, map_location='cpu', weights_only=True)
# Check if wrapped
if 'model' in ckpt:
    state = ckpt['model']
else:
    state = ckpt
# Extract dimensions from first layer weights
elem_dim = state['encoder.element_proj.weight'].shape[1]
hidden_dim = state['encoder.element_proj.weight'].shape[0]
con_dim = state['encoder.constraint_proj.weight'].shape[1]
has_fusion = any('fusion' in k for k in state.keys())
# Document: element_dim, constraint_dim, hidden_dim, fusion, total params
```

### 2. Model instantiation + load

```python
model = ModelClass(element_dim=elem_dim, constraint_dim=con_dim, hidden_dim=hidden_dim, ...)
model.load_state_dict(state, strict=True)
model.eval()
print(f'{sum(p.numel() for p in model.parameters()):,} params')
```

### 3. End-to-end inference with synthetic data

```python
# Build minimal valid inputs (not real data, just enough to exercise the pipeline)
elements = [ElementNode(...), ...]
constraints = extract_all_constraints(elements)
graph = builder.build(elements, constraints)
with torch.no_grad():
    outputs = model(graph)
# Check output shapes and value ranges
for key, tensor in outputs.items():
    print(f'{key}: {tensor.shape}, range=[{tensor.min():.3f}, {tensor.max():.3f}]')
```

### 4. Pipeline integration test

If the project has an InferencePipeline wrapper, test it end-to-end:

```python
pipeline = InferencePipeline(model, device='cpu')
result = pipeline.correct_single(synthetic_vlm_json)
assert isinstance(result, dict) and 'elements' in result
```

### 5. Dependency availability check

```python
for pkg in ['torch', 'torch_geometric', 'timm', 'fastapi', 'pillow']:
    try:
        __import__(pkg)
        print(f'{pkg}: ✓')
    except ImportError:
        print(f'{pkg}: ✗ NOT INSTALLED')
```

## Plan document structure (ML variant)

When the plan involves model inference, add a "0. Feasibility Verification" section before the implementation plan:

```markdown
# [Feature] 可执行开发报告

> Date · Feasibility verified · All critical paths tested

## 0. Feasibility Verification

| Item | Status | Finding |
|------|:------:|---------|
| Checkpoint loads | ✅/❌ | ... |
| Model architecture match | ✅/❌ | element_dim=X, hidden_dim=Y |
| E2E inference works | ✅/❌ | ... |
| Dependencies present | ✅/❌ | ... |

**Model selection decision:** [which checkpoint, why]
**Known limitations (from experiment history):** [honest about accuracy/domain shift]

## 1. Architecture adjustments

[Simplify from original design doc if verification reveals unnecessary complexity]
```

## YAGNI decisions from verification

Verification often reveals opportunities to simplify:

| Finding | Decision |
|---------|----------|
| Model doesn't need visual features | Skip timm, skip ViT preprocessing |
| CPU inference is fast enough (<5ms) | Skip GPU dependency |
| Certain model head is unreliable on target domain | Don't filter by that head, show scores instead |
| Docker is overkill for demo | `python main.py` first, Docker later |

## Key principle

**Don't plan around assumptions. Verify, then plan.** A single `torch.load()` + `model(data)` call takes 20 seconds and saves hours of mid-implementation debugging.
