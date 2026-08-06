# CUHK Poster Template — 本机依赖与编译（2026-08 实测）

模板仓库：https://github.com/zyzheng17/CUHK-Poster-Template（clone 到 `~/CUHK-Poster-Template/`）
编译：`make`（内部是 `latexmk -pdflatex='lualatex -interaction nonstopmode' -pdf poster.tex`）。lualatex 与 latexmk 都在 `/Library/TeX/texbin/`。

## 缺失依赖清单（TeX Live basic 环境）

`poster.tex` → gemini 主题 → 需要这些包和字体。系统 tlmgr 无写权限
（`/usr/local/texlive/2026basic/tlpkg/` 只读），全部装到**用户 texmf** `~/Library/texmf/tex/latex/`，无需 sudo。

| 依赖 | 安装方式（实测成功） |
|---|---|
| `beamerposter.sty` | `mkdir -p ~/Library/texmf/tex/latex/beamerposter && curl -sL "https://mirrors.tuna.tsinghua.edu.cn/CTAN/macros/latex/contrib/beamerposter/beamerposter.sty" -o .../beamerposter.sty`（单文件直下） |
| `anyfontsize.sty` | 同上，`.../contrib/anyfontsize/anyfontsize.sty`（单文件直下） |
| `type1cm.sty` | **没有单文件直下**（404）：下载 `.../contrib/type1cm.zip`，unzip 后目录里是 `.ins/.fdd`，`cd <dir> && lualatex -interaction=nonstopmode type1cm.ins` 生成 `.sty` |
| `changepage.sty` | **同样无单文件**：下载 `.../contrib/changepage.zip`，解出 `changepage.tex`（新版用 `filecontents` 包 .sty），用 Python 正则提取 `\begin{filecontents}{changepage.sty}...\end{filecontents}` 块写成 .sty，或 lualatex 跑 .ins（会因缺 filecontents.sty 报错，Python 提取更稳） |
| Raleway 字体 | `brew install --cask font-raleway` 可装，但字体落在 caskroom 缓存而非 Fonts 目录：`/opt/homebrew/var/homebrew/tmp/.caskroom/font-raleway/<ver>/Raleway-<ver>/static/TTF/*.ttf` → `cp` 到 `~/Library/Fonts/`（注意用 static/TTF，woff 是网页格式 fontspec 不认） |
| Lato 字体 | `brew install --cask font-lato` **失败**（源站 latofonts.com 403）。改用 google/fonts GitHub raw：`https://github.com/google/fonts/raw/main/ofl/lato/Lato-{Light,LightItalic,Regular,Italic}.ttf` → `~/Library/Fonts/`（模板 `\setsansfont{Lato}` 用 `*-Light/Regular/Italic` 命名，这四个字重必须有） |

验证：`luaotfload-tool --update` 刷新字体缓存；`fc-list | grep -i raleway/lato` 确认。

## 编译验证

```bash
cd ~/CUHK-Poster-Template
lualatex -interaction=nonstopmode poster.tex   # 0 errors, Output written on poster.pdf (1 page, A0)
pdftoppm -png -r 50 poster.pdf /tmp/poster_preview   # + vision 检查：紫标题栏/logo/两栏/表格/TikZ/公式/页脚
```

判断成败：`grep -c "^!" poster.log` 应为 0（nonstopmode 下 exit code 不可靠，同 xelatex 教训）。
`make clean` 后残留 `poster.nav`/`poster.snm` 未进 .gitignore，手动 `rm`。

## 模板要点

- 标题栏：`\title/\author/\institute` + `\logoleft`；`\footercontent` 可整个去掉
- 配色（beamercolorthemecuhk.sty）：cuhk-purple RGB(117,15,109) 标题栏/block 标题，orange 高亮
- 两栏：`\colwidth=0.45\paperwidth`；三栏改 `0.32` 且 `\sepwidth=0.01\paperwidth`
- **2→3 栏重排实测坑**：patch 逐段挪 block 时在 block 3 后、block 5 后各插了一次 `\end{column}\separatorcolumn\begin{column}`，结果 4 个 column → `Overfull \hbox (789.65pt too wide)`、右栏被挤出画布。修复 = 删掉多余的分隔块让 block 4+5 同栏。**核对命令**：`grep -n "begin{column}\|end{column}\|separatorcolumn" poster.tex`，3 栏应 3 begin + 4 separator
- 正文 block：`block` / `alertblock`（高亮）/ `exampleblock`（灰底）/ `\heading`（块内小标题）
- 参考文献：`\nocite{*}` + `\bibliography{poster}`；**必须完整链 lualatex → bibtex → lualatex ×2**，缺一轮 .bbl 不生成、References 空白（`pdftotext poster.pdf - | grep -c "^\["` 应为 14）。poster.bib 可直接 cp report/references.bib
