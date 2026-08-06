# ~/.agents/skills — Skill 库 SSOT

所有 agent（Claude Code / Codex / Hermes）共享的 skill 单一真源目录。

- 真身：本目录（分类结构，`<category>/<skill>/SKILL.md`）
- Hermes：经 `skills.external_dirs` 直连本目录（见 `~/.hermes/config.yaml`）
- Claude Code：经 `~/.claude/skills` symlink 引用
- git 追踪全部内容（私有仓库 mrtsels/agents-skills），敏感文件由 `.gitignore` 显式排除

## 目录结构

```
~/.agents/skills/
├── .gitignore          # 系统垃圾 + 敏感文件排除（无 ignore-all）
├── README.md           # 本文件（含 skill 清单）
├── latex-skills/       # bundle：索引 SKILL.md + 子 skill 目录
├── finance/            # 分类目录
│   └── tonghuashun/
│       └── SKILL.md
└── ego-browser         # 唯一 symlink（指向 /Applications/ego lite.app）
```

分类：`academic` `agent-patterns` `apple` `automation` `autonomous-ai-agents` `creative` `data-science` `devops` `email` `finance` `github` `infrastructure` `latex-skills` `mcp` `note-taking` `paper` `productivity` `research` `resume` `software-development` `workflow` `writing`

## Skill 清单

> 生成时间: 2026-08-06。bundle 子 skill 通过其索引 SKILL.md 访问。

### academic
- academic-citation-manager
- academic-cv-builder
- academic-study-methods
- academic-tone-guide
- automated-review-guide
- cuhk-poster-latex
- grad-school-guide
- internship-report
### agent-patterns
- knowledge-organization
- skill-farm-maintenance
### apple
- apple-mail-cli
- apple-music-control
- apple-native-cli
- apple-notes
- apple-reminders
- internal-device-access
- macos-apple-intelligence
- macos-computer-use
- macos-git-proxy-troubleshoot
- macos-network-diagnostics
- macos-smb-access
- macos-storage-management
### automation
- cron-agent-flow
- deepseek-cost-tracking
- duo-sso-automation
- email-automation
- wechat-push-message
### autonomous-ai-agents
- agent-reach
- coding-agents
- computer-use-workflow
- cusis-login
- dynamic-workflow
- graphify
- hermes-agent
- hermes-claude-workflow
- hermes-desktop-plugins
- hermes-for-agents
- hermes-themes
- holographic-memory-migration
- install-agent-cli-tool
- wechat-ai-bridge
### backend
- cpp-numerics-pybind11
- database-schema-documentation
- distributed-systems-guide
- hermes-s6-container-supervision
- spring-logging
- sql-seed-maintenance
### coding
- algorithm-visualizer-guide
- algorithms-complexity-guide
- bash-cli-patterns
- bash-scripting
- de-ai-ify-code
- debug-shell-startup
- full-output-enforcement
- python-code-style
- repository-cleanup
- spike
- subagent-driven-development
- systematic-debugging
- test-driven-development
- writing-plans
- **cs-skills**（bundle: dblp-api, formal-verification-guide, software-engineering-research, software-heritage-api）
### creative
- architecture-diagram
- brandkit
- excalidraw
- image-to-code
- imagegen-frontend-mobile
- imagegen-frontend-web
- industrial-brutalist-ui
- minimalist-ui
- redesign-existing-projects
- sketch
- svg-from-pdf-figure
- **frontend-design-skills**（bundle: design-taste-frontend, design-taste-frontend-v1, gpt-taste, high-end-visual-design, stitch-design-taste）
### data-science
- ai-model-benchmarking
- astrophysics-data-guide
- bayesian-statistics-guide
- computer-vision-guide
- csv-data-analyzer
- data-anomaly-detection
- data-cleaning-pipeline
- data-cog-guide
- data-collection-automation
- handwriting-recognition-guide
- huggingface-api
- huggingface-inference-guide
- json-data-visualizer
- jupyter-live-kernel
- jupyter-notebook-guide
- linear-algebra-applications
- llm-evaluation-guide
- llm-from-scratch-guide
- ml-experiment-tracker
- ml-pipeline-guide
- modeling-strategy-guide
- nlp-toolkit-guide
- numerical-methods-guide
- pandas-data-wrangling
- pdf-records-extraction
- pdf-to-readable-markdown
- power-analysis-guide
- python-causality-guide
- python-dataviz-guide
- python-reproducibility-guide
- pytorch-guide
- pytorch-lightning-guide
- quantum-computing-guide
- responsible-ai-guide
- tensorflow-guide
- transformer-architecture-guide
- vision-chunk-ocr
- **ai-ml-skills**（bundle: dl-transformer-finetune, domain-adaptation-papers-guide, generative-ai-guide, keras-deep-learning, kolmogorov-arnold-networks-guide, prompt-engineering-research, reinforcement-learning-guide, vmas-simulator-guide）
- **code-exec-skills**（bundle: google-colab-guide, kaggle-api-guide, r-reproducibility-guide, sandbox-execution-guide）
- **math-skills**（bundle: lean-theorem-proving-guide, oeis-api, symbolic-computation-guide, topology-data-analysis）
### devops
- aesculap-setup
- apple-container-build
- ccx-proxy-setup
- cuhk-duo-bypass
- docker-logging
- docker-production-deployment
- kanban-orchestrator
- offline-docker-deployment
- webhook-subscriptions
- windows-ssh-setup
- windows-thinkpad
- yuecai-scanner-download
### email
- agently-mail
- agently-mail-formatting
- himalaya
- imap-attachment-download
### finance
- a-stock-paper-trade
- announcement-search
- financial-data-provisioning
- hithink-astock-selector
- hithink-fund-query
- hithink-industry-query
- hithink-market-query
- market-analysis-guide
- multi-factor-strategy
- news-search
- quant-factor-screener
- quantitative-finance-guide
- report-search
- tonghuashun
- wechat-article-search
### frontend
- code-flow-visualizer
- d3-visualization-guide
- extjs-api-discovery
- hermes-agent-dashboard-install
- inspecting-hermes-desktop-dom
- local-dev-proxy
- playwright-performance-optimization
- playwright-spa-automation
- vanilla-js-spa-patterns
### github
- github
- github-kb
### infrastructure
- coremail-imap
- kylin-vm-deployment
### latex-skills
- academic-writing-latex
- arxiv-latex-source
- arxiv-preprint-template
- beamer-presentation-guide
- bibliography-management-guide
- latex-debugging
- latex-drawing-collection
- latex-drawing-guide
- latex-ecosystem-guide
- latex-ocr-guide
- latex-templates-collection
- latex-translation-guide
- math-typesetting-guide
- md-to-pdf-academic
- overleaf-cli-guide
- overleaf-collaboration-guide
- tex-render-guide
- tikz-diagrams-guide
### mcp
- native-mcp
- open-computer-use-mcp
### note-taking
- lecture-notes
- obsidian
- obsidian-citation-guide
- obsidian-zotero-guide
- zotero-actions-tags-guide
- zotero-addon-market-guide
- zotero-ai-butler-guide
- zotero-arxiv-daily-guide
- zotero-better-bibtex-guide
- zotero-better-notes-guide
- zotero-mcp-guide
- zotero-mdnotes-guide
- zotero-night-theme-guide
- zotero-pdf-translate-guide
- zotero-pdf2zh-guide
- zotero-reference-guide
- zotero-scholar-guide
- zotero-style-guide
### paper
- academic-paper-summarizer
- ai-agent-papers-guide
- ai-security-papers-guide
- anomaly-detection-papers-guide
- autonomous-agents-papers-guide
- code-llm-papers-guide
- conference-paper-template
- conference-proceedings-guide
- deep-learning-papers-guide
- gaussian-splatting-papers-guide
- graph-learning-papers-guide
- graphical-abstract-guide
- llm-aiops-guide
- markdown-academic-guide
- paper-critique-framework
- paper-parse-guide
- paper-reading-assistant
- paper-recommendation-guide
- paper-to-agent-guide
- papers-we-love-guide
- publication-figures-guide
- **academic-writing-skills**（bundle: abstract-writing-guide, discussion-writing-guide, ml-paper-writing, research-paper-writer, response-to-reviewers, thesis-writing-guide）
- **composition-skills**（bundle: introduction-writing-guide, literature-review-writing, methods-section-guide, scientific-writing-guide, scientific-writing-resources, scientific-writing-wrapper）
- **paper-review-skills**（bundle: peer-review-guide, rebuttal-writing-guide, review-response-guide, scientify-write-review-paper）
- **templates-skills**（bundle: elegant-paper-template, novathesis-guide, scientific-article-pdf, sjtuthesis-guide, thesis-template-guide, thuthesis-guide）
- **writing-polish-skills**（bundle: academic-translation-guide, academic-writing-refiner, ai-writing-humanizer, grammar-checker-guide, paper-polish-guide）
### productivity
- ai-readiness-assessment
- architecture-design-guide
- asset-pool-admission
- churn-autopsy
- client-health-dashboard
- client-proposal-generator
- concept-map-generator
- consulting-problem-solving
- document-format-conversion
- document-sanitization
- docx
- docx-content-patching
- docx-edit-rules
- email-triage
- finance-deck-build
- financial-report-docx-update
- fitness-consultation
- ml-web-demo
- notion
- ocr-and-documents
- officecli
- onboarding-checklist
- pdf
- pdf-extraction-guide
- pdf-math-translate-guide
- petdex
- powerpoint
- pptx
- quant-lecture-notes
- quant-research-backtesting
- roi-calculator
- saas-replacement-planner
- scanned-pdf-ocr
- social-media-clients
- sow-generator
- summarize-slides
- tencent-docs
- training-pipeline-debugging
- tui-widgets
- weekly-business-report
- xlsx
- xlsx-contract-data-fill
- **diagram-skills**（bundle: excalidraw-diagram-guide, kroki-diagram-api, mermaid-architect-guide, mermaid-diagram-guide, plantuml-guide, scientific-illustration-guide, tldraw-whiteboard-guide）
- **document-skills**（bundle: docsgpt-guide, grobid-pdf-parsing）
- **find-skills**（bundle）
- **meeting-skills**（bundle: meeting-intelligence, meeting-notes, meeting-to-tasks）
- **ocr-translate-skills**（bundle: multilingual-research-guide）
### research
- action-research-guide
- ai-scientist-v2-guide
- anystyle-api
- arxiv-api
- arxiv-batch-reporting
- arxiv-cli-tools
- arxiv-paper-processor
- assessment-design-guide
- auto-deep-research-guide
- chinese-policy-research
- citation-alert-guide
- citation-assistant-skill
- citation-chaining-guide
- citation-network-builder
- citation-network-guide
- citation-style-guide
- claude-academic-workflow-guide
- claude-scientific-guide
- content-retrieval
- database-comparison-guide
- datagen-research-guide
- dataset-finder-guide
- deep-searcher-guide
- financial-market-research
- google-scholar-guide
- google-scholar-scraper
- graphiti-guide
- grounded-citations
- h-index-guide
- knowledge-graph-construction
- large-document-reader
- latte-review-guide
- llm-scientific-discovery-guide
- npcpy-research-guide
- ontology-design-guide
- open-access-guide
- open-access-mining-guide
- open-researcher-guide
- open-science-guide
- repository-harvesting-guide
- research-workflow-automation
- web-sourced-market-brief
- zlib-ebook-download
- **automation-skills**（bundle: aim-experiment-guide, kedro-pipeline-guide, mle-agent-guide, rd-agent-guide）
- **citation-skills**（bundle: bibtex-management-guide, jabref-reference-guide, jasminum-zotero-guide, mendeley-api, onecite-reference-guide, papersgpt-zotero-guide, papis-cli-guide, reference-manager-comparison, zotero-api, zotero-gpt-guide, zotfile-attachment-guide）
- **deep-research-skills**（bundle: gpt-researcher-guide, in-depth-research-guide, khoj-research-guide, kosmos-scientist-guide, local-deep-research-guide, meta-synthesis-guide, scoping-review-guide, systematic-review-guide, tongyi-deep-research-guide）
- **fulltext-skills**（bundle: bioc-pmc-api, core-api-guide, dataverse-api, doaj-api, hal-archive-api, institutional-repository-guide, interlibrary-loan-guide, osf-api, pmc-ftp-bulk-download, pmc-oai-api, preprint-servers-guide, unpaywall-api）
- **humanities-skills**（bundle: digital-humanities-guide, ethical-philosophy-guide, history-research-guide, philosophy-research-guide, political-history-guide）
- **knowledge-graph-skills**（bundle: notero-zotero-notion-guide, openspg-guide, rag-methodology-guide, zotero-markdb-connect-guide）
- **research-report-skills**（bundle: quant-research-report, research-visit-memo, structured-research-report, technical-research-report）
- **search-skills**（bundle: baidu-scholar-guide, base-academic-search, biorxiv-api, boolean-search-guide, chatpaper-guide, citeseerx-api, deep-literature-search, eric-education-api, europe-pmc-api, findpapers-guide, ieee-xplore-api, lens-scholarly-api, mesh-terms-guide, open-library-api, open-semantic-search-guide, openaire-api, openalex-api, plos-open-access-api, pubmed-api, scielo-api, semantic-scholar-api, share-research-api, systematic-search-strategy, worldcat-search-api）
### resume
- application-form-filler
- career-changer-translator
- cold-email-writer
- cover-letter-generator
- creative-portfolio-resume
- executive-resume-writer
- interview-prep-generator
- job-description-analyzer
- linkedin-profile-optimizer
- offer-comparison-analyzer
- portfolio-case-study-writer
- project-to-resume
- reference-list-builder
- research-entry-from-codebase
- resume-ats-optimizer
- resume-bullet-writer
- resume-formatter
- resume-latex-workflow
- resume-quantifier
- resume-section-builder
- resume-tailor
- resume-version-manager
- resume-writing-style
- resume-zh-bullet-style
- salary-negotiation-prep
- tech-resume-optimizer
### scripts
### workflow
- demo-feedback-to-code
- document-analysis-workflow
- fuji-xerox-scanner-access
- post-investment-data-maintenance
- quant-academy-task-workflow
- resume-bullet-from-workflow
- yuecai-doc-maintenance
### writing
- humanizer
- markdown-math
- mermaid-diagrams
- project-handover-documentation
- repo-documentation
- simplified-technical-english
### latex-skills
- academic-writing-latex
- arxiv-latex-source
- arxiv-preprint-template
- beamer-presentation-guide
- bibliography-management-guide
- latex-debugging
- latex-drawing-collection
- latex-drawing-guide
- latex-ecosystem-guide
- latex-ocr-guide
- latex-templates-collection
- latex-translation-guide
- math-typesetting-guide
- md-to-pdf-academic
- overleaf-cli-guide
- overleaf-collaboration-guide
- tex-render-guide
- tikz-diagrams-guide
## 命名规范

1. **一律 kebab-case**：小写 + 连字符，禁下划线/驼峰（`pdf-extraction-guide` ✓，`pdfExtraction` ✗）
2. **名称即主题**：以领域关键词开头，让同类可聚合（`arxiv-api`、`arxiv-batch-reporting`）
3. **后缀表示形态**：
   - `-guide`：教程/方法论（`pytorch-guide`）
   - `-api`：API 集成（`openalex-api`）
   - `-template`：模板（`conference-paper-template`）
   - `-skills`：聚合 bundle 索引（`search-skills`）
   - `-builder/-generator`：产出物生成器
   - 其余默认动词短语（`pdf-extraction-guide`）
4. **长度 ≤ 35 字符**，超长需精简
5. **bundle 索引**：`<主题>-skills`，子 skill 用独立名词

## SKILL.md 写作规范

### frontmatter（必填）

```yaml
---
name: <目录名一致>
description: "<单行，≤150 字符，说明触发条件与功能>"
---
```

- `name` 必须与目录名完全一致
- `description` 必须双引号包裹；以触发场景开头（"Use when …" / "当用户需要…"），不用句号结尾
- 可选：`tags`（小写复数）、`metadata`（保留第三方原作者信息）

### 正文结构

```markdown
# <Title>

Trigger: <什么场景触发本 skill>

## <工作流/步骤>        # 按执行顺序，编号步骤
## Pitfalls            # 坑点，每条一行
## References          # 引用文件表（可选）
```

规则：
- 标题层级从 `#`（skill 名）开始，正文小节用 `##`
- 步骤用有序列表（1. 2. 3.），关键命令给完整代码块
- Pitfalls 每条一行，写"发生了什么 → 怎么避免"
- 中文 skill 正文用中文，英文 skill 用英文，不混写
- 长度控制：主 SKILL.md ≤ 10KB，长内容放 `references/`
- 合并 skill 时按主题混写，禁止"第一部分/第二部分"式分段

### 敏感信息红线

- 禁出现：个人姓名、电话、个人/公司邮箱、密码、内网 IP、内部系统账号
- 必须写示例时用占位符（`{Author Name}`、`example.com`）
- 引用私有系统（粤财/衡泰/NAS）的 skill 整体加入 `.gitignore`

## 维护命令

```bash
# 清单重新生成（写入 README 的 Skill 清单段）
python3 scripts/gen-manifest.py

# git（禁 add .）
git add <具体路径> && git commit -m "type: subject" && git push
```

提交前必须跑 PII 扫描（见 `agent-patterns/skill-farm-maintenance`）。
