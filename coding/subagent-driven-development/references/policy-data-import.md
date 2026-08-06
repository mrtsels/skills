# Policy Data Import from Research to Database

Pattern for importing policy research documents into a production database.

## Context

After completing policy research (04-政策研究), data needs to be imported into the application database so the frontend policy list shows real data instead of placeholders.

## Steps

### 1. Discover the API Contract

First, find how the frontend talks to the backend:

```bash
# Search for the policy list API endpoint
grep -n 'policy/list\|/api/policy\|f_policy' index.html | head -10
```

This reveals the data structure expected by the frontend (field names, types, nested objects).

### 2. Discover the Backend Table Structure

```bash
# Check the SQL migration or model files
grep -rl 'create.*table.*policy\|policy.*entity\|PolicyRepo' src/ | head -5
```

### 3. Read Research Documents

Each policy .md file has a metadata table (YAML-like frontmatter or markdown table):

```python
import re
with open('docs/04-政策研究/province/01-梯度培育管理实施细则.md') as f:
    content = f.read()

# Extract title from first heading
title = re.search(r'^# (.+)', content, re.M).group(1)

# Extract metadata table
meta_match = re.search(r'\| (.+) \| (.+) \|', content)
```

### 4. Map Fields and Insert

```python
policy_data = {
    'title': title,
    'level': 'province',
    'region': '广东省',
    'department': '省工信厅',
    'doc_number': '粤工信规字〔2024〕2号',
    'publish_date': '2024-08-20',
    'content': content,  # or summary
    'aiSummary': ai_summary,
    'tags': ['专精特新', '梯度培育'],  # relevance tags
}
```

### 5. Insert via API

```javascript
// POST /api/policy
await api('/policy', {
    method: 'POST',
    body: policy_data
});
```

### 6. Set Relevance Tags

Tags should reflect the enterprise's actual situation (e.g., Jinpeng's industry, scale, stage). Common tag categories:

- **Industry**: 软件和信息技术服务业, 人工智能, 智能制造
- **Scale**: 中型企业, 专精特新, 小巨人
- **Region**: 广东省, 广州市, 海珠区
- **Stage**: 初创期, 成长期, 成熟期

## Pitfalls

- **Duplicate detection**: Always check if a policy with the same doc_number already exists before inserting.
- **Long content**: Some policies have very long content that may exceed column limits. Truncate or use TEXT/MEDIUMTEXT columns.
- **Character encoding**: Chinese characters must be UTF-8. Check MySQL charset is utf8mb4.
- **Batch vs individual**: Batch insert is faster. The backend API likely accepts a JSON array.
