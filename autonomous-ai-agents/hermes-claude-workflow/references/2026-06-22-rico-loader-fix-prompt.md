# RICO 加载器修复 Prompt (2026-06-22)

## 背景
rico_loader.py (PR #17) 基于文档假设写成，但实际 RICO 数据格式不同。

## 关键格式差异

| 字段 | 文档假设 | 实际数据 |
|------|---------|---------|
| `root` 位置 | 顶层 `root` | `activity.root` (VH) 或直接顶层 (Semantic) |
| `bounds` 类型 | 字符串 `"[x1,y1][x2,y2]"` | 数组 `[x1, y1, x2, y2]` |
| `screen_width/height` | 独立字段 | 从 `root.bounds[2]/[3]` 推导 |
| `content-desc` | 字符串 | 列表 `[null]` |
| `screen_id` | JSON 字段 | 从文件名推导 |
| `componentLabel` | 不存在 | Semantic 标注的关键字段（Icon/Text 等） |

## 修改的文件
- `src/bipartite_gnn_gui/data/rico_loader.py` — bounds 解析、root 定位、Semantic 格式
- `tests/test_data_rico.py` — 84 tests, 重写所有样本数据匹配实际格式
- `docs/requirements/gt_format.md` — §3.5 更新 JSON 示例和字段表
- `src/bipartite_gnn_gui/data/ground_truth.py` — 自动检测逻辑

## 验证
- 84 rico tests + 693 existing = 777 total, all pass
- 实测读取实际 RICO JSON: 22.4 元素/图，66K screenshots
