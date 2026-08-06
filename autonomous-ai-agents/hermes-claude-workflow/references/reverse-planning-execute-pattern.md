# 反向模式：Claude 规划 → Hermes 执行

## 何时使用

用户明确说「让 Claude 生成方案，你来执行」。信号词：
- "和claude配合，让它生成一个计划，然后你执行"
- "让claude做个方案给我看看"
- 用户想要架构/方案层面的输出，但希望 Hermes 做机械实现

与标准模式（Hermes 规划 → Claude 编码）相反。

## 工作流

```
用户: "让 Claude 出个方案，你来落地"
     ↓
Hermes: 构造精确 prompt（包含项目上下文、约束条件、输出格式要求）
     ↓
terminal(claude --model sonnet --bare --dangerously-skip-permissions --output-format json -p '...')
     ↓
Claude Code 返回结构化方案（含文件路径、类设计、实施顺序、验证方法）
     ↓
Hermes: 按方案逐模块实现（write_file/patch/terminal）
     ↓
Hermes: 验证（JS syntax / YAML validity / XML well-formed / HTML structure）
     ↓
Hermes: commit
```

## 关键差异 vs 标准模式

| 维度 | 标准模式 | 反向模式 |
|------|---------|---------|
| 规划者 | Hermes | Claude Code |
| 执行者 | Claude Code | Hermes |
| prompt 构造 | Hermes 写精确任务描述 | Hermes 写上下文+约束，Claude 输出方案 |
| 实现方式 | Claude 改文件 | Hermes 用 write_file/patch |
| 验证方式 | Claude 跑测试 | Hermes 做静态检查 |
| 适用场景 | 编码/测试/PR | 基础设施/配置/文档重构/机械实现 |

## Prompt 构造要点（反向模式）

Claude Code 输出方案而非代码，所以 prompt 需要：
1. 完整项目上下文（技术栈、目录结构、约束）
2. 明确的输出格式要求（分模块、列文件路径、设计要点、验证方法）
3. 让 Claude 设计而非实现——prompt 里注明 "请输出实施计划，不要写代码"
4. 包含用户的语言偏好（中文/英文）

## 实际案例（本 session）

见 `references/reverse-logging-plan-prompt.md`：为 Spring Boot 项目设计日志追踪基础设施。

## Pitfalls

- Claude Code 可能会在方案中嵌入代码片段——Hermes 需要自行判断哪些是方案设计（保留）哪些是代码实现（用 write_file 替代）
- 方案可能过于详细或偏向特定技术栈——Hermes 负责判断方案与实际环境的兼容性
- 方案中的文件路径建议 vs 实际目录结构可能有偏差——Hermes 在实现时自行修正
- Claude 返回的 JSON 结果可能非常长（此 session: ~19K tokens）——Hermes 需要读完整，提取关键信息
