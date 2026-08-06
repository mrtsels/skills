---
# PDF Processing Workflow — Batch Reference
# From: 多和美尽调材料 session, 2026-07-06
---

## End-to-End Batch Workflow (30+ PDFs)

The session processed 34 PDFs total: 13 scanned (OCR), 13 text-based (fitz), 8 table-heavy (pdfplumber). One encrypted (skipped).

### Step 1: Scan & Classify

```python
import fitz, os
pdfs = [p for p in os.listdir(".") if p.endswith(".pdf")]
for p in sorted(pdfs):
    doc = fitz.open(p)
    txt = sum(len(doc[i].get_text()) for i in range(min(3, len(doc))))
    imgs = sum(len(doc[i].get_images()) for i in range(min(3, len(doc))))
    tag = "TEXT" if txt > 50 else "SCAN"
    print(f"[{tag}] {len(doc):3g}p {p}")
    doc.close()
```

### Step 2: Process by Category

**Text PDFs** (contracts, performance reports):
```python
doc = fitz.open(pdf_path)
text = [f"--- Page {i+1} ---\n{doc[i].get_text()}" for i in range(len(doc))]
doc.close()
with open(md_path, "w") as f:
    f.write("\n\n".join(text))
```

**Scanned PDFs** (licenses, articles, audit reports):
```python
doc = fitz.open(pdf_path)
pages = []
for i in range(len(doc)):
    pix = doc[i].get_pixmap(dpi=250)
    img = Image.open(io.BytesIO(pix.tobytes("png")))
    text = pytesseract.image_to_string(img, lang='chi_sim+eng')
    pages.append(f"--- Page {i+1} ---\n{text}")
doc.close()
with open(md_path, "w") as f:
    f.write("\n\n".join(pages))
```

**Table PDFs** (valuation reports, NAV):
```python
with pdfplumber.open(pdf_path) as pdf:
    # Summarize: extract header, last-page summary, significant holdings
    p0 = pdf.pages[0].extract_text()
    last = pdf.pages[-1].extract_text()
    # Write summary markdown
```

### Step 3: Encrypted PDF Handling

The personal credit report was password-protected (qpdf --decrypt failed with common passwords). Skipped. If the user provides the password, re-run with `qpdf --decrypt --password=...`.

### Step 4: Move Misplaced Files

If subagents write .md files to the parent directory instead of subdirectories:

```bash
# Find wrong-location files
find . -name "*.md" -type f | while read f; do
  dir=$(dirname "$f")
  base=$(basename "$f")
  # Check if a subdirectory version exists
  sub=$(find "$dir" -maxdepth 2 -name "$base" | grep -v "^$f$" | head -1)
  if [ -n "$sub" ]; then
    echo "DUPLICATE: $f vs $sub"
    # Compare and keep better one
    sz1=$(wc -c < "$f")
    sz2=$(wc -c < "$sub")
    if [ "$sz1" -gt "$sz2" ]; then
      mv "$f" "$sub"  # replace with larger (likely better) version
    fi
  fi
done
```

### Step 5: Verify Completeness

```bash
find . -name "*.pdf" -type f | while read pdf; do
  md="${pdf%.pdf}.md"
  if [ ! -f "$md" ]; then
    echo "MISSING: $pdf"
  fi
done
```

### Classification Results (Session Reference)

| Category | Files | Process | Pages |
|----------|-------|---------|-------|
| Business licenses, disclosure (short) | 6 | OCR | 1-10p each |
| Articles of association | 2 | OCR | 10-23p |
| Internal policies (info-disclosure, risk-mgmt) | 2 | 1 OCR + 1 fitz | 6-8p |
| Audit reports (2022-2025) | 4 | OCR | 24-25p each |
| Fund contracts (5 products) | 5 | fitz extract | 99-109p each |
| Performance attribution / analysis | 6 | fitz extract | 5p each |
| Asset valuation sheets | 4 | pdfplumber | 15-79p |
| NAV tables (stamped) | 3 | fitz text + summary | 1p each |
| Level-4 valuation tables | 3 | pdfplumber | 52-322p |
| Financial report filing | 1 | pdfplumber | 2p |
| Personal credit report | 1 | ENCRYPTED, skipped | 3p |
