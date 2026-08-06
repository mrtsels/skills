# Financial Research Report — Writing Conventions

## Report Structure

For research reports on financial/exchange/algorithmic trading topics:

1. **Market Details** — trading hours, auction rules, order types
2. **Alternative Venues & Trading Systems** — dark pools, SOR
3. **Agency Trading Algorithms** — definition + parameters + flowchart + code + edge cases
4. **Broker Implementation Differences** — comparison table with concrete differences and consequences
5. **Evaluation Metrics** — table with metric, definition, applies-to, target
6. **References**

## Algorithm Documentation Format

Each algorithm in section 03 must follow this structure:

```markdown
### [Number]. [Name] — [Category]

**Definition:** One-line description from the source document.

**Use case:** When to use this algorithm.

**Parameters:**

- **ParamName** — Description
- **ParamName** — Description

```mermaid
flowchart TD
    [logic flow]
```

```python
[clean Python implementation with dataclass Order + class with run()]
```

**Edge cases:**
- **Order incompletion** — how handled
- **Inadequate liquidity** — how handled
- **Open & close auctions** — how handled
```

### Python Code Style for Algorithm Implementation

- Use `@dataclass Order` for input parameters
- Implement as a class with `run(self, order)` returning executed quantity
- No verbose docstrings or AI-sounding comments
- No placeholder descriptions like "模拟" or "实际中通过经纪商 API 下单"
- Mock helpers return clean values (return qty, return qty // 2)
- Type hints required

### Mermaid Flowchart Style

- Simple TD (top-down) layout
- Diamond nodes for decisions `{condition?}`
- Rectangular nodes for actions `[action]`
- Edge labels: `-- Yes -->`, `-- No -->`
- No background colors or classDef styling

## Formatting Preferences

- **Parameter lists**: dot list (`- **Param** — description`), NOT tables
- **Broker comparison tables**: `| Dimension | Side A | Consequence | Side B | Consequence |`
- **English headings**: Title Case (capitalize all major words)
- **Section numbering**: `## 01 — Title`, `### A. Subtitle`
- **Edge case headers**: Use `Open & close auctions` (with ampersand), not `Open/close auctions`
- **Terminology**: Match source document exactly (e.g. "Agency Trading algorithms" not "Agency Trading Algorithms" if source says so)

## AI-Issue Removal Checklist

Before finalizing any code or text:

- [ ] No "模拟" or "in practice" placeholder comments in code
- [ ] No verbose explanatory prose
- [ ] No AI-isms: "comprehensive", "it is important to", "it should be noted", "in conclusion", "delve into"
- [ ] Code is clean and focused — typed, minimal, runnable
- [ ] Python code blocks pass `ast.parse()` syntax check
