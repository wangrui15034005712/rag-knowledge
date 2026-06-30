import streamlit as st
import difflib
import io

st.set_page_config(
    page_title="文档对比",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

from app.logger import setup_logger

logger = setup_logger(__name__)

st.title("🔄 文档对比")

st.markdown("""
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
</style>
""", unsafe_allow_html=True)


def read_file_content(uploaded_file):
    name = uploaded_file.name.lower()
    try:
        if name.endswith('.docx'):
            import docx2txt
            return docx2txt.process(uploaded_file)
        elif name.endswith('.pdf'):
            from pypdf import PdfReader
            reader = PdfReader(uploaded_file)
            text = []
            for page in reader.pages:
                text.append(page.extract_text() or '')
            return '\n'.join(text)
        else:
            return uploaded_file.read().decode('utf-8', errors='replace')
    except Exception as e:
        st.error(f"读取文件失败: {e}")
        return None


def render_side_by_side_diff(text_a, text_b):
    lines_a = text_a.splitlines()
    lines_b = text_b.splitlines()

    sm = difflib.SequenceMatcher(None, lines_a, lines_b)

    left_html = []
    right_html = []
    stats = {'add': 0, 'del': 0, 'same': 0}

    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            stats['same'] += i2 - i1
            for idx in range(i2 - i1):
                la = lines_a[i1 + idx]
                lb = lines_b[j1 + idx]
                la_esc = la.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;') or '&nbsp;'
                lb_esc = lb.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;') or '&nbsp;'
                left_html.append(
                    f'<tr class="diff-row">'
                    f'<td class="ln">{i1 + idx + 1}</td>'
                    f'<td class="ctx">{la_esc}</td></tr>'
                )
                right_html.append(
                    f'<tr class="diff-row">'
                    f'<td class="ln">{j1 + idx + 1}</td>'
                    f'<td class="ctx">{lb_esc}</td></tr>'
                )

        elif tag == 'replace':
            stats['del'] += i2 - i1
            stats['add'] += j2 - j1
            block_left = lines_a[i1:i2]
            block_right = lines_b[j1:j2]
            max_len = max(len(block_left), len(block_right))

            for k in range(max_len):
                if k < len(block_left):
                    c = block_left[k].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;') or '&nbsp;'
                    left_html.append(
                        f'<tr class="diff-row">'
                        f'<td class="ln">{i1 + k + 1}</td>'
                        f'<td class="del">{c}</td></tr>'
                    )
                else:
                    left_html.append(
                        '<tr class="diff-row">'
                        '<td class="ln"></td>'
                        '<td class="empty">&nbsp;</td></tr>'
                    )

                if k < len(block_right):
                    c = block_right[k].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;') or '&nbsp;'
                    right_html.append(
                        f'<tr class="diff-row">'
                        f'<td class="ln">{j1 + k + 1}</td>'
                        f'<td class="add">{c}</td></tr>'
                    )
                else:
                    right_html.append(
                        '<tr class="diff-row">'
                        '<td class="ln"></td>'
                        '<td class="empty">&nbsp;</td></tr>'
                    )

        elif tag == 'delete':
            stats['del'] += i2 - i1
            for i in range(i1, i2):
                c = lines_a[i].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;') or '&nbsp;'
                left_html.append(
                    f'<tr class="diff-row">'
                    f'<td class="ln">{i + 1}</td>'
                    f'<td class="del">{c}</td></tr>'
                )
                right_html.append(
                    '<tr class="diff-row">'
                    '<td class="ln"></td>'
                    '<td class="empty">&nbsp;</td></tr>'
                )

        elif tag == 'insert':
            stats['add'] += j2 - j1
            for j in range(j1, j2):
                c = lines_b[j].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;') or '&nbsp;'
                left_html.append(
                    '<tr class="diff-row">'
                    '<td class="ln"></td>'
                    '<td class="empty">&nbsp;</td></tr>'
                )
                right_html.append(
                    f'<tr class="diff-row">'
                    f'<td class="ln">{j + 1}</td>'
                    f'<td class="add">{c}</td></tr>'
                )

    css = """
    <style>
    .diff-wrap {
        font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
        font-size: 13px;
        line-height: 1.5;
        border: 1px solid #30363d;
        border-radius: 6px;
        overflow: hidden;
        background: #0d1117;
        color: #c9d1d9;
    }
    .diff-wrap table {
        width: 100%;
        border-collapse: collapse;
    }
    .diff-pane {
        width: 50%;
        vertical-align: top;
    }
    .diff-pane-header {
        background: #161b22;
        padding: 6px 12px;
        border-bottom: 1px solid #30363d;
        color: #8b949e;
        font-size: 11px;
        text-align: center;
    }
    .diff-row td {
        padding: 0 10px;
        white-space: pre-wrap;
        word-break: break-all;
        vertical-align: top;
    }
    .ln {
        width: 45px;
        min-width: 45px;
        text-align: right;
        color: #484f58;
        user-select: none;
        border-right: 1px solid #30363d;
    }
    .ctx {
        background: transparent;
    }
    .add {
        background: rgba(46, 160, 67, 0.25);
        color: #3fb950;
    }
    .del {
        background: rgba(248, 81, 73, 0.25);
        color: #f85149;
    }
    .empty {
        background: #161b22;
    }
    .diff-stats {
        display: flex;
        gap: 20px;
        padding: 10px 16px;
        background: #161b22;
        border-top: 1px solid #30363d;
        font-size: 12px;
        font-family: sans-serif;
    }
    .s-add { color: #3fb950; }
    .s-del { color: #f85149; }
    .s-same { color: #8b949e; }
    </style>
    """

    html = f"""{css}
    <div class="diff-wrap">
    <table><tr>
    <td class="diff-pane">
        <div class="diff-pane-header">原始内容 (Left)</div>
        <table>{"".join(left_html)}</table>
    </td>
    <td class="diff-pane">
        <div class="diff-pane-header">修改后内容 (Right)</div>
        <table>{"".join(right_html)}</table>
    </td>
    </tr></table>
    <div class="diff-stats">
        <span class="s-same">相同: {stats["same"]} 行</span>
        <span class="s-add">新增: {stats["add"]} 行</span>
        <span class="s-del">删除: {stats["del"]} 行</span>
    </div>
    </div>
    """

    return html, stats


mode = st.radio(
    "对比模式",
    ["📄 文档对比", "📝 内容对比"],
    horizontal=True
)

col_a, col_b = st.columns(2)

text_a = ""
text_b = ""

if mode == "📄 文档对比":
    with col_a:
        file_a = st.file_uploader(
            "上传文件 A（原始）",
            type=None,
            key="file_a",
            help="支持所有文本格式，以及 .docx 和 .pdf"
        )
        if file_a:
            text_a = read_file_content(file_a)
            if text_a is not None:
                with st.expander("预览内容", expanded=False):
                    st.text(text_a[:2000] + ("..." if len(text_a) > 2000 else ""))
    with col_b:
        file_b = st.file_uploader(
            "上传文件 B（修改后）",
            type=None,
            key="file_b",
            help="支持所有文本格式，以及 .docx 和 .pdf"
        )
        if file_b:
            text_b = read_file_content(file_b)
            if text_b is not None:
                with st.expander("预览内容", expanded=False):
                    st.text(text_b[:2000] + ("..." if len(text_b) > 2000 else ""))
else:
    with col_a:
        text_a = st.text_area(
            "内容 A（原始）",
            height=400,
            placeholder="粘贴原始内容...",
            key="text_a"
        )
    with col_b:
        text_b = st.text_area(
            "内容 B（修改后）",
            height=400,
            placeholder="粘贴修改后内容...",
            key="text_b"
        )

if text_a and text_b:
    if st.button("🔍 开始对比", type="primary", use_container_width=True):
        with st.spinner("正在计算差异..."):
            diff_html, stats = render_side_by_side_diff(text_a, text_b)

        st.components.v1.html(diff_html, height=600, scrolling=True)

        result_text = ''.join(difflib.unified_diff(
            text_a.splitlines(keepends=True),
            text_b.splitlines(keepends=True),
            fromfile='原始内容',
            tofile='修改后内容',
            lineterm=''
        ))

        st.download_button(
            label="📥 下载 Diff 结果",
            data=result_text,
            file_name="diff_result.patch",
            mime="text/plain",
            use_container_width=True
        )
elif not text_a and not text_b:
    st.info("👈 上传两个文件或粘贴两段内容开始对比")
