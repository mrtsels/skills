#!/usr/bin/env python3
"""
Batch classify PDFs in a directory for extraction strategy.
Outputs: classify | pages | text | imgs | strategy | size | preview

Usage:
    python batch-classify.py /path/to/pdfs
"""
import fitz, os, sys

def classify(pdf_path):
    doc = fitz.open(pdf_path)
    n = len(doc)
    total_text = sum(len(doc[i].get_text()) for i in range(min(3, n)))
    total_imgs = sum(len(doc[i].get_images()) for i in range(min(3, n)))
    p0 = doc[0].get_text()[:80].replace('\n', ' ').strip()
    doc.close()
    if doc.needs_pass:
        return "ENCRYPTED", n, 0, 0, 0, p0
    if total_text > 50:
        return "TEXT", n, total_text, total_imgs, 0, p0
    if total_imgs > 0:
        return "SCAN", n, total_text, total_imgs, 0, p0
    return "BLANK?", n, total_text, total_imgs, 0, p0

root = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()

print(f"{'Strategy':10s} {'Pages':6s} {'Text':8s} {'Imgs':5s} {'Size':10s}  Preview")
print(f"{'-'*10} {'-'*6} {'-'*8} {'-'*5} {'-'*10}  {'-'*60}")

pdfs = []
for dirpath, _, files in os.walk(root):
    for f in sorted(files):
        if f.lower().endswith('.pdf'):
            pdfs.append(os.path.join(dirpath, f))

for p in sorted(pdfs):
    strat, pages, text, imgs, _, preview = classify(p)
    size = os.path.getsize(p)
    rel = p.replace(root, '').lstrip('/')
    print(f"{strat:10s} {pages:6d} {text:8d}B {imgs:5d} {size:>8d}B  {rel[:70]:70s}")
