---
name: research-entry-from-codebase
description: Scan a code repository and produce a formatted LaTeX research entry for an academic resume's Research & Projects section
category: resume
---

# Research Entry from Codebase

Use when the user has a code repository (project, research code, course project) and needs a formatted LaTeX `\ResumeItem` entry for the Research & Projects section of their CUHK-style LaTeX resume.

## Workflow

### 1. Scan the Codebase

Read in this order:

- **README.md** — problem statement, motivation, key results, high-level architecture
- **TASK.md / plan.md / PHASES.md** — structured development plan with per-phase metrics
- **Core source files** — focus on architecture and key results:
  - `model/model.py` or equivalent — entry point, forward pass, loss function
  - `model/encoder.py` — message-passing structure
  - `eval/metrics.py` — evaluation metrics definitions
  - `graph/` or `data/` — data representation
- **Experiment results** — `experiments/`, `results/`, benchmark files

### 2. Extract Key Information

| Category | What to Extract |
|----------|-----------------|
| Problem | What gap or limitation does this address? |
| Approach | Model architecture, graph construction, loss formulation |
| Key Metrics | Accuracy, AUROC, F1 change (in pp), MSE, speedup, cross-domain transfer |
| Unique Contribution | Novel technique, ablation finding, architectural insight |

Prioritize **quantified results with baselines** — "92% acc" without context is weak. "92% acc (+3pp over baseline)" is strong.

### 3. Format as LaTeX Entry

Match the existing file convention (`entries/research-<shortname>.tex`):

```latex
\ResumeItem{\textbf{Project Title}}
[Role | Supervisor: Prof. Name]
[MM/YYYY\textendash MM/YYYY]
[Location]

\begin{itemize}
  \item Architecture/approach description with \LaTeX math notation —
        graph definition $G = (V, E)$, loss $\mathcal{L}$, key parameters
  \item Key metric-driven result with baseline comparison and specific numbers
  \item Additional contribution — ablation study, cross-domain transfer,
        architectural innovation
  \item (optional) Advanced feature — multi-modal fusion, self-supervised pretraining
\end{itemize}
```

### 4. Tone Guidelines

- **Supervisor, not Advisor** — always use "Supervisor: Prof. Name" in the role line. Never "Advisor". If no supervisor is known, use "Independent Research".
- Each bullet: dense, single sentence, starts with action verb (Designed / Built / Introduced / Achieved)
- Use \LaTeX math for: loss functions, variables, arrows ($\to$, $\Delta$, $\mathcal{L}$, $O(N^{2.807})$)
- Specific percentages over vague adjectives
- Date range format: `[MM/YYYY\textendash MM/YYYY]` — use \textendash (not `--`), no extra spaces around it
- Do NOT fabricate supervisor names — use "Independent Research" if unclear
- 4 bullets max — pick highest-impact contributions; user may request fewer after trimming/merging

### 5. Content Polishing (Post-Draft, when user requests)

- **Trim bullets**: shorten each line by ~3 words — remove filler (various, several, very, significant, comprehensive), keep metrics and technical specifics
- **Merge related bullets**: combine approach + architecture into one when they share a logical thread. Example: graph construction + multi-head prediction pipeline merge naturally — the graph IS the input to the pipeline. Don't split them.
- **Remove "(expected)"**: once the end date has passed (reference: 2026-07-22), strip "(expected)" from EVERY entry with a past end date. Check globally.
- **Remove unrealistic entries**: skip projects the user deems not practical to include (e.g. says "不现实")
- **Word-count micro-adjustments**: user may request precise per-bullet changes with syntax like `+2 +2 +2` or `+1 +2 +2` or `-1 0 0`. Each number = words to add/remove on that bullet index (1-indexed). Apply exactly — do not round. See `latex-resume-workflow` for full pattern.

### 6. Valid Bullet Content Types

When constructing bullets, draw from these categories (pick 3–4 highest impact):

- **Architecture** — graph design, message-passing scheme, loss formulation with LaTeX math
- **Key metrics** — accuracy, AUROC, F1 change (in pp), MSE, speedup — always with baseline comparison
- **Cross-modal fusion** — attention-based fusion between modalities (e.g. structural features querying visual features), architectural decisions (pre-encoder vs post-encoder), ablation results
- **Cross-domain transfer** — zero-shot and fine-tuned performance on out-of-distribution datasets
- **Real-world validation** — metrics on real (not synthetic) data, pipeline improvements on production-grade inputs

### 7. Company Name Verification

For internship/company entries, **verify the full legal name** by visiting the official website:
1. Navigate to the company's site (use the URL the user provides or look it up)
2. Check footer, about page, or English-language version for the registered name
3. Cross-reference with email signatures from correspondence when available
4. Use the full legal name (e.g. "Oakcean Capital Limited", "Guangdong Yuecai Trust Co., Ltd.")
5. Wrap in `\ResumeUrl{url}{Legal Name}`

### 7. Compilation & Review Loop

After creating the entry:
1. Add `\input{}` to `resume.tex` at the correct time-descending position
2. Run `xelatex -interaction=nonstopmode resume.tex` twice
3. Present the compiled PDF — do not skip this step

## Pitfalls

- **Don't list all features** — pick 3-4 most impressive contributions
- **Baseline context required** — "93.2% acc" without baseline is weak; "93.2% acc, AUROC 0.989" is acceptable if metric is standard
- **Don't guess supervisor** — without explicit mention, use "Independent Research"; never fabricate a name
- **Terminology consistency**: normalize all role labels to "Supervisor" (never "Advisor") across all entries in the same resume
- **Date formatting**: use `\textendash` (not `--`) for date ranges; remove "(expected)" once the end date has passed
- **File path convention** — save as `entries/research-<project-shortname>.tex` matching existing entries
- **Verify format** — read back the file to ensure no broken LaTeX, and check bullet length against existing entries for consistency
- **Codebase conventions** — if the project has a TASK.md with structured phases, prioritize Phase summaries and Results tables over README prose

## Related Skills

- `resume-bullet-writer` — fine-tuning individual bullet strength
- `resume-section-builder` — overall section structure (non-agent-created, read-only)
