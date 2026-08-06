# Reviewer Comment Revision — 7-Comment Session Record (2026-08)

Session: final-report-summer-research-intern_comments.pdf (reviewer: Ahern Tang) → fix EN `report/main.tex` + CN `report-cn/main.tex` + poster.

## Extraction (fast path, verified)

```python
import fitz
doc = fitz.open(pdf_path)
for pno, page in enumerate(doc):
    for a in page.annots():
        print(pno + 1, a.type, a.info.get("content"), a.rect)
```

- `annot.info["content"]` = the comment text directly. No vision needed to read comments.
- Rect → text mapping is the fragile part: `page.get_textbox(a.rect)` failed (highlight quads span lines); word-bbox intersection too strict. **Do not loop page renders + vision to find the highlighted phrase** — present comment + page + rect coords as a table and let the user confirm anchors (user supplied the anchor table promptly).
- 7 comments on pages 3 (abstract + §1.1 + §1.2), 10 (Figure 4 area), 11 (Figure 5).

## The 7 comments and their fixes

| # | Comment | Fix |
|---|---------|-----|
| 1 | "In abstract part, you should avoids parentheses unless indicate the abbreviation." | Removed `(assistive tools for visually impaired users, automated UI testers, and software agents)` → comma apposition. Also removed `(real Android screenshots)` in abstract. |
| 2 | "Same as above." (on §1.1 `(such as Qwen3-VL Flash [1] and MiniMax-VL-01)`) | Parenthetical → comma apposition. |
| 3 | "'look at' seems a little bit colloquial, words like Interpret should be better." | `look at` → `interpret` (EN), 看 → 解读 (CN). |
| 4 | "For this specific 10-30% omission proportion, adding citation or some experimental results to support the claim will be better." | Claim was NOT supported by project data (measured 38%: 2947/4789 on 200 real RICO screenshots, `experiments/vlm_completion/pipeline_comparison.json`). Replaced 10–30% → 38% everywhere (abstract, §1.2, pipeline figure label, discussion, poster) + `\ref{sec:endtoend}` to the end-to-end experiment. Data-honesty rule applies to revision rounds too. |
| 5 | "A direct comparison of your method and the baseline should be moved to the first subsection in the experiment part." | Moved the End-to-End subsection (method vs baseline, Table + Fig) to §4.2 right after Experimental Setup. Python block move by `\subsection{...}` start/end markers; added `\label{sec:endtoend}`; LaTeX auto-renumbers; verify with `grep -n "subsection{"`. |
| 6 | "The y-axes have no labels. And the error bars seems only have the upper ones, usually it should has both upper and lower parts." | Figure 4 (training-objective ablation): added rotated y-axis titles (Violation accuracy / Proposal MSE) + tick marks with numbers; converted upper-only error bars to symmetric `{(v-std)*sc} -- {(v+std)*sc}` with caps at both ends. |
| 7 | "Same as above. Also, you should check your poster." | Figure 5 (element completion): 8 error bars → symmetric. Poster had the SAME bugs (same TikZ charts) → fixed poster too (both charts + the 10–30% text). |

## TikZ pitfalls hit this session

1. **`re.subn` line-join bug**: multi-line regex replacement whose last line lacks `\n` swallows the newline → `});    \fill[...]` glued on one line. Fix with a second pass:
   `re.subn(r'\}\);    (\\fill|\\node)', r'});\n    \1', src)` (indent varies: 4-space report, 8-space poster).
2. **Float formatting mismatch**: f-string exact match `f"({v}*\\sc...)"` renders `0.110` as `0.11` → no match. Use regex `[\d.]+` instead of exact strings.
3. **Backslash doubling through patch tool** is a known issue (see SKILL.md); verify single backslashes after edits (`od -c` / python repr). The pipeline-figure label fix silently produced 7 backslashes — caught by `git diff` + python `repr` check.
4. **Wrong tikzpicture block matched**: `\begin{tikzpicture}[xscale=2.2...]` appeared twice in poster (constraints-per-graph scatter AND completion chart). Locate blocks by content markers (e.g. `% grouped bars: 4 drop ratios`), not by header line alone.
5. **Vision verification**: full-page render at 100 dpi caused false negatives (reported "error bars still upper-only" when code was already symmetric). Crop the figure region + render at 200 dpi + ask per-bar questions → confirmed correct. Always re-verify with vision at adequate resolution before declaring done.

## EN ↔ CN lockstep

- Every EN fix mirrored in `report-cn/main.tex` (same TikZ numbers, Chinese labels).
- `read_file` misdetects UTF-8 Chinese `.tex` as binary → read via `python3` with line numbers instead; the patch tool itself works fine on CN files.
- CN abstract also had a non-abbreviation parenthetical (打分（真实还是幻觉）) — same reviewer rule applied.

## Compile verification

- EN: `xelatex -interaction=nonstopmode -halt-on-error` ×2 → 14 pages, 0 warnings.
- CN: same → 12 pages; TOC shows "4.2 真实VLM 输出的端到端实验" confirming renumber.
- Poster: lualatex → 1 page A0.
- Check `grep -c "^!" main.log` = 0 (per SKILL.md) and grep undefined refs.
