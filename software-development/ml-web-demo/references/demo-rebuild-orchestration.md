# Parallel-Subagent Demo Rebuild — Orchestration Recipe

> Proven on the bipartite-gnn-gui web demo rebuild (2026-07). Three parallel
> `delegate_task` subagents rebuilt a broken FastAPI demo in one batch while
> the orchestrator handled non-conflicting setup edits. Total ~6.5h across
> agents; orchestration overhead ~0.5h.

## Why this shape

A demo rebuild touches three disjoint surfaces: backend (model loading + API),
data prep (hero-case generation), frontend (vanilla JS SPA). They share a
contract (JSON shapes, API routes) but share no files. Running them as 3
parallel subagents gives isolation (each has its own context) and speed, at
the cost of writing very careful prompts.

## Preconditions (orchestrator does these FIRST, in the main session)

1. **Verify feasibility before dispatching.** Load the checkpoint with
   shape-filtering, count matched keys (Pitfall 15), confirm data files exist
   (`data/…` counts), confirm torch/PyG versions. Subagents must not discover
   "the checkpoint is broken" — you already know which one works.
2. **Write the strategy doc** (`docs/development/web_demo_strategy.md`):
   measured findings table, what to build, what NOT to build (with reasons),
   dev-route section with per-task file/line-level change lists.
3. **Write the review plan** (`docs/development/demo_review_plan.md`):
   enumerate likely bugs per component (loading, data prep, API, frontend,
   integration) with severity and prevention snippets. This becomes the
   subagents' checklist.

## Agent split (file groups MUST NOT overlap)

| Agent | Files | Responsibility |
|-------|-------|----------------|
| A | `api/pipeline.py`, `api/main.py` | checkpoint fix, hero-case API routes, predict-route optimization |
| B | `scripts/prepare_demo_cases.py` (new) | run full eval set → filter hero cases → write `demo_data/cases.json` + copy screenshots |
| C | `web/index.html` | rewrite as dual-pane Canvas SPA per API contract |

Orchestrator (main session, while agents run): `pyproject.toml` demo extra,
`.gitignore` generated dirs (`demo_data/`), read live transcripts.

## API contract (paste into every agent that touches it)

```
GET  /api/cases          -> [{id, name, metrics:{before:{f1,…},after:{f1,…}}}]
GET  /api/case/{id}      -> {id, name, screenshot, img_w, img_h,
                             vlm_elements:[{bbox:[x1,y1,x2,y2] normalized,label}],
                             proposals:[{bbox, violation_score}],
                             metrics:{before:{detections,tp,fp,fn,precision,recall,f1},
                                      after:{…}}}
GET  /api/screenshot/{id} -> image file
POST /api/predict (multipart file) -> upload-mode result, same shape + vlm_time_ms/gnn_time_ms
```

## Per-agent prompt requirements (all in `context` field)

- Absolute project path, Python/torch versions, installed deps.
- The VERIFIED checkpoint facts (e.g. "joint model = 44/44 keys, threshold 0.60;
  violation_only = broken proposal head; do not use"). Prevents contradiction.
- Reference docs to read first (strategy doc section X, review plan section Y).
- The API contract verbatim.
- Exact verification commands with expected output (e.g.
  `python -c "from api.pipeline import DemoPipeline; …"` → params ≈ 220K).
- Report language (user writes Chinese → "用中文回复").
- Requirement to report real outputs, not claims.

## After the batch returns (orchestrator MUST verify, not trust)

1. Read the actual changed files (don't rely on the summary).
2. Re-run each agent's verification command yourself.
3. Run the end-to-end test: start server, curl `/api/cases`, curl a case,
   open browser for Canvas, upload a test image.
4. Then update the docs (TASK.md phase checkboxes, web_demo.md) with the
   REAL measured numbers.

## Pitfalls seen

- Agents can't see the main conversation — every fact must be in `context`
  or the docs. A prompt that says "use the joint checkpoint we discussed"
  will fail; say "checkpoints/violation_detection_joint/best_model.pt".
- Parallel agents editing the same file = merge hell. Enforce disjoint file
  lists; the API contract file (`api/main.py`) belongs to exactly ONE agent.
- `demo_data/` and generated screenshots must be gitignored or the repo
  fills with ~12 MB of generated JPEGs.
- Live transcripts (`~/.hermes/cache/delegation/live/<id>/task-N.log`) let
  the orchestrator watch progress and catch a stuck agent early.

## Execution notes (from the 2026-07 run)

- **Background server startup: use the absolute python path.** Foreground
  `python3 main.py` imported fastapi fine, but the same command via
  `terminal(background=true)` died with `ModuleNotFoundError: fastapi` — the
  background shell didn't inherit the interactive env's PATH. Fix:
  `terminal(background=true, command="/opt/homebrew/.../bin/python3 main.py")`.
  Always check `which python3` and pass the absolute path for background
  servers.
- **A delegation batch is not a process session.** `process(action='wait',
  session_id=<delegation_id>)` returns not_found — the batch handle is not a
  pollable process. Watch `live/<delegation_id>/task-N.log` with tail/grep
  for progress and completion (`grep 'final' task-N.log`).
- **Agents can hit the tool-call cap before finishing verification.** One
  agent completed all edits but reported "verification 2 not executed (tool
  call limit)". Orchestrator MUST re-run that exact verification command
  itself after the batch returns — this is part of "verify, don't trust",
  not an edge case.
- **Cross-check the data-prep agent against your own independent run.** The
  prepare agent's hero-case numbers matched the orchestrator's earlier
  visualization pass exactly (e.g. case 10027 F1 0.4444→0.6000) — a cheap
  agreement check that catches silently-wrong metrics before the demo ships.
- **Server log is the integration truth.** After killing the test server,
  read its full log: it confirms 44/44 key loading, every endpoint's status
  code (200/404), and real VLM round-trip times. Keep it as evidence for the
  doc's "tested" section.
