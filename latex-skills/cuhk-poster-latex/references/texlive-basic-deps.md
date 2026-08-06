# TeX Live basic (2026basic) — missing package install recipes

System `tlmgr install` fails on this machine: `/usr/local/texlive/2026basic/tlpkg/`
is not writable (no admin). Fix: install into the **user texmf tree**
`~/Library/texmf/tex/latex/<pkg>/`, which kpsewhich picks up automatically
(precedent: pgfplots already lives at `~/Library/texmf/tex/latex/pgfplots/`).

## General pitfalls

- **Direct CTAN `.sty` URLs can 404** on the tuna mirror even when the package
  exists. A 404 download silently writes an HTML error page — ALWAYS verify the
  file is real before using it:
  `head -3 <file>.sty` must NOT start with `<html>`.
- **Modern packages ship only `.tex` + `.ins`** (docstrip source), no ready
  `.sty` (e.g. changepage, type1cm). Two working ways to get the `.sty`:
  1. `lualatex -interaction=nonstopmode <pkg>.ins` in the unpacked dir, then
     copy the generated `.sty`. (Fails if the `.ins` itself needs a missing
     package — see changepage below.)
  2. Extract from the `filecontents` block in the `.tex` with Python:
     ```python
     import re
     t = open('changepage.tex').read()
     m = re.search(r'\\begin\{filecontents\}\{changepage\.sty\}(.*?)\\end\{filecontents\}', t, re.S)
     open('changepage.sty','w').write(m.group(1))
     ```
     (careful: `\e` etc. are invalid regex escapes — use raw string + a script
     file, not `python -c`.)

## Packages installed (all to ~/Library/texmf/tex/latex/)

| Package | Method |
|---|---|
| beamerposter | `curl -sL https://mirrors.tuna.tsinghua.edu.cn/CTAN/macros/latex/contrib/beamerposter/beamerposter.sty` (direct .sty works) |
| anyfontsize | same pattern: `.../contrib/anyfontsize/anyfontsize.sty` |
| type1cm | zip `.../contrib/type1cm.zip` → unpack → `lualatex type1cm.ins` → copy type1cm.sty |
| changepage | zip `.../contrib/changepage.zip` → unpack → `.tex` contains filecontents block → extract with Python (see above); `lualatex changepage.ins` fails because the .ins needs filecontents.sty which is missing |

## Fonts (gemini theme: Raleway + Lato)

The template's `beamerthemegemini.sty` uses:
`\newfontfamily\Raleway{...}` + `\setsansfont{Lato}[UprightFont=*-Light,...]`.
Missing fonts → lualatex error `fontspec: The font "Raleway" cannot be found`.

- **font-raleway cask quirk**: `brew install --cask font-raleway` downloads to
  `/opt/homebrew/var/homebrew/tmp/.caskroom/font-raleway/<ver>/` but does NOT
  install into `~/Library/Fonts` (files remain in the caskroom temp dir).
  Fix: manually copy the static TTFs:
  `cp "/opt/homebrew/var/homebrew/tmp/.caskroom/font-raleway/<ver>/Raleway-<ver>/static/TTF/"*.ttf ~/Library/Fonts/`
  (only TTF works with fontspec; WOFF/WOFF2 files in the same tree do not).
- **font-lato cask is broken** (latofonts.com returns 403). Download static
  TTFs from google/fonts GitHub raw instead:
  ```
  for f in Lato-Light Lato-LightItalic Lato-Regular Lato-Italic; do
    curl -sL "https://github.com/google/fonts/raw/main/ofl/lato/$f.ttf" -o ~/Library/Fonts/$f.ttf
  done
  ```
  (The gemini theme only needs Light/LightItalic/Regular/Italic variants.)
- After adding fonts, if luaotfload still can't see them:
  `luaotfload-tool --update` (fonts in `~/Library/Fonts` are found by default).

## Verification

- `lualatex -interaction=nonstopmode poster.tex` → `grep -c "^!" poster.log` = 0
  AND `grep "Output written" poster.log` shows the PDF. lualatex can exit 1
  while still writing a PDF — check the log, not just exit code.
- `grep -c "adjustwidth" changepage.sty` > 0 proves the changepage extraction worked.
