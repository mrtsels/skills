# Conventional Commits Quick Reference

Format: `type(scope): description`

## Types

| Type | When to use | Example |
|------|------------|---------|
| `feat` | New feature | `feat(auth): add OAuth2 login flow` |
| `fix` | Bug fix | `fix(api): handle null response from /users` |
| `refactor` | Code restructuring, no behavior change | `refactor(db): extract query builder` |
| `docs` | Documentation only | `docs: update API usage examples` |
| `test` | Adding or updating tests | `test(auth): add integration tests for token refresh` |
| `ci` | CI/CD configuration | `ci: add Python 3.12 to test matrix` |
| `chore` | Maintenance, dependencies, tooling | `chore: upgrade pytest to 8.x` |
| `perf` | Performance | `perf(search): add index on users.email` |
| `style` | Formatting, whitespace | `style: run black formatter on src/` |
| `build` | Build system or external deps | `build: switch from setuptools to hatch` |
| `revert` | Reverts previous commit | `revert: revert "feat(auth): add OAuth2"` |

## Breaking Changes

Add `!` after type or `BREAKING CHANGE:` in footer:
```
feat(api)!: change authentication to use bearer tokens
```

## Linking Issues

In commit body:
```
Closes #42     ← closes when merged
Fixes #42      ← same effect
Refs #42       ← references without closing
```