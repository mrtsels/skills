# Capability-Tab Frontend — Mode C (honest demo layout)

Session: bipartite-gnn-gui (2026-07), the "A plan" implementation. When the
user chose honesty over fake end-to-end numbers ("A"), the demo became three
tabs: end-to-end hero cases + two synthetic-benchmark capability panels.
This file records the frontend + API pattern that made it work, so a future
demo can reproduce it without re-deriving the layout.

## Tab structure

```html
<div class="tabs" id="tabs">
  <button class="tab-btn active" data-tab="e2e">端到端案例</button>
  <button class="tab-btn" data-tab="confidence">置信度打分</button>
  <button class="tab-btn" data-tab="completion">结构补全</button>
</div>
<div class="tab-panel active" id="tab-e2e">…hero-case canvases, legend, metrics…</div>
<div class="tab-panel" id="tab-confidence">…capability panels…</div>
<div class="tab-panel" id="tab-completion">…curve canvas…</div>
```

CSS: `.tab-panel { display:none }` / `.tab-panel.active { display:flex;
flex-direction:column; gap:12px }`; `.tab-btn.active` gets accent bg + white
text. The existing e2e content stays untouched inside its panel — wrapping it
in a div does not disturb the canvas/state code.

## Tab switch JS — lazy-load per panel

```javascript
tabsEl.addEventListener('click', (e) => {
  const btn = e.target.closest('.tab-btn');
  if (!btn) return;
  const tab = btn.dataset.tab;
  tabsEl.querySelectorAll('.tab-btn').forEach(b => b.classList.toggle('active', b === btn));
  Object.entries(tabPanels).forEach(([name, el]) => el.classList.toggle('active', name === tab));
  if (tab === 'confidence') loadConfidenceTab();
  if (tab === 'completion') loadCompletionTab();
  if (tab === 'e2e' && state.currentImage) { sizeCanvases(); drawBoth(); } // canvases hidden while in other tab
});

async function loadConfidenceTab() {
  if (grid.dataset.loaded) return;      // fetch once, never refetch on tab flips
  try {
    const resp = await fetch('/api/demo/confidence');
    …
    grid.dataset.loaded = '1';
  } catch (err) { grid.innerHTML = '<div class="cap-card" style="color:var(--amber)">…</div>'; }
}
```

Two details that matter:
- `dataset.loaded` guard — the panel fetch happens once; switching tabs
  again must not refetch or flicker.
- When the tab is hidden, `sizeCanvases()` reads `clientWidth` of hidden
  containers → 0. Re-running `sizeCanvases()+drawBoth()` on return to the
  e2e tab is required (or canvases come back blank/stale).

## Hand-drawn canvas line chart (no chart library)

```javascript
const W = cv.width, H = cv.height;              // fixed buffer 900×280
const padL = 44, padR = 14, padT = 16, padB = 30;
const x = (dr) => padL + ((dr - 0.2) / 0.6) * (W - padL - padR);
const y = (v)  => padT + (H - padT - padB) - (v / vMax) * (H - padT - padB);
// 1) grid: 4-5 horizontal lines + y labels (right-aligned, tabular)
// 2) per-run scatter: translucent 3px dots (rgba(color, 0.35)) — shows variance honestly
// 3) mean lines: GNN blue #4cc9f0, NN orange #ffa726, lineWidth 2
// 4) legend drawn in-canvas: '— GNN' / '— NN baseline'
// 5) x labels: 'drop 0.2' … centered under each tick
```

The per-run scatter is the honesty trick: mean lines alone hide the spread
(drop 0.6 GNN runs were 0.064/0.180 — a huge variance). Showing all runs as
dots makes the "GNN wins at high drop" claim visibly shaky-but-real.

## Honest annotation placement (part of the layout, not an afterthought)

```html
<div class="cap-note">   <!-- amber: the synthetic condition, stated up front -->
  <b>实验条件：</b>在 RICO 真值元素中混入随机 imposter 框（ratio 0.5）… 此任务在合成条件下验证。
</div>
…panels / curve…
<div class="cap-note muted" id="confRealNote"></div>  <!-- muted: real-data comparison -->
```

JS fills the muted note with the real-data numbers:
`真实数据对照：AUROC 仅约 0.60 … 该能力是"结构先验有效性"的方法学验证，不代表端到端精度。`

CSS: `.cap-note { color: var(--amber); background: rgba(255,200,87,0.08);
border: 1px solid rgba(255,200,87,0.25); }` and `.cap-note.muted { color:
var(--muted); background: var(--bg2); border-color: var(--border); }` — the
visual weight difference tells the reader "this is the real-data caveat".

## Backend: pre-computed demo endpoints

Serve static JSON/PNG from `demo_data/` — no model inference in the request
path. Each returns 404 with a runnable hint when assets are missing:

```python
@app.get("/api/demo/confidence")
async def demo_confidence():
    if not CONFIDENCE_DIR.is_dir():
        return JSONResponse({"error": "run scripts/prepare_confidence_demo.py"}, status_code=404)
    # aggregate per-image JSON (skip summary.json), return {summary, images}

@app.get("/api/demo/confidence/{img_id}")   # FileResponse for the overlay PNG
@app.get("/api/demo/completion")             # curve.json straight through
```

Guard rails:
- Skip `summary.json` when globbing image files.
- Verify with curl before browser testing; then click each tab and check
  console has zero JS errors (`browser_console`).
- If the user reports "没看到 tab / 界面没变化" but curl shows the new HTML:
  it's browser cache, not a code bug — add no-cache headers to the `/` route
  (see SKILL.md Pitfall 33) and hard-refresh (Cmd+Shift+R).
- Footer honesty line: `端到端：全量 200 图平均 F1 +1pp，精选案例展示最佳结果
  · 能力验证：合成条件（随机 imposter / 随机 drop）`.
