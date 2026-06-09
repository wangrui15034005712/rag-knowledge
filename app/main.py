# main.py — Streamlit UI 主入口
# 侧边栏：文档上传/管理/导入/重建索引 + 后端切换 + 连接状态
# 主区域：对话历史 + 流式问答 + 来源引用展示

import streamlit as st
from pathlib import Path
import time
import re

from app.config import DOCS_DIR, OLLAMA_BASE_URL, VLLM_BASE_URL, SILICONFLOW_BASE_URL, SILICONFLOW_API_KEY, DEFAULT_BACKEND
from app.ingest import ingest_documents, get_file_hash, get_chroma_client, get_indexed_hashes, collection_name_for_backend
from app.rag_chain import get_answer_stream, clear_memory
from app.logger import setup_logger

logger = setup_logger(__name__)

st.set_page_config(
    page_title="RAG 私人知识库",
    page_icon="🧠",
    layout="wide",
)

DOCS_PATH = Path(DOCS_DIR)
DOCS_PATH.mkdir(exist_ok=True)

# ── 初始化 Streamlit session state ──
# session_id：区分多轮对话（刷新页面后重置）
# messages：当前对话的消息列表
# ingest_status：文件导入状态 tracking
# backend：当前选中的 LLM 后端
if "session_id" not in st.session_state:
    st.session_state.session_id = f"session_{int(time.time())}"
    logger.info(f"应用启动，session_id={st.session_state.session_id}")
if "messages" not in st.session_state:
    st.session_state.messages = []
if "ingest_status" not in st.session_state:
    st.session_state.ingest_status = {}
if "backend" not in st.session_state:
    st.session_state.backend = DEFAULT_BACKEND


# ── 检查后端服务是否存活 ──

def check_ollama():
    try:
        import requests
        r = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=3)
        ok = r.status_code == 200
        logger.debug(f"Ollama 连接状态: {'正常' if ok else '失败'}")
        return ok
    except Exception:
        logger.warning(f"Ollama 连接失败: {OLLAMA_BASE_URL}")
        return False


def check_vllm():
    try:
        import requests
        r = requests.get(f"{VLLM_BASE_URL}/models", timeout=3)
        ok = r.status_code == 200
        logger.debug(f"vLLM 连接状态: {'正常' if ok else '失败'}")
        return ok
    except Exception:
        logger.warning(f"vLLM 连接失败: {VLLM_BASE_URL}")
        return False


def check_siliconflow():
    try:
        import requests
        headers = {"Authorization": f"Bearer {SILICONFLOW_API_KEY}"}
        r = requests.get(f"{SILICONFLOW_BASE_URL}/models", headers=headers, timeout=3)
        ok = r.status_code == 200
        logger.debug(f"SiliconFlow 连接状态: {'正常' if ok else '失败'}")
        return ok
    except Exception:
        logger.warning(f"SiliconFlow 连接失败: {SILICONFLOW_BASE_URL}")
        return False


# ── 获取 docs/ 目录下的文件列表（仅支持 PDF/TXT/DOCX） ──

def get_docs_files() -> list:
    files = []
    for f in sorted(DOCS_PATH.iterdir()):
        if f.is_file() and f.suffix.lower() in (".pdf", ".txt", ".docx"):
            files.append(f)
    return files


# ── 从 ChromaDB 获取已索引文件的 hash 映射 ──

def get_indexed_sources(backend: str) -> dict:
    try:
        client = get_chroma_client()
        return get_indexed_hashes(client, backend)
    except Exception:
        return {}


# ── 刷新文件导入状态（已导入 / 未导入） ──

def refresh_indexed_status():
    indexed = get_indexed_sources(st.session_state.backend)
    files = get_docs_files()
    status = {}
    for f in files:
        fp = str(f)
        file_hash = get_file_hash(fp)
        idx_hash = indexed.get(fp)
        if idx_hash and idx_hash == file_hash:
            status[fp] = "已导入"
        else:
            status[fp] = "未导入"
    st.session_state.ingest_status = status


# ── 渲染引用来源面板（折叠框，展示匹配到的文档片段） ──

def highlight_keywords(text: str, query: str) -> str:
    if not query:
        return text
    terms = [t for t in re.split(r"[\s,，。！？、；：""''()（）【】\[\]]+", query) if len(t) >= 2]
    for term in terms:
        text = re.sub(re.escape(term), lambda m: f"<mark>{m.group(0)}</mark>", text, flags=re.IGNORECASE)
    return text


def render_source_panel(sources, query=""):
    seen = set()
    unique_sources = []
    for doc in sources:
        src = doc.metadata.get("source", "未知来源")
        page = doc.metadata.get("page", "")
        content = highlight_keywords(doc.page_content[:200], query)
        key = f"{src}_{page}"
        if key not in seen:
            seen.add(key)
            unique_sources.append((src, page, content))

    if not unique_sources:
        return

    with st.expander(f"📎 引用来源（{len(unique_sources)} 项）"):
        for src, page, content in unique_sources:
            fname = Path(src).name
            page_str = f"P.{page}" if page != "" else ""
            st.markdown(f"**{fname}** {page_str}")
            st.markdown(f"<pre style='white-space:pre-wrap;font-size:0.9em'>{content}...</pre>", unsafe_allow_html=True)
            st.divider()


# ══════════════════════════════════════════════════════════
#  侧边栏：文档管理
# ══════════════════════════════════════════════════════════

with st.sidebar:
    st.header("📁 文档管理")

    # LLM 后端切换
    backend_index = {"ollama": 0, "vllm": 1, "siliconflow": 2}
    st.session_state.backend = st.radio(
        "LLM 后端",
        ["ollama", "vllm", "siliconflow"],
        index=backend_index.get(st.session_state.backend, 0),
        horizontal=True,
    )

    # 文件上传
    uploaded_files = st.file_uploader(
        "上传文档（PDF/Word/TXT，可多选）",
        type=["pdf", "txt", "docx"],
        accept_multiple_files=True,
    )

    if uploaded_files:
        for uf in uploaded_files:
            save_path = DOCS_PATH / uf.name
            save_path.write_bytes(uf.getvalue())
            logger.info(f"用户上传文件: {uf.name} ({len(uf.getvalue())} bytes)")
        st.success(f"已上传 {len(uploaded_files)} 个文件到 docs/ 目录")
        refresh_indexed_status()
        st.rerun()

    st.divider()

    # 导入到知识库（解析 → 分块 → 嵌入 → 写入 ChromaDB）
    if st.button("📥 导入到知识库", use_container_width=True):
        files = get_docs_files()
        filepaths = [str(f) for f in files]
        if not filepaths:
            st.warning("docs/ 目录中没有文档")
        else:
            logger.info(f"开始导入 {len(filepaths)} 个文档到知识库 (backend={st.session_state.backend})")
            with st.spinner("正在导入文档..."):
                results = ingest_documents(filepaths, backend=st.session_state.backend)
            for fp, msg in results.items():
                fname = Path(fp).name
                if "成功" in msg:
                    st.success(f"✅ {fname}: {msg}")
                elif "跳过" in msg:
                    st.info(f"⏭️ {fname}: {msg}")
                else:
                    st.error(f"❌ {fname}: {msg}")
            refresh_indexed_status()

    st.divider()

    # 文件列表 + 导入状态
    st.subheader("文件列表")
    files = get_docs_files()
    if not files:
        st.caption("暂无文档")
    else:
        refresh_indexed_status()
        for f in files:
            fp = str(f)
            status = st.session_state.ingest_status.get(fp, "未导入")
            icon = "✅" if status == "已导入" else "⏳"
            st.caption(f"{icon} {f.name}")

    st.divider()

    # 重建索引（删除旧集合后重新导入所有文档）
    if st.button("🔄 重建索引", use_container_width=True):
        files = get_docs_files()
        filepaths = [str(f) for f in files]
        if not filepaths:
            st.warning("docs/ 目录中没有文档")
        else:
            logger.info("开始重建索引")
            with st.spinner("正在重建索引..."):
                try:
                    client = get_chroma_client()
                    collection_name = collection_name_for_backend(st.session_state.backend)
                    try:
                        client.delete_collection(collection_name)
                        logger.debug(f"已删除集合 {collection_name}")
                    except Exception:
                        pass
                    time.sleep(0.5)
                    results = ingest_documents(filepaths, backend=st.session_state.backend)
                except Exception as e:
                    logger.error(f"重建失败: {e}")
                    st.error(f"重建失败：{e}")
                    results = {}
            for fp, msg in results.items():
                fname = Path(fp).name
                if "成功" in msg:
                    st.success(f"✅ {fname}: {msg}")
                elif "跳过" in msg:
                    st.info(f"⏭️ {fname}: {msg}")
                else:
                    st.error(f"❌ {fname}: {msg}")
            refresh_indexed_status()

    st.divider()

    # 后端连接状态指示器
    backend = st.session_state.backend
    if backend == "vllm":
        vllm_ok = check_vllm()
        st.caption(
            f"{'🟢' if vllm_ok else '🔴'} vLLM: {'已连接' if vllm_ok else '未连接'}"
        )
    elif backend == "siliconflow":
        siliconflow_ok = check_siliconflow()
        st.caption(
            f"{'🟢' if siliconflow_ok else '🔴'} SiliconFlow: {'已连接' if siliconflow_ok else '未连接'}"
        )
    else:
        ollama_ok = check_ollama()
        st.caption(
            f"{'🟢' if ollama_ok else '🔴'} Ollama: {'已连接' if ollama_ok else '未连接'}"
        )

    # 导入进度统计
    files = get_docs_files()
    indexed_count = sum(
        1 for fp in st.session_state.ingest_status
        if st.session_state.ingest_status[fp] == "已导入"
    )
    st.caption(f"✅ 已导入 {indexed_count}/{len(files)} 个文档")


# ══════════════════════════════════════════════════════════
#  主区域：聊天问答
# ══════════════════════════════════════════════════════════

# 标题 + 清空对话按钮
col1, col2 = st.columns([0.8, 0.2])
with col1:
    st.title("🧠 RAG 私人知识库")
with col2:
    if st.button("🗑️ 清空对话", use_container_width=True):
        logger.info(f"用户清空对话: {st.session_state.session_id}")
        st.session_state.messages = []
        clear_memory(st.session_state.session_id)
        st.rerun()

# 渲染历史消息
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "sources" in msg and msg["sources"]:
            render_source_panel(msg["sources"], msg.get("query", ""))

# 用户输入 → 提问
if prompt := st.chat_input("💬 输入问题..."):
    logger.info(f"用户提问: {prompt}")
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 流式生成回答
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        sources = []

        try:
            for answer, source_docs in get_answer_stream(
                prompt, st.session_state.session_id, backend=st.session_state.backend
            ):
                # answer 不为 None → 文本 token，追加并刷新 UI（带光标 ▌）
                if answer is not None:
                    full_response += answer
                    placeholder.markdown(full_response + "▌")
                # source_docs 不为 None → 最终的来源文档列表
                if source_docs:
                    sources = source_docs

            # 去掉光标，显示最终回答
            placeholder.markdown(full_response)

            # 显示引用来源
            if sources:
                render_source_panel(sources, prompt)

            # 保存到对话历史
            st.session_state.messages.append({
                "role": "assistant",
                "content": full_response,
                "sources": sources,
                "query": prompt,
            })
            logger.info(f"回答完成，引用 {len(sources)} 个来源")

        except Exception as e:
            logger.error(f"回答异常: {e}")
            backend_name = st.session_state.backend.upper()
            error_msg = f"⚠️ 出错啦：{e}。请检查 {backend_name} 是否正常运行。"
            placeholder.error(error_msg)

# 首次启动时提示（后端未连接且无历史消息）
backend = st.session_state.backend
if backend == "vllm":
    if not check_vllm() and not st.session_state.messages:
        st.info("🔴 vLLM 未连接，请确保远程 vLLM 服务已启动")
elif backend == "siliconflow":
    if not check_siliconflow() and not st.session_state.messages:
        st.info("🔴 SiliconFlow 未连接，请检查 API Key 和网络")
else:
    if not check_ollama() and not st.session_state.messages:
        st.info(
            "🔴 Ollama 未连接，请确保 Ollama 已启动（`ollama serve`）"
        )
