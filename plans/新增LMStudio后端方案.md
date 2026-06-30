# 新增 LM Studio 后端方案

## 背景

用户在本地安装了 LM Studio，加载了 qwen3-4b（LLM）和 bge-m3-gguf（embedding）两个模型。LM Studio 暴露 OpenAI 兼容 API（默认 `http://localhost:1234/v1`），但一次只能加载一个模型。

## 方案：新增 `lmstudio` 后端

不改现有三后端逻辑，新增一个 `lmstudio` 选项。

## 改动文件清单

### 1. `app/config.py` — 新增 3 行配置

```python
# ============================================================
# LM Studio（本地，OpenAI 兼容 API）
# ============================================================
LM_STUDIO_BASE_URL = os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1")
LM_STUDIO_MODEL = os.getenv("LM_STUDIO_MODEL", "qwen3-4b")
LM_STUDIO_EMBEDDING_MODEL = os.getenv("LM_STUDIO_EMBEDDING_MODEL", "bge-m3-gguf")
```

### 2. `app/rag_chain.py` — `get_llm()` 新增 `lmstudio` 分支

位置：`rag_chain.py:106` 附近，`get_llm()` 函数内。

```python
if backend == "lmstudio":
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(
        model=LM_STUDIO_MODEL,
        base_url=LM_STUDIO_BASE_URL,
        api_key="not-needed",
        temperature=0.1,
        streaming=True,
        callbacks=[LoggingCallbackHandler()],
    )
```

import 新增：`LM_STUDIO_BASE_URL, LM_STUDIO_MODEL`

### 3. `app/ingest.py` — `get_embedding()` 新增 `lmstudio` 分支

位置：`ingest.py:77` 附近，`get_embedding()` 函数内。

```python
if backend == "lmstudio":
    from langchain_openai import OpenAIEmbeddings
    return OpenAIEmbeddings(
        model=LM_STUDIO_EMBEDDING_MODEL,
        base_url=LM_STUDIO_BASE_URL,
        api_key="not-needed",
    )
```

import 新增：`LM_STUDIO_BASE_URL, LM_STUDIO_EMBEDDING_MODEL`

### 4. `app/main.py` — 三处改动

| 位置 | 改动 |
|------|------|
| L156-162 | radio 选项从 `["ollama", "vllm", "siliconflow"]` → `["ollama", "vllm", "siliconflow", "lmstudio"]` |
| L54-64 | `check_backend()` 加 `elif backend == "lmstudio": url = f"{LM_STUDIO_BASE_URL}/models"` |
| L340 | 未连接提示加 `"lmstudio": "请确保 LM Studio 已启动 Local Inference Server"` |

import 新增：`LM_STUDIO_BASE_URL`

## 用户日常使用流程

```
导入文档时：LM Studio 加载 bge-m3-gguf → Streamlit 侧边栏选 lmstudio → 点"导入到知识库" 或 "重建索引"
问答时：    LM Studio 加载 qwen3-4b    → 正常聊天（侧边栏保持 lmstudio）
```

侧边栏 radio 固定选 `lmstudio`，只需在 LM Studio GUI 中切换加载的模型。

## 注意事项

1. **LM Studio 单模型限制**：一次只能加载一个模型，用户需手动切换
2. **Embedding 接口兼容性**：bge-m3-gguf 在 LM Studio 下是否暴露 `/v1/embeddings` 需实测验证
3. **首次切后端需重建索引**：新 collection `rag_knowledge_lmstudio`，用 bge-m3-gguf 重新向量化
4. **回退方案**：若 LM Studio 不支持 embedding 接口，则 LLM 走 LM Studio，embedding 走 SiliconFlow（`Qwen3-Embedding-8B`，免费额度）
