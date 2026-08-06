# 实际 Prompt：Claude 生成日志方案 → Hermes 执行

## 上下文

Spring Boot 3.4.5 + Vanilla JS SPA + Docker Compose 离线部署项目。
需求：构建完整的日志追踪基础设施。

## 发送给 Claude 的 Prompt

```
TASK: 为下面的 Enterprise MVP 项目设计一套完整的日志追踪基础设施方案。

CONTEXT:
这是广州市企业智能服务平台，技术栈：
- 后端：Spring Boot 3.4.5 + JPA + MySQL 8.0，JAR 运行在 Docker 容器中
- 前端：单文件 Vanilla JS SPA（index.html，5100+ 行），无框架
- 部署：Docker Compose 3 容器（db/backend/frontend），后端容器已映射 /app/logs → 宿主机 logs/backend/
- 现有日志：后端通过 logback 输出到 stdout（Docker 容器），前端无日志
- 服务器：CentOS 7 / Kylin Linux 内网离线环境，无网络无 DNS
- AI 模型：DashScope qwen3-vl-flash（OCR 识别 + AI 分析）

需求：
1. 后端服务输出结构化日志（JSON 格式），含 source="backend", traceId, userId, requestPath, duration
2. 前端通过 API 上报日志（浏览器端 JS logger，缓冲批量 POST 到 /api/logs）
3. 日志从采集点到中央处理的可靠传输
4. 对原始日志解析、过滤、格式转换和字段增强（添加 source 标识）
5. 集中存储所有处理后的日志在 logs/，按日期滚动，7 天自动删除旧日志
6. 数据库慢查询定位

约束：
- Spring Boot 已有 logback，可在 logback-spring.xml 中配置
- 不要引入重量级日志系统（ELK/Loki/Graylog）
- logs/ 目录结构：logs/backend/ / logs/frontend/ / logs/access/
- 所有新增后端代码必须符合项目现有风格
- 无新增 Maven 依赖

OUTPUT FORMAT：
请输出一个完整的实施计划，分模块列出：
1. 每个模块需要创建/修改的文件路径
2. 关键接口/类设计
3. 配置要点
4. 验证方法
```

## Claude 返回的方案结构

Claude 返回了 14 个章节的详尽方案（~19K tokens）：

1. 项目总览（设计原则、目录结构）
2. 模块 1：后端 JSON 结构化日志（JsonLayout.java + logback-spring.xml）
3. 模块 2：MDC 增强字段注入（LoggingFilter.java）
4. 模块 3：前端浏览器 Logger（index.html 追加 LogCollector）
5. 模块 4：前端日志接收 API（LogController.java）
6. 模块 5：慢查询定位（application.yml Hibernate 配置）
7. 模块 6：Nginx JSON 访问日志（nginx.conf）
8. 模块 7：Docker Compose 卷映射调整
9. 模块 8：日志清理（cleanup-logs.sh）
10. SecurityConfig 放行 /api/logs
11. 完整日志流总结表
12. 实施顺序与依赖关系
13. 全部文件变更清单
14. 关键设计决策说明（含零依赖决策理由）

## Hermes 执行结果

11 个步骤，10 个文件变更，零新增 Maven 依赖。详见 git commit `61eae42`。
