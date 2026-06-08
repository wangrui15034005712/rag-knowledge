# RAG 私人知识库 — 项目计划

## 方案概述

基于 **LangChain + ChromaDB + Ollama** 的纯本地 RAG 知识库系统，支持上传 PDF/Word/TXT 文档，通过自然语言问答检索文档内容。

## 技术栈

| 组件 | 技术选型 | 说明 |
|------|---------|------|
| 框架 | LangChain | 成熟 RAG 生态，文档完善 |
| LLM | Qwen2.5:7b (Ollama) | 阿里千问，中文效果优秀，本地运行 |
| Embedding | bge-m3 (Ollama) | 中英文通用嵌入模型 |
| 向量数据库 | ChromaDB | 轻量级，零配置，本地持久化 |
| 文档解析 | PyPDF / docx2txt / TextLoader | PDF/Word/TXT 文字版解析 |
| Web UI | Streamlit | Python 原生，快速搭建 |
| 数据存储 | 本地文件系统 | 所有数据在本地，不联网 |

## 数据流

```
用户上传文档 / 放入 docs/
         ↓
  保存到 docs/ 目录
         ↓
  点击"导入"按钮（手动触发）
         ↓
  解析文件 (PyPDF / docx2txt / TextLoader)
         ↓
  文本分块 (RecursiveCharacterTextSplitter, 500字符/块, 重叠100字符)
         ↓
  Embedding 向量化 (bge-m3 via Ollama)
         ↓
  存入 ChromaDB (hash 去重，增量更新)
         ↓
  ─────────────────────────────────────
         ↑
  用户提问
         ↓
  语义检索 Top-K (K=4)
         ↓
  构建上下文 + 最近5轮对话历史
         ↓
  LLM 流式生成回答 (Qwen2.5:7b via Ollama)
         ↓
  打字机效果输出 + 引用来源展示（折叠面板）
```

## 项目结构

```
rag-test/
├── main.py              # Streamlit 主入口（UI + 路由）
├── config.py            # 配置（模型、分块、检索参数）
├── requirements.txt     # Python 依赖
├── ingest.py            # 文档解析 → 分块 → 向量化 → 存储（hash 去重）
├── rag_chain.py         # 检索 + LLM 生成（流式 + 多轮记忆）
├── docs/                # 上传的文档存放目录
├── chroma_db/           # ChromaDB 持久化目录（自动创建）
└── PLAN.md              # 项目计划文档
```

## 页面布局设计

```
┌──────────────────────────────────────────────────────────┐
│  🧠 RAG 私人知识库                           [🗑 清空对话] │
├──────────────┬───────────────────────────────────────────┤
│  📁 文档管理  │                                           │
│  ──────────  │  ┌─ 🙋 用户 ──────────────────────────┐  │
│  [📤 上传文档] │  │ 什么是 RAG？                        │  │
│  (多文件)     │  └────────────────────────────────────┘  │
│              │  ┌─ 🤖 助手 ──────────────────────────┐  │
│  ──────────  │  │ RAG 是检索增强生成... ▍(打字机效果)   │  │
│  已入库文件   │  │                                      │  │
│  ☑ report.pdf│  │  📎 引用来源 [展开 ▼]               │  │
│  ☑ 笔记.docx │  │  ├ report.pdf P.3: "RAG是一种..."   │  │
│  ☐ 新文档.txt │  │  └ 笔记.docx P.1: "检索增强..."    │  │
│              │  └────────────────────────────────────┘  │
│  [📥 导入到   │                                           │
│   知识库]     │  ┌─ 🙋 用户 ──────────────────────────┐  │
│              │  │ 它有什么优势？                       │  │
│  ──────────  │  └────────────────────────────────────┘  │
│  [🔄 重建索引] │  ┌─ 🤖 助手 ──────────────────────────┐  │
│              │  │ 优势包括... ▍(打字机效果)             │  │
│  状态指示器   │  │  📎 引用来源 [展开 ▼]               │  │
│  ✅ 已导入    │  └────────────────────────────────────┘  │
│  2 个文档     │                                           │
│  🔗 Ollama ✓ │  ┌────────────────────────────────────┐  │
│              │  │ 💬 输入问题...          [发送 ➤]    │  │
│              │  └────────────────────────────────────┘  │
└──────────────┴───────────────────────────────────────────┘
```

## 交互说明

| 区域 | 元素 | 行为 |
|------|------|------|
| **侧边栏** | 上传按钮 | `st.file_uploader` 多选 PDF/Word/TXT，上传后自动保存到 `docs/` |
| | 文件列表 | 展示 `docs/` 中所有文件，已索引的标 ☑，未导入的标 ☐ |
| | 导入按钮 | 手动触发增量索引导入（hash 去重），需等待进度条 |
| | 重建索引 | 重新扫描全部文件进行增量刷新 |
| | 状态区 | 显示已导入文档数 + Ollama 连接状态（绿点/红点） |
| **主聊天区** | 消息气泡 | 用户消息右对齐（蓝色背景），助手回复左对齐（灰色背景） |
| | 流式输出 | Streamlit `st.write_stream` 实现打字机效果 |
| | 引用来源 | 折叠面板 Collapsible，展示文件名 + 页码 + 片段预览 |
| | 输入框 | `st.chat_input` 底部固定，发送后清空 |
| | 清空按钮 | 顶部右侧，重置会话消息和记忆 |

## 模块设计

### `config.py` — 配置

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama 服务地址 |
| `LLM_MODEL` | `qwen2.5:7b` | 大语言模型 |
| `EMBEDDING_MODEL` | `bge-m3` | 嵌入模型 |
| `CHUNK_SIZE` | `500` | 文本块大小（字符数） |
| `CHUNK_OVERLAP` | `100` | 块间重叠字符数 |
| `TOP_K` | `4` | 检索返回的最相关片段数 |
| `MEMORY_WINDOW` | `5` | 对话记忆保留轮数 |
| `CHROMA_DB_DIR` | `./chroma_db` | 向量库持久化路径 |
| `DOCS_DIR` | `./docs` | 文档存放路径 |

### `ingest.py` — 文档入库

- `get_file_hash(filepath: str) -> str` — 计算文件 SHA256
- `load_document(filepath: str) -> List[Document]` — 根据扩展名调用不同 Loader
- `split_documents(docs: List[Document]) -> List[Document]` — RecursiveCharacterTextSplitter 分块
- `get_embedding_function() -> Embeddings` — 返回 bge-m3 嵌入模型（OllamaEmbeddings）
- `get_vector_store() -> Chroma` — 加载/创建 ChromaDB（持久化）
- `ingest_documents(filepaths: List[str]) -> Dict` — 增量导入：对每个文件计算 hash，查询 ChromaDB `file_hash` metadata 判断是否已存在，不存在则解析 → 分块 → 嵌入 → 存入

**去重策略：** 每个 Document 的 metadata 中存储 `file_hash`，入库前按 filepath 去 ChromaDB 的 metadata filter 查询是否已存在。

### `rag_chain.py` — RAG 检索链

- `setup_llm() -> ChatOllama` — 初始化 Qwen2.5:7b，设置 stream=True
- `setup_retriever() -> BaseRetriever` — 加载 ChromaDB 为 retriever，search_kwargs={"k": TOP_K}
- `get_session_history(session_id: str) -> ChatMessageHistory` — 会话历史管理（基于内存 dict，按 session_id 隔离）
- `format_docs(docs: List[Document]) -> str` — 格式化检索结果
- `build_chain() -> Runnable` — 构建 LCEL 链：context（retriever 格式化） + question → prompt → llm → output
- `get_answer_stream(query: str, session_id: str) -> Generator` — 接收问题，结合 context 和历史，流式生成回答，同时返回引用的 source 列表

**Prompt 模板：**
```
你是一个基于本地知识库的智能问答助手。

已知信息：
{context}

对话历史：
{history}

用户问题：{question}

请基于已知信息回答，如果无法从已知信息中找到答案，请如实告知。回答要简洁准确。
```

### `main.py` — Streamlit UI

**侧边栏逻辑：**
1. `st.file_uploader` 接收上传 → 保存到 `docs/`
2. 刷新文件列表，读取 `docs/` 全部文件
3. 查询 ChromaDB 已索引的 hash 集合，对比标记 ☑/☐
4. "导入"按钮 → 调用 `ingest_documents()`（显示进度）
5. "重建索引"按钮 → 重新扫描全部
6. 显示 Ollama 连接状态

**主区逻辑：**
1. 初始化 session_state（messages 列表、session_id、memory）
2. 顶部导航栏 + 清空按钮
3. 遍历 messages 渲染历史对话
4. `st.chat_input` 接收用户输入
5. 调用 `get_answer_stream()` 流式输出
6. 输出完成后渲染引用来源折叠面板
7. 新消息追加到 messages，保留 <= 5 轮

## 功能清单

### 文档管理（侧边栏）
- [x] 上传文档（PDF/Word/TXT，可多选）
- [x] 上传后自动保存到 `docs/` 目录
- [x] 手动导入文档到向量库（增量更新，hash 去重）
- [x] 查看 `docs/` 目录文件列表及索引状态
- [x] 重建知识库索引（增量刷新）
- [x] 显示已导入文档数量
- [x] Ollama 连接状态指示器

### 问答交互（主区域）
- [x] 聊天式问答界面
- [x] 流式输出（打字机效果）
- [x] 展示引用来源（折叠面板，文件名 + 页码 + 片段）
- [x] 多轮对话记忆（最多保留最近 5 轮）
- [x] 清空对话记录
- [x] Ollama 连接异常提示

## 环境要求

| 项目 | 最低要求 | 推荐配置 |
|------|---------|---------|
| 操作系统 | Windows / macOS / Linux | - |
| Python | 3.9+ | 3.12 |
| 内存 | 16 GB | 32 GB |
| 显存 | 6 GB | 8 GB+ |
| Ollama | 已安装并运行 | 最新版 |
| 模型 | qwen2.5:7b + bge-m3 | 已拉取 |

## 启动方式

```bash
# 1. 安装 Python 依赖
pip install -r requirements.txt

# 2. 启动 Ollama（需提前安装并拉取模型）
ollama serve

# 3. 启动知识库
python main.py
# 浏览器打开 http://localhost:8501
```

## 实施步骤

1. 创建 `requirements.txt`
2. 编写 `config.py`
3. 编写 `ingest.py`
4. 编写 `rag_chain.py`
5. 编写 `main.py`
6. 端到端验证测试
