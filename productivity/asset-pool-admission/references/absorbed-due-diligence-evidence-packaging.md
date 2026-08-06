---
name: due-diligence-evidence-packaging
description: "Organize Chinese financial due diligence evidence packages for trust/fund admission applications. Covers zip/rar extraction with GBK encoding, numbered Chinese-named evidence files, flat directory structure, docx form creation from template, and cross-referencing."
version: 1.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [due-diligence, fund, trust, chinese-finance, document-organization]
    related_skills: [holographic-memory-migration, document-format-conversion]
---

# Due Diligence Evidence Packaging

## Overview

Chinese trust companies and fund managers require standardized evidence packages when applying to enter asset pools (基础池/备选池). The raw materials arrive as WeChat-sent zip/rar archives with Chinese filenames, and must be organized into a clean, numbered, self-documenting package that maps to the admission conditions in the application form.

## When to Use

- User says "新打来了一个压缩包，解压之后调整好命名" (new archive arrived, extract and organize)
- User asks to organize DD materials matching numbered conditions (01- through 08-)
- Creating evidence packages for trust/fund asset pool admission applications
- User passes raw zip/rar files from WeChat Downloads directory
- When the user's application form needs evidence files that match its numbered condition rows

## CRITICAL: Git Discipline (Enforced Preference)

commit+push is a single atomic action — do not batch. After EVERY file operation (cp, mv, mkdir, write_file, rename, delete), immediately git add + git commit + git push. This repo is shared with colleagues; unpushed commits are invisible. The user will call it out instantly if you batch.

Granularity rules for yuecai (AGENTS.md sec 11):
- Different pool = different commit (basic vs alternative pool)
- One manager x one pool per commit
- Max ~10 files per commit; split larger batches
- Only stage files relevant to that commit
- Reference conditions.md numbers in commit messages

Prefix + message format: `<type>: English imperative, <=72 chars`
Types: feat (new materials), fix (correct errors), docs (reports), refactor (restructure), chore (maintenance), cleanup (remove superseded)

Correct pattern after every operation:
```
git add <specific-paths>
git commit -m "feat: add duohemei basic pool admission materials (business license, AMAC filing)"
git push
```

Banned: git add ., wip messages, git commit --amend (on pushed), git push --force.

## Screenshot Collection: Third-Party Credit/Enforcement Queries

Due diligence requires verifying the manager against government blacklists. Use Computer Use (open-computer-use MCP) to open Safari, then the user handles real-name auth and screenshots.

Sites to open:
- 证券期货市场失信记录查询平台: neris.csrc.gov.cn/shixinchaxun/
- 中国执行信息公开网: zxgk.court.gov.cn
- 国家企业信用信息公示系统: gsxt.gov.cn

Workflow:
1. Open Safari tabs via open-computer-use (get_app_state + type_text + Return)
2. User queries manually (real-name / CAPTCHA required) and screenshots results
3. Save screenshots from ~/.hermes/images/clip_*.png to pool directory
4. Merge into PDF using PIL (Image.open.convert(RGB) + save with save_all + append_images)
5. Delete originals, commit+push immediately
6. Name: 4-第三方查询结果汇总.pdf for first batch, 5-<descriptive>.pdf for supplementary

Note: Wind Terminal (3.1M etc.) is a desktop app, not a web page. Cannot open via browser.

## Workflow

### Step 1: Locate the raw archive

WeChat downloads live in:
```
/Users/minimx/Library/Containers/com.tencent.xinWeChat/Data/Documents/xwechat_files/wxid_*/msg/file/YYYY-MM/<filename>.zip|.rar
```

Search with `search_files(target='files', pattern='*.zip', path='~')` to find recent compressed files.

### Step 2: Extract with Chinese encoding

**ZIP files** — filenames may be GBK or UTF-8 encoded:

```python
import zipfile, os, shutil
with zipfile.ZipFile(src, 'r') as z:
    for info in z.infolist():
        if info.is_dir():
            continue
        raw = info.filename.encode('cp437')
        try:
            decoded = raw.decode('gbk')
        except:
            decoded = raw.decode('utf-8', errors='replace')
        # Fix common single-file corruption: '4銆佹壙璇哄嚱.pdf' → '4、承诺函.pdf'
        # (This happens when UTF-8 bytes are decoded as GBK)
        outpath = os.path.join(dst, decoded)
        os.makedirs(os.path.dirname(outpath), exist_ok=True)
        with z.open(info) as srcf, open(outpath, 'wb') as dstf:
            shutil.copyfileobj(srcf, dstf)
```

**RAR files** — need `unrar` installed:
```bash
brew install unrar
unrar x <file.rar> <target_dir/>
```

### Step 3: Map raw files to admission conditions

Trust asset pool conditions follow this pattern:
- Condition 1 (01-): AMAC filing proof + business license
- Condition 2 (02-): Paid-in capital ≥ 10M RMB
- Condition 3 (03-): ≥1 year establishment, ≥3 products with traceable performance
- Condition 4 (04-): No legal/regulatory violations in past year
- Condition 5 (05-): Completed questionnaire + supporting docs
- Condition 6 (06-): Team composition (≥50% research/tech, 3yr+ experience, low turnover)
- Condition 7 (07-): 1yr+ positive returns, index-enhanced products beat benchmark
- Condition 8 (08-): Sound risk control system, no risk incidents since founding

### Step 4: Naming convention

Use this naming scheme — critical for acceptance:

```
{numbered-prefix}–{Chinese-descriptive-name}.{pdf|docx|xlsx}
```

Rules:
- **Prefix**: Match the application form's evidence numbering (1-1, 1-2, 2, 3-1, 3-2, 4-1, 4-2, 5-1, 5-2, 5-3, 5-4, 5-5). The application form itself gets `0–`.
- **Separator**: Use en-dash (U+2013, `–`), not space or hyphen.
- **Name**: Chinese descriptive name matching the application form's evidence column, e.g. `私募基金管理人公示信息`, `营业执照副本`, not English-prefix names.
- **Format**: Use original document formats (.pdf for scanned/sealed docs, .docx for editable forms, .xlsx for data tables). Do NOT use .md for evidence files — convert to .docx if needed.
- **Flat structure**: All files in the same directory. No subdirectories. If subdirectories exist (e.g. 03-products/, 05-materials), flatten them.
- **Cross-references**: When the same file supports multiple conditions (e.g. 私募基金管理人公示信息 supports both conditions 1 and 4), name it under its primary condition number and reference it by that name in other conditions.

### Step 5: Create the application form DOCX

Use python-docx to create a table-based form modeled on the existing template:

1. Parse the Chenyuan template (`references/chenyuan/08-asset-pool-adjustment-application-20250213.docx`) to understand the table structure
2. Key table operations: merged cells (`cell.merge()`), `merge_row_cells()` and `merge_col_cells()` helpers
3. Fill in: manager name, pool type, condition text, evidence file names, "是" (complete) status
4. Leave 调出/保留/复核意见 rows empty (filled by risk management)

Update `conditions.md` with a summary table mapping conditions → evidence files.

### Step 6: Post-package cleanup of source materials

After the evidence package is finalized and the application form references are locked:

1. **Add `references/` to `.gitignore`** — the raw DD materials (PDFs, contracts, audit reports) are bulky and proprietary. Once extracted into the numbered evidence package, they don't need to be in git. Remove them from tracking:

```bash
echo "references/" >> .gitignore
git rm -r --cached references/
git commit -m "chore: ignore references/ (raw DD materials stay local)"
```

2. **Consolidate under `references/<manager>/`** — before gitignoring, move all materials for the same manager into a single subdirectory:

```bash
mkdir -p references/duohemei
git mv references/due-diligence-materials references/duohemei/
git mv references/supplementary-due-diligence references/duohemei/
```

3. **Clean up standalone documents** — move any orphaned top-level reference files into a topic-named subdirectory (e.g. `references/trust-classification/`) before the gitignore removal, so the local filesystem stays organized even though git stops tracking.

4. **Keep workspace conventions in AGENTS.md** — after settling the workspace structure, update AGENTS.md (or create it) with a workspace conventions section documenting the directory layout, date-directory naming, file numbering rules, tmp/ usage, and which areas are git-tracked vs ignored.

## Common Pitfalls

1. **Batch-and-commit-later trap** — See the Git Discipline section at the top. This is the most frequently corrected mistake.
2. **Pinyin reversal** — Chinese two-character company names in pinyin are easy to transpose. 多和美 = duohemei, NOT heduomei. Read the characters aloud to verify.
3. **Subdirectories** — The user prefers all evidence files flat in one directory. If you created subdirectories (03-products/, 05-materials/), flatten them with `mv subdir/* . && rmdir subdir`.
4. **.md for formal evidence** — Markdown is not acceptable for formal evidence files. Convert to .docx using python-docx, or use the original PDF/.docx from the raw archive. The only exception is 5-1 (the questionnaire) which may arrive as .docx.
5. **Original source preference** — When the raw archive contains the original file (e.g. a .docx questionnaire), always use that instead of a converted version you created from a .md copy.
6. **Space vs en-dash** — The separator between the numbered prefix and the Chinese name must be en-dash (U+2013), not a space or regular hyphen. This is a user-specific formatting requirement.
7. **Encoding in zip files** — Chinese Windows zips use GBK encoding; macOS creates with UTF-8. If `unzip -O gbk` fails with "Illegal byte sequence", use the Python extraction script in Step 2.
8. **Clean up duplicates** — After flattening and renaming, delete stale .md files, old directories (06-team, 07-performance, 08-risk-control), and the English-named copy of the application form if it exists.
9. **RAR on macOS** — `unrar` is not installed by default. Install via `brew install unrar` or `brew install homebrew/cask/rar`.
10. **Git-ignoring references/ too early** — don't add `references/` to `.gitignore` until AFTER the materials are consolidated, organized into the numbered evidence package, and the application form is finalized. Once gitignored, re-instating tracking requires manual intervention.
11. **Previously-tracked files** — if the raw DD materials were previously committed, `git rm -r --cached references/` is needed to stop tracking them (keeps local copies). Do this as part of the final cleanup, not during the initial organization phase.

## Verification Checklist

- [ ] All raw files extracted with correct Chinese filenames
- [ ] Each condition (1-5 for 基础池, 6-8 for 备选池) has corresponding evidence files
- [ ] File names use numbered prefix + en-dash + Chinese descriptive name
- [ ] No .md files among evidence (converted to .docx where needed)
- [ ] No subdirectories — all files flat
- [ ] Application form references match actual filenames exactly
- [ ] Old/moved directories cleaned up
- [ ] Committed and pushed
