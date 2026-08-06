# Session Reference: Enterprise MVP UI Pattern Fixes

Date: 2026-06-29

## 1. Empty ReviewComment Bug

**Problem:** `reviewComment` stored as JSON `{"globalReview":"","materialNotes":{}}`. When `globalReview` is empty string `""`, the code `rc.globalReview || d.reviewComment` falls through because `""` is falsy, showing raw JSON in the textarea.

**Fix:** `rc.globalReview || ''`

**Pattern:** Never use `||` fallback after a variable that could legitimately be empty string, 0, or false.

## 2. Dynamic Button Labels by Status

**Pattern:** In the declaration list table, buttons show different text based on declaration status:
- PENDING/SUBMITTED → "审核"
- APPROVED/REJECTED → "查看"

```javascript
var btnLabel = i.status === 'PENDING' || i.status === 'SUBMITTED' ? '审核' : '查看';
```

## 3. Conditional Score Display

For pending declarations, score column shows "--" instead of the computed score:

```javascript
(i.status === 'PENDING' || i.status === 'SUBMITTED'
  ? '<span style="color:#B0B8C4;font-size:14px">--</span>'
  : aiEval)
```

## 4. Button Size Reference

Matching existing page conventions:
- Activity management: 56px
- Declaration list: 60px (matched to user's preference)
- Enterprise/Policy management: 90px
- User management: 60px
