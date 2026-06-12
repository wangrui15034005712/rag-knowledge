# Docker 打包方案

## 最终目录结构

```
rag-test/
├── Dockerfile                  ← 项目根目录
├── docker-compose.yml          ← 项目根目录
├── .dockerignore               ← 项目根目录
├── app/
│   ├── main.py
│   ├── config.py
│   ├── ingest.py
│   ├── rag_chain.py
│   ├── ocr_engine.py
│   ├── reranker.py
│   ├── logger.py
│   └── pages/
│       ├── 1_OCR.py
│       ├── 2_JSON格式化.py
│       ├── 3_MD在线编辑.py
│       ├── 4_局域网IP扫描器.py
│       ├── 5_MySQL_Redis连通性测试_版本显示.py
│       ├── 6_英中翻译.py
│       └── 7_中英翻译.py
├── scripts/
│   └── docker-entrypoint.sh    ← 按需下载翻译模型 + 转交 tini
├── chroma_db/                  ← 持久化挂载（命名卷）
├── docs/                       ← 持久化挂载（命名卷）
├── models/argos-translate/packages/  ← 持久化挂载（命名卷，按需下载）
├── .env                        ← 只读挂载
├── requirements.txt
└── ...
```

---

## 1. `Dockerfile`

```dockerfile
FROM python:3.12-slim

WORKDIR /app
ENV PYTHONPATH=/app

# 翻译模型目录（ENABLE_TRANSLATION=true 时会自动下载到此目录）
ENV ARGOS_PACKAGES_DIR=/app/models/argos-translate/packages
ENV ENABLE_TRANSLATION=false

RUN apt-get update && apt-get install -y --no-install-recommends tini \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com -r requirements.txt

COPY . .
COPY scripts/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

EXPOSE 8501

# 持久化目录（chroma_db 向量库 + 用户上传文档 + 翻译模型）
VOLUME ["/app/chroma_db", "/app/docs", "/app/models/argos-translate/packages"]

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501')" || exit 1

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.fileWatcherType=none"]
```

### 设计决策

| 决策 | 理由 |
|------|------|
| `python:3.12-slim` | 轻量 Python 镜像，项目使用 Python 3.12 |
| `tini` | Docker 内正确的 init 进程，避免 streamlit 收不到 SIGTERM |
| `docker-entrypoint.sh` | 启动前按 `ENABLE_TRANSLATION` 判断是否下载翻译模型 |
| `ENABLE_TRANSLATION=false` | 默认不加载翻译模型，加速启动；需要时设 `true` |
| `ARGOS_PACKAGES_DIR` | 翻译模型目录环境变量，指向命名卷路径 |
| `--server.fileWatcherType=none` | Docker 环境下禁用文件监听，减少 CPU/内存开销 |
| `HEALTHCHECK` | 每 30s 探测 8501 端口，K8s / Compose 可感知容器健康状态 |
| `.env` 不 COPY | 敏感信息通过卷挂载注入，不写入镜像层 |
| 阿里云 pip 镜像 | `-i https://mirrors.aliyun.com/pypi/simple/` 加速国内构建 |

---

## 2. `.dockerignore`

```
venv/
__pycache__/
*.pyc
*.pyo
*.egg-info/
chroma_db/
docs/
models/
.env
.git/
.gitignore
.idea/
.vscode/
*.log
README.md
AGENTS.md
PLAN.md
Docker打包方案.md
```

> `models/` 排除构建上下文，翻译模型由 entrypoint 脚本在运行时按需下载到命名卷中，保持镜像轻量。

> ⚠️ 必须放在项目根目录，Docker CLI 只从 build context 根目录读取 `.dockerignore`。

---

## 3. `docker-compose.yml`

```yaml
services:
  rag-app:
    build: .
    container_name: rag-knowledge
    ports:
      - "8501:8501"
    volumes:
      - chroma_data:/app/chroma_db
      - docs_data:/app/docs
      - argos_model_data:/app/models/argos-translate/packages
      - ./.env:/app/.env:ro
    environment:
      - DEFAULT_BACKEND=siliconflow
      - ENABLE_TRANSLATION=false
    profiles: [""]              # 默认启动

  ollama:
    image: ollama/ollama:latest
    container_name: rag-ollama
    profiles: ["ollama"]        # 仅 --profile ollama 时启动
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama

volumes:
  chroma_data:
  docs_data:
  argos_model_data:
  ollama_data:
```

### 设计决策

| 决策 | 理由 |
|------|------|
| `build: .` | build context 为项目根目录，Dockerfile 在根目录 |
| `DEFAULT_BACKEND=siliconflow` | 默认不经本地 Ollama，开箱即用（需 .env 配 API Key） |
| `ENABLE_TRANSLATION=false` | 默认跳过翻译模型下载，加速首次部署 |
| `argos_model_data` 命名卷 | 翻译模型持久化，重启/重建容器不重复下载 |
| profiled ollama | 不强制 GPU，用户按需 `--profile ollama` 启用 |
| `.env:ro` | 安全：容器内只读，防止运行时意外写入 |
| 命名卷 | 容器删除后 chroma_db/docs/models 数据不丢失 |

---

## 使用方式

```bash
# 1. 确保 .env 已配置（至少 SILICONFLOW_API_KEY）
# 2. 默认启动（SiliconFlow 模式，不加载翻译模型）
docker compose up -d

# 3. 启用翻译功能（首次会下载 ~200MB 翻译模型）
ENABLE_TRANSLATION=true docker compose up -d

# 4. 重新构建镜像并启动（推荐）
docker compose up -d --build
# 或分两步：先构建再启动
docker compose build
docker compose up -d

# 5. 含本地 Ollama（可选翻译）
ENABLE_TRANSLATION=true docker compose --profile ollama up -d
docker exec rag-ollama ollama pull qwen2.5:7b
docker exec rag-ollama ollama pull bge-m3

# 6. 浏览器打开 http://localhost:8501
```

如需切换后端，在 `.env` 中改 `DEFAULT_BACKEND=ollama`，或在 Streamlit 侧边栏手动切换。

---

## 与初始方案的主要变化

| 项目 | 初始方案 | 最终方案 |
|------|----------|----------|
| 目录位置 | `docker/` 子目录 | 项目根目录 |
| 默认后端 | ollama（需外部服务） | siliconflow（开箱即用） |
| Streamlit | 默认 | `--server.fileWatcherType=none` |
| GPU 配置 | deploy.resources | 已移除（CPU only） |
| `.dockerignore` | N/A | 单独文件，项目根目录 |
| 入口进程 | `tini -- streamlit` | `docker-entrypoint.sh → tini → streamlit` |
| 翻译模型 | 未考虑 | 命名卷持久化，`ENABLE_TRANSLATION` 按需下载 |
| 持久化卷 | 2 个（chroma_data, docs_data） | 3 个（+ argos_model_data） |
