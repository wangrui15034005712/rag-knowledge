# Docker + Nginx 多站点自动化部署方案

## 目录结构

```
deploy/
├── README.md                   # 本文档
├── sites.json                  # 全局配置文件（站点定义、全局参数）
├── nginx/
│   ├── http.conf.template      # HTTP Nginx 配置模板
│   └── https.conf.template     # HTTPS Nginx 配置模板
├── scripts/
│   └── deploy.sh               # 主部署脚本
├── certs/                      # SSL 证书目录（按域名分目录）
│   └── <domain>/
│       ├── fullchain.pem       # 证书链
│       └── privkey.pem         # 私钥
├── generated/                  # 生成的配置文件（部署时自动生成）
│   └── nginx.conf              # 最终 Nginx 配置
└── logs/                       # Nginx 日志目录
    ├── <site>_access.log
    └── <site>_error.log
```

## 快速开始

### 1. 前置条件

- Docker 已安装并运行
- jq 已安装（用于 JSON 解析）
- openssl 已安装（如需 SSL）

```bash
# Ubuntu/Debian
apt-get install -y docker.io jq openssl

# CentOS/RHEL
yum install -y docker jq openssl
```

### 2. 配置站点

编辑 `sites.json`，添加你的站点：

```json
{
  "global": {
    "nginx_http_port": 80,
    "nginx_https_port": 443,
    "timezone": "Asia/Shanghai"
  },
  "sites": [
    {
      "name": "my-app",
      "domain": "app.example.com",
      "enabled": true,
      "ssl": false,
      "upstream_port": 3000,
      "container_name": "my-app",
      "project_path": "/opt/my-app",
      "compose_profile": "",
      "env_vars": {},
      "custom_headers": {
        "X-Frame-Options": "SAMEORIGIN",
        "X-Content-Type-Options": "nosniff"
      },
      "websocket": false,
      "static_cache_days": 7
    }
  ]
}
```

### 3. 一键部署

```bash
cd deploy
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

## 配置文件说明

### sites.json

#### 全局配置 (global)

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `nginx_http_port` | 80 | HTTP 监听端口 |
| `nginx_https_port` | 443 | HTTPS 监听端口 |
| `timezone` | Asia/Shanghai | 服务器时区 |
| `log_level` | warn | Nginx 日志级别 (debug/info/notice/warn/error/crit) |
| `worker_processes` | auto | Nginx worker 进程数 |
| `worker_connections` | 1024 | 每个 worker 的最大连接数 |
| `client_max_body_size` | 50m | 最大请求体大小 |
| `ssl_protocols` | TLSv1.2 TLSv1.3 | 支持的 SSL 协议版本 |
| `ssl_ciphers` | ECDHE-ECDSA-AES128-GCM-SHA256:... | SSL 加密套件 |
| `proxy_connect_timeout` | 60 | 代理连接超时（秒） |
| `proxy_send_timeout` | 60 | 代理发送超时（秒） |
| `proxy_read_timeout` | 60 | 代理读取超时（秒） |
| `gzip` | true | 是否启用 Gzip 压缩 |
| `gzip_types` | text/plain text/css... | Gzip 压缩的 MIME 类型 |

#### 站点配置 (sites[])

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | ✅ | 站点唯一标识 |
| `domain` | string | ✅ | 域名 |
| `enabled` | boolean | 否 | 是否启用（默认 true） |
| `ssl` | boolean | 否 | 是否启用 SSL（默认 false） |
| `ssl_cert_path` | string | 否 | SSL 证书路径 |
| `ssl_key_path` | string | 否 | SSL 私钥路径 |
| `upstream_port` | number | ✅ | 后端服务端口 |
| `container_name` | string | ✅ | Docker 容器名称 |
| `project_path` | string | ✅ | 项目根目录路径 |
| `compose_profile` | string | 否 | Docker Compose profile |
| `env_vars` | object | 否 | 环境变量 |
| `custom_headers` | object | 否 | 自定义响应头 |
| `websocket` | boolean | 否 | 是否启用 WebSocket 支持 |
| `static_cache_days` | number | 否 | 静态文件缓存天数（0 禁用） |
| `access_log` | boolean | 否 | 是否记录访问日志 |
| `error_log` | boolean | 否 | 是否记录错误日志 |

## 部署步骤

### 步骤 1：配置站点

编辑 `sites.json`，添加或修改站点配置。

### 步骤 2：确保项目就绪

确保每个站点的 `project_path` 目录下有 `docker-compose.yml`：

```bash
ls /opt/my-app/docker-compose.yml
```

### 步骤 3：运行部署

```bash
# 部署所有启用的站点
./scripts/deploy.sh

# 或部署特定站点
./scripts/deploy.sh --site my-app
```

### 步骤 4：验证部署

```bash
# 查看部署状态
./scripts/deploy.sh --status

# 查看所有站点
./scripts/deploy.sh --list
```

### 步骤 5：配置域名解析

在 DNS 服务器或 `/etc/hosts` 中添加域名解析：

```bash
echo "192.168.1.100 app.example.com" >> /etc/hosts
```

## SSL 证书配置

### 自动生成自签名证书

```bash
# 为指定站点生成自签名证书
./scripts/deploy.sh --ssl my-app
```

这会在 `certs/<domain>/` 下生成：
- `fullchain.pem` - 证书链
- `privkey.pem` - 私钥

同时会自动更新 `sites.json` 中的 SSL 配置。

### 使用 Let's Encrypt 证书

1. 安装 certbot：

```bash
apt-get install -y certbot
```

2. 获取证书：

```bash
certbot certonly --standalone -d app.example.com
```

3. 更新 `sites.json`：

```json
{
  "name": "my-app",
  "ssl": true,
  "ssl_cert_path": "/etc/letsencrypt/live/app.example.com/fullchain.pem",
  "ssl_key_path": "/etc/letsencrypt/live/app.example.com/privkey.pem"
}
```

4. 重新部署：

```bash
./scripts/deploy.sh --site my-app
```

## 常用命令

### 部署管理

```bash
# 部署所有站点
./scripts/deploy.sh

# 部署特定站点
./scripts/deploy.sh --site rag-knowledge

# 仅更新 Nginx 配置
./scripts/deploy.sh --nginx-only

# 查看状态
./scripts/deploy.sh --status

# 列出站点
./scripts/deploy.sh --list
```

### Docker 操作

```bash
# 查看运行中的容器
docker ps

# 查看所有容器
docker ps -a

# 查看容器日志
docker logs -f <container_name>

# 进入容器
docker exec -it <container_name> bash

# 重启容器
docker restart <container_name>

# 停止容器
docker stop <container_name>

# 删除容器
docker rm <container_name>
```

### Nginx 操作

```bash
# 查看 Nginx 状态
docker exec nginx nginx -t

# 重新加载配置
docker exec nginx nginx -s reload

# 查看 Nginx 日志
docker exec nginx tail -f /var/log/nginx/access.log
docker exec nginx tail -f /var/log/nginx/error.log
```

### 日志查看

```bash
# 查看站点访问日志
tail -f deploy/logs/<site>_access.log

# 查看站点错误日志
tail -f deploy/logs/<site>_error.log

# 查看 Nginx 错误日志
tail -f deploy/logs/error.log
```

## 故障排查

### 问题 1：Nginx 启动失败

**症状**：Nginx 容器无法启动或立即退出

**排查步骤**：

```bash
# 查看 Nginx 错误日志
docker logs nginx

# 测试配置文件
docker exec nginx nginx -t

# 检查端口占用
netstat -tlnp | grep -E ':(80|443)'
```

**常见原因**：
- 端口被占用：停止占用 80/443 端口的服务
- 配置语法错误：检查 `generated/nginx.conf`
- 权限问题：确保日志目录可写

### 问题 2：后端服务无法访问

**症状**：访问域名返回 502 Bad Gateway

**排查步骤**：

```bash
# 检查后端容器是否运行
docker ps | grep <container_name>

# 检查后端容器日志
docker logs <container_name>

# 检查端口映射
docker port <container_name>

# 测试后端连接
curl http://localhost:<upstream_port>
```

**常见原因**：
- 后端容器未启动：`docker start <container_name>`
- 端口配置错误：检查 `sites.json` 中的 `upstream_port`
- 应用未就绪：等待应用启动完成

### 问题 3：SSL 证书错误

**症状**：浏览器提示证书不受信任

**排查步骤**：

```bash
# 检查证书文件
ls -la certs/<domain>/

# 验证证书
openssl x509 -in certs/<domain>/fullchain.pem -text -noout

# 检查证书有效期
openssl x509 -in certs/<domain>/fullchain.pem -dates -noout
```

**解决方案**：
- 自签名证书：浏览器会警告，需手动信任
- 证书过期：重新生成或续期证书
- 证书路径错误：检查 `sites.json` 中的路径

### 问题 4：WebSocket 连接失败

**症状**：WebSocket 连接超时或断开

**排查步骤**：

```bash
# 检查 Nginx 配置中的 WebSocket 设置
grep -A 5 "WebSocket" generated/nginx.conf

# 检查代理超时设置
grep "proxy_read_timeout" generated/nginx.conf
```

**解决方案**：
- 确保 `websocket: true` 已设置
- 增加 `proxy_read_timeout`（默认 86400s = 24小时）
- 检查应用是否正确处理 WebSocket 升级

### 问题 5：配置不生效

**症状**：修改 `sites.json` 后没有效果

**解决步骤**：

```bash
# 1. 重新生成 Nginx 配置
./scripts/deploy.sh --nginx-only

# 2. 重新加载 Nginx
docker exec nginx nginx -s reload

# 3. 或重启 Nginx 容器
docker restart nginx
```

### 问题 6：Docker Compose 错误

**症状**：容器构建或启动失败

**排查步骤**：

```bash
# 查看详细错误
docker compose up --build

# 检查 docker-compose.yml 语法
docker compose config

# 清理旧容器和镜像
docker compose down
docker system prune
```

## 高级配置

### 自定义 Nginx 配置

如需添加自定义 Nginx 配置，可以在站点配置中使用 `custom_headers`：

```json
{
  "custom_headers": {
    "X-Frame-Options": "SAMEORIGIN",
    "X-Content-Type-Options": "nosniff",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin"
  }
}
```

### 多实例部署

同一应用部署多个实例：

```json
{
  "sites": [
    {
      "name": "app-v1",
      "domain": "v1.example.com",
      "upstream_port": 3001,
      "container_name": "app-v1"
    },
    {
      "name": "app-v2",
      "domain": "v2.example.com",
      "upstream_port": 3002,
      "container_name": "app-v2"
    }
  ]
}
```

### 负载均衡

如需负载均衡，可修改 Nginx 模板添加 upstream 多节点：

```nginx
upstream app_backend {
    server 127.0.0.1:3001;
    server 127.0.0.1:3002;
    server 127.0.0.1:3003;
}
```

## 安全建议

1. **限制访问**：使用防火墙限制 80/443 端口访问
2. **启用 HTTPS**：生产环境务必使用 SSL
3. **定期更新**：定期更新 Docker 镜像和系统
4. **日志监控**：定期检查访问日志和错误日志
5. **备份配置**：定期备份 `sites.json` 和证书文件

## 技术支持

如有问题，请检查：
1. Docker 是否正常运行
2. `sites.json` 配置是否正确
3. 项目目录下是否有 `docker-compose.yml`
4. 查看 `deploy/logs/` 下的日志文件
