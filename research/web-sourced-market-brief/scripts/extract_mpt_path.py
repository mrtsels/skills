#!/usr/bin/env python3
"""Extract Atlanta Fed Market Probability Tracker data from the official xlsx.

Why not openpyxl: mpt_histdata.xlsx ships with a drawing reference that
openpyxl chokes on (KeyError: 'xl/drawings/drawing2.xml'). Parse the sheet
XML directly via zipfile + regex instead. ~86k rows parse in ~1s.

Download:
    curl -s -A "Mozilla/5.0" -o /tmp/mpt_histdata.xlsx \
      "https://www.atlantafed.org/-/media/Project/Atlanta/FRBA/Documents/cenfis/market-probability-tracker/mpt_histdata.xlsx"

Usage:
    python3 extract_mpt_path.py /tmp/mpt_histdata.xlsx [--ref 2026-12-16]

Outputs (to CWD unless --outdir):
    MPT_sofr_path.csv    — per reference window (12 quarterly contracts):
                           rate_mean / p25 / p75 (bp) + prob_hike / prob_cut (%)
    MPT_<ref>_dist.csv   — 25bp SOFR-band probability distribution for one window

Data layout (sheet3 = DATA, long format):
    A=date (shared string), B=reference_start (Excel serial → date),
    C=target_range (e.g. "350bps - 375bps"), D=field, E=value (shared string)
Fields: 'Rate: mean' | 'Rate: 25th percentile' | 'Rate: 75th percentile' |
        'Prob: hike' | 'Prob: cut' | 'Prob: <lo>bps - <hi>bps'
Hike-count derivation: avg SOFR ≈ target midpoint + ~2.5bp, so
hikes ≈ (path_rate − current_midpoint) / 25.
"""
import argparse
import datetime
import html
import re
import zipfile

FIELD_SET = {"Rate: mean", "Rate: 25th percentile", "Rate: 75th percentile",
             "Prob: hike", "Prob: cut"}


def ex_serial(n):
    return (datetime.date(1899, 12, 30) + datetime.timedelta(days=int(float(n)))).isoformat()


def load_rows(xlsx_path):
    z = zipfile.ZipFile(xlsx_path)
    ss = z.read("xl/sharedStrings.xml").decode("utf-8", "ignore")
    strings = [html.unescape(re.sub(r"<[^>]+>", "", s))
               for s in re.findall(r"<si>(.*?)</si>", ss, re.S)]
    data = z.read("xl/worksheets/sheet3.xml").decode("utf-8", "ignore")
    rows = []
    for _rno, cells in re.findall(r"<row[^>]*r=\"\d+\"[^>]*>(.*?)</row>", data, re.S):
        vals = {}
        for cm in re.finditer(r'<c r="([A-Z]+)\d+"([^>]*)>(?:<v>(.*?)</v>)?', cells):
            col, attrs, v = cm.group(1), cm.group(2), cm.group(3)
            if v is None:
                vals[col] = ""
                continue
            t = re.search(r't="(\w+)"', attrs)
            vals[col] = strings[int(v)] if t and t.group(1) == "s" else v
        rows.append(vals)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("xlsx")
    ap.add_argument("--ref", default=None, help="reference window (e.g. 2026-09-16) for band dist")
    ap.add_argument("--outdir", default=".")
    args = ap.parse_args()

    rows = load_rows(args.xlsx)
    last = sorted({r["A"] for r in rows if r.get("A") and r["A"] != "date"})[-1]
    print(f"MPT rows: {len(rows)}; last observation date: {last}")

    path = {}
    for r in rows:
        if r.get("A") == last and r.get("D") in FIELD_SET:
            key = ex_serial(r["B"])
            path.setdefault(key, {})[r["D"]] = r["E"]

    out = [f"# Atlanta Fed MPT — expected 3M avg SOFR by reference window (obs {last})",
           "reference_start,rate_mean_bp,rate_p25_bp,rate_p75_bp,prob_hike_pct,prob_cut_pct"]
    for k in sorted(path):
        p = path[k]
        out.append(f"{k},{p.get('Rate: mean','')},{p.get('Rate: 25th percentile','')},"
                   f"{p.get('Rate: 75th percentile','')},{p.get('Prob: hike','').strip()},"
                   f"{p.get('Prob: cut','').strip()}")
    with open(f"{args.outdir}/MPT_sofr_path.csv", "w") as f:
        f.write("\n".join(out) + "\n")
    print(f"wrote MPT_sofr_path.csv ({len(path)} windows)")

    if args.ref:
        buckets = []
        for r in rows:
            if r.get("A") == last and ex_serial(r["B"]) == args.ref:
                m = re.match(r"Prob: (\d+)bps - (\d+)bps", r["D"])
                if m:
                    buckets.append((int(m.group(1)), int(m.group(2)), float(r["E"])))
        buckets.sort()
        out = [f"# Atlanta Fed MPT — 3M avg SOFR band probabilities for {args.ref} (obs {last})",
               "sofr_band_bps,prob_pct"]
        for lo, hi, p in buckets:
            out.append(f"{lo}-{hi},{p:.2f}")
        with open(f"{args.outdir}/MPT_{args.ref}_dist.csv", "w") as f:
            f.write("\n".join(out) + "\n")
        print(f"wrote MPT_{args.ref}_dist.csv ({len(buckets)} bands, "
              f"sum {sum(p for _,_,p in buckets):.1f}%)")


if __name__ == "__main__":
    main()
