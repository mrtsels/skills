---
name: evidence-package-organization
description: "Organize raw due diligence / compliance materials into numbered evidence packages. Covers archive extraction (Chinese encoding), condition-based sorting, index documents, form generation from templates, and workspace conventions (date dirs, hierarchical numbering, tmp/ management)."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [document-processing, due-diligence, compliance, file-organization, workspace]
    related_skills: [document-format-conversion, repository-cleanup, project-handover-documentation]
---

# Evidence Package Organization

## Overview

Standard workflow for receiving raw DD/compliance material archives, extracting them, organizing evidence files by numbered conditions/requirements, generating summary indexes, and producing final application forms from templates.

Target output: a clean, flat directory of numbered files that cross-reference to an application form, with a conditions.md summary.

## Workflow

### Step 1: Receive raw archives

Raw materials typically arrive as:
- WeChat-shared `.zip` or `.rar` files (`~/Library/Containers/com.tencent.xinWeChat/.../msg/file/`)
- Email attachments

Always check WeChat's file directory first when the user mentions receiving a file. Copy to `tmp/` (gitignored) for processing.

### Step 2: Extract with encoding handling

Chinese-encoded zip filenames require special handling:

```python
# Python-based extraction handles GBK vs UTF-8
with zipfile.ZipFile(src, 'r') as z:
    for info in z.infolist():
        if info.is_dir(): continue
        raw = info.filename.encode('cp437')  # zip stores non-ASCII in cp437
        try:
            decoded = raw.decode('gbk')  # Chinese Windows uses GBK
        except:
            decoded = raw.decode('utf-8', errors='replace')
```

For `.rar` files, install unrar: `brew install homebrew/cask/rar`. Verify with `unrar t archive.rar`.

**Pitfall**: macOS `unzip -O gbk` often fails with "Illegal byte sequence". Always use Python zipfile with cp437→gbk decode chain.

**Verification**: After extraction, always verify files exist before deleting the archive. Run `ls -la` on the output directory or check expected file count. Never delete the archive before confirming extraction produced files — if the user re-presents an archive they want it processed, not just deleted.

### Step 3: Compare with existing references and prefer original formats

After extraction, scan for:
- **Format upgrades**: `.docx` > `.md`, `.xlsx` > `.csv`. If the raw zip contains a `.docx` (even with a different filename), use it instead of a converted `.md`.
- **Duplicate files**: compare file sizes to identify identical files already in `references/`
- **New content**: screenshots (&#95;ling.png), element tables (要素表.xlsx), manager profiles (.doc) may not exist in references/

When both `.md` and `.pdf` exist for the same document: **only rename the `.pdf`**. The `.md` is an index/reference file; the `.pdf` is the deliverable. Exception: if only `.md` exists, convert to `.docx` with python-docx before discarding.

### Step 4: Organize by numbered conditions

Apply hierarchical numbering matching the application form's evidence list:

| Pattern | Example | Meaning |
|---------|---------|---------|
| `X–Name.pdf` | `2–财务报表.pdf` | Condition 2, single file |
| `X-Y–Name.pdf` | `1-1–AMAC公示.pdf` | Condition 1, item 1 |
| `X-Y-Z–Name.pdf` | `3-1-1–对冲1号合同.pdf` | Condition 3, item 1, file 1 |
| `0–申请表.docx` | Application form (0 = always sorts first) |

**En-dash rule**: Always use en-dash (U+2013 `–`) between the number prefix and the Chinese name. Never use:
- Space (`1-1 名称.pdf`) — renders ugly in terminal
- Hyphen (`1-1-名称.pdf`) — confuses number with name
- Em dash (`1-1—名称.pdf`) — too wide

### Step 5: Create index summary

Write `conditions.md` with a table mapping each condition number to:
- The condition text
- The evidence files that satisfy it
- Key data points (performance numbers, dates, amounts)

### Step 6: Generate application form from template

When a template `.docx` exists (e.g. from a previous submission):
1. Read the template structure with python-docx
2. Fill in the new manager's name and evidence references
3. Save with `0–` prefix for sort order

Ensure the "对应申请辅证材料明细" column uses the exact Chinese filenames from the evidence directory, not English-prefix names.

### Step 7: Workspace conventions

| Path | Purpose | Git-tracked? |
|------|---------|-------------|
| `jul-06/` | Date-based work dir (month-twoDigitDay) | Yes |
| `jul-06/管理人/` | Per-manager subdirectory | Yes |
| `meetings/jul-06.md` | Dated meeting notes | Yes |
| `tmp/` | Temp files (zips, extracts) | No (.gitignore) |
| `references/` | Raw source materials | No (.gitignore) |

Date dir format: three-letter English month + **two-digit** day. E.g. `jul-06`, `aug-01`, `sep-03`. Two digits ensure correct alphabetical sorting alongside other date dirs.

### Step 8: Final cleanup and flat structure

1. **Flatten subdirectories** — move all evidence files from subdirs (`03-products/`, `05-materials/`) into the evidence folder root. The form references files by name, not path.
2. **Delete unreferenced files** — remove any file NOT listed in the application form's evidence column. This includes: old `.md` index files in the evidence folder, intermediate `.csv` files that were replaced by numbered PDFs, and any condition subdirs (`06-team/`, `07-performance/`, `08-risk-control/`) that held working copies.
3. **Delete the tmp/ zip** after confirming successful extraction and file verification.
4. **Only commit**: the application form + evidence PDFs/DOCXs + conditions.md summary.

## Common Pitfalls

### Archive extraction order

**Extract FIRST, verify files exist, THEN delete the archive.** Never delete an archive without first confirming the files extracted correctly. If the user re-attaches/re-presents an archive, they want something done with it — assume re-extract or re-process, not delete.

The correct sequence for every archive operation:
1. Extract to target directory
2. Verify files exist (check with `ls` or expected file count)
3. Only then delete the original archive (.rar/.zip)

Skipping step 2 or reversing steps 1 and 3 destroys the source with nothing to show for it.

### references/ is gitignored — don't try to commit it

**Trigger:** after organizing raw PDFs into `references/<company>/`, `git add references/...` fails with "The following paths are ignored by one of your .gitignore files".

**Rule:** `references/` is deliberately gitignored (comment: "Raw DD materials (keep local only)"). Raw materials live only on disk — never `git add -f` them. Only deliverables under `docs/jul-NN-*/` (filled xlsx, converted md, reports) are committed. This applies even when AGENTS.md's 压缩包处理 row says "commit+push" — that refers to the docs/ outputs, not the raw references themselves. Check `git ls-files references/` (empty = confirmed untracked-by-design).

1. **Filename order reversal** — Chinese company names in pinyin transpose easily (多和美→duohemei, NOT heduomei). Say the Chinese characters aloud to verify.
2. **Verify company name by opening documents before renaming** — Never guess the company name from the directory context or a similar file. A file in `zhenyuan/` directory may still reference `多和美` in its actual content. Open `.docx` files with `python-docx` and check table cells (especially "申请调整的私募管理人名称" row) before committing to a rename. Getting this wrong wastes git history and user trust.
3. **Source file format** — always prefer the original format (.docx over .md, .xlsx over .csv). Check if the source zip has a better version.
3. **md-only fallback** — if only .md exists for a required evidence file, convert to .docx via python-docx before discarding the .md.
4. **git move cascading** — renaming files in git can cause large rename chains. Do all renames in one commit, or use `git mv` for clarity.
5. **Encoded filenames on macOS** — files with Chinese characters extracted from zip show as garbled bytes in ls output but display correctly in Finder. Verify with `file` and `ls -la`.
6. **Duplicate git cleanup** — when adding `references/` to .gitignore, remember `git rm -r --cached references/` first to untrack already-committed files.
7. **PDF rename only** — when both `.md` and `.pdf` exist for a source file, only rename the `.pdf` to its Chinese name. The `.md` keeps its English name (it's the agent's reference). The deliverable is the `.pdf`.
8. **Application form naming mismatch** — the user's final form often uses slightly different Chinese names than what you initially assign. After the user produces the final form, re-check all evidence filenames against the form's evidence column and rename to match if different.

## Verification Checklist

- [ ] Every file in the evidence directory matches an entry in the application form
- [ ] Chinese filenames use en-dash (U+2013 `–`) between number and name — **never** space or hyphen
- [ ] Application form's evidence column uses exact Chinese filenames (not English-prefix names)
- [ ] conditions.md maps every condition to its evidence files
- [ ] No stray `.md`/`.csv` intermediate files remain in the evidence directory
- [ ] No subdirectories inside the evidence folder (everything flat at root)
- [ ] Only 1 application form DOCX (the one with `0–` prefix)
- [ ] tmp/ zip is deleted after extraction
- [ ] `git add` + `git commit` + `git push` completed
- [ ] AGENTS.md updated if new workspace conventions emerged
- [ ] `references/` moved to .gitignore (with `git rm -r --cached references/`) if decided

## Related: yuecai Email Access

For email-based evidence collection (receiving manager questionnaires, valuation reports via Coremail), see `references/coremail-cli-setup.md` — covers `yuecai-mail` CLI tool for IMAP/SMTP access to yuecai Coremail using `lizhiyuan` account.

## Related: Bank Wealth Product Kit (银行理财产品三件套)

For bank wealth products (金米嘉富 series: 产品说明书 + 登记通知书 + 开户通知书), see `references/bank-wealth-product-kit.md` — the 3-PDF field-source mapping, `references/<manager>/` naming, and xlsx 合同录入 fill rules (证件有效期 range vs 合同结束日期 single date, which fields stay constant per issuer).
