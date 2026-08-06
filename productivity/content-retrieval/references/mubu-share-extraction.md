# Mubu (幕布) Share Page Content Extraction

Mubu (幕布) is a popular Chinese outlining/mindmap service. Shared documents render as web pages that are fully visible to unauthenticated users, but the content is rendered dynamically via JavaScript — it won't appear in the raw HTML source.

## Technique: Browser Console Extraction

Mubu share pages load the full document content into the DOM even for anonymous viewers. Extract it with:

### Quick extraction (flattened text)

Open the share URL in the browser tool, then:

```javascript
// Get ALL visible text from the page
document.querySelector('*').innerText
```

This returns a flat text dump. Useful for getting the gist, but loses outline hierarchy.

### Tree walker (better for structured content)

```javascript
(() => {
  const texts = [];
  const walker = document.createTreeWalker(
    document.body, NodeFilter.SHOW_TEXT, null, false
  );
  let node;
  while (node = walker.nextNode()) {
    const t = node.textContent.trim();
    if (t && t.length > 2) {
      // Filter out UI chrome (login buttons, nav text, etc.)
      const noise = ['幕布', '登录', '验证码', '注册', '思维导图', '立即加入'];
      if (!noise.some(n => t.includes(n))) {
        texts.push(t);
      }
    }
  }
  return texts.join('\n');
})()
```

### Full page snapshot (when browser_snapshot truncates)

```javascript
// First scroll down to lazy-load any off-screen content
// Then grab all text
document.body.innerText
```

Note: Mubu login wall covers the bottom of the page, not the document content. The document body is fully rendered. The `innerText` approach should capture everything.

## Limitations

- **No hierarchy recovery** — Mubu renders all nodes as flat divs. Outline depth (parent/child relationships) is not preserved in text extraction. You must reconstruct the structure manually.
- **Scrolling may be needed** — if the document is long, some nodes may be lazy-loaded. Scroll first, then extract.
- **Login-only content** — some Mubu documents restrict full content to logged-in users. The share preview may only show the top-level headings. If the extracted content looks truncated (e.g., only section headers, no body text), the document probably requires login.

## Reconstructing Structure from Flat Text

Mubu's outline uses indentation levels. After extracting flat text:

1. Group related items by topic context (they appear in order)
2. H1 = document title / section header
3. H2 = subsections
4. H3+ = detailed content under subsections
5. Numbered references (1️⃣, 2️⃣, etc.) indicate ordered steps

## API approach (when browser is not available)

The Mubu API requires authentication headers. Anonymous API calls return `{"code": 17, "msg": "illegal request"}`. The share page's `window.PRELOADED_DATA` is empty `{}` for share views — content is loaded dynamically via WebSocket.

**Conclusion**: browser console extraction is the only reliable method for anonymous access.
