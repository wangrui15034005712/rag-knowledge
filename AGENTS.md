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
- vLLM 地址 `http://192.168.2.60:8888/v1`；SiliconFlow 地址 `https://api.siliconflow.cn/v1`（需在 `config.py:25` 填 API Key）

## 关键目录

| 路径 | 用途 |
|------|------|
| `app/main.py` | Streamlit UI 入口 |
| `app/rag_chain.py` | RAG 检索链 + 流式输出 |
| `app/ingest.py` | 文档解析 → 分块 → 嵌入 → 写入 ChromaDB |
| `app/config.py` | 所有可调参数（模型名、chunk 大小、TOP_K、API Key 等） |
| `docs/` | 上传文档存放目录 |
| `chroma_db/` | ChromaDB 持久化目录（自动创建） |

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
- **不走大 LLM**，只走 embedding 模型（`bge-m3` / `octen-embedding-4b` / `BAAI/bge-m3` via SiliconFlow）
- 增量去重：SHA256 hash 对比，内容无变化自动跳过
- 分块打印在导入日志中可见（前 2 个 chunk 预览）

## Debug 日志

`LoggingCallbackHandler` **全文无截断**打印：
- LLM 收到的完整 Prompt（含 System/Human/AI 每条消息 + `{context}` 完整文档块）
- 改写后的搜索查询
- 检索到的每个文档块全文
- LLM 生成的完整回答
- 日志级别在 `config.py:53` 设置 `LOG_LEVEL`

## 已知问题

- `httpx`（openai SDK 底层）在 Windows 下偶发 ReadTimeout，`requests` 不受影响
- `RunnableWithMessageHistory` 有 DeprecationWarning，但 langchain 0.3.x 仍可用
- GBK 编码问题：含 `\xa0` 等内容日志到 console 可能崩溃，日志文件不受影响
