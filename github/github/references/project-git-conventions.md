# Extracting & Formalizing Project Git Conventions from History

When a project has no documented git conventions, extract them from its existing commit log before formalizing. This ensures the conventions match what the team actually does, not an arbitrary external standard.

## Steps

1. **Dump the full commit log**

   ```bash
   git log --oneline --all | head -50
   ```

   This shows every commit type prefix in use across all branches.

2. **Categorize by prefix**

   ```bash
   git log --format="%h %s" | sed -E 's/^[0-9a-f]+ //' | sed -E 's/([a-z]+).*/\1/' | sort | uniq -c | sort -rn
   ```

   This counts how many times each prefix appears — reveals the de facto convention.

3. **Check subject line patterns**

   - Tense: imperative (`"add"`, `"fix"`, `"update"`) vs past tense (`"added"`, `"fixed"`)
   - Language: English, Chinese, or bilingual
   - Length: typical subject line length (target ≤ 72 chars)
   - Capitalization: sentence case vs lowercase

4. **Check body patterns**

   - `git log --format="%b" | grep -v "^$" | head -20`
   - Look for issue references (`#42`), `why` explanations, breaking change markers

5. **Identify project-specific types**

   Some projects use non-standard prefixes that reflect their domain:
   - `reorg` — large-scale directory reorganization (docs/materials repos)
   - `cleanup` — removing superseded files
   - `wip` — checkpoint commits (should be minimized)

6. **Formalize as a section in the project's AGENTS.md**

   Structure to write:
   - **类型表** — prefix, when to use, real example from the project's own history
   - **消息格式** — subject template, body conventions
   - **留痕要求** — what each commit must reference (issue numbers, condition IDs, file paths)
   - **操作规范** — allowed and forbidden commands
   - **检查清单** — end-of-day or pre-push checklist

## Example: yuecai (FOF due diligence materials repo)

```bash
# De facto types from ~60 commits:
# feat   → 新文件/笔记/评分表
# fix    → 修正编号/文件内容
# docs   → 文档撰写
# refactor → 重构目录/重命名
# chore  → gitignore/维护
# reorg  → 大规模重组
# cleanup → 清旧文件

# Convention documented in AGENTS.md §11:
# - 7 types matching actual usage
# - English imperative, ≤72 chars
# - Label condition numbers (e.g. "conditions 06-08")
# - Prohibit: git add ., git commit --amend (pushed), git push --force
# - commit + push = one action
```

## When to Skip

- Single-developer side projects with no conventions needed
- Templates/starter repos that will be thrown away
- Repos with an existing CONTRIBUTING.md that already covers this
