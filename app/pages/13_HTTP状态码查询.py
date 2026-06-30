import streamlit as st

st.set_page_config(
    page_title="HTTP 状态码查询",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

from app.logger import setup_logger

logger = setup_logger(__name__)

st.title("🌐 HTTP 状态码查询")

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

HTTP_STATUS = {
    # 1xx 信息
    100: ("Continue", "继续", "客户端应继续请求"),
    101: ("Switching Protocols", "切换协议", "服务器同意切换协议（如 WebSocket 升级）"),
    102: ("Processing", "处理中", "服务器已收到请求，正在处理"),
    103: ("Early Hints", "早期提示", "服务器提前返回部分响应头"),

    # 2xx 成功
    200: ("OK", "成功", "请求成功，GET 返回资源，POST/PUT 返回操作结果"),
    201: ("Created", "已创建", "请求成功且创建了新资源"),
    202: ("Accepted", "已接受", "请求已接受但尚未处理完成"),
    203: ("Non-Authoritative Information", "非权威信息", "响应来自第三方副本"),
    204: ("No Content", "无内容", "请求成功但无返回内容（常用于 DELETE）"),
    205: ("Reset Content", "重置内容", "请求成功，客户端应重置文档视图"),
    206: ("Partial Content", "部分内容", "服务器成功处理了部分 GET 请求（断点续传）"),
    207: ("Multi-Status", "多状态", "多个操作的结果（WebDAV）"),
    208: ("Already Reported", "已报告", "成员已列出，避免重复枚举（WebDAV）"),
    226: ("IM Used", "已使用增量编码", "服务器成功处理了范围请求"),

    # 3xx 重定向
    300: ("Multiple Choices", "多种选择", "请求有多种可能的响应"),
    301: ("Moved Permanently", "永久重定向", "资源已永久迁移到新 URL"),
    302: ("Found", "临时重定向", "资源临时在不同 URL 下"),
    303: ("See Other", "查看其他", "客户端应 GET 请求另一个 URL"),
    304: ("Not Modified", "未修改", "资源未变化，使用缓存"),
    305: ("Use Proxy", "使用代理", "必须通过代理访问"),
    306: ("Switch Proxy", "切换代理", "已废弃"),
    307: ("Temporary Redirect", "临时重定向", "资源临时在不同 URL，方法不变"),
    308: ("Permanent Redirect", "永久重定向", "资源永久迁移，方法不变"),

    # 4xx 客户端错误
    400: ("Bad Request", "错误请求", "请求语法错误，服务器无法理解"),
    401: ("Unauthorized", "未授权", "需要身份验证（未登录或 Token 无效）"),
    402: ("Payment Required", "需要付款", "保留给未来使用"),
    403: ("Forbidden", "禁止访问", "服务器理解请求但拒绝执行（无权限）"),
    404: ("Not Found", "未找到", "请求的资源不存在"),
    405: ("Method Not Allowed", "方法不允许", "请求方法对该资源不支持"),
    406: ("Not Acceptable", "不可接受", "无法生成客户端要求的内容格式"),
    407: ("Proxy Authentication Required", "需要代理认证", "需要先通过代理服务器认证"),
    408: ("Request Timeout", "请求超时", "服务器等待请求超时"),
    409: ("Conflict", "冲突", "请求与服务器当前状态冲突"),
    410: ("Gone", "已删除", "资源已被永久删除，不再可用"),
    411: ("Length Required", "需要长度", "需要 Content-Length 头"),
    412: ("Precondition Failed", "前置条件失败", "请求头中的条件不满足"),
    413: ("Content Too Large", "内容过大", "请求体超过服务器限制"),
    414: ("URI Too Long", "URI 过长", "请求 URL 超过服务器限制"),
    415: ("Unsupported Media Type", "不支持的媒体类型", "请求体格式服务器不支持"),
    416: ("Range Not Satisfiable", "范围不可满足", "请求的 Range 无法满足"),
    417: ("Expectation Failed", "期望失败", "Expect 头无法满足"),
    418: ("I'm a Teapot", "我是茶壶", "愚人节彩蛋（RFC 2324）"),
    421: ("Misdirected Request", "请求指向错误", "请求被定向到无法生成响应的服务器"),
    422: ("Unprocessable Content", "无法处理内容", "语法正确但语义错误（WebDAV）"),
    423: ("Locked", "已锁定", "资源被锁定（WebDAV）"),
    424: ("Failed Dependency", "依赖失败", "前一个请求失败导致此请求失败（WebDAV）"),
    425: ("Too Early", "过早", "服务器担心重放攻击"),
    426: ("Upgrade Required", "需要升级", "服务器要求客户端升级协议"),
    428: ("Precondition Required", "需要前置条件", "请求需要条件头"),
    429: ("Too Many Requests", "请求过多", "客户端请求频率超过限制"),
    431: ("Request Header Fields Too Large", "请求头过大", "请求头字段太长"),
    451: ("Unavailable For Legal Reasons", "因法律原因不可用", "资源因法律要求被屏蔽"),

    # 5xx 服务端错误
    500: ("Internal Server Error", "内部服务器错误", "服务器遇到意外错误"),
    501: ("Not Implemented", "未实现", "服务器不支持该请求方法"),
    502: ("Bad Gateway", "网关错误", "网关或代理从上游收到无效响应"),
    503: ("Service Unavailable", "服务不可用", "服务器暂时过载或维护中"),
    504: ("Gateway Timeout", "网关超时", "网关或代理等待上游响应超时"),
    505: ("HTTP Version Not Supported", "HTTP 版本不支持", "服务器不支持该 HTTP 版本"),
    506: ("Variant Also Negotiates", "变体也协商", "服务器配置错误"),
    507: ("Insufficient Storage", "存储不足", "服务器存储空间不足（WebDAV）"),
    508: ("Loop Detected", "检测到循环", "请求导致无限循环（WebDAV）"),
    510: ("Not Extended", "未扩展", "请求需要进一步扩展"),
    511: ("Network Authentication Required", "需要网络认证", "需要网络认证才能访问"),
}

COLOR_MAP = {
    1: ("#5b7fa5", "#f0f4f8"),
    2: ("#4a8a5a", "#f0f8f2"),
    3: ("#b89040", "#fdf6e8"),
    4: ("#b05a5a", "#fdf0f0"),
    5: ("#7a5a9a", "#f5f0f8"),
}

col_search, col_filter = st.columns([2, 1])

with col_search:
    query = st.text_input("🔍 输入状态码或关键词", placeholder="如：200、404、timeout、未找到", label_visibility="collapsed")

with col_filter:
    category = st.selectbox("分类筛选", ["全部", "1xx 信息", "2xx 成功", "3xx 重定向", "4xx 客户端错误", "5xx 服务端错误"])

cat_filter = None
if category.startswith("1xx"):
    cat_filter = 1
elif category.startswith("2xx"):
    cat_filter = 2
elif category.startswith("3xx"):
    cat_filter = 3
elif category.startswith("4xx"):
    cat_filter = 4
elif category.startswith("5xx"):
    cat_filter = 5

results = {}
for code, (en, cn, desc) in sorted(HTTP_STATUS.items()):
    if cat_filter and code // 100 != cat_filter:
        continue
    if query:
        q = query.lower()
        if (q in str(code) or q in en.lower() or q in cn or q in desc):
            results[code] = (en, cn, desc)
    else:
        results[code] = (en, cn, desc)

st.caption(f"共 {len(results)} 个状态码")

for code in sorted(results.keys()):
    en, cn, desc = results[code]
    group = code // 100
    accent, bg = COLOR_MAP.get(group, ("#888", "#333"))

    st.markdown(f"""
    <div style="background:{bg}; border-left:3px solid {accent}; border-radius:6px; padding:12px 16px; margin:8px 0;">
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:4px;">
            <span style="background:{accent}; color:#fff; font-weight:bold; padding:2px 10px; border-radius:4px; font-size:14px;">{code}</span>
            <span style="color:{accent}; font-weight:bold; font-size:14px;">{en}</span>
            <span style="color:#666; font-size:13px;">{cn}</span>
        </div>
        <div style="color:#555; font-size:13px; margin-left:4px;">{desc}</div>
    </div>
    """, unsafe_allow_html=True)

if not results:
    st.warning("未找到匹配的状态码")

st.divider()
st.caption("📋 HTTP 状态码参考 — 涵盖 HTTP/1.1 至 HTTP/2 标准定义的所有状态码")
