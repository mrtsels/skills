# PyTorch NaN Loss Debugging

When training loss goes to `NaN`, the root cause is almost always one of these patterns:

## Common Causes (check in order)

| Cause | Symptom | Fix |
|-------|---------|-----|
| **LayerNorm on empty tensor** | Tensor shape `[0, D]` passed to `nn.LayerNorm(D)` → `0/0 = NaN` | Guard: `norm(x) if x.numel() > 0 else x` |
| **BCE on empty tensor** | `F.binary_cross_entropy(torch.Size([0, 1]), torch.Size([0, 1]))` returns NaN in some PyTorch versions | Guard: return `0.0` if `x.numel() == 0` |
| **Division by zero** | `F.mse_loss` with large values from random init | Clamp inputs or use smaller init |
| **Log of zero/negative** | `torch.log()` on zero or negative values | Add epsilon or clamp |
| **Sigmoid + BCE with extreme activations** | Random init produces logits far from 0 → sigmoid becomes 0.0 or 1.0 → log(0) = -inf | Use smaller weight initialization |
| **CrossEntropy on empty class** | 0 samples of a class in a batch | Skip empty targets |
| **In-place operation on gradient** | `x += ...` instead of `x = x + ...` breaking autograd | Use out-of-place ops |

## Detection

```python
# Enable anomaly detection to find the source
torch.autograd.set_detect_anomaly(True)

# Or for the training loop only
with torch.autograd.detect_anomaly():
    loss = model(data)
    loss.backward()
```

This pinpoints the exact operation producing NaN.

## Diagnosis Steps

1. Run one batch with `detect_anomaly(True)` to find which operation produces NaN
2. Check if any tensor in the forward pass has shape `[0, N]` — common when there are 0 constraints or 0 elements
3. Check if `LayerNorm`, `BCE`, `MSE`, or `log` is being called on empty tensors
4. Add guard checks for `numel() == 0` at each loss component
5. If root cause is in the encoder, trace: projection → SAGEConv → LayerNorm → ReLU → Dropout — check which step produces NaN
