# LangChain 全面升级到 1.x 方案

## 背景

当前已安装 `langchain 1.3.4` / `langchain-core 1.4.1`，但 `requirements.txt` 仍写 `>=0.3.0`，
且代码中使用了已 sunset 的 `langchain-community` 组件。需要做版本锁定 + 代码迁移。

## 流程

```
master ──→ v1 (保存当前代码快照并推送) ─→ 切回 master 做升级改动 ─→ 验证
```

## 阶段 1：保存 v1 快照

```bash
git checkout -b v1          # 从 master 创建 v1，包含当前代码
git push origin v1          # 推送到远端
git checkout master         # 回到 master
```

## 阶段 2：在 master 上做改动

### 2.1 `requirements.txt` — 版本约束更新

| 包 | 旧值 | 新值 | 原因 |
|---|---|---|---|
| `langchain` | `>=0.3.0` | `>=1.0.0` | 1.x LTS |
| `langchain-core` | `>=0.3.0` | `>=1.0.0` | 1.x LTS |
| `langchain-classic` | `>=0.3.0` | `>=1.0.0` | 1.x 已发布 |
| `langchain-chroma` | `>=0.2.0` | `>=1.0.0` | `langchain-chroma` 1.x 可用 |
| `langchain-ollama` | `>=0.2.0` | `>=1.0.0` | `langchain-ollama` 1.x 可用 |
| `langchain-openai` | `>=0.2.0` | `>=1.0.0` | `langchain-openai` 1.x 可用 |
| `langchain-text-splitters` | `>=0.3.0` | `>=1.0.0` | `langchain-text-splitters` 1.x 可用 |
| `langchain-community` | `>=0.3.0` | **不变** | 无 1.x，仅用于 document loaders |

### 2.2 `app/rag_chain.py` — 迁移 ChatMessageHistory

**import 行（第 14 行）：**

```python
# 删除
from langchain_community.chat_message_histories import ChatMessageHistory

# 改为
from langchain_core.chat_history import InMemoryChatMessageHistory
```

**3 处引用替换：**

| 行号 | 原内容 | 替换为 |
|---|---|---|
| 34 | `sessions: Dict[str, ChatMessageHistory] = {}` | `sessions: Dict[str, InMemoryChatMessageHistory] = {}` |
| 67 | `def get_session_history(session_id: str) -> ChatMessageHistory:` | `def get_session_history(session_id: str) -> InMemoryChatMessageHistory:` |
| 70 | `sessions[session_id] = ChatMessageHistory()` | `sessions[session_id] = InMemoryChatMessageHistory()` |

> `InMemoryChatMessageHistory` API 与 `ChatMessageHistory` 完全一致（继承自同一基类），纯改名，无行为差异。

### 2.3 `langchain-community` 保留原因

- `TextLoader` / `PyPDFLoader` 仍在 `langchain_community` 中，尚无 standalone 替代包
- 官方已 sunset，但代码仍正常工作
- 等官方拆出独立包后再迁移

## 阶段 3：升级依赖

```bash
.\venv\Scripts\python.exe -m pip install -U ^
  langchain langchain-core langchain-classic ^
  langchain-chroma langchain-ollama ^
  langchain-openai langchain-text-splitters
```

## 阶段 4：验证

```bash
# 1. 检查 import
.\venv\Scripts\python.exe -c "import app.rag_chain; import app.ingest; print('OK')"

# 2. 检查各包版本
.\venv\Scripts\python.exe -c "
import langchain; print('langchain', langchain.__version__)
import langchain_core; print('core', langchain_core.__version__)
import langchain_chroma; print('chroma', langchain_chroma.__version__)
import langchain_ollama; print('ollama', langchain_ollama.__version__)
"

# 3. 启动 Streamlit 确认无报错
.\venv\Scripts\python.exe -m streamlit run app/main.py --server.headless true
```

## 预期结果

- 所有包版本 >= 1.0.0（`langchain-community` 除外）
- 对话记忆正常工作（`InMemoryChatMessageHistory`）
- 文档导入 / 检索 / 问答全流程正常
- 无 deprecated warning（除了 community 自身的 sunset 提示）
