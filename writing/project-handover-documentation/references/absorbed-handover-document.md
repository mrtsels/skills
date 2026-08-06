---
name: handover-document
description: 工作交接文档撰写 — 面向中国企业甲方，总分结构，单文件汇总，关键信息前置
category: software-development
---

# 工作交接文档撰写

交接对象是接手你工作的同事，不熟悉项目细节。文档必须做到**拿过来就能上手**。

## 结构要求（严格执行）

### 1. 架构图和ER图的位置

**README 单文件交接：** 标题之下、目录之前，先放**系统架构图**（Mermaid flowchart）和**数据库 ER 图**（Mermaid erDiagram），让接手人第一眼看到系统全貌。两图各占一个独立章节，用 `##` 标题。

**HANDBOOK 多章节交接：** 架构图放在 `## 二、项目全景` 开头，ER 图放在 `## 四、数据库核心表与权限` 开头。不在顶部重复，目录在前。

#### ER 图规则

**用 Mermaid `erDiagram` 语法直接内嵌在 markdown 中**，不依赖外部 HTML/SVG 文件。

写法要点：
- 类型中的括号用下划线代替：`varchar(64)` → `varchar_64`
- PK/FK 直接标注在字段后
- 关系行用 `||--o{`（一对多）、`}o--||`（多对一）、`||--||`（一对一）
- 每个字段的注释用英文双引号包裹
- `erDiagram` 块放在 markdown 的 ` ```mermaid ` fenced block 中
- ER 图的 DDL 数据从 `init.sql` 解析获得（不是猜测），FK 关系从 JPA 实体注解获取

> **Mermaid 语法坑：** 注释（双引号内的文本）中不能包含 `/` 字符，Mermaid 会解析失败。用 `-` 代替，如 `"创新型-省级-小巨人"`。

#### 补充可视化：实体类图

除了 `erDiagram`，可以用 Mermaid `classDiagram` 补充展示 **JPA 实体类之间的继承和关联关系**（如 BaseEntity 基类、`--|>` 继承箭头）。classDiagram 和 erDiagram 一起放在同一个 markdown 文件中，不生成独立 HTML 文件。

写法要点：
- 每个实体是一个 `class` 块，字段前加 `+`（public）
- 继承用 `--|>` 箭头，标注 `: extends`
- 关联用 `"1" --> "0..*"` 标注基数
- FK 字段用 Java 类型（`Long enterpriseId`）而不是数据库类型

#### 架构图规则

用 Mermaid `flowchart TD`（自顶向下）或纯 ASCII 分层架构图。每层下方紧跟一行文字说明（技术栈、角色、关键配置）。

写法要点：
- 层与层之间用 `subgraph` 分组
- 虚线箭头用 `-.->` 表示弱依赖（如外部 API 调用）
- 文本换行用 `<br/>`

### 2. 目录紧随其后

两图之后放目录（TOC），接收者知道内容范围、可快速跳转。

### 3. 总分结构，不分散

- 所有信息集中在**一个文件**（README.md），不分多份文档到处跳转
- 先总览，再逐项展开
- 关键信息往前放（服务器地址、SSH方式、账号密码）

### 4. 必含内容

| 模块 | 内容 |
|------|------|
| 项目概况 | 一句话定位、技术栈、团队、账号密码 |
| 系统架构 | Mermaid flowchart 分层架构图 + 各层说明 |
| 数据库设计 | Mermaid erDiagram + classDiagram（10 张表概览） |
| 从零搭建 | 分Step: 数据库→编译→启动→验证，每个Step一条命令 |
| 数据库 | 连接信息、表清单、账号密码、数据迁移注意点 |
| 业务流 | 三端操作流程图、核心数据流 |
| 评分引擎 | 规则说明、四维评分 |
| 已知问题 | 按严重程度排序(P0/P1/P2)，附兜底方案 |
| 演示指南 | 每步操作、核心展示点、数据来源 |
| API清单 | 全部Controller端点一览 |

### 5. 已知问题章节

按优先级分三级：

| 级别 | 标注 | 内容 |
|------|------|------|
| P0 紧急 | 🔴 | 安全漏洞、系统不可用、数据风险——须优先修复 |
| P1 高 | 🟡 | 健壮性问题、功能缺陷——须关注 |
| P2 中 | 🟢 | 可维护性、代码质量——持续改进 |

每条问题标注**来源文件:行号**，方便定位。

### 6. 部署章节

- 服务器无网络是事实，不要写"如服务器无网络"
- 写清楚从0到启动的每个Step
- 能预配置的就预配好（如docker-compose extra_hosts），不要留给同事手工操作
- 注意延展性：IP用变量不硬编码

### 7. CLI工具设计

- 提供 `enterprise start/stop/status/logs` 一键管理
- 支持 `-h`/`--help`/`help` 和 `-v`/`--version`
- 路径自动检测，支持 `ENTERPRISE_HOME` 环境变量

### 8. 代码更新流程（部署后的运维）

面向接手运维同事的代码更新说明，参考 `references/code-update-process.md` 模板。关键规则：

- **Maven JAR 保持原名**：不要改名为 `app.jar`，CLI 用 `enterprise-mvp-*.jar` 的 glob 查找
- **热更新不需要重建 Docker 镜像**：`docker cp` 替换容器内文件再重启
- **不要 `rm` 源码文件**：`index.html` 是源码正本，不是临时拷贝
- **后端就绪用轮询（每 3s，最多 90s）**，不用固定 sleep
- **CLI 也能自更新**：检测项目根是否有新版 CLI 脚本并复制到 `/usr/local/bin`

## 格式约定

- 中文文档，术语可保留英文
- 表格比段落清晰
- 命令行用代码块
- 文件路径用反引号
- CLI 命令表必须完整（对照 `enterprise` 源码的 case 分支），所有文档的 CLI 表要保持一致。常见遗漏：`restart`、`setup`、`ssh`、`uninstall` 以及 `logs` 各子命令（backend/nginx/frontend/search）
- 架构图用 Mermaid `flowchart TD` 或纯 ASCII 绘制
- **所有图（架构图、ER 图、类图）都用 Mermaid ` ```mermaid ` fenced block 直接写在 markdown 中**，不生成独立的 HTML/SVG 文件
- Mermaid 注释中不要使用 `/`，用 `-` 替代
- **架构图中的数据层只需写 "MySQL · N 张业务表 → 详见 DATABASE.md"**，不展示具体表名和字段。ER 图同理在 HANDBOOK 中只保留关系线（不展示字段），引用 DATABASE.md 获取完整字段明细。关系线也是合法的 Mermaid erDiagram：去掉 {} 字段块，只保留 ||--o{ 行即可。

## 验证

Mermaid 图写完后必须用 `mermaid.parse()` 验证语法：
```js
mermaid.parse(`erDiagram\n  ...你的代码...\n`)
// 返回 true 表示语法通过
```
如果报错，定位到具体行号修复后再验。不要不验就宣称完成。
