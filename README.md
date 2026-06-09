# RAG 私人知识库

基于 **LangChain + ChromaDB + Streamlit** 的纯本地 RAG 知识库系统，支持上传 PDF/Word/TXT 文档，通过自然语言问答检索文档内容。

## 功能

- 上传文档（PDF / Word / TXT）
- 自动解析、分块、向量化，存入 ChromaDB
- 多轮对话，历史记忆中检索
- 流式输出（打字机效果）+ 引用来源展示
- 支持 Ollama（本地）、vLLM（远程 GPU）、SiliconFlow（硅基流动 API）三后端
- OCR 图片文字识别（Qwen3.5-35B-A3B 多模态视觉模型，支持 SiliconFlow / vLLM）
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

### 5. 使用流程

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
│       └── 1_OCR.py         # OCR 图片文字识别
├── docs/                    # 上传文档目录（手动放置或 UI 上传）
├── chroma_db/               # ChromaDB 持久化（自动生成）
├── venv/                    # 虚拟环境
├── .env                     # 环境变量（API Key 等，不入库）
├── .env.example             # 环境变量模板（可入库）
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

三种方式：

1. **Streamlit 侧边栏** — radio 按钮切换 `ollama` / `vllm` / `siliconflow`
2. **改配置** — 修改 `app/config.py` 的 `DEFAULT_BACKEND`
3. **环境变量** — `$env:DEFAULT_BACKEND="siliconflow"`

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
| Web UI | Streamlit |
| LLM 后端 | Ollama（本地）/ vLLM（远程）/ SiliconFlow（云 API） |
