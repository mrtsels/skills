# Due Diligence Research Document Compilation

Compile a structured Q&A document from live interview draft notes + source materials (尽调问卷/净值表/审计报告).

## Workflow

### Phase 1: Initial Setup

1. Read the 调研纪要 template (has pre-filled Q&A from existing materials + questions marked "待调研确认")
2. Read the user's raw draft notes (zhenyuan draft.md)
3. Write the formal document (`zhenyuan.md` in `docs/jul-NN-zhenyuan/`)

### Phase 2: Map Draft Content to Template Questions

Cross-reference each draft line against the 调研纪要 questions. Fill what you can, leave others as `——待补充`.

| Source | Maps to |
|--------|---------|
| 规模数据 | 公司最新情况 |
| 产品细节（安心一号/臻远一号） | 投资策略与业绩 |
| 方法论/理念 | 投资策略—选股方法 |
| 团队、股权关系 | 公司最新情况—团队背景 |

### Phase 3: Iterative Sync

The user will update the draft incrementally during the meeting. Each time:

1. Re-read the draft to detect new/updated lines
2. Identify which Q&A sections they correspond to
3. `patch` the formal document to add/update content
4. Deduplicate — if new info is already covered elsewhere in the formal doc, consolidate

### Phase 4: Cross-Reference Source Materials

When source docs become available (尽调问卷/docx), search for answers to remaining `待补充` items:

- **尽调问卷** → fill: 产品要素、费率、团队履历、风控设置、压力测试、IT系统、资金来源、财务数据
- **净值表** → fill: 分年度收益/回撤/夏普
- **审计报告** → fill: 财务验证

### Phase 5: Commit After Every Change

Per yuecai-git-workflow rules, commit+push immediately after every file modification — no asking.

## Document Structure

```markdown
# 管理人名称 — 调研纪要（续）

> 基于调研日期及后续沟通整理。仍在进行中，本节仅覆盖已确认部分。

## 公司最新情况
- 规模/团队/股权/财务

## 投资策略与业绩
- 产品要素/方法论/深度价值标准

## 风控与合规
- 投决会/风控/压力测试/IT

## 渠道与募资
- 资金来源/渠道拓展/募资规划

## 管理人核心定位
- 策略风格/竞争理念/规模容量
```

## Common Pitfalls

1. **Draft-to-document drift** — user updates draft but you miss lines. Always re-read the full draft after user says "更新了" / "有了"
2. **Out-of-order updates** — user may add content in any order. Don't assume linear progression. Each draft line may map to a different section.
3. **Duplicate team info** — draft often mentions team/equity structure in multiple places. Put it once under 公司最新情况, avoid repeating in 投资策略 section.
4. **Financial data placement** — 财务数据 (revenue/profit/assets) belongs under 公司最新情况, not 渠道与募资. The 调研纪要 template puts it separately.
5. **Keep 待补充 markers** — don't remove them until you have a verified answer from a source (not from inference).
