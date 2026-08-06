# Docker 镜像构建：macOS (apple/container) → Linux VM

## 适用场景

在**没有 Docker Desktop** 的 macOS 上构建 Linux/amd64 Docker 镜像，导出为 tar.gz，传输到仅单向出站的 Linux VM 上运行。

## 工具链

- **apple/container**: macOS 原生容器运行时（`/usr/local/bin/container`）
- **JDK 17**: Homebrew 安装但不默认生效（`/opt/homebrew/opt/openjdk@17/bin/java`）
- **container build**: 替代 `docker build`

## Spring Boot 预编译 JAR 模式（推荐）

**核心思路**：在本地编译好 JAR，Docker 只做 JRE + JAR 打包，秒级完成。

### Dockerfile

```dockerfile
FROM eclipse-temurin:17-jre
WORKDIR /app
COPY target/enterprise-mvp-0.1.0-SNAPSHOT.jar app.jar
RUN mkdir -p /app/uploads
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD curl -f http://localhost:8080/api/health || exit 1
ENTRYPOINT ["java", "-Xms256m", "-Xmx512m", "-jar", "/app/app.jar"]
```

### 编译 JAR（本地 JDK 17）

```bash
export JAVA_HOME=/opt/homebrew/opt/openjdk@17
cd backend && $JAVA_HOME/bin/java -version  # 确认 17
mvn package -DskipTests
```

### 构建并导出 Docker 镜像

```bash
cd backend
container build --platform linux/amd64 -t enterprise-mvp-backend:latest \
  -f Dockerfile -o type=tar,dest=../enterprise-mvp-backend.tar .
gzip -f ../enterprise-mvp-backend.tar
```

### 在 Linux VM 上部署

```bash
gunzip enterprise-mvp-backend.tar.gz
docker load -i enterprise-mvp-backend.tar
docker pull mysql:8.4
docker compose -f docker-compose.prod.yml up -d
```

## ❌ 多阶段 Maven 构建（不推荐）

Dockerfile 里写 `FROM maven:3.9-eclipse-temurin-17 AS build` 然后 `mvn package`，看起来干净但：

- Maven 容器内首次需要下载全部依赖（几百 MB），10-30 分钟
- apple/container 的 pull 插件可能缺失
- 难以调试编译失败

**何时可用**：另一台机器上完全没有 JDK 17 时。

## 替代方案：Colima + qemu（当 apple/container 不可用时）

当 `container` 命令不存在时，使用 Colima 提供 Docker 守护进程 + qemu 提供 x86_64 模拟：

### 首次安装

```bash
# 1. 安装 Colima + qemu
brew install colima qemu

# 2. 启动 x86_64 虚拟机（下载 ~500MB VM 镜像，需数分钟）
colima start --arch x86_64 --cpu 4 --memory 8

# 3. 验证
docker info --format '{{.OSType}}/{{.Architecture}}'  # → linux/amd64
```

### 构建镜像

启动 Colima 后，`docker` 命令直接可用，`docker compose build` 自然产生 x86_64 镜像：

```bash
# 先编译 JAR（本地 JDK）
export JAVA_HOME=/opt/homebrew/opt/openjdk
cd backend && $JAVA_HOME/bin/mvn package -DskipTests -q

# Colima 上下文下直接 docker compose build
cd ~/enterprise
docker compose build
```

### 导出镜像（传给 Linux VM）

```bash
docker save enterprise-mvp-backend:latest | gzip > /tmp/enterprise-mvp-backend.tar.gz
```

### 已知问题

- **Colima 首次启动需下载 VM 镜像**（~500MB），取决于网络速度，在 Shadowrocket 代理下约 3-5 分钟
- **brew install colima 自身不含 qemu**，必须额外安装 `brew install qemu`（711MB），否则 x86_64 启动报 `qemu-img not found`
- Colima 停止后 Docker 上下文也消失，需要用 `colima start` 重新激活
- 如果本地已有 MySQL（Homebrew），`docker compose up` 的 MySQL 服务端口 3306 会冲突。要么停本地 MySQL (`brew services stop mysql`)，要么修改 host MySQL 端口

## 注意

- `container save` 和 `container pull` 命令通常不存在
- 用 `container build -o type=tar,dest=<path>` 直接输出 tar
- 目标 VM 用 `docker load -i` 加载
- JDK 17 Homebrew 安装路径：`/opt/homebrew/opt/openjdk@17`，不注册进 java_home
- apple/container 构建的镜像默认 Linux/amd64，可直接在 Linux VM 运行
