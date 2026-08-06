# Synology DSM Web API — NAS 文件浏览（当 SMB 挂载失败时的备选）

Synology NAS 暴露 REST API，可在 SMB 挂载失败时通过 HTTP 浏览和下载文件。

## 关键：禁用代理

```python
import os
for k in ['http_proxy','https_proxy','HTTP_PROXY','HTTPS_PROXY','no_proxy','NO_PROXY']:
    os.environ.pop(k, None)
```

如果这步不执行，curl/urllib 会通过本地代理（如 `127.0.0.1:1082`）发请求，代理不认识内网 IP 导致超时。

## 获取 Session ID

```python
import urllib.request, urllib.parse, json

base = 'http://NAS_IP:5000/webapi'
params = urllib.parse.urlencode({
    'api': 'SYNO.API.Auth', 'version': '6', 'method': 'login',
    'account': 'USER', 'passwd': 'PASS',
    'session': 'FileStation', 'format': 'cookie'
})
r = urllib.request.urlopen(f'{base}/auth.cgi?{params}', timeout=10)
sid = json.loads(r.read())['data']['sid']
```

⚠️ 密码含 `!` `}` `~` 等符号时，Python f-string 会报错（`!` 是 f-string 转义符）。用 `urllib.parse.quote(pw, safe='')` 编码或 `params` 字典传原值即可。

## 列出共享目录

```python
params = urllib.parse.urlencode({
    'api': 'SYNO.FileStation.List', 'version': '2', 'method': 'list_share',
    '_sid': sid, 'additional': 'real_path,size'
})
r = urllib.request.urlopen(f'{base}/entry.cgi?{params}', timeout=10)
data = json.loads(r.read())
# data['data']['shares'] = [{name, path}, ...]
```

## 列出目录内容

```python
params = urllib.parse.urlencode({
    'api': 'SYNO.FileStation.List', 'version': '2', 'method': 'list',
    '_sid': sid, 'folder_path': '/SHARE_NAME/SUBDIR',
    'additional': 'size,type'
})
r = urllib.request.urlopen(f'{base}/entry.cgi?{params}', timeout=10)
data = json.loads(r.read())
# data['data']['files'] = [{name, isdir, additional: {size}}, ...]
```

## 下载文件

```python
params = urllib.parse.urlencode({
    'api': 'SYNO.FileStation.Download', 'version': '2', 'method': 'download',
    '_sid': sid, 'path': '/SHARE_NAME/FILE.pdf', 'mode': 'download'
})
r = urllib.request.urlopen(f'{base}/entry.cgi?{params}', timeout=30)
with open('local_file.pdf', 'wb') as f:
    f.write(r.read())
```

## API 端点参考

| 功能 | API | Version |
|------|-----|---------|
| 登录 | SYNO.API.Auth | v6 |
| 列共享目录 | SYNO.FileStation.List | v2 (method=list_share) |
| 浏览目录 | SYNO.FileStation.List | v2 (method=list) |
| 下载文件 | SYNO.FileStation.Download | v2 |
| 上传文件 | SYNO.FileStation.Upload | v2 |
| 系统信息 | SYNO.DSM.Info | v1 |

## 注意事项

- 端口：5000 = HTTP, 5001 = HTTPS（Synology 默认）
- API 可列出隐藏目录（如 `#recycle`）
- 中文路径：Python 直接传 unicode 字符串，urllib 会自动编码
