import streamlit as st
import streamlit.components.v1 as components
import time
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.config import (
    OLLAMA_BASE_URL, LLM_MODEL,
    VLLM_BASE_URL, VLLM_MODEL,
    SILICONFLOW_BASE_URL, SILICONFLOW_LLM_MODEL, SILICONFLOW_API_KEY,
    LM_STUDIO_BASE_URL, LM_STUDIO_MODEL,
    DEFAULT_BACKEND,
)

st.set_page_config(
    page_title="大模型翻译",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("🤖 大模型英中翻译")

st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 100%;
    }
    .stTextArea textarea {
        min-height: 370px !important;
    }
    header { visibility: hidden; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# === 后端映射 ===

BACKEND_OPTIONS = {
    "Ollama": "ollama",
    "vLLM": "vllm",
    "SiliconFlow": "siliconflow",
    "LM Studio": "lmstudio",
}

# === LLM 加载 ===

@st.cache_resource
def get_llm(backend: str):
    if backend == "ollama":
        from langchain_ollama import ChatOllama
        return ChatOllama(
            model=LLM_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=0.1,
            streaming=True,
        )
    if backend == "vllm":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=VLLM_MODEL,
            base_url=VLLM_BASE_URL,
            api_key="none",
            temperature=0.1,
            streaming=True,
        )
    if backend == "lmstudio":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=LM_STUDIO_MODEL,
            base_url=LM_STUDIO_BASE_URL,
            api_key="not-needed",
            temperature=0.1,
            streaming=True,
        )
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(
        model=SILICONFLOW_LLM_MODEL,
        base_url=SILICONFLOW_BASE_URL,
        api_key=SILICONFLOW_API_KEY,
        temperature=0.1,
        streaming=True,
    )

TRANSLATION_PROMPT = (
    "You are a professional translator. Translate the following English text to "
    "Chinese naturally and accurately. Output ONLY the translation, no explanations, "
    "no notes, no greetings.\n\n{text}"
)

# === Session State ===

if "en_input" not in st.session_state:
    st.session_state.en_input = ""
if "zh_output" not in st.session_state:
    st.session_state.zh_output = ""
if "translate_time" not in st.session_state:
    st.session_state.translate_time = 0
if "selected_backend" not in st.session_state:
    st.session_state.selected_backend = DEFAULT_BACKEND

# === 翻译函数 ===

def clear_all():
    st.session_state.en_input = ""
    st.session_state.zh_output = ""
    st.session_state.translate_time = 0

# === UI 布局 ===

col_input, col_buttons, col_output = st.columns([4, 1, 4], gap="medium")

with col_input:
    st.subheader("英文原文")

    en_input = st.text_area(
        "英文原文",
        value=st.session_state.en_input,
        height=370,
        placeholder="在此输入英文文本...\n\nEnter 发送 | Shift+Enter 换行",
        label_visibility="collapsed",
    )
    if en_input != st.session_state.en_input:
        st.session_state.en_input = en_input

    input_len = len(st.session_state.en_input.strip())
    st.caption(f"字符数: {input_len}")

with col_buttons:
    st.markdown("<br>", unsafe_allow_html=True)

    backend_label = st.selectbox(
        "翻译引擎",
        options=list(BACKEND_OPTIONS.keys()),
        index=list(BACKEND_OPTIONS.values()).index(st.session_state.selected_backend),
        label_visibility="collapsed",
    )
    st.session_state.selected_backend = BACKEND_OPTIONS[backend_label]

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("英->中", use_container_width=True, type="primary"):
        st.session_state.translate_trigger = True

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("清空", use_container_width=True):
        clear_all()
        st.rerun()

with col_output:
    st.subheader("中文译文")
    output_placeholder = st.empty()

    if st.session_state.get("translate_trigger", False):
        text = st.session_state.en_input.strip()
        if text:
            try:
                llm = get_llm(st.session_state.selected_backend)
                from langchain_core.messages import HumanMessage

                prompt = TRANSLATION_PROMPT.format(text=text)

                start = time.time()
                full = ""
                stream = llm.stream([HumanMessage(content=prompt)])
                for chunk in stream:
                    content = chunk.content if hasattr(chunk, "content") else str(chunk)
                    full += content
                    output_placeholder.markdown(full + "▍")
                output_placeholder.markdown(full)

                elapsed = time.time() - start
                st.session_state.zh_output = full
                st.session_state.translate_time = elapsed
            except Exception as e:
                st.error(f"翻译失败: {e}")
                output_placeholder.markdown(st.session_state.zh_output or "")
        st.session_state.translate_trigger = False

    elif st.session_state.zh_output:
        output_placeholder.markdown(st.session_state.zh_output)

    output_len = len(st.session_state.zh_output)
    stats_col1, stats_col2 = st.columns(2)
    with stats_col1:
        st.caption(f"字符数: {output_len}")
    with stats_col2:
        if st.session_state.translate_time > 0:
            st.caption(f"耗时: {st.session_state.translate_time*1000:.0f} ms")

# === Enter 快捷键 ===

components.html("""
<script>
(function() {
    var doc = window.parent.document;
    var input = doc.querySelector('textarea[data-testid="stTextArea"]');
    var btn = doc.querySelector('button[kind="primary"]');
    if (input && btn) {
        input.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                btn.click();
            }
        });
    }
})();
</script>
""", height=0)

# === 底部 ===

st.divider()
backend_name = next((k for k, v in BACKEND_OPTIONS.items() if v == st.session_state.selected_backend), "?")
model_name = {
    "ollama": LLM_MODEL,
    "vllm": VLLM_MODEL,
    "siliconflow": SILICONFLOW_LLM_MODEL,
    "lmstudio": LM_STUDIO_MODEL,
}.get(st.session_state.selected_backend, "?")
col_footer1, col_footer2 = st.columns([1, 3])
with col_footer1:
    st.caption("大模型翻译工具 v1.0")
with col_footer2:
    st.caption(f"引擎: {model_name} ({backend_name}) | Enter 发送 | Shift+Enter 换行")
