---
name: bilingual-latex-resume
description: Iterate bilingual LaTeX resumes with GIT workflow.
version: 0.1.0
author: Hermes
---

# Bilingual LaTeX Resume Workflow

Maintain Chinese and English versions of a resume from shared entry files. Each entry uses `\resumeenif{EN content}{ZH content}` to hold both languages in one `.tex` file. Two separate `.cls` files (`resume-en.cls`, `resume-zh.cls`) handle language-specific formatting. Compile with `xelatex` ×2 per language.

## When to Use

- "Make a Chinese version of my resume"
- "Add/adjust bullets in the bilingual resume"
- "Trim/fill resume bullets to fit one line"
- "Add/remove N characters from bullet"
- "Balance bullet lengths across entries"
- "Test linespread values"
- The user says `+N`, `-N` on a bullet reference — means add/remove N characters

## Prerequisites

- macOS with `xelatex` (TeX Live) and `Songti SC` system font.
- Existing bilingual resume structure: `resume-en.cls`, `resume-zh.cls`, entries/ with `\resumeenif{}`.
- `resumes-git-workflow` skill loaded for automatic commit+push after each `.tex` edit.

## How to Run

```bash
cd resume-alex/ && rm -f *.pdf && xelatex resume-en.tex && xelatex resume-en.tex
xelatex resume-zh.tex && xelatex resume-zh.tex
```

Then show the PDF with `vision_analyze` or `qlmanage` thumbnail. Commit after each group of changes.

## Procedure

### 1. Load Required Skills

Always load `resumes-git-workflow` at the start so every `.tex`/`.cls` change is auto-committed and pushed.

### 2. Read the Entry File

Use `read_file` on the specific entry (e.g. `entries/internships-yuecai.tex`). Identify whether the user wants EN or ZH adjustments — the ZH branch is inside `\resumeenif{...}{ZH branch here}`.

### 3. Apply Character Count Edits

When the user says `#N +M`, `#N -M` (bullet N, add/remove M chars):

- Count characters with `python3 -c 'print(len("..."))'` using the raw string from the file.
- Find cuttable filler: removed `的`, `了`, `进行`, `实现`, `使用`, `完成`, `通过`, `以`, `与`, `在`, `来` as well as redundant `算法`, `模型`, `技术`, `系统`, `测试`, `数据`, etc.
- CV-safe cuts preserve: company names, tech stack names, metric numbers, domain terms, action verbs.

For `+N` edits, add back detail that was previously cut: qualifiers (`详细`, `完整`), context (`在...上`, `用于...`), explicit verbs (`实现`, `完成`, `构建`), or explanatory nouns (`测试`, `分析`, `方案`, `模型`, `方法`).

### 4. Compile and Verify

```bash
cd resume-alex/ && rm -f resume-en.pdf && xelatex -interaction=nonstopmode resume-en.tex | tail -3 && xelatex -interaction=nonstopmode resume-en.tex | tail -3
```

Repeat for `resume-zh.pdf`.

Check `Output written on ...pdf (N page(s)).` — if N jumps from 1 to 2, revert or trim more.

### 5. Show PDF

```bash
qlmanage -t -s 1200 -o /tmp/ resume-alex/main.pdf
```

Then `vision_analyze` the thumbnail at `/tmp/main.pdf.png` with a targeted question.

### 6. Commit Changes

`resumes-git-workflow` auto-commits. If not loaded, commit manually:

```bash
git add -A && git commit -m "feat: adjust zh bullets n char" && git push
```

## Pitfalls

- **Bare `%` in LaTeX**: In entry `.tex` files, every `%` outside math mode must be `\%`. Forgetting this truncates the rest of the line silently. Always escape `%` in Chinese bullets (`60%` → `60\%`, `94%` → `94\%`).
- **Linespread in zh.cls > 1.35 breaks 1 page**: At 11pt with 1.5cm margins, `\linespread{1.35}` is the maximum that fits content on 1 page. Higher values push to 2 pages.
- **Character counts are approximate**: Mixed CJK/Latin content renders at different widths. A bullet of ~50-60 chars at 11pt fits approximately one line; ~100-115 fits approximately two lines.
- **`\ifresumeen` does not work inside `\ProvidesExplClass`**: Use `\bool_new:N` with `\bool_if:NTF` or the `\resumeenif` wrapper instead. Never use raw `\ifresumeen...\else...\fi` in a LaTeX3 class.
- **Sed replacement of `\ifresumeen`**: When converting entries from `\ifresumeen...\else...\fi` to `\resumeenif{}{}`, use `sed -i '' 's/\\ifresumeen/\\resumeenif{/g; s/\\else/}{/g; s/\\fi/}/g'`.
- **Company full names**: When asked to use full legal names, verify via the company website's title/copyright info, not guess. Common patterns: `Domain Co., Ltd.` → `XX有限公司`, `Corp., Ltd.` → `XX股份有限公司`.

## Verification

All four PDFs compile cleanly to 1 page each: `resume-alex/resume-en.pdf`, `resume-alex/resume-zh.pdf`, `resume-bilingual/resume-en.pdf`, `resume-bilingual/resume-zh.pdf`. Check with `grep "Output written on" *.log` in each project dir.
