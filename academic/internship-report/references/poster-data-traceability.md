# Poster 硬编码数据核查与复算（2026-08 实测案例）

poster.tex 的数据图没有生成脚本，数据硬编码在 TikZ 里。核查 = 在 `experiments/*.json` 找到权威数据并复算比对。

## 权威数据文件（bipartite-gnn-gui 仓库）

| 文件 | 内容 | 与 poster 图的对应 |
|------|------|-------------------|
| `experiments/vlm_completion/pipeline_per_image.json` | `before`/`after` 各 200 张，字段 `image_id, tp, fp, fn, precision, recall, f1, n_pred, n_gt` | missed-fraction 直方图（fn/n_gt 分桶） |
| `experiments/vlm_completion/per_image_results.json` | 32 张早期评估，字段 `n_gt, n_vlm, n_matched, n_missed, n_constraints, n_violated` | 约束数 vs 违反数散点图（32 点） |
| `experiments/ablation_results.json` | 6 组消融（config n=500 drop=0.6），字段 `avg_constraints_per_graph, violation_acc, ...` | 约束数量条形图（37.3/37.2/30.9/28.7/22.4/15.1） |

聚合数字核对：`pipeline_per_image.json` 的 sum(n_gt)=4789、sum(n_pred)=2947、sum(fn)=3663、sum(tp)=1126、sum(fp)=1821 —— 与报告完全一致才可信。

## 直方图复算（missed fraction = fn/n_gt）

```python
import json
d = json.load(open('experiments/vlm_completion/pipeline_per_image.json'))
before = d['before']
edges = [0.2, 0.4, 0.6, 0.8]
counts = [0]*5
for im in before:
    mf = im['fn']/im['n_gt'] if im['n_gt'] > 0 else 0.0
    idx = 4
    for i, e in enumerate(edges):
        if mf < e:          # 左闭右开; mf==1.0 归最后一桶
            idx = i
            break
    counts[idx] += 1
print(counts)   # [4, 12, 31, 59, 94] (旧 poster 硬编码 [4, 12, 36, 54, 94])
```

- 口径：fn/n_gt = 匹配失败率（中心距离 0.1 匹配，检测到了但框偏也算漏），逐图平均 76.5%；摘要里"38%"是未检测到口径 (1 - 2947/4789)。两者含义不同，写注释时标明。
- 桶边界试遍 [0.15~0.25]/[0.35~0.5]/[0.55~0.65]/[0.75~0.85] 组合都无法精确复现旧值 → 判定旧值为早期不同口径运行，诚实告知用户后重新生成。

## 散点图复算（32 点 r = 0.96）

```python
import json
d = json.load(open('experiments/vlm_completion/per_image_results.json'))
pairs = sorted((im['n_constraints'], im['n_violated']) for im in d)
# poster 硬编码点: \node[circle,...] at ({x*0.14},{y*0.16})  -> 原始值 (x, y)
poster_raw = [(11,10),(9,3),(24,20),(12,7),(16,15),(26,21),(5,0),(8,8),(21,16),(6,5),
              (21,16),(34,29),(23,15),(9,7),(32,20),(14,9),(9,3),(4,3),(28,23),(15,7),
              (13,9),(33,27),(5,5),(10,6),(2,0),(7,6),(10,9),(9,9),(15,12),(9,5),(5,0),(4,0)]
assert sorted(poster_raw) == pairs          # 逐点一致
# 相关系数
xs=[p[0] for p in pairs]; ys=[p[1] for p in pairs]; n=len(xs)
mx,my=sum(xs)/n,sum(ys)/n
r = sum((x-mx)*(y-my) for x,y in zip(xs,ys)) / (sum((x-mx)**2 for x in xs)*sum((y-my)**2 for y in ys))**0.5
print(f'{r:.4f}')   # 0.9604 ≈ poster 标注 0.96; OLS y=0.8299x-1.4884 (r^2=0.92)
```

## 更新 poster.tex 的写法

```latex
% 注释注明来源与口径（2026-08 用户接受的做法）
% Fraction of GT elements missed by the VLM, per screenshot (200 RICO;
% fn/n_gt with center-distance matching at 0.1, from
% experiments/vlm_completion/pipeline_per_image.json)
\foreach \i/\c/\t in {1/4/30,2/12/45,3/31/60,4/59/75,5/94/90} { ... }
```

替换后 `latexmk -lualatex poster.tex` 编译验证（exit 0 + PDF 生成；柱高随 \sc 自动适应，无需改 y 轴）。
