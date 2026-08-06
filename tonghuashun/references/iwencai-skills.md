# 已安装 Iwencai 问财 Skills

以下技能均通过 iwencai-skillhub-cli 从同花顺问财 SkillHub 安装，已转换为 Hermes skill 格式。

## Hithink 系列（端点: POST /v1/query2data）

| Skill | 用途 | Claw-Skill-Id |
|-------|------|---------------|
| hithink-astock-selector | 问财选A股（行情/财务/技术/概念筛选） | hithink-astock-selector |
| hithink-market-query | 行情数据查询（价格/资金流/技术指标） | hithink-market-query |
| hithink-industry-query | 行业数据查询（估值/财务/排名） | hithink-industry-query |

所有 hithink 请求体：`{"query": "...", "page": "1", "limit": "10", "is_cache": "1", "expand_index": "true"}`

## Comprehensive Search 系列（端点: POST /v1/comprehensive/search）

| Skill | 用途 | channels |
|-------|------|----------|
| news-search | 财经资讯搜索 | `["news"]` |
| report-search | 研究报告搜索 | `["report"]` |
| announcement-search | 公告搜索 | `["announcement"]` |

请求体：`{"query": "...", "channels": [...], "app_id": "AIME_SKILL", "size": 10}`

## 其他

| Skill | 说明 |
|-------|------|
| a-stock-paper-trade | A股模拟炒股（本地，akshare+新浪财经） |
| multi-factor-strategy | 多因子选股策略（quantcli YAML） |
| quant-factor-screener | 量化因子筛选器（Factor investing框架） |

## 环境变量

已配置于 ~/.zshrc：
- `IWENCAI_BASE_URL=https://openapi.iwencai.com`
- `IWENCAI_API_KEY=sk-proj-...`

## 安装流程（从 iwencai square 安装新 skill）

1. 搜索 slug：`curl -s "https://lightmake.site/api/v1/search?q=关键词" | python3 -m json.tool`
2. 下载 zip：`curl -s "http://ms.10jqka.com.cn/gateway/market/api/v1/skills/square/download?name={slug}" -o /tmp/{slug}.zip`
3. 解压查看 SKILL.md + scripts
4. 用 skill_manage create + write_file 安装为 Hermes skill
5. 如需调用 API，确保 Claw Headers 正确（Authorization, X-Claw-* 系列）
