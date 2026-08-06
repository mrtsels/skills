# resume.cls v0.2 — Significant Changes from Upstream

## Font: Times New Roman via PostScript Name

Upstream uses `heiti` (ctex default Chinese sans-serif). We replaced it with
Times New Roman via fontspec. However, `ctexart` strips spaces from font names
during xeCJK init, so `\setmainfont{Times New Roman}` fails with
"Font 'TimesNewRoman' cannot be found."

**Fix:** Use PostScript names (no spaces):

```latex
\setmainfont{TimesNewRomanPSMT}[
  BoldFont = TimesNewRomanPS-BoldMT,
  ItalicFont = TimesNewRomanPS-ItalicMT,
  BoldItalicFont = TimesNewRomanPS-BoldItalicMT,
]
```

## Style Changes

| Aspect | Upstream | This version |
|--------|----------|-------------|
| Name | heiti LARGE | `\bfseries \MakeUppercase \LARGE` |
| Section headers | `\zihao{4} \heiti` (~14pt) | `\normalsize \bfseries \MakeUppercase` (~10pt) |
| Line spacing | `\linespread{1.15}`, parsep 0.20em | `\linespread{1.0}`, parsep 0.10em |
| Body font | ctex default (heiti) | Times New Roman (TimesNewRomanPSMT) |
