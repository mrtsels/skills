---
name: bilingual-resume
description: Design bilingual EN/ZH resumes sharing entries/
  files.
version: 0.3.0
author: Hermes
platforms: [macos]
metadata:
  hermes:
    tags: [LaTeX, XeLaTeX, CJK, Resume, Bilingual]
---

# Bilingual Resume (shared entries/ + \resumeenif)

Create a single `entries/` directory where each `.tex` file contains both English and Chinese content, gated by `\resumeenif{EN}{ZH}`. Two main documents (`resume-en.tex`, `resume-zh.tex`) compile from the same entries with separate cls files. This avoids compromising font size (10pt EN / 11pt ZH), `\ResumeItem` signature (5 vs 6 params), or CJK font setup.

## When to Use

- User wants to maintain EN and ZH resumes side by side without duplicating structure.
- User wants to add an entry once and have it appear in both language outputs.
- User asks for a bilingual resume folder.

## Prerequisites

- macOS, XeLaTeX, Songti SC font.
- Two separate cls files: `resume-en.cls` and `resume-zh.cls`, each with `\resumeenif` appended.

## Architecture: Two Separate cls Files

Do NOT merge EN and ZH into one bilingual cls. Use **two separate files**, each a verbatim copy of its respective template, with `\resumeenif` appended:

```latex
% resume-en.cls (appended at end)
\ExplSyntaxOn
\cs_set_eq:NN \resumeenif \use_i:nn    % picks first arg (EN)
\ExplSyntaxOff
```

```latex
% resume-zh.cls (appended at end)
\ExplSyntaxOn
\cs_set_eq:NN \resumeenif \use_ii:nn   % picks second arg (ZH)
\ExplSyntaxOff
```

### Why NOT a single bilingual cls

- **Different base font sizes**: EN uses 10pt, ZH uses 11pt (ctexart default).
- **Different `\ResumeItem` signatures**: EN has 5 params (two-line format), ZH has 6 params (one-line format with `【】` and supervisor field).
- **CJK dependencies**: ZH requires `SongtiBlack`, `PunctStyle=kaiming` — none of which should touch the EN compile.
- **`\ifresumeen` inside `\ProvidesExplClass`** renders both branches due to catcode changes. `\resumeenif` at the TeX level is safe.

### Entry File Pattern

Entry files use `\resumeenif{EN content}{ZH content}`:

```latex
\resumeenif{
  \ResumeItem{English Co.}[Role][Date][City]
  \begin{itemize}
    \item English bullet.
  \end{itemize}
}{
  \ResumeItem{中文公司}[岗位][日期][城市][导师信息]
  \begin{itemize}
    \item 中文bullet.
  \end{itemize}
}
```

### Bulk migration from `\ifresumeen` to `\resumeenif`

```bash
cd entries
sed -i '' 's/\\ifresumeen/\\resumeenif{/g; s/\\else/}{/g; s/\\fi/}/g' *.tex
```

After migration, always check `%` escaping (see Pitfalls).

## Setup Procedure (from existing EN + ZH resumes)

1. **Create directory**: `mkdir resume-alex/entries`
2. **Copy cls files** — verbatim from originals, with `\resumeenif` appended.
3. **Create bilingual entry files** with `\resumeenif` wrapping.
4. **Convert existing entries** with sed (see above).
5. **Write main tex files** — each uses its own cls.
6. **Compile both**:
   ```bash
   xelatex resume-en.tex && xelatex resume-en.tex
   xelatex resume-zh.tex && xelatex resume-zh.tex
   ```

## Chinese Content Guidelines

- **Bold verbs**: DO NOT bold opening verbs (`\item \textbf{Designed}` → `\item Designed`).
- **Conciseness**: Remove padding text a technical interviewer already knows. Cut `实现`, `用于`, `通过`, `产出报告` etc.
- **No em-dashes**: Never use `—` (EN) or `——` (ZH) in bullets. Replace with `:` (EN) or `，` (ZH).
- **Currency units**: `¥800M` → `8亿元`, `¥5B+` → `50亿元`.
- **Word order**: `60%缺失` → `缺失60%` (CN), `60% missing` (EN).
- **Skills alignment**: Use `\makebox[5em][l]` for CN labels, `\makebox[7em][l]` for EN.
- **Section order (ZH)**: 教育经历 → 实习经历 → 项目经历 → 技能.

### Bullet Compression (one-line per bullet)

For Chinese bullets, compress each `\item` to fit on **one PDF line** (~48 chars at 10pt / ~52 at 11pt, 1.5cm margins on A4). Visually verify after each compile.

**One-Line-or-Two-Line Rule**: When two adjacent bullets both wrap (~1.5 lines each), DO NOT leave them in that state. Pick the desired line count (1 or 2) and apply paired adjustments — cut one, add to the other. A 1.5-line bullet looks sloppy.

**User notation**: Edits as `#N +M -K` (add M / remove K chars from bullet N). These are additive relative to the current length.

**User notation**: Edits as `#N +M -K` (add M / remove K chars from bullet N). These are additive relative to the current length.

**Priority-ordered cuts (try in this order):**

1. **Inferable detail**: drop algorithm names (`Pearson`/`Ward`/`Engle-Granger`), bond codes (`GC001..GC014`), version numbers (`3.4`).
2. **Introductory verbs**: `产出报告指出` → `指出`, `构建系统用于` → `构建`, `完成赛道研究` → `研究赛道`.
3. **Redundant appellations**: `信号` (Z-score implies it), `Strassen算法` → `Strassen`, `配对交易系统` → `配对交易`.
4. **Merge clause chains**: `经Pearson相关矩阵、Ward层次聚类、Engle-Granger协整检验` → `经相关矩阵与协整`.
5. **Comparison fillers**: `较最近邻基线提升` → `较最近邻提升`, `较MongoDB加速` → `加速` when context is clear.
6. **Recursion/indirection**: `自适应` → drop, `递归调用` → `调用`, `约` → drop, `实现` → drop.
7. **Monetary unit mixing**: `¥800M` → `8亿元`, `¥5B+` → `50亿元`.

### Linespread Control (per-cls)

The EN cls sets `\linespread{1.0}`, ZH cls sets `\linespread{1.2}`. Override in main tex (not cls) when needed:

```latex
\linespread{0.95}   % place after \setlength{\parskip}{0pt}
```

For EN, `0.95` compresses 2→1 page for a full resume. For ZH at 11pt, `1.35` is the max for 1 page.

### The `%` Trap After sed Bulk-Edits

When running sed bulk-edits, the pattern can strip the backslash from `\%` characters. A bare `%` in LaTeX comments out the rest of the line. **Always run this check after any bulk edit:**

```bash
cd entries
grep -n '%' *.tex | grep -v '\\\\%'
```

Any matches are unescaped `%`. Fix them to `\%`.

## Maintenance Workflow

### Date Changes → Reorder Entries

When the user changes a date on any entry:

1. Update the date in BOTH the EN and ZH branches of the entry file.
2. Reorder all entries in that section by date (most recent first) in BOTH `resume-en.tex` and `resume-zh.tex`.
3. Compile both versions and confirm order visually. Follow the project's AGENTS.md if it has a date-sort rule.

### Contact Info Per Language

- **ZH version** (`resume-zh.tex`): use mainland China number (`86-...`).
- **EN version** (`resume-en.tex`): use Hong Kong number (`852-...`).
- Save personal contact info (phone, email) to USER memory with `memory(action='add', target='user')`.

### Linespread Tuning (batch test)

When asked to find the maximum linespread while keeping 1 page:

```bash
cd resume-alex
for val in 1.25 1.30 1.35 1.40; do
  sed -i '' "s/linespread{[0-9.]*}/linespread{$val}/" resume-XX.cls
  rm -f resume-XX.pdf
  xelatex -interaction=nonstopmode resume-XX.tex | grep "Output written"
done
```

Pick the highest value that still reports `(1 page)`. Reset the cls to that value afterward.

### Company Role Abbreviations

| Full | Abbreviation |
|------|-------------|
| 资产管理部实习 | 资管实习 |
| 解决方案研发部实习 | 研发实习 |
| 研发部实习 | 研发实习 |

### Project-Rule Placement

- Workflow rules (date sort, commit discipline, directory structure) → **AGENTS.md** in project root.
- Personal facts (phone numbers, preferences, identity) → **USER memory** via `memory(target='user')`.
- Never put project rules in memory or personal facts in AGENTS.md.

## Maintenance Workflow

### Date Changes → Reorder Entries

When the user changes a date on any entry:

1. Update the date in BOTH the EN and ZH branches of the entry file.
2. Reorder all entries in that section by date (most recent first) in BOTH `resume-en.tex` and `resume-zh.tex`.
3. Compile both versions and confirm order visually. Follow the project's `AGENTS.md` if it has a date-sort rule.

### Contact Info Per Language

- **ZH version** (`resume-zh.tex`): use mainland China number (`86-...`).
- **EN version** (`resume-en.tex`): use Hong Kong number (`852-...`).
- Save personal contact info (phone, email) to USER memory with `memory(action='add', target='user')`.

### Linespread Tuning (batch test)

When asked to find the maximum linespread while keeping 1 page:

```bash
cd resume-alex
for val in 1.25 1.30 1.35 1.40; do
  sed -i '' "s/linespread{[0-9.]*}/linespread{$val}/" resume-XX.cls
  rm -f resume-XX.pdf
  xelatex -interaction=nonstopmode resume-XX.tex | grep "Output written"
done
```

Pick the highest value that still reports `(1 page)`. Reset the cls to that value afterward.

### Company Role Abbreviations

| Full | Abbreviation |
|------|-------------|
| 资产管理部实习 | 资管实习 |
| 解决方案研发部实习 | 研发实习 |
| 研发部实习 | 研发实习 |

### Project-Rule Placement

- Workflow rules (date sort, commit discipline, directory structure) → **AGENTS.md** in project root.
- Personal facts (phone numbers, preferences, identity) → **USER memory** via `memory(target='user')`.
- Never put project rules in memory or personal facts in AGENTS.md.

## Pitfalls

- `main.tex` overrides `\linespread` and `\ctexset` set in `resume.cls`. Check lines 8-11 of main.tex when cls changes don't take effect.
- `\normalfont` after `\SongtiBlack` resets Black to Regular. Always omit `\normalfont` when using `\SongtiBlack`.
any sed bulk-edit, verify ALL `%` signs are `\\%`. Run `grep -n '%' entries/*.tex | grep -v '\\\\\\\\%'`.\n- **Bold verbs in ZH bullets**: `\\item \\textbf{设计}` is WRONG. Opening Chinese verbs are plain. Bold is for `【角色】` and company names only.\n- \\
- **Chinese tofu (boxes)**: Check `.log` for `fontspec Error: The font "Songti SC" cannot be found`. Use TTC file path + `FontIndex=0` for Black weight.
- **`\ifresumeen` inside `\ProvidesExplClass`** renders both branches. Only use `\resumeenif{}`.
- **Too-long bullets**: A bullet of ~50-60 chars at 11pt fits ~1 line; ~100-115 fits ~2 lines. 1.5-line bullets look uneven — fix them.

## Verification

```bash
cd resume-bilingual && xelatex resume-en.tex && xelatex resume-zh.tex
# Both should produce 1-2 page PDFs with no font errors
grep -c "error" resume-en.log resume-zh.log
# Should return 0 0
```
