# CI Troubleshooting Quick Reference

Common CI failure patterns and how to diagnose them from the logs.

## Reading CI Logs

```bash
gh run view <RUN_ID> --log-failed
```

## Common Failure Patterns

### Test Failures
**Signatures:** `FAILED tests/test_foo.py::test_bar - AssertionError`
**Diagnosis:** Find the test file and line from traceback. Read the test.
**Common fixes:** Update assertion for new behavior, add missing dependency, fix flaky test.

### Lint / Formatting Failures
**Signatures:** `src/auth.py:45:1: E302 expected 2 blank lines`
**Diagnosis:** Read the file:line, check which linter (ruff, flake8, black, mypy).
**Common fixes:** `ruff check --fix .`, `black .`, `isort .`

### Type Check Failures
**Signatures:** `src/api.py:23: error: Argument 1 has incompatible type`
**Diagnosis:** Read file at mentioned line, check function signature.
**Common fixes:** Add type cast, fix signature, add `# type: ignore` as last resort.

### Build / Compilation Failures
**Signatures:** `ModuleNotFoundError: No module named 'package'`
**Diagnosis:** Check requirements.txt / package.json / pyproject.toml.
**Common fixes:** Add missing dep, pin compatible version, update lockfile.

### Permission / Auth Failures
**Signatures:** `403 Forbidden`, `Resource not accessible by integration`
**Diagnosis:** Check workflow permissions, token scopes.
**Common fixes:** Add `permissions:` block to workflow, verify secrets exist.

### Timeout Failures
**Signatures:** `The operation was canceled`, `exceeded maximum execution time`
**Diagnosis:** Check which step timed out.
**Common fixes:** Add `timeout-minutes: 10` to step, fix perf issue, split into parallel jobs.

### Docker / Container Failures
**Signatures:** `COPY failed: file not found in build context`
**Diagnosis:** Check Dockerfile for failing step.
**Common fixes:** Fix path in COPY/ADD, update base image tag.

## Auto-Fix Decision Tree

```
CI Failed
├── Test failure → update test or fix logic / add dependency
├── Lint failure → run formatter, fix style  
├── Type error → fix types
├── Build failure → add/update dependencies
├── Permission error → update workflow permissions (needs user)
└── Timeout → investigate perf (may need user input)
```

## Re-running After Fix

```bash
git add <fixed_files> && git commit -m "fix: resolve CI failure" && git push
gh pr checks --watch
```