# Screenshot/Overlay Separation — 4-Canvas Layout (Pitfall 30)

User-mandated layout for the bipartite-gnn-gui web demo, after rejecting
boxes drawn on top of the screenshot:
> "你不要直接在截图上画框 你在截图旁边再开一个矩形 在上面画框"

## Final DOM structure (web/index.html)

```html
<div class="panel">
  <div class="panel-head"><span>VLM 检测</span><span class="tag red">红色框</span></div>
  <div class="canvas-box" id="boxLeft">
    <div class="cv-col">
      <div class="cv-label">截图</div>
      <canvas id="canvasLeft" width="300" height="500"></canvas>
    </div>
    <div class="cv-col">
      <div class="cv-label">检测框</div>
      <canvas id="canvasLeftOv" class="ov" width="300" height="500"></canvas>
    </div>
  </div>
</div>
<!-- Panel 2 identical with canvasRight / canvasRightOv -->
```

## CSS

```css
.canvas-box {
  display: flex; align-items: center; justify-content: center;
  gap: 14px; padding: 10px;
  height: min(62vh, 640px); min-height: 320px;
}
.cv-col { display: flex; flex-direction: column; align-items: center; gap: 6px; }
.cv-label { font-size: 11px; color: var(--muted); letter-spacing: 0.5px; }
.canvas-box canvas.ov { background: #1c1f33; }  /* dark bg for overlay */
```

## JS

```javascript
let ctxLeft  = canvasLeft.getContext('2d');
let ctxRight = canvasRight.getContext('2d');
let ctxLeftOv  = canvasLeftOv.getContext('2d');
let ctxRightOv = canvasRightOv.getContext('2d');

function sizeCanvases() {
  // contain-fit on screenshot aspect; apply SAME cssW/cssH to all four
  const scale = Math.min(boxW/iw, boxH/ih);
  const cssW = Math.max(1, Math.floor(iw*scale));
  const cssH = Math.max(1, Math.floor(ih*scale));
  ctxLeft   = setupCanvas(canvasLeft,   cssW, cssH);
  ctxRight  = setupCanvas(canvasRight,  cssW, cssH);
  ctxLeftOv = setupCanvas(canvasLeftOv, cssW, cssH);
  ctxRightOv = setupCanvas(canvasRightOv, cssW, cssH);
}

function drawLeft() {
  const T = getTransform(); if (!T) return;
  clearCanvas(ctxLeft); drawImageFit(ctxLeft, state.currentImage, T);  // clean image
  const ctx = ctxLeftOv;                                                // all boxes here
  clearCanvas(ctx);
  ctx.fillStyle = '#1c1f33'; ctx.fillRect(0, 0, ctx.canvas.clientWidth, ctx.canvas.clientHeight);
  if (!state.currentData) return;
  // ... red VLM strokes + red-X missed marks on ctx ...
}
// drawRight(): clean image on ctxRight; red+green+blue-dashed on ctxRightOv
```

Key invariant: `getTransform()` stays keyed to the screenshot canvas dims;
all four canvases share cssW/cssH so `mapBBox` maps identically everywhere.

## Verified

- `node --check` on extracted <script> passes.
- Browser screenshot confirms: image canvases have ZERO colored strokes;
  overlay canvases show red (VLM), green solid (GT matched), blue dashed
  (unmatched proposals) on dark bg with clear labels.
- Backend unchanged by this refactor (purely frontend layout); 942 pytest
  suite unaffected.
