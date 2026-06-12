# RAG 私人知识库

基于 **LangChain + ChromaDB + Streamlit** 的纯本地 RAG 知识库系统，支持上传 PDF/Word/TXT 文档，通过自然语言问答检索文档内容。

## 功能

- 上传文档（PDF / Word / TXT）
- 自动解析、分块、向量化，存入 ChromaDB
- 多轮对话，历史记忆中检索
- 流式输出（打字机效果）+ 引用来源展示
- 支持 Ollama（本地）、vLLM（远程 GPU）、SiliconFlow（硅基流动 API）三后端
- OCR 图片文字识别（Qwen3.5-35B-A3B 多模态视觉模型，支持 SiliconFlow / vLLM）
- 英中翻译（Argos Translate 离线翻译引擎，纯本地无需联网）
- 中英翻译（Argos Translate 离线翻译引擎，zh→en 双向支持）
- 重排序（Reranker）精排检索结果，剔除噪音文档，提高回答质量

## 快速开始（从零搭建）

### 1. 创建虚拟环境（Python 3.12）

```bash
py -3.12 -m venv venv
```

如果上述命令无效，请手动指定 Python 3.12 安装路径：

```bash
"C:\Program Files\Python312\python.exe" -m venv venv
```

### 2. 激活虚拟环境

```bash
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Windows CMD
venv\Scripts\activate.bat
```

激活后终端前面会出现 `(venv)` 前缀。

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 启动知识库

```bash
streamlit run app/main.py
```

浏览器打开 http://localhost:8501

### 5. Docker 部署（替代上述步骤 1-4）

```bash
# 确保 .env 已配置（至少 SILICONFLOW_API_KEY）
# 默认 SiliconFlow 模式
docker compose up -d

# 如需启动本地 Ollama
docker compose --profile ollama up -d
docker exec rag-ollama ollama pull qwen2.5:7b
docker exec rag-ollama ollama pull bge-m3
```

浏览器打开 http://localhost:8501

### 6. 使用流程

1. 上传文档（PDF/Word/TXT）到 `docs/` 目录，或通过 UI 页面上传
2. 点击侧边栏 **"导入到知识库"** 按钮
3. 在输入框提问，等待流式回答

## 目录结构

```
rag-test/
├── app/                     # 源代码
│   ├── main.py              # Streamlit UI 入口
│   ├── rag_chain.py         # RAG 检索链 + 流式输出
│   ├── ingest.py            # 文档解析 → 分块 → 嵌入 → 入库
│   ├── config.py            # 全局配置
│   ├── ocr_engine.py        # OCR 视觉识别引擎
│   ├── logger.py            # 日志工具
│   └── pages/               # Streamlit 多页面
│       ├── __init__.py
│       ├── 1_OCR.py         # OCR 图片文字识别
│       ├── 2_JSON格式化.py   # JSON 格式化工具
│       ├── 3_MD在线编辑.py    # Markdown 在线编辑器
│       ├── 4_局域网IP扫描器.py # 局域网 IP 扫描
│       ├── 5_MySQL_Redis连通性测试_版本显示.py  # MySQL/Redis 连通性测试
│       ├── 6_英中翻译.py        # 英中翻译（Argos Translate 离线）
│       └── 7_中英翻译.py        # 中英翻译（Argos Translate 离线，zh→en）
├── models/                  # 离线模型文件（不入库）
│   └── argos-translate/
│       └── packages/
│           ├── translate-en_zh-1_9/  # en-zh 翻译模型
│           └── translate-zh_en-1_9/  # zh-en 翻译模型
├── scripts/
│   └── download_argos_model.py  # 预下载 en-zh + zh-en 翻译模型
├── docs/                    # 上传文档目录（手动放置或 UI 上传）
├── chroma_db/               # ChromaDB 持久化（自动生成）
├── venv/                    # 虚拟环境
├── .env                     # 环境变量（API Key 等，不入库）
├── .env.example             # 环境变量模板（可入库）
├── Dockerfile               # Docker 镜像构建
├── .dockerignore            # Docker build context 过滤
├── docker-compose.yml       # 服务编排（含 ollama profile）
└── requirements.txt
```

## 配置

所有参数在 `app/config.py` 中，支持环境变量覆盖：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `DEFAULT_BACKEND` | `ollama` | 后端：`ollama` / `vllm` / `siliconflow` |
| `LLM_MODEL` | `qwen2.5:7b` | 本地 LLM 模型 |
| `EMBEDDING_MODEL` | `bge-m3` | 本地嵌入模型 |
| `VLLM_MODEL` | `qwen35-35b-a3b` | vLLM 侧 LLM 模型 |
| `VLLM_EMBEDDING_MODEL` | `octen-embedding-4b` | vLLM 侧嵌入模型 |
| `CHUNK_SIZE` | `300` | 文本分块大小（字符） |
| `SILICONFLOW_LLM_MODEL` | `deepseek-ai/DeepSeek-V4-Flash` | SiliconFlow LLM 模型 |
| `SILICONFLOW_EMBEDDING_MODEL` | `Qwen/Qwen3-Embedding-8B` | SiliconFlow 嵌入模型 |
| `SILICONFLOW_API_KEY` | `（见 .env 文件）` | SiliconFlow API 密钥 |
| `CHUNK_SIZE` | `500` | 文本分块大小（字符） |
| `TOP_K` | `8` | 检索返回的最相关块数 |
| `MEMORY_WINDOW` | `5` | 保留的对话轮数 |
| `RERANK_ENABLED` | `false` | 是否启用重排序（当前仅 SiliconFlow） |
| `RERANK_TOP_K` | `4` | 重排序后保留的文档块数 |
| `SILICONFLOW_RERANK_MODEL` | `Qwen/Qwen3-Reranker-4B` | SiliconFlow 重排序模型 |

## 重排序（Reranker）

在向量检索之后引入交叉编码重排序模型，对 `TOP_K` 个文档块精细打分，保留最相关的 `RERANK_TOP_K` 个传给 LLM。当前仅 SiliconFlow 后端支持。

启用（在 `.env` 中添加）：
```
RERANK_ENABLED=true
RERANK_TOP_K=4
```

## 切换后端

四种方式：

1. **Streamlit 侧边栏** — radio 按钮切换 `ollama` / `vllm` / `siliconflow`
2. **改配置** — 修改 `app/config.py` 的 `DEFAULT_BACKEND`
3. **环境变量** — `$env:DEFAULT_BACKEND="siliconflow"`
4. **Docker 环境变量** — 修改 `docker-compose.yml` 的 `environment.DEFAULT_BACKEND`，或写入 `.env` 文件

各后端地址：

| 后端 | 地址 |
|------|------|
| Ollama | `http://localhost:11434` |
| vLLM | `http://192.168.2.60:8888/v1` |
| SiliconFlow | `https://api.siliconflow.cn/v1` |

使用 SiliconFlow 前需在项目根目录创建 `.env` 文件（参考 `.env.example`），填入真实的 `SILICONFLOW_API_KEY`。

## OCR 图片文字识别

项目包含独立的 OCR 页面（Streamlit 侧边栏自动出现「OCR 图片文字识别」入口），功能：

1. 上传图片（JPG / PNG / BMP / WebP，单张）
2. 选择 OCR 后端（siliconflow / vllm）
3. 点击「OCR 识别」按钮
4. 下方展示：
   - **渲染预览** — Markdown 格式化后的识别结果
   - **Markdown 源码** — `st.code` 原生展示，带一键复制按钮

使用的模型为 **Qwen/Qwen3.5-35B-A3B**（原生多模态视觉语言模型），通过 OpenAI 兼容的视觉 API（`data:image/...;base64`）传入图片。输出自动剥离 thinking 模型的 `<think>` 标签。

## 英中翻译

项目包含独立的英中翻译页面（Streamlit 侧边栏自动出现「英中翻译」入口），基于 **Argos Translate** 离线翻译引擎，纯本地运行，无需联网。

### 首次使用

```bash
# 1. 安装依赖
pip install argostranslate

# 2. 下载 en-zh 翻译模型
.\venv\Scripts\python.exe scripts\download_argos_model.py

# 3. 启动 Streamlit，侧边栏点击「英中翻译」进入
streamlit run app/main.py
```

### 页面功能

1. **左栏** — 输入英文原文（`st.text_area`，高度 370px）
2. **中间按钮** — 「英→中」翻译按钮（`st.button(type="primary")`）+ 清空按钮
3. **右栏** — 中文译文展示（`st.text_area(disabled=True)`，只读）
4. **底部** — 字符数统计 + 翻译耗时（毫秒）

### 技术实现

| 组件 | 选型 | 说明 |
|------|------|------|
| 翻译引擎 | Argos Translate 1.11.0 | 基于 CTranslate2 的离线神经机器翻译 |
| 句子分割 | MiniSBD | `ARGOS_CHUNK_TYPE=MINISBD`，避免 stanza 联网下载资源 |
| 模型路径 | `models/argos-translate/packages/` | 项目本地目录，不依赖全局安装 |
| 模型包 | `translate-en_zh-1_9` | en→zh 翻译模型（CTranslate2 格式） |
| 分词器 | SentencePiece | 内置在模型包中 |
| 下载方式 | 通过 `install_package_for_language_pair()` | 绕过 SSL 验证适配国内网络环境 |

### 关键文件

| 文件 | 说明 |
|------|------|
| `app/pages/6_英中翻译.py` | Streamlit 翻译页面（page_title="英中翻译", layout="wide"） |
| `scripts/download_argos_model.py` | 预下载 en-zh 模型到项目本地目录 |
| `models/argos-translate/packages/` | 模型文件存放目录（已加入 .gitignore） |

### 目录结构

```
models/argos-translate/packages/
└── translate-en_zh-1_9/
    ├── model/                # CTranslate2 模型权重
    ├── stanza/               # 句子分割资源（内置，不需联网下载）
    ├── sentencepiece.model   # SentencePiece 分词器
    └── metadata.json         # 包元信息
```

### 注意事项

- **模型预下载**：首次使用必须运行 `download_argos_model.py`，下载 en-zh 翻译模型到本地
- **MINISBD 模式**：页面前置设置 `os.environ["ARGOS_CHUNK_TYPE"] = "MINISBD"`，避免 stanza 依赖 torch 联网下载资源（国内网络限制）
- **SSL 验证**：下载脚本全局 patch `requests` 跳过 SSL 验证，适配 GitHub 证书验证失败的网络环境
- **翻译质量**：受限于 Argos Translate 内置 en-zh 模型大小，长文本或专业术语翻译可能不够准确
- **离线可用**：模型下载完成后，翻译引擎完全离线运行，无需任何网络请求
- **仅英→中**：当前只支持英文到中文单向翻译，中间按钮列预留了空间便于日后拓展双向翻译

## 中英翻译

项目包含独立的中英翻译页面（Streamlit 侧边栏自动出现「中英翻译」入口），与英中翻译对称实现，基于 **Argos Translate** 离线翻译引擎。

### 首次使用

与英中翻译共享同一下载脚本，下载后自动包含 zh-en 模型：

```bash
# 1. 安装依赖
pip install argostranslate

# 2. 下载 en-zh + zh-en 翻译模型
.\venv\Scripts\python.exe scripts\download_argos_model.py

# 3. 启动 Streamlit，侧边栏点击「中英翻译」进入
streamlit run app/main.py
```

### 页面功能

1. **左栏** — 输入中文原文（`st.text_area`，高度 370px）
2. **中间按钮** — 「中→英」翻译按钮（`st.button(type="primary")`）+ 清空按钮
3. **右栏** — 英文译文展示（`st.text_area(disabled=True)`，只读）
4. **底部** — 字符数统计 + 翻译耗时（毫秒）
5. **Enter 快捷键** — 回车触发送翻译，Shift+Enter 换行

### 技术实现

| 组件 | 选型 | 说明 |
|------|------|------|
| 翻译引擎 | Argos Translate 1.11.0 | 基于 CTranslate2 的离线神经机器翻译 |
| 句子分割 | MiniSBD | `ARGOS_CHUNK_TYPE=MINISBD`，避免 stanza 联网下载资源 |
| 模型路径 | `models/argos-translate/packages/` | 项目本地目录，不依赖全局安装 |
| 模型包 | `translate-zh_en-1_9` | zh→en 翻译模型（CTranslate2 格式） |
| 分词器 | SentencePiece | 内置在模型包中 |
| 下载方式 | 通过 `install_package_for_language_pair()` | 绕过 SSL 验证适配国内网络环境 |

### 关键文件

| 文件 | 说明 |
|------|------|
| `app/pages/7_中英翻译.py` | Streamlit 翻译页面（page_title="中英翻译", layout="wide"） |
| `scripts/download_argos_model.py` | 预下载 en-zh + zh-en 模型到项目本地目录 |
| `models/argos-translate/packages/` | 模型文件存放目录（已加入 .gitignore） |

### 注意事项

- 与英中翻译共享同一下载脚本，无需额外操作
- Enter 快捷键通过 `components.html` 注入 JS 实现，自动绑定到 primary 按钮
- 翻译质量受限于 Argos Translate 内置 zh-en 模型大小
- 离线可用，模型下载完成后无需任何网络请求

## ⚠️ 注意事项

- **Thinking 模型会破坏检索**：`qwen35-35b-a3b` 等 thinking 模型在改写搜索查询时会输出英文思考过程，导致 ChromaDB 匹配失效。应使用 `qwen2.5-32b`、`qwen35-9b` 等非 thinking 模型。
- **文档需手动导入**：上传到 `docs/` 后需点击"导入到知识库"按钮，不走大 LLM，只走 embedding 模型。
- **API Key 存于 `.env`**：密钥配置在项目根目录 `.env` 文件中，该文件已加入 `.gitignore`，不会因 git 操作泄露。
- **按后端分 collection**：每个后端使用独立的 ChromaDB collection（`rag_knowledge_ollama` / `rag_knowledge_vllm` / `rag_knowledge_siliconflow`），避免不同嵌入模型的向量空间混叠。旧 `rag_knowledge` 集合需手动重建索引。
- **引用来源搜索词高亮**：在折叠面板的文档片段中，与用户问题匹配的关键词会以 `<mark>` 标记高亮显示。
- **Windows 网络**：`openai` SDK 底层 `httpx` 偶发 ReadTimeout，不影响 `requests`。

## 技术栈

| 组件 | 选型 |
|------|------|
| 框架 | LangChain 0.3.x |
| 向量库 | ChromaDB |
| 嵌入模型 | bge-m3 / octen-embedding-4b / Qwen3-Embedding-8B |
| 文档解析 | PyPDF / docx2txt |
| 离线翻译 | Argos Translate 1.11.0（en↔zh，CTranslate2） |
| Web UI | Streamlit |
| LLM 后端 | Ollama（本地）/ vLLM（远程）/ SiliconFlow（云 API） |
