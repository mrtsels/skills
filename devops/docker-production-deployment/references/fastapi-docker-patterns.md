# FastAPI Docker Deployment Patterns

> Python (FastAPI) 版本的 Docker 部署模式。核心模式与 Spring Boot / Java 一致，
> 但 artifact 类型和启动命令不同。参照 SKILL.md 中的 crash-loop wrapper、独立重启、
> 预编译 artifact、运维 CLI 等原则。

---

## 模式对照

| 模式 | Java/Spring Boot | Python/FastAPI |
|------|-----------------|----------------|
| 后端 artifact | `app.jar` | `app.whl` |
| 预编译方式 | `mvn package -DskipTests` | `pip wheel . -w dist` |
| 运行时命令 | `java -jar app.jar` | `uvicorn main:app --host 0.0.0.0 --port 8080` |
| Docker 基础镜像 | `eclipse-temurin:17-jre` | `python:3.11-slim` |
| 健康检查端点 | `/api/health` | `/api/health` |

---

## FastAPI Dockerfile（预编译 wheel 模式）

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 预编译 wheel（对应 SKILL.md JAR 模式）
COPY api/dist/app-*.whl .
RUN pip install --no-cache-dir *.whl && rm *.whl

# 启动包装脚本
COPY api/docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD curl -sf http://localhost:8080/api/health || exit 1

ENTRYPOINT ["/app/docker-entrypoint.sh"]
```

## FastAPI 启动包装脚本（crash-loop wrapper）

```bash
#!/bin/bash
# docker-entrypoint.sh — 保持容器 Up
set -e
echo "[entrypoint] Starting FastAPI server..."

while true; do
  uvicorn main:app --host 0.0.0.0 --port 8080 --workers 1
  echo "[entrypoint] Server exited with code $?, restarting in 3s..."
  sleep 3
done
```

## FastAPI 健康检查端点

```python
@app.get("/api/health")
async def health():
    return {"status": "ok"}
```

---

## Nginx 反向代理（FastAPI 后端）

```nginx
# nginx.conf
upstream api {
    server api:8080;   # 对应 docker-compose 中的 service 名
}

server {
    listen 80;
    server_name _;
    client_max_body_size 20M;    # FastAPI 需较大 body 限制

    location / {
        root /usr/share/nginx/html;
        index index.html;
    }

    location /api/ {
        proxy_pass http://api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 120s;   # 长推理任务需要
    }
}
```

---

## MySQL 初始化（Docker entrypoint）

直接放在 `docker/init.sql`，挂载到 MySQL 容器的 entrypoint 目录：

```yaml
# docker-compose.yml
services:
  db:
    image: mysql:8.0
    container_name: myapp-db
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD:-root123}
      MYSQL_DATABASE: myapp
      MYSQL_USER: app
      MYSQL_PASSWORD: ${MYSQL_PASSWORD:-app123}
    volumes:
      - mysql_data:/var/lib/mysql
      - ./init.sql:/docker-entrypoint-initdb.d/01-init.sql:ro
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5
```

```sql
-- docker/init.sql
CREATE TABLE IF NOT EXISTS my_table (
    id   VARCHAR(36) PRIMARY KEY,
    data JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 完整 docker-compose.yml 模板（nginx + FastAPI + MySQL）

```yaml
services:
  db:
    image: mysql:8.0
    container_name: myapp-db
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD:-root123}
      MYSQL_DATABASE: myapp
      MYSQL_USER: app
      MYSQL_PASSWORD: ${MYSQL_PASSWORD:-app123}
    volumes:
      - mysql_data:/var/lib/mysql
      - ./init.sql:/docker-entrypoint-initdb.d/01-init.sql:ro
    ports:
      - "${DB_PORT:-3307}:3306"
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

  api:
    image: myapp-api:latest
    build:
      context: ..
      dockerfile: api/Dockerfile
    container_name: myapp-api
    restart: always
    environment:
      DB_HOST: db
      DB_PORT: 3306
      DB_NAME: myapp
      DB_USER: app
      DB_PASSWORD: ${MYSQL_PASSWORD:-app123}
    volumes:
      - uploads_data:/app/uploads
    ports:
      - "${API_PORT:-8080}:8080"
    # 无 depends_on — 独立重启

  frontend:
    image: myapp-frontend:latest
    build:
      context: ..
      dockerfile: web/Dockerfile
    container_name: myapp-frontend
    restart: always
    volumes:
      - ../web/index.html:/usr/share/nginx/html/index.html:ro
    ports:
      - "${FRONTEND_PORT:-8088}:80"

volumes:
  mysql_data:
  uploads_data:
```

> **重要：** 去掉 `depends_on` — 参照 SKILL.md "核心原则"。Spring Boot 和 FastAPI 都自带数据库重试机制，不需要 Compose 层面的依赖耦合。

---

## FastAPI 项目目录结构（参考）

```
my-project/
├── api/                      # FastAPI 后端
│   ├── main.py               # FastAPI app + 路由
│   ├── inference.py          # 业务逻辑
│   ├── requirements.txt      # pip 依赖
│   ├── Dockerfile            # python:3.11-slim
│   └── docker-entrypoint.sh  # crash-loop wrapper
├── web/                      # 前端
│   ├── index.html            # 单页应用
│   ├── nginx.conf            # 反向代理配置
│   └── Dockerfile            # nginx:alpine
├── docker/                   # 编排 + 运维
│   ├── docker-compose.yml
│   ├── .env.example
│   ├── init.sql
│   └── myapp-cli             # 运维 CLI 脚本
└── docs/
    └── development/
        └── web_demo.md
```

---

## CLI 运维脚本（start/stop/status/logs/update/check-api）

参照 SKILL.md "Service CLI Tool for Production Management" 部分。FastAPI 版本的关键差异：

| CLI 字段 | Java 版本 | FastAPI 版本 |
|----------|----------|-------------|
| 后端容器名 | `enterprise-backend` | `myapp-api` |
| 后端端口 | `${BACKEND_PORT:-8080}` | `${API_PORT:-8080}` |
| 前端端口 | `${FRONTEND_PORT:-80}` | `${FRONTEND_PORT:-8088}` |
| 后端 artifact | `*.jar` | `*.whl` |
| 热更新命令 | `docker cp jar` + restart | `docker cp whl` + `pip install --force-reinstall` + restart |
| API 诊断 | 自定义健康端点 | `/api/health` |
