# RAG 私人知识库

基于 **LangChain + ChromaDB + Streamlit** 的纯本地 RAG 知识库系统，支持上传 PDF/Word/TXT 文档，通过自然语言问答检索文档内容。

## 功能

- 上传文档（PDF / Word / TXT）
- 自动解析、分块、向量化，存入 ChromaDB
- 多轮对话，历史记忆中检索
- 流式输出（打字机效果）+ 引用来源展示
- 支持 Ollama（本地）、vLLM（远程 GPU）、SiliconFlow（硅基流动 API）三后端

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
│   └── logger.py            # 日志工具
├── docs/                    # 上传文档目录（手动放置或 UI 上传）
├── chroma_db/               # ChromaDB 持久化（自动生成）
├── venv/                    # 虚拟环境
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
| `SILICONFLOW_LLM_MODEL` | `Qwen/Qwen3.6-27B` | SiliconFlow LLM 模型 |
| `SILICONFLOW_EMBEDDING_MODEL` | `BAAI/bge-m3` | SiliconFlow 嵌入模型 |
| `SILICONFLOW_API_KEY` | `your-siliconflow-api-key` | SiliconFlow API 密钥 |
| `TOP_K` | `10` | 检索返回的最相关块数 |
| `MEMORY_WINDOW` | `5` | 保留的对话轮数 |

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

使用 SiliconFlow 前需在 `app/config.py` 中填入真实的 `SILICONFLOW_API_KEY`。

## ⚠️ 注意事项

- **Thinking 模型会破坏检索**：`qwen35-35b-a3b` 等 thinking 模型在改写搜索查询时会输出英文思考过程，导致 ChromaDB 匹配失效。应使用 `qwen2.5-32b`、`qwen35-9b` 等非 thinking 模型。
- **文档需手动导入**：上传到 `docs/` 后需点击"导入到知识库"按钮，不走大 LLM，只走 embedding 模型。
- **Windows 网络**：`openai` SDK 底层 `httpx` 偶发 ReadTimeout，不影响 `requests`。

## 技术栈

| 组件 | 选型 |
|------|------|
| 框架 | LangChain 0.3.x |
| 向量库 | ChromaDB |
| 嵌入模型 | BGE-M3 / octen-embedding-4b |
| 文档解析 | PyPDF / docx2txt |
| Web UI | Streamlit |
| LLM 后端 | Ollama（本地）/ vLLM（远程）/ SiliconFlow（云 API） |
