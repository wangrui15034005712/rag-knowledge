import streamlit as st
import json
import base64
import socket
import time


# ======================
# 数据库连通性测试模块
# ======================

class DatabaseTester:
    """数据库连接测试器"""

    @staticmethod
    def test_mysql(host="localhost", port=3306, user="root", password="", database=""):
        """测试 MySQL 连接并返回版本"""
        try:
            import mysql.connector
            from mysql.connector import Error

            start_time = time.time()

            # 建立连接
            connection = mysql.connector.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database if database else None,
                connection_timeout=5
            )

            if connection.is_connected():
                cursor = connection.cursor()
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()[0]
                cursor.close()

                latency = round((time.time() - start_time) * 1000, 2)

                return {
                    "success": True,
                    "type": "MySQL",
                    "host": host,
                    "port": port,
                    "database": database or "未指定",
                    "version": version,
                    "latency_ms": latency,
                    "message": "连接成功"
                }

        except ImportError:
            return {
                "success": False,
                "type": "MySQL",
                "message": "未安装 mysql-connector-python，请执行: pip install mysql-connector-python"
            }
        except Exception as e:
            return {
                "success": False,
                "type": "MySQL",
                "host": host,
                "port": port,
                "message": str(e)
            }
        finally:
            if 'connection' in locals() and connection.is_connected():
                connection.close()

    @staticmethod
    def test_redis(host="localhost", port=6379, password="", db=0):
        """测试 Redis 连接并返回版本"""
        try:
            import redis

            start_time = time.time()

            # 建立连接
            r = redis.Redis(
                host=host,
                port=port,
                password=password if password else None,
                db=db,
                socket_connect_timeout=5,
                decode_responses=True
            )

            # 测试连接
            r.ping()

            # 获取版本
            info = r.info()
            version = info.get('redis_version', '未知')

            latency = round((time.time() - start_time) * 1000, 2)

            return {
                "success": True,
                "type": "Redis",
                "host": host,
                "port": port,
                "db": db,
                "version": version,
                "mode": info.get('redis_mode', 'standalone'),
                "memory_used": info.get('used_memory_human', '未知'),
                "connected_clients": info.get('connected_clients', 0),
                "latency_ms": latency,
                "message": "连接成功"
            }

        except ImportError:
            return {
                "success": False,
                "type": "Redis",
                "message": "未安装 redis-py，请执行: pip install redis"
            }
        except Exception as e:
            return {
                "success": False,
                "type": "Redis",
                "host": host,
                "port": port,
                "message": str(e)
            }

    @staticmethod
    def test_port(host, port, timeout=3):
        """基础端口连通性测试"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, int(port)))
            sock.close()

            return {
                "success": result == 0,
                "host": host,
                "port": int(port),
                "message": "端口开放" if result == 0 else "端口关闭或不可达"
            }
        except Exception as e:
            return {
                "success": False,
                "host": host,
                "port": int(port),
                "message": str(e)
            }


# ======================
# Streamlit UI 部分
# ======================

st.set_page_config(
    page_title="数据库连通性测试",
    page_icon="🗄️",
    layout="wide"
)

st.title("🗄️ 数据库连通性测试工具")
st.caption("支持 MySQL / Redis 连接测试与版本检测")

# 初始化 session state
if 'test_results' not in st.session_state:
    st.session_state.test_results = []

tester = DatabaseTester()

# 创建三个标签页
tab1, tab2, tab3 = st.tabs(["🐬 MySQL 测试", "🔴 Redis 测试", "🌐 端口测试"])

with tab1:
    st.header("MySQL 连接测试")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("连接参数")
        mysql_host = st.text_input("主机地址", value="localhost", key="mysql_host")
        mysql_port = st.number_input("端口", value=3306, min_value=1, max_value=65535, key="mysql_port")
        mysql_user = st.text_input("用户名", value="root", key="mysql_user")
        mysql_password = st.text_input("密码", type="password", key="mysql_password")
        mysql_db = st.text_input("数据库名（可选）", key="mysql_db")

        if st.button("🔍 测试 MySQL 连接", use_container_width=True, type="primary"):
            with st.spinner("正在测试 MySQL 连接..."):
                result = tester.test_mysql(
                    mysql_host,
                    mysql_port,
                    mysql_user,
                    mysql_password,
                    mysql_db
                )
                st.session_state.test_results.append(result)
                st.rerun()

    with col2:
        st.subheader("测试结果")
        # 显示最新的 MySQL 测试结果
        mysql_results = [r for r in st.session_state.test_results if r["type"] == "MySQL"]
        if mysql_results:
            latest = mysql_results[-1]

            if latest["success"]:
                st.success(f"✅ {latest['message']}")
                st.metric("版本", latest["version"])
                st.metric("延迟", f"{latest['latency_ms']} ms")

                with st.expander("详细信息"):
                    st.json(latest)
            else:
                st.error(f"❌ {latest['message']}")
        else:
            st.info("👈 填写左侧参数并点击测试按钮")

with tab2:
    st.header("Redis 连接测试")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("连接参数")
        redis_host = st.text_input("主机地址", value="localhost", key="redis_host")
        redis_port = st.number_input("端口", value=6379, min_value=1, max_value=65535, key="redis_port")
        redis_password = st.text_input("密码（可选）", type="password", key="redis_password")
        redis_db = st.number_input("数据库编号", value=0, min_value=0, max_value=15, key="redis_db")

        if st.button("🔍 测试 Redis 连接", use_container_width=True, type="primary"):
            with st.spinner("正在测试 Redis 连接..."):
                result = tester.test_redis(
                    redis_host,
                    redis_port,
                    redis_password,
                    redis_db
                )
                st.session_state.test_results.append(result)
                st.rerun()

    with col2:
        st.subheader("测试结果")
        redis_results = [r for r in st.session_state.test_results if r["type"] == "Redis"]
        if redis_results:
            latest = redis_results[-1]

            if latest["success"]:
                st.success(f"✅ {latest['message']}")

                metric_col1, metric_col2, metric_col3 = st.columns(3)
                with metric_col1:
                    st.metric("版本", latest["version"])
                with metric_col2:
                    st.metric("模式", latest["mode"])
                with metric_col3:
                    st.metric("延迟", f"{latest['latency_ms']} ms")

                with st.expander("详细信息"):
                    st.json(latest)
            else:
                st.error(f"❌ {latest['message']}")
        else:
            st.info("👈 填写左侧参数并点击测试按钮")

with tab3:
    st.header("基础端口连通性测试")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("测试参数")
        port_host = st.text_input("主机地址", value="localhost", key="port_host")
        port_number = st.number_input("端口", value=3306, min_value=1, max_value=65535, key="port_number")
        timeout = st.slider("超时时间(秒)", min_value=1, max_value=10, value=3)

        if st.button("🔍 测试端口连通性", use_container_width=True, type="primary"):
            with st.spinner("正在测试端口..."):
                result = tester.test_port(port_host, port_number, timeout)
                st.session_state.test_results.append({**result, "type": "Port"})
                st.rerun()

    with col2:
        st.subheader("测试结果")
        port_results = [r for r in st.session_state.test_results if r["type"] == "Port"]
        if port_results:
            latest = port_results[-1]

            if latest["success"]:
                st.success(f"✅ {latest['message']}")
                st.metric("测试地址", f"{latest['host']}:{latest['port']}")
            else:
                st.error(f"❌ {latest['message']}")
                st.metric("测试地址", f"{latest['host']}:{latest['port']}")
        else:
            st.info("👈 填写左侧参数并点击测试按钮")

# 历史记录
st.divider()
with st.expander("📜 测试历史记录"):
    if st.session_state.test_results:
        for i, result in enumerate(reversed(st.session_state.test_results[-10:])):
            status = "✅" if result["success"] else "❌"
            st.write(
                f"{status} [{result['type']}] {result.get('host', '')}:{result.get('port', '')} - {result['message']}")

        if st.button("🗑️ 清空历史"):
            st.session_state.test_results = []
            st.rerun()
    else:
        st.info("暂无测试记录")

# 依赖安装说明
with st.expander("📦 依赖安装说明"):
    st.code("""
# 安装 MySQL 驱动
pip install mysql-connector-python

# 安装 Redis 驱动
pip install redis

# 同时安装
pip install mysql-connector-python redis
    """)

# 底部信息
st.divider()
st.caption("🛠️ 数据库连通性测试工具 v1.0 | 支持 MySQL & Redis")