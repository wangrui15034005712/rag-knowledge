import streamlit as st
import streamlit.components.v1 as components
import markdown
import re
from pathlib import Path

st.set_page_config(
    page_title="学习资源",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

MD_STYLES = """
.markdown-body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif;
    font-size: 16px;
    line-height: 1.6;
    color: #1f2328;
    word-wrap: break-word;
}
.markdown-body h1 { font-size: 2em; border-bottom: 1px solid #d0d7de; padding-bottom: 0.3em; margin: 0.67em 0; }
.markdown-body h2 { font-size: 1.5em; border-bottom: 1px solid #d0d7de; padding-bottom: 0.3em; margin: 0.83em 0; }
.markdown-body h3 { font-size: 1.25em; margin: 1em 0; }
.markdown-body h4 { font-size: 1em; margin: 1.33em 0; }
.markdown-body p { margin: 0 0 16px; }
.markdown-body code {
    background: #afb8c133;
    border-radius: 6px;
    padding: 0.2em 0.4em;
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
    font-size: 85%;
}
.markdown-body pre {
    background: #0d1117;
    border-radius: 6px;
    padding: 16px;
    overflow: auto;
    line-height: 1.45;
}
.markdown-body pre code {
    background: none;
    padding: 0;
    font-size: 85%;
    color: #e6edf3;
}
.markdown-body .highlight pre {
    background: #0d1117;
    border-radius: 6px;
    padding: 16px;
    overflow: auto;
}
.markdown-body table {
    border-collapse: collapse;
    width: 100%;
    margin: 16px 0;
}
.markdown-body th, .markdown-body td {
    border: 1px solid #d0d7de;
    padding: 8px 12px;
    text-align: left;
}
.markdown-body th {
    background: #f6f8fa;
    font-weight: 600;
}
.markdown-body tr:nth-child(even) { background: #f6f8fa; }
.markdown-body blockquote {
    margin: 0 0 16px;
    padding: 0 1em;
    color: #656d76;
    border-left: 0.25em solid #d0d7de;
}
.markdown-body ul, .markdown-body ol { padding-left: 2em; margin: 0 0 16px; }
.markdown-body li { margin: 0.25em 0; }
.markdown-body a { color: #0969da; text-decoration: none; }
.markdown-body a:hover { text-decoration: underline; }
.markdown-body hr {
    border: none;
    border-top: 1px solid #d0d7de;
    margin: 24px 0;
}
.markdown-body img { max-width: 100%; }
.markdown-body input[type="checkbox"] { margin-right: 0.5em; }
"""

GITHUB_CSS = """
<style>
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    padding-left: 2rem;
    padding-right: 2rem;
    max-width: 100%;
}
header { visibility: hidden; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

.file-tree-container div[data-testid="stButton"] button {
    background: transparent !important;
    border: none !important;
    text-align: left !important;
    padding: 2px 8px !important;
    font-weight: normal !important;
    font-size: 0.9rem !important;
    width: 100%;
    justify-content: flex-start !important;
}
.file-tree-container div[data-testid="stButton"] button:hover {
    background: #f0f2f6 !important;
}
.file-tree-container div[data-testid="stButton"] button p {
    font-size: 0.9rem !important;
}
</style>
"""

st.markdown(GITHUB_CSS, unsafe_allow_html=True)

BASE_DIR = Path(__file__).parent.parent / "学习资源"

if "selected_file" not in st.session_state:
    st.session_state.selected_file = None


def render_md(content: str) -> str:
    return markdown.markdown(
        content,
        extensions=[
            "fenced_code",
            "codehilite",
            "tables",
            "sane_lists",
        ],
        extension_configs={
            "codehilite": {"css_class": "highlight", "use_pygments": True},
        },
    )


def get_file_tree(base_dir: Path) -> list[dict]:
    if not base_dir.exists():
        return []
    items = []
    seen_dirs = set()
    for f in sorted(base_dir.rglob("*.md")):
        rel = f.relative_to(base_dir)
        parts = list(rel.parts)
        for i in range(len(parts) - 1):
            dir_rel = str(Path(*parts[:i + 1]))
            if dir_rel not in seen_dirs:
                items.append({"path": dir_rel, "name": parts[i], "indent": i, "is_dir": True})
                seen_dirs.add(dir_rel)
        items.append({"path": str(rel), "name": parts[-1].replace(".md", ""), "indent": len(parts) - 1, "is_dir": False})
    return items


# === UI ===

st.title("📚 学习资源")

if not BASE_DIR.exists():
    st.warning("请先创建目录 `app/学习资源/` 并放入 .md 文件")
    st.stop()

all_files = sorted(BASE_DIR.rglob("*.md"))
if not all_files:
    st.info("暂无学习资源，请先在 `app/学习资源/` 目录下添加 .md 文件")
    st.stop()

if st.session_state.selected_file is None:
    first_rel = str(all_files[0].relative_to(BASE_DIR.parent))
    st.session_state.selected_file = first_rel

col_tree, col_content = st.columns([1, 2.5], gap="large")

with col_tree:
    st.markdown("##### 📂 文件")
    search = st.text_input("搜索", placeholder="过滤文件名...", label_visibility="collapsed")

    tree_items = get_file_tree(BASE_DIR)

    st.markdown('<div class="file-tree-container">', unsafe_allow_html=True)

    for item in tree_items:
        if item["is_dir"]:
            st.markdown(
                f'<div style="padding-left:{12 + item["indent"] * 20}px;font-weight:600;color:#666;font-size:0.85rem;padding:3px 0;">📁 {item["name"]}</div>',
                unsafe_allow_html=True,
            )
        else:
            name = item["name"]
            rel_path = f"学习资源/{item['path']}"
            is_selected = st.session_state.selected_file == rel_path
            matches = not search or search.lower() in name.lower()

            if not matches:
                continue

            label = f"📄 {name}"
            if is_selected:
                label = f"📄 **{name}**"

            if st.button(label, key=f"file_{item['path']}", use_container_width=True):
                st.session_state.selected_file = rel_path
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

with col_content:
    if not st.session_state.selected_file:
        st.info("请在左侧选择一个文件")
        st.stop()

    file_path = BASE_DIR.parent / st.session_state.selected_file
    if not file_path.exists():
        st.error(f"文件不存在: {file_path}")
        st.stop()

    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        st.error(f"读取文件失败: {e}")
        st.stop()

    md_html = render_md(content)
    components.html(
        f"<style>{MD_STYLES}</style><div class='markdown-body'>{md_html}</div>",
        height=700,
        scrolling=True,
    )

st.divider()
st.caption("📚 学习资源 v1.0 | GitHub 风格渲染 + 搜索过滤")
