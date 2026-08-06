# NaN 损失排查：PyTorch 空张量陷阱

训练时 loss 变为 `nan` 且不下降，最常见的隐式原因是**空张量上的数值运算返回 NaN**。

## 典型场景

### 1. `LayerNorm([0, D])` → 全 NaN

```python
nn.LayerNorm(hidden_dim)(torch.zeros(0, hidden_dim))
# → tensor([], nan, nan, ...)  ← NaN 传播到整个后续计算
```

**原因：** `LayerNorm` 计算 `(x - mean) / std`，空张量的 `mean = 0/0 = NaN`。

**修复：**
```python
x = self.norm(x) if x.numel() > 0 else x  # 跳过空张量的 norm
```

### 2. `BCE([], [])` → NaN（PyTorch < 2.2）

```python
F.binary_cross_entropy(torch.zeros(0, 1), torch.zeros(0, 1))
# → tensor(nan)  ← 版本依赖
```

**原因：** 空张量的 BCE 在旧版 PyTorch 中返回 NaN。新版返回 0.0。

**修复：**
```python
def safe_bce(pred, target):
    if pred.numel() == 0 or target.numel() == 0:
        return torch.tensor(0.0, device=pred.device)
    return F.binary_cross_entropy(pred, target)
```

## 排查方法

当训练 loss 为 NaN 时，依次检查：

1. **排除严重过大/过小的数值：** 梯度爆炸通常产生 `inf` 而非 `nan`。`inf` 会在后续操作转 `NaN`。
2. **检查空张量路径：** 任何 `N=0` 的批次/特征都可能触发。常见位置：
   - 约束数 `N_con = 0` → `compute_violation_loss` 收到空张量
   - 元素数 `N_elem = 0` → `compute_existence_loss` 收到空张量
   - 消息传递层数 `N_con = 0` → `LayerNorm([0, D])`
3. **添加张量守卫：** 在所有损失函数和归一化层前加 `numel() > 0` 检查。

## 验证

```python
# 测试空张量 norm
x = torch.zeros(0, 128)
safe = nn.LayerNorm(128)(x) if x.numel() > 0 else x
assert not safe.isnan().any()  # True

# 测试空张量 BCE
pred = torch.zeros(0, 1)
target = torch.zeros(0, 1)
loss = F.binary_cross_entropy(pred, target)  # 可能 NaN
assert not torch.isnan(loss)  # 在 PyTorch 2.2+ 上 True
```
