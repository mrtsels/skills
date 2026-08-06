# Image-based PDF Extraction

When a PDF is generated from Canva/PPTX/Keynote and contains only embedded images (no text layer):

## Detection

`read_file` on the PDF returns garbled/unreadable content. The `fitz` `page.get_text()` call also returns empty or minimal text.

## Extraction Pipeline

```python
import fitz

doc = fitz.open("document.pdf")
for i, page in enumerate(doc):
    pix = page.get_pixmap(dpi=300)
    pix.save(f"page_{i+1}.png")
    print(f"Extracted page {i+1}")
doc.close()
```

Then use `vision_analyze(image_url=f"path/page_{i+1}.png")` for each page.

## Cleanup

After extracting text, remove the temp PNGs:

```bash
rm page_*.png
```

## Better Approach for Multi-page

For 3+ pages, batch in a script:

```python
import fitz, time, json
from hermes_tools import terminal

doc = fitz.open("input.pdf")
for i, page in enumerate(doc):
    pix = page.get_pixmap(dpi=300)
    pix.save(f"/tmp/vision_page_{i+1}.png")
    # Then call vision_analyze on each via the tool interface
doc.close()
```

## Limitations

- Tables in the PDF may be misinterpreted by vision model
- Fine print (footnotes, legal disclaimers) may be missed at 300dpi
- Color-coded information may be lost if vision model describes in black/white terms
