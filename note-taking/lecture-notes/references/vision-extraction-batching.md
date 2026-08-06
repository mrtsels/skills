# Vision Extraction Batching for PDF Slides

When PyMuPDF `get_text()` returns little content (slide-type PDF with images/charts instead of text), use vision extraction.

## Setup

```python
import fitz, os

doc = fitz.open("Lecture N.pdf")
os.makedirs("frames", exist_ok=True)
for i, page in enumerate(doc):
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x for readable text
    pix.save(f"frames/page_{i+1:02d}.png")
print(f"Done: {len(doc)} pages")
```

## Extraction Pattern

Batch 5 pages per turn (concurrent vision_analyze calls):

```
vision_analyze(image_url="frames/page_01.png", question="Extract all text...")
vision_analyze(image_url="frames/page_02.png", question="Extract all text...")
...
vision_analyze(image_url="frames/page_05.png", question="Extract all text...")
```

Question template:
```
"Extract all text from this lecture slide page. Include slide title, bullet points, code, formulas, and any visual elements. Be precise."
```

## Post-Extraction Processing

- Combine slide 1 (title page) → header info (lecturer, version, pages)
- Combine TOC slides (often slide 2) → table of contents structure
- Section header slides (single line like "Trading Strategies") → section dividers
- Content slides → structured notes per topic

## Cleanup

```bash
rm -rf frames/
```
