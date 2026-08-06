---
name: overleaf-guide
description: "Work with Overleaf end-to-end — CLI sync via Git bridge, multi-author collaboration, and compilation debugging."
metadata:
  openclaw:
    emoji: "💻"
    category: "tools"
    subcategory: "code-exec"
    keywords: ["Overleaf", "LaTeX", "CLI", "sync", "git", "collaboration", "academic writing"]
    source: "https://github.com/overleaf/overleaf"
---

# Overleaf CLI Guide

Sync, manage, and automate Overleaf LaTeX projects from the command line. Work in your preferred local editor while keeping Overleaf as the collaboration and compilation hub for your research team.

## Overview

Overleaf is the dominant online LaTeX editor in academia, used by millions of researchers for collaborative paper writing. However, many researchers prefer local editors (VS Code, Neovim, Emacs) for their superior editing capabilities, version control integration, and ability to run custom scripts. The Overleaf CLI bridge enables a hybrid workflow: edit locally with full tooling, then sync changes to Overleaf for collaboration and compilation.

This skill covers three approaches to Overleaf CLI integration: Overleaf's built-in Git bridge (available on paid plans), the open-source `overleaf-sync` tool (works with free plans), and direct API interaction. Each approach has different trade-offs in terms of cost, features, and reliability.

Beyond simple sync, this guide covers automation workflows that are particularly valuable for research: automated bibliography updates from reference managers, figure regeneration from data analysis scripts, CI-based PDF compilation, and multi-author merge conflict resolution.

## Overleaf Git Bridge

Overleaf Server Pro and paid plans include a Git bridge that exposes each project as a Git repository.

### Setup

```bash
# Clone your Overleaf project (requires paid plan)
git clone https://git.overleaf.com/YOUR_PROJECT_ID my-paper
cd my-paper

# The remote is already configured
git remote -v
# origin  https://git.overleaf.com/YOUR_PROJECT_ID (fetch)
# origin  https://git.overleaf.com/YOUR_PROJECT_ID (push)
```

### Daily Workflow

```bash
# Pull latest changes from collaborators
git pull origin master

# Edit locally in your preferred editor
vim main.tex

# Push changes back to Overleaf
git add -A
git commit -m "Revise methodology section"
git push origin master
```

### Conflict Resolution

When collaborators edit the same section simultaneously:

```bash
git pull origin master
# If conflicts occur:
# 1. Open conflicted files
# 2. Resolve LaTeX merge conflicts (look for <<<<<<< markers)
# 3. Verify the document compiles
git add -A
git commit -m "Resolve merge conflict in results section"
git push origin master
```

## Open-Source Sync Tools

### overleaf-sync (Python)

For free Overleaf accounts without Git bridge access:

```bash
# Install
pip install overleaf-sync

# Login (stores credentials securely)
ols login

# List your projects
ols list

# Download a project
ols download "My Research Paper" --path ./my-paper

# Upload local changes
ols upload ./my-paper --project "My Research Paper"

# Two-way sync (pull then push)
ols sync ./my-paper --project "My Research Paper"
```

### Automated Sync Script

```bash
#!/bin/bash
# sync-overleaf.sh - Run periodically or before/after editing sessions

PROJECT_DIR="$1"
PROJECT_NAME="$2"

echo "Pulling latest from Overleaf..."
ols download "$PROJECT_NAME" --path "$PROJECT_DIR" --skip-existing

echo "Compiling locally to verify..."
cd "$PROJECT_DIR"
latexmk -pdf -interaction=nonstopmode main.tex

if [ $? -eq 0 ]; then
    echo "Compilation successful. Pushing to Overleaf..."
    ols upload "$PROJECT_DIR" --project "$PROJECT_NAME"
else
    echo "Compilation failed. Fix errors before syncing."
    exit 1
fi
```

## Automation Workflows

### Auto-Update Bibliography from Zotero

```python
import subprocess
from pathlib import Path

def sync_bibliography(zotero_lib_id, bib_file, project_dir):
    """Export Zotero library and sync to Overleaf project."""
    # Export from Zotero using Better BibTeX
    subprocess.run([
        "curl", "-s",
        f"http://localhost:23119/better-bibtex/export/library?/"
        f"{zotero_lib_id}/library.biblatex",
        "-o", str(Path(project_dir) / bib_file)
    ])
    print(f"Updated {bib_file} from Zotero library {zotero_lib_id}")
```

### Auto-Regenerate Figures from Data

```python
import subprocess
from pathlib import Path

def regenerate_figures(scripts_dir, figures_dir):
    """Run all figure generation scripts and update outputs."""
    scripts = sorted(Path(scripts_dir).glob("fig_*.py"))
    for script in scripts:
        print(f"Running {script.name}...")
        subprocess.run(["python", str(script)], cwd=figures_dir)

    print(f"Regenerated {len(scripts)} figures in {figures_dir}")
```

### CI/CD PDF Compilation

```yaml
# .github/workflows/compile-paper.yml
name: Compile LaTeX Paper
on:
  push:
    branches: [main]
    paths: ['**.tex', '**.bib', '**.sty']

jobs:
  compile:
    runs-on: ubuntu-latest
    container:
      image: texlive/texlive:latest
    steps:
      - uses: actions/checkout@v4
      - name: Compile PDF
        run: |
          latexmk -pdf -interaction=nonstopmode main.tex
      - name: Upload PDF
        uses: actions/upload-artifact@v4
        with:
          name: paper-pdf
          path: main.pdf
      - name: Check for warnings
        run: |
          grep -i "warning" main.log | grep -v "Font" || true
```

## Project Organization

Recommended directory structure for CLI-managed Overleaf projects:

```
my-paper/
  main.tex              # Main document
  sections/
    01-introduction.tex
    02-related-work.tex
    03-methodology.tex
    04-results.tex
    05-discussion.tex
    06-conclusion.tex
  figures/
    fig1-architecture.pdf
    fig2-results.pdf
  tables/
    tab1-comparison.tex
  references.bib
  custom.sty            # Custom LaTeX macros
  scripts/              # Not synced to Overleaf
    fig_architecture.py
    fig_results.py
    sync.sh
  .gitignore
```

### .gitignore for LaTeX Projects

```gitignore
# LaTeX build artifacts
*.aux
*.bbl
*.blg
*.fdb_latexmk
*.fls
*.log
*.out
*.synctex.gz
*.toc

# Local scripts (don't sync to Overleaf)
scripts/

# OS files
.DS_Store
```

## Editor Integration

### VS Code

Install the "LaTeX Workshop" extension and configure local compilation:

```json
{
  "latex-workshop.latex.tools": [
    {
      "name": "latexmk",
      "command": "latexmk",
      "args": ["-pdf", "-interaction=nonstopmode", "%DOC%"]
    }
  ]
}
```

### Neovim with VimTeX

```lua
-- init.lua
vim.g.vimtex_compiler_method = 'latexmk'
vim.g.vimtex_view_method = 'skim'  -- macOS
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Git push rejected | Pull first, resolve conflicts, then push |
| Sync tool authentication error | Re-run login, check 2FA settings |
| Compilation differs locally vs Overleaf | Match TeX Live versions; Overleaf uses TeX Live 2024 |
| Binary files (images) cause large diffs | Use `.gitattributes` to mark as binary |
| Overleaf rate limiting | Add delays between API calls, use Git bridge if available |

## References

- Overleaf Git bridge documentation: https://www.overleaf.com/learn/how-to/Git_integration
- overleaf-sync: https://github.com/moritzgloeckl/overleaf-sync
- LaTeX Workshop (VS Code): https://github.com/James-Yu/LaTeX-Workshop
- latexmk documentation: https://mg.readthedocs.io/latexmk.html

---

## Multi-Author Collaboration

Set up and manage collaborative LaTeX projects on Overleaf with best practices for multi-author workflows, version control, and project organization.

## Getting Started with Overleaf

### Creating a Project

Overleaf (overleaf.com) is a browser-based LaTeX editor that provides real-time collaboration, automatic compilation, and integrated version history.

Project creation options:

| Method | When to Use |
|--------|-------------|
| Blank project | Starting from scratch |
| Upload project | Migrating existing local LaTeX project |
| Import from GitHub | Existing repo-based project |
| Use a template | Conference/journal submissions (IEEE, ACM, Springer, Elsevier templates available) |
| Copy from existing | Forking a previous project |

### Recommended Project Structure

```
project-root/
├── main.tex              # Main document (entry point)
├── preamble.tex          # Packages, macros, custom commands
├── sections/
│   ├── 01-introduction.tex
│   ├── 02-related-work.tex
│   ├── 03-methods.tex
│   ├── 04-results.tex
│   ├── 05-discussion.tex
│   └── 06-conclusion.tex
├── figures/
│   ├── fig1-overview.pdf
│   ├── fig2-results.pdf
│   └── fig3-comparison.pdf
├── tables/
│   └── results-table.tex
├── references.bib        # Bibliography database
└── README.md             # Project notes (not compiled)
```

### Main File Setup

```latex
% main.tex
\documentclass[conference]{IEEEtran}  % or article, etc.
\input{preamble}  % load packages and macros

\begin{document}

\title{Your Paper Title}
\author{Author One \and Author Two \and Author Three}
\maketitle

\begin{abstract}
Your abstract here.
\end{abstract}

\input{sections/01-introduction}
\input{sections/02-related-work}
\input{sections/03-methods}
\input{sections/04-results}
\input{sections/05-discussion}
\input{sections/06-conclusion}

\bibliographystyle{IEEEtran}
\bibliography{references}

\end{document}
```

## Multi-Author Collaboration

### Sharing and Permissions

| Role | Capabilities |
|------|-------------|
| Owner | Full control, can delete project, manage collaborators |
| Editor | Can edit all files, cannot manage collaborators |
| Viewer | Read-only access, can download but not modify |

Share via:
- **Link sharing**: Generate a read-only or edit link (anyone with the link can access)
- **Email invitation**: Invite specific collaborators by email with role assignment

### Author Coordination Best Practices

1. **Assign sections**: Each author owns specific `.tex` files to minimize merge conflicts.
2. **Use comments**: Overleaf supports inline comments (`% TODO: revise this paragraph`) and threaded review comments.
3. **Use custom commands for notes**:

```latex
% In preamble.tex, define author-specific annotation commands
\usepackage{xcolor}
\newcommand{\alice}[1]{\textcolor{blue}{[Alice: #1]}}
\newcommand{\bob}[1]{\textcolor{red}{[Bob: #1]}}
\newcommand{\todo}[1]{\textcolor{orange}{[TODO: #1]}}

% In text:
This result is surprising \alice{Should we add more analysis here?}
and warrants further investigation \todo{Add statistical test}.
```

4. **Track changes**: Overleaf Premium includes a track-changes mode. For free plans, use the `changes` package:

```latex
\usepackage{changes}
\definechangesauthor[name={Alice}, color=blue]{AL}
\definechangesauthor[name={Bob}, color=red]{BO}

% Usage:
\added[id=AL]{This is new text added by Alice.}
\deleted[id=BO]{This text was removed by Bob.}
\replaced[id=AL]{new text}{old text}
```

## Git Integration

### Overleaf + GitHub Sync

Overleaf Premium supports bidirectional GitHub sync:

1. In Overleaf, go to Menu > Sync > GitHub
2. Link your GitHub account and select or create a repository
3. Pull/push changes between Overleaf and GitHub

### Overleaf + Local Git

```bash
# Clone your Overleaf project via git
git clone https://git.overleaf.com/YOUR_PROJECT_ID my-paper
cd my-paper

# Edit locally, then push back to Overleaf
git add -A
git commit -m "Updated results table"
git push origin master

# Pull changes made on Overleaf
git pull origin master
```

**Credentials**: Use your Overleaf email as username and an Overleaf-generated token as password.

## Compilation and Debugging

### Common Compilation Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `Undefined control sequence` | Missing package or typo in command | Check `\usepackage` or spelling |
| `Missing $ inserted` | Math symbol outside math mode | Wrap in `$...$` or `\text{...}` |
| `File not found` | Incorrect path in `\input` or `\includegraphics` | Check file names (case-sensitive on Overleaf) |
| `Overfull \hbox` | Content too wide for column | Resize figure, adjust text, or add `\sloppy` |
| `Citation undefined` | BibTeX entry missing or key mismatch | Verify `.bib` entry key matches `\cite{}` |

### Debugging Tips

- Use **Recompile from scratch** (Ctrl+Shift+Enter) to clear cache
- Check the **Logs and output files** panel for detailed error messages
- Use `\listfiles` in preamble to see which packages are loaded
- Overleaf uses TeX Live 2024; check package compatibility if using older templates

## Submission Workflow

### Preparing for Journal Submission

1. **Flatten the project**: Some journals require a single `.tex` file.

```bash
# Use latexpand to flatten \input commands
latexpand main.tex > submission.tex
```

2. **Check formatting**: Verify page limits, font sizes, margin requirements.
3. **Download as zip**: Menu > Download > Source to get all files.
4. **Convert figures**: Ensure all figures are in accepted formats (PDF, EPS, or high-res PNG/TIFF).
5. **Clean up**: Remove TODO comments, author annotation commands, and debug code.

```latex
% Add to preamble for submission: disable all annotation commands
\renewcommand{\alice}[1]{}
\renewcommand{\bob}[1]{}
\renewcommand{\todo}[1]{}
```

## Useful Overleaf Keyboard Shortcuts

| Action | Shortcut (Mac) | Shortcut (Windows) |
|--------|---------------|-------------------|
| Compile | Cmd+Enter | Ctrl+Enter |
| Bold | Cmd+B | Ctrl+B |
| Italic | Cmd+I | Ctrl+I |
| Comment toggle | Cmd+/ | Ctrl+/ |
| Find & replace | Cmd+H | Ctrl+H |
| Go to line | Cmd+Shift+L | Ctrl+Shift+L |
| Toggle PDF | Cmd+Shift+O | Ctrl+Shift+O |
