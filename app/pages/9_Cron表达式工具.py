import streamlit as st
import datetime
from cronexpr import next_fire, prev_fire
from cron_descriptor import get_description

st.set_page_config(
    page_title="Cron 表达式工具",
    page_icon="🕐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("🕐 Cron 表达式工具")

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


WEEKDAY_NAMES_CN = ["日", "一", "二", "三", "四", "五", "六"]


def is_valid_cron(expr: str) -> bool:
    try:
        next_fire(expr, datetime.datetime.now(datetime.timezone.utc))
        return True
    except Exception:
        return False


def get_next_times(expr: str, count: int = 10) -> list[datetime.datetime]:
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    times = []
    d = now_utc
    for _ in range(count):
        d = next_fire(expr, d + datetime.timedelta(seconds=1))
        times.append(d.astimezone().replace(tzinfo=None))
    return times


def format_time_until(dt: datetime.datetime) -> str:
    now = datetime.datetime.now()
    diff = dt - now
    if diff.total_seconds() < 0:
        return "已过期"
    total_sec = int(diff.total_seconds())
    days, rem = divmod(total_sec, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, seconds = divmod(rem, 60)
    parts = []
    if days:
        parts.append(f"{days}天")
    if hours:
        parts.append(f"{hours}小时")
    if minutes:
        parts.append(f"{minutes}分")
    parts.append(f"{seconds}秒")
    return "".join(parts)


PRESETS = [
    ("每分钟", "* * * * *"),
    ("每5分钟", "*/5 * * * *"),
    ("每15分钟", "*/15 * * * *"),
    ("每30分钟", "*/30 * * * *"),
    ("每小时", "0 * * * *"),
    ("每天0点", "0 0 * * *"),
    ("每天8点", "0 8 * * *"),
    ("工作日9点", "0 9 * * 1-5"),
    ("周一0点", "0 0 * * 1"),
    ("每月1号0点", "0 0 1 * *"),
    ("每小时6秒", "6 0 * * * ?"),
    ("最后一天0点", "0 0 0 L * ?"),
    ("最后周五", "0 0 0 * * 5L"),
    ("第二周五", "0 0 0 * * 5#2"),
    ("工作日每15分", "*/15 9-17 * * 1-5"),
]


COMMON_REFERENCE = [
    ("每分钟", "* * * * *"),
    ("每5分钟", "*/5 * * * *"),
    ("每15分钟", "*/15 * * * *"),
    ("每小时整点", "0 * * * *"),
    ("每天 00:00", "0 0 * * *"),
    ("每天 08:00", "0 8 * * *"),
    ("工作日 09:00", "0 9 * * 1-5"),
    ("每周一 00:00", "0 0 * * 1"),
    ("每月1日 00:00", "0 0 1 * *"),
    ("每小时 00:06", "6 0 * * * ?"),
    ("每月最后一天 00:00", "0 0 0 L * ?"),
    ("最后周五 00:00", "0 0 0 * * 5L"),
    ("第二周五 00:00", "0 0 0 * * 5#2"),
    ("工作日每15分 9-17", "*/15 9-17 * * 1-5"),
]


# === Session State ===

if "cron_input" not in st.session_state:
    st.session_state.cron_input = "*/5 * * * *"
if "last_valid" not in st.session_state:
    st.session_state.last_valid = True


def set_cron(val: str):
    st.session_state.cron_input = val


# === UI ===

col_input, col_output = st.columns([1, 1], gap="large")

with col_input:
    st.subheader("Cron 表达式")

    cron_input = st.text_input(
        "Cron 表达式",
        value=st.session_state.cron_input,
        placeholder="例如: */5 * * * *  或  6 0 * * * ?",
        label_visibility="collapsed",
        help="Quartz 格式: 秒 分 时 日 月 周 | 支持 ? L W #",
    )
    st.session_state.cron_input = cron_input

    expr = cron_input.strip()

    # Detect format
    fields = expr.split()
    fmt_hint = ""
    if len(fields) == 6:
        fmt_hint = "6 字段 Quartz 格式"
    elif len(fields) == 5:
        fmt_hint = "5 字段标准格式"
    elif len(fields) == 7:
        fmt_hint = "7 字段 Quartz 格式（含年）"

    # Validation
    is_valid = is_valid_cron(expr) if expr else False
    st.session_state.last_valid = is_valid

    if not expr:
        st.info("请输入 cron 表达式")
    elif not is_valid:
        st.error("表达式无效 — Quartz 格式: 秒(0-59) 分(0-59) 时(0-23) 日(1-31) 月(1-12) 周(1-7 或 SUN-SAT)")
    else:
        if fmt_hint:
            st.caption(f"检测到 {fmt_hint}")
        try:
            desc = get_description(expr)
            st.success(desc)
        except Exception:
            pass

    # Presets
    st.markdown("##### 常用预设")
    rows = [PRESETS[i:i+5] for i in range(0, len(PRESETS), 5)]
    for row in rows:
        cols = st.columns(len(row))
        for col, (label, val) in zip(cols, row):
            with col:
                if st.button(label, use_container_width=True, key=f"preset_{val}"):
                    set_cron(val)
                    st.rerun()

    # Reference table
    with st.expander("📖 常用表达式速查"):
        ref_data = []
        for label, expr_ref in COMMON_REFERENCE:
            ref_data.append({"说明": label, "表达式": f"  {expr_ref}"})
        st.dataframe(ref_data, use_container_width=True, hide_index=True)

with col_output:
    if is_valid and expr:
        st.subheader("最近 10 次执行时间")

        try:
            times = get_next_times(expr, 10)
            now = datetime.datetime.now()

            table_data = []
            for i, t in enumerate(times):
                weekday_cn = WEEKDAY_NAMES_CN[t.weekday()]
                diff = t - now
                total_sec = int(diff.total_seconds())
                if total_sec < 60:
                    time_str = f"{total_sec} 秒后"
                elif total_sec < 3600:
                    time_str = f"{total_sec // 60} 分 {total_sec % 60} 秒后"
                elif total_sec < 86400:
                    time_str = f"{total_sec // 3600} 小时 {(total_sec % 3600) // 60} 分后"
                else:
                    days = total_sec // 86400
                    rem = total_sec % 86400
                    time_str = f"{days} 天 {rem // 3600} 小时后"
                table_data.append({
                    "#": i + 1,
                    "日期": t.strftime("%Y-%m-%d"),
                    "时间": t.strftime("%H:%M:%S"),
                    "星期": f"周{weekday_cn}",
                    "距现在": time_str,
                })

            st.dataframe(
                table_data,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "#": st.column_config.NumberColumn(width=30),
                    "日期": st.column_config.TextColumn(width=100),
                    "时间": st.column_config.TextColumn(width=85),
                    "星期": st.column_config.TextColumn(width=50),
                    "距现在": st.column_config.TextColumn(width=130),
                }
            )

            # Countdown to next
            next_time = times[0]
            delta = next_time - now
            if delta.total_seconds() > 0:
                remaining = format_time_until(next_time)
                st.info(f"📅 距下次执行: **{remaining}**")

                # Progress bar
                if len(times) > 1:
                    total_interval = (times[1] - times[0]).total_seconds()
                    if total_interval > 0:
                        elapsed = (now - (times[0] - datetime.timedelta(seconds=total_interval))).total_seconds()
                        progress = min(max(elapsed / total_interval, 0), 1)
                        st.progress(progress, text="当前周期进度")

            # Time bar
            st.markdown("##### 时间轴")
            start = now - datetime.timedelta(minutes=5)
            end = times[-1] + datetime.timedelta(minutes=5)
            total_span = (end - start).total_seconds()

            bar_html = '<div style="position:relative;height:40px;background:#f0f2f6;border-radius:6px;overflow:hidden;">'

            now_pct = max(0, min(100, (now - start).total_seconds() / total_span * 100))
            bar_html += f'<div style="position:absolute;left:{now_pct:.1f}%;top:0;bottom:0;width:2px;background:#ff4b4b;z-index:3;" title="现在"></div>'

            for t in times:
                pct = (t - start).total_seconds() / total_span * 100
                if 0 <= pct <= 100:
                    bar_html += f'<div style="position:absolute;left:{pct:.1f}%;top:2px;bottom:2px;width:6px;margin-left:-3px;background:#00c853;border-radius:3px;z-index:2;" title="{t.strftime("%H:%M:%S")}"></div>'

            bar_html += '</div>'
            bar_html += f'<div style="display:flex;justify-content:space-between;font-size:0.7rem;color:#888;"><span>{start.strftime("%H:%M")}</span><span style="color:#ff4b4b;">▼ 现在</span><span>{end.strftime("%H:%M")}</span></div>'

            st.markdown(bar_html, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"计算执行时间失败: {e}")
    else:
        st.info("👈 在左侧输入有效的 cron 表达式")

# === Footer ===

st.divider()
col_f1, col_f2, col_f3 = st.columns([1, 1, 2])
with col_f1:
    st.caption("🕐 Cron 表达式工具 v2.0")
with col_f2:
    st.caption("引擎: cronexpr (Quartz)")
with col_f3:
    st.caption("格式: 秒 分 时 日 月 周 | 支持 ? L W # | 例如: 6 0 * * * ? = 每小时第0分6秒")
