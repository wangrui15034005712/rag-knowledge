import streamlit as st
import json
import base64

# 修改为宽屏模式，占满整个屏幕
st.set_page_config(
    page_title="JSON 格式化",
    page_icon="🛠",
    layout="wide",  # 关键：设置为宽屏模式
    initial_sidebar_state="collapsed"
)

from app.logger import setup_logger

logger = setup_logger(__name__)

st.title("🛠 JSON 格式化")

# 使用自定义CSS让容器占满屏幕
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 100%;
    }

    /* 让textarea占满高度 */
    .stTextArea textarea {
        min-height: 370px !important;
    }

    /* 让code block占满高度 */
    .stCodeBlock {
        min-height: 370px !important;
    }

    /* 隐藏顶部空白 */
    header {
        visibility: hidden;
    }

    /* 隐藏菜单按钮 */
    #MainMenu {
        visibility: hidden;
    }

    /* 隐藏footer */
    footer {
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True)

# 初始化 session state
if 'json_input' not in st.session_state:
    st.session_state.json_input = ''
if 'formatted_json' not in st.session_state:
    st.session_state.formatted_json = ''


def clear_input():
    st.session_state.json_input = ''


def load_example():
    example_json = {
        "name": "JSON Formatter",
        "version": "1.0.0",
        "features": ["format", "validate", "minify"],
        "author": {
            "name": "Developer",
            "email": "dev@example.com"
        },
        "metadata": {
            "created": "2024-01-01",
            "tags": ["tool", "utility"]
        }
    }
    st.session_state.json_input = json.dumps(example_json, indent=2, ensure_ascii=False)


def download_json(json_str):
    b64 = base64.b64encode(json_str.encode()).decode()
    href = f'<a href="data:application/json;base64,{b64}" download="formatted.json">下载 JSON 文件</a>'
    return href


# 创建两列，比例可以调整
col_input, col_output = st.columns([1, 1], gap="large")

with col_input:
    # 按钮区域
    btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 1])

    with btn_col1:
        if st.button("📋 示例", use_container_width=True):
            load_example()
            st.rerun()

    with btn_col2:
        if st.button("🗑️ 清除", use_container_width=True):
            clear_input()
            st.rerun()

    with btn_col3:
        if st.button("📏 压缩", use_container_width=True):
            if st.session_state.json_input.strip():
                try:
                    parsed = json.loads(st.session_state.json_input)
                    st.session_state.json_input = json.dumps(parsed, separators=(',', ':'))
                    st.rerun()
                except:
                    pass

    json_input = st.text_area(
        "输入 JSON",
        value=st.session_state.json_input,
        height=370,  # 增加高度
        placeholder='{\n  "key": "value"\n}',
        key="input_area",
        label_visibility="visible"
    )

    # 实时同步输入
    st.session_state.json_input = json_input

with col_output:
    if json_input.strip():
        try:
            parsed = json.loads(json_input)
            formatted = json.dumps(parsed, indent=2, ensure_ascii=False)
            st.session_state.formatted_json = formatted

            # 显示格式化后的 JSON
            st.code(formatted, language="json", height=370)  # 增加高度

            # 操作按钮
            dl_col1, dl_col2 = st.columns([1, 1])

            with dl_col1:
                st.markdown(download_json(formatted), unsafe_allow_html=True)

            with dl_col2:
                if st.button("📋 复制", use_container_width=True):
                    st.toast("已复制到剪贴板！", icon="✅")
                    st.session_state['copied'] = True

            # 统计信息
            stats_col1, stats_col2, stats_col3 = st.columns(3)
            with stats_col1:
                st.metric("大小", f"{len(formatted)} 字符")
            with stats_col2:
                st.metric("键数量", len(parsed) if isinstance(parsed, dict) else "N/A")
            with stats_col3:
                st.metric("类型", type(parsed).__name__)

        except json.JSONDecodeError as e:
            error_msg = str(e)
            error_pos = e.pos

            # 尝试定位错误位置
            lines = json_input.split('\n')
            current_pos = 0
            error_line = 1
            error_col = 1

            for i, line in enumerate(lines):
                if current_pos + len(line) >= error_pos:
                    error_line = i + 1
                    error_col = error_pos - current_pos + 1
                    break
                current_pos += len(line) + 1

            st.error(f"""
            **JSON 解析错误**
            - 错误信息: {error_msg}
            - 位置: 第 {error_line} 行, 第 {error_col} 列
            - 建议: 检查引号、逗号或括号是否匹配
            """)

            # 显示原始输入（带行号）
            st.subheader("原始输入 (带行号)")
            numbered_lines = [f"{i + 1:3d}: {line}" for i, line in enumerate(lines)]
            st.text('\n'.join(numbered_lines))
    else:
        st.info("👈 在左侧输入 JSON 数据，将自动格式化显示在这里")

        # 快捷键提示
        with st.expander("💡 使用技巧"):
            st.markdown("""
            - **Ctrl/Cmd + Enter**: 格式化 JSON
            - **示例按钮**: 加载示例 JSON
            - **清除按钮**: 清空输入
            - **压缩按钮**: 移除所有空格和换行
            - **下载按钮**: 保存格式化后的 JSON
            """)

# 底部状态栏
st.divider()
status_col1, status_col2, status_col3 = st.columns([1, 1, 2])

with status_col1:
    st.caption("🛠 JSON 格式化工具 v2.0")

with status_col2:
    if st.session_state.get('copied'):
        st.caption("✅ 已复制")

with status_col3:
    st.caption("💡 提示: 支持粘贴多层嵌套 JSON")