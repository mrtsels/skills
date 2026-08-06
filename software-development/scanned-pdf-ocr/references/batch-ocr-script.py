#!/usr/bin/env python3
"""
Batch OCR all scanned PDFs in a directory tree using fitz + pytesseract.
Usage:
    python3 batch-ocr.py [--dpi 300] [--dir /path/to/pdfs]
"""

import fitz
from PIL import Image
import pytesseract
import io, os, sys, time, argparse

DPI = 300  # default

def ocr_pdf(pdf_path, md_path, dpi=DPI):
    """OCR a single PDF, save .md alongside. Returns (pages, chars)."""
    if not os.path.exists(pdf_path):
        return (0, 0)
    
    doc = fitz.open(pdf_path)
    if doc.needs_pass:
        print(f"  ⚠  SKIP (encrypted): {os.path.basename(pdf_path)}")
        doc.close()
        return (0, 0)
    
    total = len(doc)
    pages_text = []
    total_chars = 0
    start = time.time()
    
    for i in range(total):
        try:
            pix = doc[i].get_pixmap(dpi=dpi)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            text = pytesseract.image_to_string(img, lang='chi_sim+eng')
            
            if not text.strip():
                text = "[OCR: page is blank]\n"
            
            pages_text.append(f"--- 第{i+1}页 ---\n{text}")
            total_chars += len(text)
            elapsed = time.time() - start
            print(f"  ✓ page {i+1}/{total} | {len(text):5d} chars | {elapsed:.0f}s", end="\r")
            sys.stdout.flush()
        except Exception as e:
            pages_text.append(f"--- 第{i+1}页 ---\n[OCR ERROR: {e}]\n")
    
    doc.close()
    
    os.makedirs(os.path.dirname(md_path), exist_ok=True)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(pages_text))
    
    elapsed = time.time() - start
    print(f"\n  ✓ DONE — {total_chars:,} chars in {total} pages ({elapsed:.0f}s)")
    return (total, total_chars)


def main():
    parser = argparse.ArgumentParser(description="Batch OCR scanned PDFs")
    parser.add_argument("--dpi", type=int, default=300, help="Render DPI (default: 300)")
    parser.add_argument("--dir", required=True, help="Root directory containing PDFs")
    args = parser.parse_args()
    
    # Find all PDFs
    pdfs = []
    for root, dirs, files in os.walk(args.dir):
        for f in files:
            if f.lower().endswith(".pdf"):
                pdfs.append(os.path.join(root, f))
    
    pdfs.sort()
    print(f"Found {len(pdfs)} PDF(s). Processing at {args.dpi} DPI...\n")
    
    results = []
    total_p = total_c = 0
    
    for pdf_path in pdfs:
        md_path = pdf_path.rsplit(".pdf", 1)[0] + ".md"
        label = os.path.relpath(pdf_path, args.dir)
        print(f"--- {label} ---")
        p, c = ocr_pdf(pdf_path, md_path, args.dpi)
        results.append((label, p, c))
        total_p += p
        total_c += c
    
    # Summary
    print(f"\n{'='*70}")
    print(f"{'RESULTS':^70}")
    print(f"{'='*70}")
    for label, p, c in results:
        s = "OK" if p > 0 else "SKIP"
        print(f"  {s:6s} | {p:3d}p | {c:>8,}c | {label}")
    print(f"{'='*70}")
    print(f"  TOTAL: {total_p} pages, {total_c:,} chars")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
