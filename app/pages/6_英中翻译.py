import os

# 必须在 import argostranslate 前设置，避免 stanza 联网下载资源
os.environ["ARGOS_CHUNK_TYPE"] = "MINISBD"

import streamlit as st
import streamlit.components.v1 as components
import time
from pathlib import Path

st.set_page_config(
    page_title="英中翻译",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("🌐 英中翻译")

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

# === 模型加载 ===

@st.cache_resource
def load_translation_model():
    model_dir = str(Path(__file__).parent.parent.parent / "models" / "argos-translate" / "packages")
    # 必须在 import 前设置，settings 模块加载时读取 package_data_dir
    os.environ["ARGOS_PACKAGES_DIR"] = model_dir

    try:
        import argostranslate.settings
        import argostranslate.package
        import argostranslate.translate

        argostranslate.settings.chunk_type = argostranslate.settings.ChunkType.MINISBD

        installed = argostranslate.package.get_installed_packages()
        en_zh = next(
            (p for p in installed if p.from_code == "en" and p.to_code == "zh"),
            None
        )

        if en_zh is None:
            pkg_path = Path(model_dir) / "en-zh.argosmodel"
            if pkg_path.exists():
                argostranslate.package.install_from_path(str(pkg_path))
                installed = argostranslate.package.get_installed_packages()
                en_zh = next(
                    (p for p in installed if p.from_code == "en" and p.to_code == "zh"),
                    None
                )

        if en_zh is None:
            return None

        return argostranslate.translate.get_translation_from_codes("en", "zh")

    except ImportError:
        return "missing_package"


translation_model = load_translation_model()

# === Session State ===

if "en_input" not in st.session_state:
    st.session_state.en_input = ""
if "zh_output" not in st.session_state:
    st.session_state.zh_output = ""
if "translate_time" not in st.session_state:
    st.session_state.translate_time = 0

# === 异常状态处理 ===

if translation_model is None:
    st.warning("""
    ### 翻译模型未安装

    请先运行以下命令下载 en-zh 翻译模型：

    ```bash
    .\\venv\\Scripts\\python.exe scripts\\download_argos_model.py
    ```

    下载完成后刷新页面即可使用。
    """)

    with st.expander("其他方案"):
        st.markdown("""
        - 确保已安装依赖: `pip install argostranslate`
        - 若镜像下载失败，可手动下载模型文件放入 `models/argos-translate/packages/` 目录
        - 下载地址: `https://github.com/argosopentech/argos-translate-packages/releases/download/en-zh/en-zh.argosmodel`
        """)
    st.stop()

elif translation_model == "missing_package":
    st.warning("""
    ### 缺少 argostranslate 依赖

    请安装依赖:

    ```bash
    pip install argostranslate
    ```
    """)
    st.stop()

# === 翻译函数 ===

def do_translate():
    text = st.session_state.en_input.strip()
    if not text:
        st.session_state.zh_output = ""
        st.session_state.translate_time = 0
        return

    try:
        start = time.time()
        result = translation_model.translate(text)
        elapsed = time.time() - start
        st.session_state.zh_output = result
        st.session_state.translate_time = elapsed
    except Exception as e:
        st.error(f"翻译失败: {e}")


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
    st.markdown("<br><br>", unsafe_allow_html=True)

    if st.button("英->中", use_container_width=True, type="primary"):
        do_translate()

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("清空", use_container_width=True):
        clear_all()
        st.rerun()

with col_output:
    st.subheader("中文译文")

    st.text_area(
        "中文译文",
        value=st.session_state.zh_output,
        height=370,
        placeholder="翻译结果将显示在这里...",
        label_visibility="collapsed",
        disabled=True,
    )

    output_len = len(st.session_state.zh_output)
    stats_col1, stats_col2 = st.columns(2)
    with stats_col1:
        st.caption(f"字符数: {output_len}")
    with stats_col2:
        if st.session_state.translate_time > 0:
            st.caption(f"耗时: {st.session_state.translate_time*1000:.0f} ms")

# === Enter 快捷键：回车自动翻译 ===

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
col_footer1, col_footer2 = st.columns([1, 3])
with col_footer1:
    st.caption("英中翻译工具 v1.0")
with col_footer2:
    st.caption("引擎: Argos Translate (离线) | Enter 发送 | Shift+Enter 换行")
