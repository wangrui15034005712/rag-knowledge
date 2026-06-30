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
    page_title="正则表达式代码模板生成器",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("📝 正则表达式代码模板生成器")

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
    .code-block {
        background: #1e1e1e;
        border-radius: 8px;
        padding: 1rem;
        font-family: 'Courier New', monospace;
        color: #d4d4d4;
        overflow-x: auto;
        white-space: pre-wrap;
        word-break: break-all;
    }
    .template-card {
        background: #f8f9fa;
        border: 1px solid #e1e4e8;
        border-radius: 8px;
        padding: 0.8rem;
        margin-bottom: 0.5rem;
        cursor: pointer;
        transition: all 0.2s;
    }
    .template-card:hover {
        background: #e8f4f8;
        border-color: #0066cc;
    }
    .template-title {
        font-weight: 600;
        margin-bottom: 0.3rem;
    }
    .template-desc {
        font-size: 0.85rem;
        color: #666;
    }
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

# === 常用模板 ===

COMMON_TEMPLATES = [
    {"name": "手机号码", "desc": "中国大陆11位手机号", "prompt": "匹配中国大陆手机号码，11位数字，1开头，第二位3-9"},
    {"name": "邮箱地址", "desc": "电子邮箱格式", "prompt": "匹配电子邮箱地址，支持常见格式"},
    {"name": "身份证号", "desc": "18位身份证", "prompt": "匹配中国大陆18位身份证号码"},
    {"name": "IP地址", "desc": "IPv4地址", "prompt": "匹配IPv4地址格式"},
    {"name": "URL链接", "desc": "HTTP/HTTPS链接", "prompt": "匹配HTTP和HTTPS的URL链接"},
    {"name": "日期格式", "desc": "YYYY-MM-DD", "prompt": "匹配日期格式YYYY-MM-DD"},
    {"name": "时间格式", "desc": "HH:MM:SS", "prompt": "匹配时间格式HH:MM:SS"},
    {"name": "邮政编码", "desc": "6位邮编", "prompt": "匹配中国6位邮政编码"},
    {"name": "车牌号", "desc": "中国车牌", "prompt": "匹配中国大陆车牌号"},
    {"name": "十六进制颜色", "desc": "#RRGGBB", "prompt": "匹配十六进制颜色值#RRGGBB格式"},
    {"name": "密码强度", "desc": "大小写+数字+特殊字符", "prompt": "匹配强密码，包含大小写字母、数字和特殊字符，至少8位"},
    {"name": "文件扩展名", "desc": ".txt/.pdf等", "prompt": "匹配常见文件扩展名如.txt、.pdf、.doc等"},
    {"name": "HTML标签", "desc": "匹配HTML元素", "prompt": "匹配HTML/XML标签"},
    {"name": "Markdown链接", "desc": "[text](url)格式", "prompt": "匹配Markdown格式的链接[text](url)"},
    {"name": "版本号", "desc": "x.y.z格式", "prompt": "匹配语义化版本号x.y.z格式"},
    {"name": "驼峰命名", "desc": "camelCase", "prompt": "匹配驼峰命名法camelCase格式的变量名"},
    {"name": "蛇形命名", "desc": "snake_case", "prompt": "匹配蛇形命名法snake_case格式的变量名"},
    {"name": "中文字符", "desc": "匹配汉字", "prompt": "匹配中文汉字字符"},
    {"name": "浮点数", "desc": "小数和负数", "prompt": "匹配浮点数，包括正数、负数和小数"},
    {"name": "JSON字符串", "desc": "匹配JSON内容", "prompt": "匹配JSON格式的字符串内容"},
]

# === Prompt 模板 ===

REGEX_PROMPT = """你是一个Python正则表达式专家。请根据以下需求生成Python正则表达式代码。

需求：{description}

要求：
1. 生成完整的Python代码，包含re模块导入
2. 包含正则表达式变量定义
3. 包含测试用例和匹配结果展示
4. 添加详细的中文注释说明每个部分的作用
5. 使用原始字符串（r"..."）定义正则表达式
6. 代码简洁实用，可直接运行

请直接输出Python代码，不要包含其他说明文字。"""

# === Session State ===

if "regex_input" not in st.session_state:
    st.session_state.regex_input = ""
if "regex_output" not in st.session_state:
    st.session_state.regex_output = ""
if "regex_time" not in st.session_state:
    st.session_state.regex_time = 0
if "selected_backend" not in st.session_state:
    st.session_state.selected_backend = DEFAULT_BACKEND

# === 函数 ===

def clear_all():
    st.session_state.regex_input = ""
    st.session_state.regex_output = ""
    st.session_state.regex_time = 0

def use_template(prompt):
    st.session_state.regex_input = prompt
    st.rerun()

# === UI 布局 ===

# 左侧：输入和输出
col_main, col_templates = st.columns([3, 1], gap="medium")

with col_main:
    # 后端选择
    col_backend, col_btn1, col_btn2 = st.columns([2, 1, 1])
    with col_backend:
        backend_label = st.selectbox(
            "AI引擎",
            options=list(BACKEND_OPTIONS.keys()),
            index=list(BACKEND_OPTIONS.values()).index(st.session_state.selected_backend),
            label_visibility="collapsed",
        )
        st.session_state.selected_backend = BACKEND_OPTIONS[backend_label]
    
    with col_btn1:
        if st.button("生成代码", use_container_width=True, type="primary"):
            st.session_state.generate_trigger = True
    
    with col_btn2:
        if st.button("清空", use_container_width=True):
            clear_all()
            st.rerun()
    
    # 输入框
    regex_input = st.text_area(
        "描述你要匹配的内容",
        value=st.session_state.regex_input,
        height=120,
        placeholder="例如：匹配中国大陆手机号码（11位，1开头）",
        label_visibility="collapsed",
    )
    if regex_input != st.session_state.regex_input:
        st.session_state.regex_input = regex_input
    
    input_len = len(st.session_state.regex_input.strip())
    st.caption(f"字符数: {input_len}")
    
    st.divider()
    
    # 输出区域
    st.subheader("生成的Python代码")
    output_placeholder = st.empty()
    
    if st.session_state.get("generate_trigger", False):
        text = st.session_state.regex_input.strip()
        if text:
            try:
                llm = get_llm(st.session_state.selected_backend)
                from langchain_core.messages import HumanMessage
                
                prompt = REGEX_PROMPT.format(description=text)
                
                start = time.time()
                full = ""
                stream = llm.stream([HumanMessage(content=prompt)])
                for chunk in stream:
                    content = chunk.content if hasattr(chunk, "content") else str(chunk)
                    full += content
                    output_placeholder.markdown(f"```python\n{full}\n```")
                output_placeholder.markdown(f"```python\n{full}\n```")
                
                elapsed = time.time() - start
                st.session_state.regex_output = full
                st.session_state.regex_time = elapsed
            except Exception as e:
                st.error(f"生成失败: {e}")
                output_placeholder.markdown(f"```python\n{st.session_state.regex_output}\n```")
        st.session_state.generate_trigger = False
    
    elif st.session_state.regex_output:
        output_placeholder.markdown(f"```python\n{st.session_state.regex_output}\n```")
    
    # 统计信息
    if st.session_state.regex_output:
        stats_col1, stats_col2 = st.columns(2)
        with stats_col1:
            st.caption(f"代码行数: {len(st.session_state.regex_output.splitlines())}")
        with stats_col2:
            if st.session_state.regex_time > 0:
                st.caption(f"生成耗时: {st.session_state.regex_time*1000:.0f} ms")

with col_templates:
    st.subheader("常用模板")
    st.caption("点击快速填入")
    
    for template in COMMON_TEMPLATES:
        if st.button(
            f"**{template['name']}**\n\n{template['desc']}",
            use_container_width=True,
            key=f"tpl_{template['name']}",
        ):
            use_template(template["prompt"])

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
    st.caption("正则表达式代码模板生成器 v1.0")
with col_footer2:
    st.caption(f"引擎: {model_name} ({backend_name}) | 20+常用模板 | 一键生成Python代码")
