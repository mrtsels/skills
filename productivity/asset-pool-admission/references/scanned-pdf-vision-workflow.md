# Scanned PDF → Vision OCR Workflow

When a PDF has no extractable text layer (all pages are images/scans), tesseract OCR is an option but vision_analyze often produces cleaner results for structured slides/presentations.

## Workflow

### Step 1: Render PDF to images

```python
import fitz, os

out_dir = "/path/to/tmp/pages"
os.makedirs(out_dir, exist_ok=True)

doc = fitz.open("/path/to/file.pdf")
for i in range(len(doc)):
    mat = fitz.Matrix(3, 3)  # 216-300 DPI (3x works well)
    pix = doc[i].get_pixmap(matrix=mat)
    pix.save(os.path.join(out_dir, f"page_{i+1:02d}.png"))
```

### Step 2: Read each page with vision_analyze

Batch independent pages in parallel:

```python
# In terminal/eshell: call vision_analyze for each page
# Group 5 pages per batch for efficiency
vision_analyze(image_url="page_01.png", question="Read ALL text.")
vision_analyze(image_url="page_02.png", question="Read ALL text.")
# ... up to 5 per batch (independent calls)
```

### Step 3: Compile notes

Extract key data points from each page's vision output:
- Company name, registration number, founding year
- Core team backgrounds
- Strategy descriptions
- Performance metrics (annualized return, Sharpe, max drawdown, win rate)
- Product elements (management fee, performance fee, lock-up period)
- Partner/custodian institutions

### Limitations

| Aspect | Note |
|--------|------|
| Pages per batch | 5 per turn (independent vision_analyze calls) |
| Total page limit | ~25-30 pages per session before hitting context constraints |
| Image clarity | 3x matrix (216 DPI) is minimum. For dense tables or small fonts, increase to 4x |
| Table extraction | vision_analyze reads tables as text — for complex tables with many columns, mention "Read the table row by row" in the question |
| Handwriting | Not reliable. Skip handwritten annotations |

### When to use vs tesseract

| Criteria | Use Vision | Use Tesseract |
|----------|-----------|---------------|
| Presentation slides with clean text | ✅ Fast, good | ✅ But slower setup |
| Dense text pages (books, reports) | ❌ Too many pages | ✅ Batch OCR |
| Tables with numbers | ⚠ OK for simple tables | ✅ Better for structured tables |
| Chinese-only content | ✅ Good | ✅ Good (chi_sim) |
| Mix of text and charts | ✅ Reads chart labels | ❌ Only reads text |
| Under 15 pages | ✅ | ⚠ Overhead not worth it |
