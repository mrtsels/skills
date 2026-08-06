# ML Pipeline E2E Smoke Test

验证多阶段 ML 管线（data → graph → model → eval）集成正确性的通用模式。
适用于研究项目（GNN、CV、NLP 等）首次连接所有模块时发现集成问题。

## 触发条件

- 多阶段管线首次端到端连接
- 各模块独立测试都通过但未一起跑过
- 用户说「看看代码结构和有效性」「跑一次试试」

## 核心流程

### 1. 用真实数据（小批量）

```python
# 不要用随机合成数据 — 需要真实的 shape/type/distribution 暴露集成问题
entries = load_raw_data(path, n=10)  # 小批量真实样本
```

### 2. 模拟上游输入（如 VLM 预测）

当上游模块（如 VLM）还不存在时，用 GT + 噪声模拟：

```python
# GT bbox + 加噪 → 模拟 VLM 输出
noise = torch.randn(4) * 0.03  # 3% 归一化噪声
vlm_bbox = [x1 + n[0], y1 + n[1], x2 + n[2], y2 + n[3]]
```

### 3. 验证中间数据结构

每个阶段之间打印关键信息：

```python
sample = dataset[0]
logger.info("Sample keys: %s", list(sample.keys()))

graph = builder.build(elements, constraints)
n_elem = graph["element"].x.shape[0]
n_con = graph["constraint"].x.shape[0]
n_edge = graph["element", "to", "constraint"].edge_index.shape[1]
logger.info("Graph: %d elements, %d constraints, %d edges", n_elem, n_con, n_edge)
```

### 4. 训练/推理

即使训练不收敛（初始权重）也要确认 forward+backward 不崩溃：

```python
for epoch in range(5):
    predictions = model(data)
    loss = compute_loss(predictions, targets)
    loss.backward()  # ✅ 确认梯度流通过所有层
    optimizer.step()
    logger.info("Epoch %d — loss: %.6f", epoch + 1, loss.item())
```

### 5. 基线对比

一定要跟简单基线比，验证 GNN 确实在工作（而非 nan/零输出）：

| 基线 | 说明 |
|------|------|
| NoOp | VLM 预测原样输出 — 最低上界 |
| Identity | 返回 GT — 理论上界 |
| RandomJitter | 随机扰动 — GNN 应优于随机 |

```python
noop_metrics = compute_all_metrics(noop_boxes, gt_boxes)
logger.info("NoOp metrics: %s", noop_metrics)
```

## 典型发现（Session 实战总结）

| 问题 | 表现 | 根因 |
|------|------|------|
| **Shape mismatch** | loss 报 `different size` | 模型输出 [N, 1]，target 构造为 [N] |
| **NaN loss** | loss: nan | 空约束图 → 对齐损失在空张量上计算 |
| **0 constraints** | 约束提取器不返回约束 | 数据太稀疏（每图 1-2 元素）→ 需要数据增强或更大样本 |
| **GNN 不如 NoOp** | baseline 指标更好 | 期望结果 — 随机初始化还没学到东西 |
| **device mismatch** | Tensor 跨设备错误 | 模型在 GPU 但 HeteroData 没移到 device |
| **collate 类型错** | `'element'` KeyError | dataset 输出 dict 但模型期望 HeteroData |

## 输出格式

确认每条管线组件用 ✅/❌ 标识，输出总结表：

```
Pipeline component          Status
──────────────────────────────────────
Data loading                ✅
Graph construction          ✅
Model forward               ✅
Loss computation            ✅
Backward + optimizer        ✅
Metrics                     ✅
Baseline comparison         ✅
```

## 不要做的事情

- ❌ 不要期待训练收敛（5 epoch 不可能）
- ❌ 不要花时间修复所有集成问题（先记录再分批修）
- ❌ 不要生成正式报告（结果只用于内部验证）
- ❌ 不要在复杂数据上跑（小批量足矣暴露问题）
- ❌ 不要跟随机数据混在一起（区分「数据问题」和「代码问题」）
