import streamlit as st

st.set_page_config(
    page_title="正则表达式查看器",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("🔍 正则表达式查看器")

st.markdown("""<style>
    .main .block-container { padding-top:2rem;padding-bottom:2rem;padding-left:2rem;padding-right:2rem;max-width:100%; }
    header { visibility:hidden; }
    #MainMenu { visibility:hidden; }
    footer { visibility:hidden; }
    .pattern-box { font-family:"Courier New",monospace; font-size:1.3rem; text-align:center; padding:1rem; background:#1e1e1e; color:#d4d4d4; border-radius:8px; line-height:2; margin-bottom:1rem; }
</style>""", unsafe_allow_html=True)

CATEGORIES = ["网络相关","文本相关","日期时间","编码命名","代码相关","颜色值","中国专用","其他"]

PRESETS = [
    {"category":"网络相关","name":"匹配邮箱","pattern":r"[\w.-]+@[\w.-]+\.\w+","desc":"匹配电子邮箱地址","tokens":[(r"[\w.-]+","字符类+量词","匹配单词字符、点号、连字符，1次或多次"),("@","字面字符","匹配 @ 符号"),(r"[\w.-]+","字符类+量词","匹配单词字符、点号、连字符，1次或多次"),(r"\.","转义字符","匹配点号 ."),(r"\w+","预定义+量词","匹配单词字符，1次或多次")]},
    {"category":"网络相关","name":"匹配手机号","pattern":r"1[3-9]\d{9}","desc":"匹配中国大陆手机号（11位，1开头，第二位3-9）","tokens":[("1","字面字符","匹配数字1"),("[3-9]","字符类","匹配3到9的任意数字"),(r"\d{9}","预定义+量词","匹配9位数字")]},
    {"category":"网络相关","name":"匹配 URL","pattern":r"https?://[\w./?=&%-]+","desc":"匹配 HTTP/HTTPS URL","tokens":[("http","字面字符","匹配字符串 http"),("s?","量词","匹配 s 0次或1次（http或https）"),(":","字面字符","匹配冒号 :"),("//","字面字符","匹配双斜杠 //"),(r"[\w./?=&%-]+","字符类+量词","匹配URL路径字符，1次或多次")]},
    {"category":"网络相关","name":"匹配 IPv4","pattern":r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}","desc":"匹配 IPv4 地址（不验证范围）","tokens":[(r"\d{1,3}","预定义+量词","匹配1-3位数字"),(r"\.","转义字符","匹配点号 ."),(r"\d{1,3}","预定义+量词","匹配1-3位数字"),(r"\.","转义字符","匹配点号 ."),(r"\d{1,3}","预定义+量词","匹配1-3位数字"),(r"\.","转义字符","匹配点号 ."),(r"\d{1,3}","预定义+量词","匹配1-3位数字")]},
    {"category":"网络相关","name":"匹配域名","pattern":r"[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)+","desc":"匹配域名（如 example.com）","tokens":[("[a-zA-Z0-9-]+","字符类+量词","匹配字母、数字、连字符，1次或多次"),(r"(\.[a-zA-Z0-9-]+)+","分组+量词","点号+字母数字连字符，整体1次或多次")]},
    {"category":"网络相关","name":"匹配 MAC 地址","pattern":r"([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}","desc":"匹配 MAC 地址","tokens":[("([0-9A-Fa-f]{2}[:-]){5}","分组+量词","2位十六进制+分隔符，重复5次"),("[0-9A-Fa-f]{2}","字符类+量词","2位十六进制数（最后一段）")]},
    {"category":"文本相关","name":"匹配中文","pattern":r"[\u4e00-\u9fff]+","desc":"匹配连续中文字符","tokens":[(r"[\u4e00-\u9fff]+","字符类+量词","匹配 CJK 统一表意文字，1次或多次")]},
    {"category":"文本相关","name":"匹配数字","pattern":r"\d+","desc":"匹配连续数字","tokens":[(r"\d+","预定义+量词","\d 匹配数字[0-9]，+ 表示1次或多次")]},
    {"category":"文本相关","name":"匹配英文字母","pattern":r"[a-zA-Z]+","desc":"匹配连续英文字母","tokens":[("[a-zA-Z]+","字符类+量词","匹配 a-z 或 A-Z，1次或多次")]},
    {"category":"文本相关","name":"匹配空白字符","pattern":r"\s+","desc":"匹配空白字符（空格、制表符、换行等）","tokens":[(r"\s+","预定义+量词","\s 匹配空白字符，+ 表示1次或多次")]},
    {"category":"文本相关","name":"匹配 Emoji","pattern":r"[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF]","desc":"匹配常见 Emoji 表情","tokens":[(r"[\U0001F600-\U0001F64F]","字符类","匹配脸部表情符号范围"),(r"[\U0001F300-\U0001F5FF]","字符类","匹配杂项符号范围"),(r"[\U0001F680-\U0001F6FF]","字符类","匹配交通符号范围")]},
    {"category":"日期时间","name":"匹配日期 YYYY-MM-DD","pattern":r"\d{4}-\d{2}-\d{2}","desc":"匹配日期格式（不验证有效性）","tokens":[(r"\d{4}","预定义+量词","匹配4位数字（年份）"),("-","字面字符","匹配连字符 -"),(r"\d{2}","预定义+量词","匹配2位数字（月份）"),("-","字面字符","匹配连字符 -"),(r"\d{2}","预定义+量词","匹配2位数字（日期）")]},
    {"category":"日期时间","name":"匹配时间 HH:MM:SS","pattern":r"\d{2}:\d{2}:\d{2}","desc":"匹配时间格式（不验证有效性）","tokens":[(r"\d{2}","预定义+量词","匹配2位数字（小时）"),(":","字面字符","匹配冒号 :"),(r"\d{2}","预定义+量词","匹配2位数字（分钟）"),(":","字面字符","匹配冒号 :"),(r"\d{2}","预定义+量词","匹配2位数字（秒）")]},
    {"category":"编码命名","name":"匹配驼峰命名","pattern":r"\b[a-z]+[A-Z][a-zA-Z]*\b","desc":"匹配小驼峰命名（camelCase）","tokens":[(r"\b","位置","匹配单词边界"),("[a-z]+","字符类+量词","匹配1个或多个小写字母"),("[A-Z]","字符类","匹配1个大写字母"),("[a-zA-Z]*","字符类+量词","匹配0个或多个字母"),(r"\b","位置","匹配单词边界")]},
    {"category":"编码命名","name":"匹配蛇形命名","pattern":r"\b[a-z]+(_[a-z]+)+\b","desc":"匹配蛇形命名（snake_case）","tokens":[(r"\b","位置","匹配单词边界"),("[a-z]+","字符类+量词","匹配1个或多个小写字母"),("(_[a-z]+)+","分组+量词","下划线+小写字母，整体1次或多次"),(r"\b","位置","匹配单词边界")]},
    {"category":"编码命名","name":"匹配版本号","pattern":r"\d+\.\d+\.\d+","desc":"匹配语义化版本号 x.y.z","tokens":[(r"\d+","预定义+量词","匹配1位或多位数字（主版本号）"),(r"\.","转义字符","匹配点号 ."),(r"\d+","预定义+量词","匹配1位或多位数字（次版本号）"),(r"\.","转义字符","匹配点号 ."),(r"\d+","预定义+量词","匹配1位或多位数字（修订号）")]},
    {"category":"编码命名","name":"匹配文件扩展名","pattern":r"\.\w+$","desc":"匹配文件扩展名（如 .txt）","tokens":[(r"\.","转义字符","匹配点号 ."),(r"\w+","预定义+量词","\w 匹配单词字符[a-zA-Z0-9_]，+ 表示1次或多次"),("$","锚点","匹配字符串结尾")]},
    {"category":"代码相关","name":"匹配 HTML 标签","pattern":r"<[^>]+>","desc":"匹配 HTML/XML 标签","tokens":[("<","字面字符","匹配左尖括号 <"),("[^>]+","字符类+量词","匹配除 > 外的字符，1次或多次"),(">","字面字符","匹配右尖括号 >")]},
    {"category":"代码相关","name":"匹配 HTML 注释","pattern":r"<!--[\s\S]*?-->","desc":"匹配 HTML 注释","tokens":[("<!--","字面字符","匹配注释开始标记 <!--"),(r"[\s\S]*?","字符类+量词","匹配任意字符（含换行），0次或多次，非贪婪"),("-->","字面字符","匹配注释结束标记 -->")]},
    {"category":"代码相关","name":"匹配 Markdown 链接","pattern":r"\[([^\]]+)\]\(([^)]+)\)","desc":"匹配 Markdown 链接 [text](url)","tokens":[(r"\[","转义字符","匹配左方括号 ["),("([^\]]+)","捕获分组","捕获链接文本"),(r"\]","转义字符","匹配右方括号 ]"),(r"\(","转义字符","匹配左括号 ("),("([^)]+)","捕获分组","捕获 URL"),(r"\)","转义字符","匹配右括号 )")]},
    {"category":"颜色值","name":"匹配十六进制颜色","pattern":r"#[0-9a-fA-F]{6}\b","desc":"匹配十六进制颜色值 #RRGGBB","tokens":[("#","字面字符","匹配井号 #"),("[0-9a-fA-F]{6}","字符类+量词","匹配6位十六进制数字"),(r"\b","位置","匹配单词边界")]},
    {"category":"颜色值","name":"匹配颜色 RGB","pattern":r"rgb\(\d{1,3},\s*\d{1,3},\s*\d{1,3}\)","desc":"匹配 RGB 颜色值","tokens":[("rgb","字面字符","匹配字符串 rgb"),(r"\(","转义字符","匹配左括号 ("),(r"\d{1,3}","预定义+量词","匹配1-3位数字（红色值）"),(",","字面字符","匹配逗号 ,"),(r"\s*","预定义+量词","匹配空白字符，0次或多次"),(r"\d{1,3}","预定义+量词","匹配1-3位数字（绿色值）"),(",","字面字符","匹配逗号 ,"),(r"\s*","预定义+量词","匹配空白字符，0次或多次"),(r"\d{1,3}","预定义+量词","匹配1-3位数字（蓝色值）"),(r"\)","转义字符","匹配右括号 )")]},
    {"category":"中国专用","name":"匹配身份证号","pattern":r"\d{17}[\dXx]","desc":"匹配18位身份证号（不验证校验位）","tokens":[(r"\d{17}","预定义+量词","匹配17位数字（地址+出生日期+顺序码）"),("[\dXx]","字符类","匹配数字或 X/x（校验码）")]},
    {"category":"中国专用","name":"匹配邮政编码","pattern":r"\d{6}","desc":"匹配6位邮政编码","tokens":[(r"\d{6}","预定义+量词","匹配6位数字")]},
    {"category":"中国专用","name":"匹配车牌号","pattern":r"[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤川青藏琼宁][A-Z][A-HJ-NP-Z0-9]{4,5}[A-HJ-NP-Z0-9挂学警]","desc":"匹配中国大陆车牌号","tokens":[("[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤川青藏琼宁]","字符类","匹配省份简称"),("[A-Z]","字符类","匹配大写字母（城市代码）"),("[A-HJ-NP-Z0-9]{4,5}","字符类+量词","匹配4-5位字母数字（不含I/O）"),("[A-HJ-NP-Z0-9挂学警]","字符类","匹配最后一位（含警/学/挂）")]},
    {"category":"其他","name":"匹配密码强度","pattern":r"(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*]).{8,}","desc":"匹配强密码（大小写+数字+特殊字符，至少8位）","tokens":[("(?=.*[a-z])","零宽断言","正向先行断言：必须包含小写字母"),("(?=.*[A-Z])","零宽断言","正向先行断言：必须包含大写字母"),("(?=.*\d)","零宽断言","正向先行断言：必须包含数字"),("(?=.*[!@#$%^&*])","零宽断言","正向先行断言：必须包含特殊字符"),(".{8,}","通配符+量词","匹配任意字符，至少8次")]},
    {"category":"其他","name":"匹配浮点数","pattern":r"-?\d+\.\d+","desc":"匹配浮点数（含负数）","tokens":[("-?","量词","匹配负号 - 0次或1次"),(r"\d+","预定义+量词","匹配1位或多位数字（整数部分）"),(r"\.","转义字符","匹配点号 ."),(r"\d+","预定义+量词","匹配1位或多位数字（小数部分）")]},
    {"category":"其他","name":"匹配百分比","pattern":r"\d+(\.\d+)?%","desc":"匹配百分比值","tokens":[(r"\d+","预定义+量词","匹配1位或多位数字"),("(\.\d+)?","分组+量词","可选小数部分"),("%","字面字符","匹配百分号 %")]},
    {"category":"其他","name":"匹配路径（Unix）","pattern":r"(/[a-zA-Z0-9._-]+)+","desc":"匹配 Unix/Linux 文件路径","tokens":[("(/[a-zA-Z0-9._-]+)+","分组+量词","斜杠开头+路径名，整体1次或多次")]},
]

if "selected_idx" not in st.session_state:
    st.session_state.selected_idx = 0
if "category" not in st.session_state:
    st.session_state.category = "全部"

filtered = PRESETS
cat = st.session_state.category
if cat != "全部":
    filtered = [p for p in PRESETS if p["category"] == cat]

col_cat, _ = st.columns([1, 1])
with col_cat:
    cat = st.selectbox("分类", ["全部"] + CATEGORIES, index=0 if st.session_state.category == "全部" else CATEGORIES.index(st.session_state.category) + 1, label_visibility="collapsed")
    st.session_state.category = cat

if not filtered:
    st.info("没有匹配的预设")
else:
    rows = [filtered[i:i+4] for i in range(0, len(filtered), 4)]
    for row in rows:
        cols = st.columns(len(row))
        for col, p in zip(cols, row):
            with col:
                idx = PRESETS.index(p)
                if st.button(p["name"], use_container_width=True, key=f"b_{idx}"):
                    st.session_state.selected_idx = idx
                    st.rerun()

st.divider()

p = PRESETS[st.session_state.selected_idx]

st.markdown(f'<div class="pattern-box">{p["pattern"]}</div>', unsafe_allow_html=True)
st.caption(f"分类: {p['category']}  |  {p['desc']}")

tokens = p["tokens"]
tok_data = []
for i, (tok, typ, meaning) in enumerate(tokens):
    tok_data.append({"#": i+1, "Token": f"  {tok}", "类型": typ, "含义": meaning})
st.dataframe(tok_data, use_container_width=True, hide_index=True)

st.divider()
col_f1, col_f2, col_f3 = st.columns([1, 1, 2])
with col_f1:
    st.caption("🔍 正则表达式查看器 v1.0")
with col_f2:
    st.caption("引擎: Python re")
with col_f3:
    st.caption("30+ 常用正则 | 逐 Token 含义解析")