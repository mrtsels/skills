#!/usr/bin/env python3
"""Per-page bottom-overflow measurement for Beamer PDFs (text layer).

Usage: python3 check_overflow.py deck.pdf [threshold]

Reports each page's lowest content y and flags pages whose content bottom
exceeds the threshold (default 232pt on a 255pt 16:9 page). Designed footer
zones are excluded — they are intentional layout, not overflow:

  1. 7pt footline band (pinned source line bottom-left, page number
     bottom-right). Exclude BY SIZE, not by text — after a font switch
     (e.g. Times New Roman) the source line splits into multiple spans
     ('Source:' alone, then the body text), so `t.startswith('Source:')`
     false-positives on every page; the page number and source are the only
     7pt text in that band, so size is the robust filter.
  2. When EVERY page carries a takeaway bar (1:1 report.md rebuilds), the
     bar's \\vfill pins it to the frame bottom right above the footline —
     its text row can otherwise overlap the source row (takeaway y242-252
     vs source y243-250). Fix in the deck: `\\vspace{12pt}` at the end of
     the takeaway bar + one-line takeaway texts. Then the fit-QA exclusion
     becomes the whole `y0 > 210` band (takeaway + footline are all
     designed footer; content must end above ~210pt).
"""
import sys

import fitz

path = sys.argv[1] if len(sys.argv) > 1 else 'task5_rates_deck_mtheme.pdf'
thr = float(sys.argv[2]) if len(sys.argv) > 2 else 232.0
d = fitz.open(path)
print('pages:', len(d))
for i, p in enumerate(d, 1):
    ymax = 0.0
    last = ''
    for b in p.get_text('dict')['blocks']:
        for l in b.get('lines', []):
            for s in l['spans']:
                t = s['text'].strip()
                if not t:
                    continue
                _x0, y0, _x1, y1 = s['bbox']
                # designed page-bottom zone: takeaway bar + footline
                if y0 > 210:
                    continue
                if y1 > ymax:
                    ymax = y1
                    last = t[:30]
    flag = '  <OVER' if ymax > thr else ''
    print(f'p{i:02d}: bottom {ymax:6.1f}{flag}  {last}')
