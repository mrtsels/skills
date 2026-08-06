# LaTeX Resume-NG Formatting Guide

When using the `resume-ng` LaTeX class (fky2015/resume-ng variant), these are the formatting conventions:

## \ResumeItem 5-Parameter Macro

```
\ResumeItem[bookmark]{title}[subtitle][date][location]
```

- **Line 1**: `\textbf{title}` (bold, left) + `\textit{location}` (italic, right)
- **Line 2**: `\textit{subtitle}` (italic, left) + `date` (roman, right)
- 0.15em vspace between entries

## Visual Specs

| Element | Value |
|---------|-------|
| Name | 18pt bold ALL CAPS |
| Section headers | 11pt bold ALL CAPS + hrule, beforeskip=0.5em |
| Body | 10pt, \linespread{1.0} |
| Font | Times New Roman (PostScript: TimesNewRomanPSMT) |
| Bullet indent | leftmargin=1.8em, labelsep=0.5em |
| Margins | A4, 1cm all sides |

## Dependencies

TeXLive packages: `ctex`, `enumitem`, `footmisc`, `xcolor`, `xeCJKfntef`, `fontspec`, `latexmk`
