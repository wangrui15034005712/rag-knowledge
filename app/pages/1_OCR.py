import streamlit as st

st.set_page_config(page_title="OCR 图片文字识别", page_icon="📄")

from app.ocr_engine import ocr_image
from app.logger import setup_logger

logger = setup_logger(__name__)

st.title("📄 OCR 图片文字识别")

# ── 侧边栏 ──
with st.sidebar:
    backend = st.radio(
        "OCR 后端",
        ["siliconflow", "vllm"],
        index=0,
        horizontal=True,
        key="ocr_backend",
    )

# ── 文件上传 ──
uploaded_file = st.file_uploader(
    "选择一张图片",
    type=["jpg", "jpeg", "png", "bmp", "webp"],
    accept_multiple_files=False,
)

# 新文件上传时清除旧结果
if uploaded_file is not None:
    file_key = f"{uploaded_file.name}_{uploaded_file.size}"
    if "ocr_file_key" not in st.session_state or st.session_state.ocr_file_key != file_key:
        st.session_state.ocr_result = None
        st.session_state.ocr_file_key = file_key

# ── OCR 识别按钮 + 结果 ──
if uploaded_file is not None:
    col_img, col_btn = st.columns([2, 1])
    with col_img:
        st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)
    with col_btn:
        st.write("")
        if st.button("🔄 OCR 识别", use_container_width=True, type="primary"):
            with st.spinner("正在识别图片文字..."):
                try:
                    md_text = ocr_image(
                        uploaded_file.getvalue(),
                        st.session_state.ocr_backend,
                        uploaded_file.type or "image/png",
                    )
                    st.session_state.ocr_result = md_text
                    logger.info(f"OCR 识别成功: {uploaded_file.name}")
                except Exception as e:
                    logger.error(f"OCR 识别失败: {e}")
                    st.error(f"识别失败：{e}")

    # 显示结果
    if st.session_state.get("ocr_result"):
        st.divider()
        st.markdown("### 📝 预览")
        with st.container(border=True):
            st.markdown(st.session_state.ocr_result)
        st.markdown("### Markdown 源码")
        st.code(st.session_state.ocr_result, language="markdown")
