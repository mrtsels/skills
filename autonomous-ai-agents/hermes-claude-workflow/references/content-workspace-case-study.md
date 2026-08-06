# Content Workspace Case Study: Doctor Fitness Consultation

> Session: June 20, 2026 — Claude Code v2.1.170, DeepSeek V4 Flash

## Context

**User:** A doctor who helps female patients with muscle gain and fat loss
**Tool:** Claude Code CLI (--bare mode via Hermes Agent)
**Goal:** Build a structured workspace that produces weekly fitness plans + ChatGPT Image 2 prompts
**Output:** 6 reusable plans + intake template + outline + image prompts

## Full Conversation Flow

### Turn 1 — Plan First
```
User: read CLAUDE.md 给我如何开始的建议
  AI: 项目全新状态，告诉我患者情况即可
User: 先列一个整体的计划，存为TASKS.md /plan
  AI: 创建 TASKS.md（5 个阶段：P1-P5）
```

**Key lesson:** User did NOT want to jump into patient intake. They wanted to see the entire workflow first. Always offer to create a task plan before executing.

### Turn 2 — Granularity Alignment
```
User: + 把"对齐颗粒度"记在CLAUDE.md里
  AI: 写入 CLAUDE.md 5.5 节（4条硬规则：先读TASKS/对齐粒度/同步更新/TASKS是主线）
```

**Key lesson:** When user enforces a procedural constraint, it must go into CLAUDE.md (not just memory). The next Claude Code session reads it automatically.

### Turn 3 — Scope Discovery
```
User: 我只知道全是女性，不分年龄，怎么办？
  AI: 方案A=单次模板 / B=预制计划 / C=两者结合
User: 先分大类 + 建模版 + 执行相应的计划 /plan
```

**Key lesson:** User revealed scope only after being asked. Classification system emerged from iterative refinement, not upfront specification.

### Turn 4 — Classification Design
```
AI proposed: 设备(居家/健身房)×时间(低频/中频)×体重(常规/大体重) = 2×2×2 = 8 combos
  User approved → Simplified to 6 plans (A-F)
```

**Key lesson:** Present options with clear dimensions, let user approve the simplified set. Confirm classification BEFORE building content.

### Turn 5 — Bulk Generation + Subagent Fallback
```
AI: 启动 3 Agent 并行生成（失败：模型名错误）
AI: fallback to serial writing → 6 plans + 6 prompt sets + template
```

**Key lesson:** Sub-agents may fail due to model routing through CC Switch. Always have a serial fallback plan ready.

### Turn 6 — End-to-End Verification
```
User: OK你编一个患者，测试一下
  AI: 创建小美（32F, 162cm/70kg, 居家, 减脂）
  → 匹配计划A → 个性化 → outline.md + chatgpt-image-prompts.md
```

**Key lesson:** Self-created test case validates the entire pipeline. User didn't need to provide real patient data.

### Turn 7 — Package as Skill
```
User: 把这个流程做成skill
User: 打包zip存到桌面
  AI: SKILL.md created + zip packaged
```

**Key lesson:** Final deliverable isn't the content — it's the reusable workflow skill.

## Pitfalls Encountered

1. **Sub-agent model routing failure** — CC Switch didn't route model name correctly for sub-agent spawns. Fallback to serial was necessary.
2. **Initial tendency to dive into details** — AI wanted to jump into patient intake; user wanted the plan first. The skill's Pattern H now enforces plan-first.
3. **Missing classification confirmation** — Had the AI generated 24 plans before user approval, 18 would have been wasted.

## Output Artifacts

```
fitness/
├── CLAUDE.md                      ← Behavioral rules + workflow
├── TASKS.md                       ← 2-phase task plan (build-out + consultation)
├── templates/
│   └── patient-intake-template.md ← Information collection questionnaire
├── plans/
│   ├── plan-A-home-low.md         ← Home, 2-3 days/week
│   ├── plan-B-home-mid.md         ← Home, 4-5 days/week
│   ├── plan-C-gym-low.md          ← Gym, 2-3 days/week
│   ├── plan-D-gym-mid.md          ← Gym, 4-5 days/week
│   ├── plan-E-heavy-home.md       ← Heavy/BMI≥28, home
│   └── plan-F-heavy-gym.md        ← Heavy/BMI≥28, gym
├── prompts/
│   ├── prompts-A-home-low.md
│   ├── prompts-B-home-mid.md
│   ├── prompts-C-gym-low.md
│   ├── prompts-D-gym-mid.md
│   ├── prompts-E-heavy-home.md
│   └── prompts-F-heavy-gym.md
├── outline.md                     ← Generated for test case "小美"
└── chatgpt-image-prompts.md       ← 11 DALL·E 3 prompts
```
