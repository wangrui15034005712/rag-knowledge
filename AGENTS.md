# AGENTS.md — RAG 私人知识库

## 启动

```bash
cd D:\User\git\rag-test
.\venv\Scripts\python.exe -m streamlit run app/main.py --server.port 8501
# 浏览器打开 http://localhost:8501
```

## 架构要点

- **Streamlit + LangChain + ChromaDB**，所有组件纯本地（vLLM / SiliconFlow 可选远程）
- 三后端：`ollama`（本地 Ollama）| `vllm`（远程 OpenAI 兼容 API）| `siliconflow`（硅基流动 API）
- 切换后端在 `app/config.py:30` 改 `DEFAULT_BACKEND`，或 Streamlit 侧边栏 radio
- vLLM 地址 `http://192.168.2.60:8888/v1`；SiliconFlow 地址 `https://api.siliconflow.cn/v1`（需在 `.env` 文件填 API Key）

## 关键目录

| 路径 | 用途 |
|------|------|
| `app/main.py` | Streamlit UI 入口 |
| `app/rag_chain.py` | RAG 检索链 + 流式输出 |
| `app/ingest.py` | 文档解析 → 分块 → 嵌入 → 写入 ChromaDB |
| `app/config.py` | 所有可调参数（模型名、chunk 大小、TOP_K 等） |
| `app/ocr_engine.py` | OCR 视觉识别引擎（base64 → 视觉 API → Markdown） |
| `app/pages/1_OCR.py` | OCR 图片文字识别页面（独立 Streamlit 页面） |
| `docs/` | 上传文档存放目录 |
| `chroma_db/` | ChromaDB 持久化目录（自动创建） |
| `.env` | 环境变量（API Key 等，不入库） |
| `.env.example` | 环境变量模板（可入库） |

## 流程：提问 → 回答

1. LLM 将用户问题 + 对话历史 **改写为独立搜索查询**（`create_history_aware_retriever`）
2. ChromaDB 做 **向量相似度匹配**，返回 TOP_K=10 个文档块
3. 检索结果填入 QA Prompt 的 `{context}`，LLM 生成回答
4. 回答通过 `chain.stream()` **逐 token 流式返回**，UI 显示光标效果

## ⚠️ Thinking 模型会破坏检索

`qwen35-35b-a3b` 是 thinking 模型，在步骤 1（查询改写）会输出英文思考过程而非搜索词，导致 ChromaDB 匹配完全失效。

**解决办法**：`config.py:9` 换非 thinking 模型，如 `qwen2.5-32b`、`qwen35-9b`。

## 文档导入

- 上传文档到 `docs/` 后，需点击"导入到知识库"按钮（手动触发）
- **不走大 LLM**，只走 embedding 模型（`bge-m3` / `octen-embedding-4b` / `Qwen3-Embedding-8B` via SiliconFlow）
- 增量去重：SHA256 hash 对比，内容无变化自动跳过
- 分块打印在导入日志中可见（前 2 个 chunk 预览）
- **按后端分 collection**：各后端使用独立 ChromaDB 集合（`rag_knowledge_ollama` / `rag_knowledge_vllm` / `rag_knowledge_siliconflow`），避免不同 embedding 模型的向量空间混叠

## Debug 日志

`LoggingCallbackHandler` **全文无截断**打印：
- LLM 收到的完整 Prompt（含 System/Human/AI 每条消息 + `{context}` 完整文档块）
- 改写后的搜索查询
- 检索到的每个文档块全文
- LLM 生成的完整回答
- 日志级别在 `config.py:53` 设置 `LOG_LEVEL`

## OCR 图片文字识别

独立页面（`app/pages/1_OCR.py`），入口在 Streamlit 侧边栏自动出现。

1. 侧边栏选择 OCR 后端（siliconflow / vllm）
2. 上传一张图片（JPG / PNG / BMP / WebP）
3. 点击「OCR 识别」→ 调用视觉 API（OpenAI 兼容格式，base64 传图）
4. 展示渲染预览 + Markdown 源码（`st.code` 带复制按钮）

**视觉模型**：`Qwen/Qwen3.5-35B-A3B`（原生多模态，支持 text + image + video 输入）
**thinking 处理**：`ocr_engine.py:23` 的 `_clean_thinking()` 剥离 `<think>`/`<reasoning>` 标签
**不保存文件**：识别结果仅预览，不写入 `docs/` 目录

## 已知问题

- `httpx`（openai SDK 底层）在 Windows 下偶发 ReadTimeout，`requests` 不受影响
- `RunnableWithMessageHistory` 有 DeprecationWarning，但 langchain 0.3.x 仍可用
- GBK 编码问题：含 `\xa0` 等内容日志到 console 可能崩溃，日志文件不受影响
- 旧 `rag_knowledge` 集合不会自动迁移到新命名 `rag_knowledge_{backend}`，切换后端后需手动「重建索引」
