# PDF Text Cleanup — Reusable Functions

> ⚠️ **Limitation notice**: The automated line-joining functions below are provided for quick pass-through cleanup only. They are **not reliable** for Chinese legal/regulatory documents (laws, regulations, policy notices). These documents have unique structure (inline section headers, merged title elements, nested numbering) that heuristics cannot correctly handle. **The user prefers manual section-by-section formatting** for such documents — see the "Manual Formatting Workflow" section in the parent SKILL.md.

Reusable cleanup functions for text-based Chinese PDF extraction post-processing. Drop into any script after `fitz.get_text()` extraction.

## Full Cleanup Pipeline

```python
import re

def clean_text(content, remove_page_headers=True):
    """Clean PDF-extracted Chinese text: page markers, headers, broken lines."""
    lines = content.split('\n')

    # Step 1: Remove page comment markers
    lines = [l for l in lines if not l.strip().startswith('<!-- Page')]

    # Step 2: Remove repeated 3-line page headers
    # e.g. "国家金融监督管理总局规章 / 发布 / - N -"
    if remove_page_headers:
        cleaned = []
        i = 0
        while i < len(lines):
            if (i + 2 < len(lines) and
                lines[i].strip() == '国家金融监督管理总局规章' and
                lines[i+1].strip() == '国家金融监督管理总局发布' and
                re.match(r'^-\s*\d+\s*-$', lines[i+2].strip())):
                i += 3
                continue
            cleaned.append(lines[i])
            i += 1
        lines = cleaned

    # Step 3: Remove standalone page number lines
    lines = [l for l in lines if not re.match(r'^-\s*\d+\s*-$', l.strip())]

    # Step 4: Join broken lines
    sentence_end = set('。！？；：」』）】】、，,.')
    section_starters = ['第', '（', '(', '一、', '二、', '三、', '四、', '五、',
                        '六、', '七、', '八、', '九、', '十、',
                        '第一章', '第二章', '第三章', '第四章', '第五章',
                        '第六章', '第七章', '第八章',
                        '第一条', '第二条', '第三条', '第四条', '第五条',
                        '第六条', '第七条', '第八条', '第九条', '第十条',
                        '第十一条', '第十二条', '第十三条', '第十四条',
                        '第十五条', '第十六条', '第十七条', '第十八条',
                        '第十九条', '第二十条']

    result = []
    for i, line in enumerate(lines):
        if not line.strip():
            result.append('')
            continue

        if result and result[-1]:
            prev = result[-1]
            prev_stripped = prev.strip()
            curr_stripped = line.strip()

            should_join = True

            if prev_stripped and prev_stripped[-1] in sentence_end:
                should_join = False

            if curr_stripped:
                for s in section_starters:
                    if curr_stripped.startswith(s):
                        should_join = False
                        break

            if len(prev_stripped) < 15 and prev_stripped and prev_stripped[-1] not in '的、，':
                should_join = False

            if should_join:
                result[-1] = prev + line
                continue

        result.append(line)

    # Step 5: Normalize whitespace
    result = [re.sub(r' +', ' ', l) for l in result]
    result = [l.rstrip() for l in result]

    # Step 6: Remove leading blank lines
    while result and not result[0].strip():
        result.pop(0)

    return '\n'.join(result)


def second_pass(content):
    """Fix blank-line-separated fragments from PDF extraction."""
    lines = content.split('\n')
    sentence_end = set('。！？；：」』）】】、，,.')
    section_starters = ['第', '（', '(', '一、', '二、', '三、']

    result = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if (line.strip() and i + 2 < len(lines)
            and not lines[i+1].strip()
            and lines[i+2].strip()
            and line.strip()[-1] not in sentence_end):
            nxt = lines[i+2].strip()
            if not any(nxt.startswith(s) for s in section_starters):
                result.append(line + nxt)
                i += 3
                continue
        result.append(line)
        i += 1

    # Collapse multiple consecutive blank lines
    cleaned = []
    prev_empty = False
    for l in result:
        if not l.strip():
            if not prev_empty:
                cleaned.append('')
                prev_empty = True
        else:
            cleaned.append(l)
            prev_empty = False

    return '\n'.join(cleaned)


def cleanup_full(md_path, remove_page_headers=True):
    """Apply full cleanup pipeline to a markdown file in-place."""
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    content = clean_text(content, remove_page_headers)
    content = second_pass(content)
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return len(content)
```

## Usage Examples

```python
# Simple text PDF (信托法): no special page headers
cleanup_full('path/to/中华人民共和国信托法.md', remove_page_headers=False)

# Document with NFR repeated headers (信托公司管理办法)
cleanup_full('path/to/信托公司管理办法（2025）.md', remove_page_headers=True)

# Already clean (textutil .doc conversion): just remove PAGE footer
doc_lines = content.split('\n')
doc_lines = [l for l in doc_lines if 'MERGEFORMAT' not in l]
```

## Pitfalls

- **Over-joining headings**: Very short lines (<15 chars) that end in `的、，` may get wrongly joined to the next line. The `len < 15` guard handles most cases.
- **File-specific headers**: The 3-line header pattern `规章/发布/-N-` is specific to NFR documents — pass `remove_page_headers=False` for other PDFs.
- **Blank lines in tables**: The second pass may over-join cell values in table-like sections. Spot-check after cleanup.
