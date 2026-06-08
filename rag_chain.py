# rag_chain.py — RAG 检索链：检索 ChromaDB + LLM 生成 + 多轮对话记忆管理
#
# 流程：
#   用户问题 → 改写为搜索查询 → ChromaDB 向量检索 TOP_K 文档块
#   → 检索结果作为 {context} 填入 QA Prompt → LLM 生成回答 → 逐 token 流式返回

from typing import List, Dict, Generator, Tuple
from pathlib import Path
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.callbacks import BaseCallbackHandler
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_classic.chains import create_history_aware_retriever, create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain_core.documents import Document

from config import (
    OLLAMA_BASE_URL, LLM_MODEL, EMBEDDING_MODEL,
    VLLM_BASE_URL, VLLM_MODEL, DEFAULT_BACKEND,
    CHROMA_DB_DIR, TOP_K, MEMORY_WINDOW,
)
from ingest import get_embedding
from logger import setup_logger

logger = setup_logger(__name__)

# ── 内存会话历史：key = session_id, value = ChatMessageHistory ──
sessions: Dict[str, ChatMessageHistory] = {}


# ── 回调处理器：打印 LLM 输入/输出 和 检索结果，便于调试 ──

class LoggingCallbackHandler(BaseCallbackHandler):
    def on_chat_model_start(self, serialized, messages, **kwargs):
        logger.info(f"--- LLM Prompt ---\n{messages[0][0].content[:500]}\n--- End Prompt ---")

    def on_llm_start(self, serialized, prompts, **kwargs):
        logger.info(f"--- LLM Prompt ---\n{prompts[0][:500]}\n--- End Prompt ---")

    def on_llm_end(self, response, **kwargs):
        text = response.generations[0][0].text
        logger.info(f"LLM 回答: {text[:300]}..." if len(text) > 300 else f"LLM 回答: {text}")

    def on_retriever_start(self, serialized, query, **kwargs):
        logger.info(f"检索查询: {query}")

    def on_retriever_end(self, documents, **kwargs):
        logger.info(f"检索结果: {len(documents)} 个文档块")
        for i, doc in enumerate(documents):
            src = Path(doc.metadata.get("source", "?")).name
            logger.info(f"  [{i}] {src}: {doc.page_content[:150]}...")


# ── 根据 session_id 获取/创建会话历史 ──

def get_session_history(session_id: str) -> ChatMessageHistory:
    if session_id not in sessions:
        logger.debug(f"创建新会话记忆: {session_id}")
        sessions[session_id] = ChatMessageHistory()
    return sessions[session_id]


# ── 加载 ChromaDB 向量库（指定 embedding 模型用于查询时向量化） ──

def get_vector_store(backend: str = DEFAULT_BACKEND) -> Chroma:
    embedding = get_embedding(backend)
    logger.debug(f"加载向量库: {CHROMA_DB_DIR}")
    return Chroma(
        collection_name="rag_knowledge",
        embedding_function=embedding,
        persist_directory=CHROMA_DB_DIR,
    )


def format_docs(docs: List[Document]) -> str:
    return "\n\n".join(d.page_content for d in docs)


# ── 初始化 LLM：根据后端类型选择 ChatOpenAI（vLLM）或 ChatOllama ──

def get_llm(backend: str = DEFAULT_BACKEND):
    if backend == "vllm":
        from langchain_openai import ChatOpenAI
        logger.info(f"初始化 LLM(vLLM): {VLLM_MODEL} @ {VLLM_BASE_URL}")
        return ChatOpenAI(
            model=VLLM_MODEL,
            base_url=VLLM_BASE_URL,
            api_key="none",
            temperature=0.1,
            streaming=True,
            callbacks=[LoggingCallbackHandler()],
        )
    logger.info(f"初始化 LLM(Ollama): {LLM_MODEL} @ {OLLAMA_BASE_URL}")
    return ChatOllama(
        model=LLM_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=0.1,
        streaming=True,
        callbacks=[LoggingCallbackHandler()],
    )


# ── 构建 RAG 链 ──
#
# 链结构：
#   输入 → 历史感知检索 (history_aware_retriever)
#        → 文档链 (document_chain: 基于检索结果 + 对话历史生成回答)
#        → 输出 answer + context
#
# 外层包 RunnableWithMessageHistory 管理多轮对话记忆

def build_chain(backend: str = DEFAULT_BACKEND):
    logger.info(f"构建 RAG 链: backend={backend}, TOP_K={TOP_K}, MEMORY_WINDOW={MEMORY_WINDOW}")
    llm = get_llm(backend)
    vector_store = get_vector_store(backend)
    retriever = vector_store.as_retriever(search_kwargs={"k": TOP_K})

    # Prompt 1：将对话历史 + 用户问题改写为独立搜索查询（用于检索）
    #
    # 用户说 "它多少钱" 但前面聊过 "iPhone15"，LLM 改写后变成 "iPhone15 价格"
    # ⚠️ 如果 LLM 是 thinking 模型，这里会输出思考过程而非搜索词，导致检索跑偏
    contextualize_prompt = ChatPromptTemplate.from_messages([
        ("system", "基于对话历史和用户最新问题，生成一个独立表述的搜索查询。"),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_prompt
    )

    # Prompt 2：基于检索到的文档块（{context}）+ 对话历史 回答问题
    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个基于本地知识库的智能问答助手。请基于以下已知信息回答问题。"
                   "如果无法从已知信息中找到答案，请如实告知。回答要简洁准确。"
                   "请全程使用中文思考和回答。\n\n已知信息：\n{context}"),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])
    document_chain = create_stuff_documents_chain(llm, qa_prompt)

    # 组合：检索 → 生成
    retrieval_chain = create_retrieval_chain(history_aware_retriever, document_chain)

    # 外层包装对话记忆管理
    chain_with_history = RunnableWithMessageHistory(
        retrieval_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )

    return chain_with_history


# ── 流式问答入口：逐 token 将回答推给 Streamlit UI ──
#
# 返回值格式：
#   (token_str, None)       → 生成的文本片段
#   (None, [Document, ...]) → 检索到的来源文档（最后一个 yield）

def get_answer_stream(
    query: str, session_id: str, backend: str = DEFAULT_BACKEND
) -> Generator[Tuple[str, List[Document]], None, None]:
    logger.info(f"收到用户问题: {query} (backend={backend})")

    chain = build_chain(backend)

    config = {"configurable": {"session_id": session_id}}

    source_docs = []
    seen_sources = set()

    # 逐 chunk 消费 chain.stream 的输出
    for chunk in chain.stream({"input": query}, config=config):
        if isinstance(chunk, dict):
            if "answer" in chunk and chunk["answer"]:
                yield chunk["answer"], None
            elif "context" in chunk:
                source_docs = chunk.get("context", [])
                for doc in source_docs:
                    src = Path(doc.metadata.get("source", "?")).name
                    if src not in seen_sources:
                        seen_sources.add(src)
                        logger.info(f"引用来源: {src}")

    logger.info(f"回答完成, 引用 {len(seen_sources)} 个来源文件")

    # 裁剪超出窗口的旧对话历史
    trim_memory(session_id)

    # 最后 yield 来源文档，通知前端展示引用
    yield None, source_docs


# ── 裁剪对话记忆：保留最近 MEMORY_WINDOW 轮（每轮一问一答 = 2 条消息） ──

def trim_memory(session_id: str):
    history = sessions.get(session_id)
    if not history:
        return
    messages = history.messages
    max_messages = MEMORY_WINDOW * 2
    if len(messages) > max_messages:
        before = len(messages)
        history.messages = messages[-max_messages:]
        logger.debug(f"裁剪会话记忆: {before} -> {len(history.messages)} 条消息")


# ── 清空指定会话的记忆 ──

def clear_memory(session_id: str):
    if session_id in sessions:
        logger.debug(f"清除会话记忆: {session_id}")
        del sessions[session_id]
