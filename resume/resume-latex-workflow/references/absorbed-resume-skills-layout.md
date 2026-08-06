---
name: resume-skills-layout
description: Format skills section with left-aligned
  label columns.
version: 0.1.0
author: Hermes
platforms: [macos]
metadata:
  hermes:
    tags: [Resume, LaTeX, Formatting]
---

# Resume Skills Section Layout

Format the Skills section in `resume-alex-en/entries/skills.tex` with 4 category rows, left-aligned content via `\makebox`.

## When to Use

- User asks to restructure or simplify the skills section.
- User says skills section is too long, has overlapping categories, or contains skills not backed by projects.

## Format

```latex
\section{Skills}
\begin{itemize}
  \item \makebox[7em][l]{\textbf{Languages:}} English (TOEFL 109), Mandarin (native), Cantonese (fluent)
  \item \makebox[7em][l]{\textbf{Programming:}} Python, Java, JavaScript, SQL, Bash, \LaTeX, Git
  \item \makebox[7em][l]{\textbf{ML Frameworks:}} PyTorch, HuggingFace, Transformers/LLMs, GNN, Bayesian inference
  \item \makebox[7em][l]{\textbf{Infrastructure:}} Docker, Linux, MongoDB, DuckDB, FastAPI, Flask, Nginx
\end{itemize}
```

## Rules

- **4 categories only**: Languages, Programming, ML Frameworks, Infrastructure.
- **No parentheses detail**: List the language/framework name only, not sub-libraries.
- **Each item project-backed**: Every skill must appear in at least one entry's bullet points.
- **Left-aligned content**: `\makebox[7em][l]{\textbf{Label:}}` ensures content starts at same column regardless of label width.
- **Brevity preferred**: Fewer items per line is better — split into 4 rows rather than 2 dense ones.

## Procedure

1. Audit all entries for actually used skills.
2. Group into the 4 categories.
3. Remove any skill not found in any entry (e.g. JAX, RLHF, RAG if unused).
4. Trim parenthetical details from each item.
5. Write the section with `\makebox[7em][l]` for label column alignment.
6. Compile and verify 1-page fit.

## Pitfalls

- **Overlapping categories**: "Git" belongs in Programming, not Infrastructure. "FastAPI" belongs in Infrastructure (it's a web framework), not ML.
- **Too many items per line**: If a line overflows, remove the least relevant item rather than abbreviating.
- **Inventing skills**: Only list skills the user has actually demonstrated in resume entries. No "deep learning" if no DL entry exists.
