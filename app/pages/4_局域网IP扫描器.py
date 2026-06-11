import streamlit as st
import ipaddress
import concurrent.futures
import time
import socket
from ping3 import ping
import pandas as pd
import requests

st.set_page_config(page_title="局域网 IP 扫描器", page_icon="🌐", layout="wide")
st.title("🌐 局域网 IP 扫描器")


# ---------- 辅助函数：获取本机 IP 并推荐网段 ----------
def get_local_network():
    try:
        # 通过连接外部服务获取本机公网 IP（但局域网用不到，这里用 socket 获取本机局域网 IP）
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        # 提取前三位，假设是 /24 网段
        parts = local_ip.split('.')
        suggested = f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"
        return suggested, local_ip
    except:
        return "192.168.1.0/24", "未知"


default_subnet, local_ip = get_local_network()

# ---------- 侧边栏参数 ----------
with st.sidebar:
    st.header("扫描参数")
    subnet = st.text_input("网段 (CIDR)", value=default_subnet)
    timeout = st.slider("Ping 超时 (秒)", 0.5, 3.0, 1.0, 0.1)
    max_workers = st.number_input("并发线程数", 10, 200, 50, step=10)
    resolve_hostname = st.checkbox("解析主机名", value=False)
    auto_scan = st.checkbox("页面加载后自动扫描", value=True)

    col1, col2 = st.columns(2)
    with col1:
        scan_button = st.button("🚀 开始扫描", type="primary")
    with col2:
        refresh_button = st.button("🔄 刷新", type="secondary")


# ---------- 核心扫描函数 ----------
def ping_host(ip, timeout, resolve):
    try:
        delay = ping(str(ip), timeout=timeout)
        if delay is None:
            return (str(ip), None, None)
        hostname = None
        if resolve:
            try:
                hostname = socket.gethostbyaddr(str(ip))[0]
            except:
                hostname = ""
        return (str(ip), round(delay * 1000, 1), hostname)
    except:
        return (str(ip), None, None)


def scan_subnet(subnet_cidr, timeout, max_workers, resolve):
    network = ipaddress.ip_network(subnet_cidr, strict=False)
    hosts = list(network.hosts())
    total = len(hosts)
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(ping_host, ip, timeout, resolve): ip for ip in hosts}
        done_count = 0
        for future in concurrent.futures.as_completed(futures):
            done_count += 1
            progress = done_count / total
            progress_bar.progress(progress)
            status_text.text(f"扫描进度: {done_count}/{total} ({progress * 100:.1f}%)")
            result = future.result()
            if result[1] is not None:
                results.append(result)

    progress_bar.empty()
    status_text.text(f"扫描完成，共发现 {len(results)} 个存活主机")
    return results


# ---------- 执行扫描 ----------
if scan_button or refresh_button or (auto_scan and 'initial_scan_done' not in st.session_state):
    # 标记初始扫描已完成
    st.session_state.initial_scan_done = True

    if not subnet:
        st.error("请输入有效的网段")
        st.stop()

    try:
        ipaddress.ip_network(subnet, strict=False)
    except ValueError as e:
        st.error(f"网段格式错误: {e}")
        st.stop()

    st.info(f"正在扫描 {subnet} ... 共 {2 ** (32 - int(subnet.split('/')[1])) - 2} 个可用 IP")
    start_time = time.time()
    results = scan_subnet(subnet, timeout, max_workers, resolve_hostname)
    elapsed = time.time() - start_time

    # 保存结果到 session_state
    st.session_state.scan_results = results
    st.session_state.elapsed = elapsed
    st.session_state.subnet = subnet

# ---------- 显示结果 ----------
if 'scan_results' in st.session_state and st.session_state.scan_results:
    results = st.session_state.scan_results
    elapsed = st.session_state.elapsed
    subnet = st.session_state.subnet

    # 用彩色卡片展示在线 IP（更直观）
    st.success(f"扫描耗时 {elapsed:.2f} 秒，发现 {len(results)} 个存活主机")

    # 使用 columns 分多列显示
    cols_per_row = 6
    cols = st.columns(cols_per_row)
    for idx, (ip, delay, hostname) in enumerate(results):
        col = cols[idx % cols_per_row]
        with col:
            # 根据延迟高低显示不同颜色
            if delay < 5:
                color = "#28a745"  # 绿色，很快
            elif delay < 20:
                color = "#ffc107"  # 黄色，中等
            else:
                color = "#dc3545"  # 红色，较慢
            host_display = hostname if hostname else "-"
            st.markdown(
                f"""
                <div style="border:1px solid {color}; border-radius:8px; padding:8px; margin:4px; text-align:center;">
                    <div style="font-weight:bold; font-size:14px;">{ip}</div>
                    <div style="font-size:12px; color:{color};">{delay} ms</div>
                    <div style="font-size:10px; color:#666;">{host_display}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # 同时显示表格（方便复制）
    with st.expander("📊 查看表格详情"):
        df = pd.DataFrame(results, columns=["IP 地址", "延迟 (ms)", "主机名"])
        df = df.sort_values(by="IP 地址")
        st.dataframe(df, use_container_width=True, hide_index=True)

        # 导出 CSV
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 下载结果 (CSV)",
            data=csv,
            file_name=f"scan_{subnet.replace('/', '_')}.csv",
            mime="text/csv",
        )

elif 'scan_results' in st.session_state and not st.session_state.scan_results:
    st.warning("未发现存活主机，请检查网段是否正确或防火墙设置。")
else:
    st.info("👈 请在左侧设置扫描参数，然后点击「开始扫描」")

# ---------- 使用说明 ----------
with st.expander("📖 使用说明"):
    st.markdown("""
    - **自动检测网段**：页面会尝试获取本机 IP 并推荐 /24 网段。
    - **自动扫描**：勾选后，页面加载或刷新时会自动执行一次扫描。
    - **彩色卡片**：绿色=延迟<5ms，黄色=5~20ms，红色=>20ms。
    - **权限要求**：使用 ICMP Ping 需要管理员/root 权限（Windows 以管理员运行，Linux/macOS 加 `sudo`）。
    - **防火墙**：目标主机可能禁 ping，此时不会被扫描到。
    """)