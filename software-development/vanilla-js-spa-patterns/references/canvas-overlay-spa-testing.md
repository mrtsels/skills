# Canvas-Overlay SPA: Mock-Backend Browser Smoke Test Recipe

Proven in session 2026-07-31 (dual-canvas GUI-GNN demo rewrite, backend hero-case API not
implemented yet). The whole render path — case list, dual-canvas drawing, metrics card,
upload success + 400 error — was verified without any real backend.

## Setup

```bash
cd web && python3 -m http.server 8899   # background process
# browser_navigate http://localhost:8899/index.html
```

With no backend, the page itself proves the error path: `/api/cases` 404 → error bar shows,
sidebar shows 暂无案例, `browser_console` reports `js_errors: []`. That alone validates the
graceful-failure design.

## Install mocks in page context (browser_console expression)

Run this as one `browser_console` expression, then trigger flows from later expressions.
`window.fetch` mock must return real `Response` objects so `.ok` / `.json()` behave.

```javascript
(() => {
  // 1) Generated test image — img.src loads bypass fetch, so subclass Image
  const c = document.createElement('canvas');
  c.width = 360; c.height = 640;
  const cx = c.getContext('2d');
  cx.fillStyle = '#223355'; cx.fillRect(0, 0, 360, 640);
  const dataUrl = c.toDataURL('image/jpeg', 0.8);
  const OrigImage = window.Image;
  class MockImage extends OrigImage {
    set src(v) { super.src = String(v).includes('/api/screenshot/') ? dataUrl : v; }
    get src() { return super.src; }
  }
  window.Image = MockImage;

  // 2) Mock API data (per contract: vlm_elements, proposals, metrics before/after)
  const caseData = { id: '10027', name: 'Weather App', img_w: 360, img_h: 640,
    vlm_elements: [{bbox: [0.05,0.05,0.45,0.12], label: 'text'}],
    proposals: [{bbox: [0.1,0.45,0.9,0.55], violation_score: 0.82}],
    gt_matches: [[0.1,0.6,0.45,0.7]],   // optional field → green GT-match layer
    metrics: { before: {detections:27,tp:22,fp:5,fn:50,precision:0.8152631,recall:0.3055555,f1:0.4444444},
               after:  {detections:38,tp:33,fp:5,fn:39,precision:0.8684210,recall:0.4583333,f1:0.6} } };

  const origFetch = window.fetch;
  window.fetch = (url, opts) => {
    const u = String(url);
    if (u === '/api/cases') return Promise.resolve(new Response(JSON.stringify([{id:'10027',name:'Weather App',metrics:caseData.metrics}]), {status:200,headers:{'Content-Type':'application/json'}}));
    if (u.startsWith('/api/case/')) return Promise.resolve(new Response(JSON.stringify(caseData), {status:200,headers:{'Content-Type':'application/json'}}));
    if (u === '/api/predict') return Promise.resolve(new Response(JSON.stringify({error:'VLM API key not configured...'}), {status:400,headers:{'Content-Type':'application/json'}}));
    return origFetch(url, opts);
  };
  return 'mock installed';
})()
```

## Assert canvas drawing by pixel counting

Sampling a single point is fragile (can land inside a box or on a dash gap). Count pixels
within a tolerance of the target stroke color over the whole canvas:

```javascript
const countColor = (ctx, target, tol) => {
  const img = ctx.getImageData(0, 0, ctx.canvas.width, ctx.canvas.height).data;
  let n = 0;
  for (let i = 0; i < img.length; i += 4) {
    const dr = img[i]-target[0], dg = img[i+1]-target[1], db = img[i+2]-target[2];
    if (dr*dr + dg*dg + db*db < tol*tol*3) n++;
  }
  return n;
};
// red VLM boxes [255,82,82], blue dashed [76,201,240], green GT [61,220,151], tol ~70
```

Per-layer pixel counts of a few thousand per box set confirm each layer actually drew.
Note `getImageData` reads device pixels — canvas.width already includes dpr.

## Assert upload flow

Create a `File` from a canvas blob and call the global upload handler directly:

```javascript
c.toBlob((blob) => {
  handleUploadFile(new File([blob], 'shot.png', {type: 'image/png'}));
});
// then after a delay: overlay hidden, metrics note shows VLM/GNN times, status line updated
```

For the error path, flip a flag so `/api/predict` returns 400 → expect: error bar with the
backend's `error` message verbatim, loading overlay hidden, metrics card hidden, and the
object-URL preview canvas still rendered (canvas size > 0).

## Keyboard / nav assertions

- Dispatch `new KeyboardEvent('keydown', {key:'ArrowRight', cancelable:true, bubbles:true})` and assert `ev.defaultPrevented === true`.
- Boundary buttons (prev at index 0) must be `disabled`.

## HTML hygiene checks (terminal)

```bash
# JS syntax — extract inline script, node --check
python3 -c "
import re
html = open('web/index.html', encoding='utf-8').read()
m = re.search(r'<script>(.*?)</script>', html, re.S)
open('/tmp/app.js','w',encoding='utf-8').write(m.group(1))
" && node --check /tmp/app.js

# Tag balance via HTMLParser (catches unclosed/mismatched tags)
python3 - <<'EOF'
from html.parser import HTMLParser
class C(HTMLParser):
    VOID = {'meta','link','br','img','input','hr','source','area','base','col','embed','track','wbr'}
    def __init__(self):
        super().__init__(); self.stack=[]; self.errs=[]
    def handle_starttag(self,t,a):
        if t not in self.VOID: self.stack.append(t)
    def handle_endtag(self,t):
        if t in self.VOID: return
        if not self.stack or self.stack.pop()!=t: self.errs.append('mismatch '+t)
    def close(self):
        super().close(); self.errs += ['unclosed '+t for t in self.stack]
c=C(); c.feed(open('web/index.html',encoding='utf-8').read()); c.close()
print('html balance:', 'OK' if not c.errs else c.errs)
EOF
```
