# MySQL 编码陷阱：Docker 下写入中文乱码

## 现象

通过 `docker exec -i mysql ... < file.sql` 写入包含中文的 SQL 后，数据库内容变成乱码（`å¹¿å·žå¸‚` 等 mojibake）。

## 根因

`mysql` 命令行客户端默认使用 `latin1` 连接。当 SQL 文件是 UTF-8 编码时：
1. mysql 客户端把 UTF-8 字节流按 latin1 解析
2. 发送到服务端时，服务端再按 `utf8mb4` 存储
3. 相当于对 UTF-8 字节流做了第二次 UTF-8 编码 → 双编码乱码

## 修复

```bash
# ❌ 错误
docker exec -i mysql mysql db < data.sql

# ✅ 正确：显式声明 UTF-8 连接
docker exec -i mysql mysql --default-character-set=utf8mb4 db < data.sql
```

## SQL 文件头

即使 mysql 命令行指定了 charset，也建议在 SQL 文件头部加上：

```sql
SET NAMES utf8mb4;
START TRANSACTION;
...
COMMIT;
```

## 验证

```bash
# 检查连接字符集
docker exec mysql mysql -e "SHOW VARIABLES LIKE 'character_set_%';"

# 正常状态：client/connection/results 应为 utf8mb4
# 异常状态：这三个是 latin1 → 需要 --default-character-set=utf8mb4
```

## 已恢复的乱码数据的处理

数据已双编码存在库中时，无法通过简单 UPDATE 恢复。正确的做法是：
1. 将正确的 UTF-8 内容重新生成 SQL（用 `--default-character-set=utf8mb4` 执行）
2. 或通过 API 逐条写入（API 的 HTTP 传输天然处理 UTF-8）

不要尝试用 CONVERT/CONVERT_BYTE 等 MySQL 函数恢复——双重编码后的字节序列是不确定的。
