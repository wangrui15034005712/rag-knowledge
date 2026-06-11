import streamlit as st

st.set_page_config(page_title="Markdown 实时预览", layout="wide")
st.title("📝 Markdown 实时预览编辑器")

col1, col2 = st.columns(2)

with col1:
    md_text = st.text_area(
        "编辑 Markdown",
        value="# Hello World\n\n这是一段 **粗体** 和 *斜体* 文字。\n\n- 列表项1\n- 列表项2\n\n```python\nprint('代码块')\n```",
        height=500,
        placeholder="在此输入 Markdown..."
    )

with col2:
    st.markdown("**预览效果**")
    st.markdown(md_text)  # 直接渲染