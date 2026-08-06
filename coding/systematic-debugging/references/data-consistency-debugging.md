# 数据一致性调试指南

当 UI 显示重复记录、缺失记录或状态错误的列表时，问题可能来自前端渲染、后端代码或数据库数据本身。

## 核心原则：先确定问题层面

不要在猜测层面就开始修代码。**先定位问题发生在哪一层。**

```
UI 显示异常
    │
    ├─→ 检查 API 原始响应
    │       │
    │       ├─→ API 数据正确 → 前端渲染问题
    │       │                    └─ 检查渲染逻辑、分组、过滤
    │       │
    │       └─→ API 数据错误 → 后端数据问题
    │                           │
    │                           ├─→ 代码逻辑错误（CRUD 漏检查）
    │                           │
    │                           └─→ 数据库数据不一致（脏数据）
    │                                   └─ 检查全量数据找规律
    │
    └─→ 直接查数据库
```

## 调试流程

### 1. 验证 API 层

用 curl 直接拉取原始数据，绕过前端渲染：

```bash
# 拉取列表
curl -s http://localhost:8080/api/declarations?page=0&size=20 | python3 -m json.tool

# 拉取详细子资源（如材料列表）
curl -s http://localhost:8080/api/declarations/123/materials | python3 -c "
import json,sys
mats=json.load(sys.stdin)
# 统计重复
names=[m['materialName'] for m in mats]
dupes={n:names.count(n) for n in set(names) if names.count(n)>1}
if dupes:
    print(f'重复项: {dupes}')
    for m in mats:
        if m['materialName'] in dupes:
            print(f'  id={m[\"id\"]} name={m[\"materialName\"]} status={m.get(\"status\")} docId={m.get(\"documentId\")}')
else:
    print(f'无重复，共 {len(mats)} 项')
"
```

### 2. 确定影响范围

对全量数据做批量检查，判断是单条记录异常还是系统性错误：

```bash
# 检查所有声明的材料是否有重复
curl -s 'http://localhost:8080/api/declarations?page=0&size=50' | python3 -c "
import json, sys, urllib.request
d = json.load(sys.stdin)
for item in d.get('content', []):
    did = item['id']
    resp = urllib.request.urlopen(f'http://localhost:8080/api/declarations/{did}/materials')
    mats = json.loads(resp.read())
    names = [m['materialName'] for m in mats]
    dupes = {n: names.count(n) for n in set(names) if names.count(n) > 1}
    if dupes:
        print(f'ID {did} ({item[\"type\"]}): 重复 {dupes}')
    else:
        print(f'ID {did}: OK ({len(mats)} 项)')
"
```

### 3. 追溯重复来源

找到重复后，分析其 ID 规律判断来源：

- **ID 接近** → 可能是在初始化时创建了两次（`initMaterials` 被调用两次）
- **ID 显著偏高** → 可能是后续通过 POST 新增的（`POST /materials` endpoint）
- **一条有文档，一条没有** → 正常的初始化记录 + 后续误创建的孤立记录

追踪后端可能的创建路径：

| 创建路径 | 代码位置 | 特征 |
|----------|----------|------|
| 初始化 | `initMaterials()` | 创建时调用，ID 较低，且 `materialRepo.findByDeclarationId().isEmpty()` 时触发 |
| 克隆 | `clone()` → material copy | 复制源的所有材料，ID 紧跟在克隆动作之后 |
| POST 新增 | `addMaterial()` endpoint | 任何客户端都可调用，不检查是否已存在同名的材料 |

### 4. 修复数据

**对于孤立重复记录（无文档关联）：**

```bash
# 通过 API 删除
curl -s -X DELETE http://localhost:8080/api/declarations/materials/{duplicate_id}
```

**确认修复后数据：**
```bash
curl -s http://localhost:8080/api/declarations/{decl_id}/materials | python3 -c "
import json,sys; mats=json.load(sys.stdin);
names=[m['materialName'] for m in mats];
dupes={n:names.count(n) for n in set(names) if names.count(n)>1};
print('重复:', dupes if dupes else '无');
print(f'总数: {len(mats)}')
"
```

### 5. 预防复发

检查代码中是否有路径会创建重复数据：

1. **`POST /{id}/materials`** — 是否需要在 Service 层加重复检查？同一声明的同名材料应该走 `PUT` 更新而非新增。
2. **克隆操作** — 如果克隆后又被初始化，就会产生重复。确认 `clone()` 和 `initMaterials()` 不会同时触发。
3. **前端物料上传** — 上传前先 `find` 已有材料再 `update`，而不是直接 `POST` 新增。

## 常见场景

### 场景：材料列表出现两个同名物料

**症状：** 左侧佐证材料列表出现两条"营业执照（副本）"，一条已识别、一条缺失。

**调试步骤：**
1. curl API 确认数据层有两条同名的材料记录
2. 批量检查所有申报，确认是单例还是全局问题
3. 对比两条记录的 ID、status、documentId
4. 检查后端代码：`POST /{id}/materials` 是否做了重复判断

**典型根因：** 某次 API 调用（可能来自前端测试或手动 curl）通过 POST endpoint 新增了一条同名材料，而该 endpoint 未做重复性检查。

**修复：** 直接删除孤立重复记录（无 documentId 的那条）。
