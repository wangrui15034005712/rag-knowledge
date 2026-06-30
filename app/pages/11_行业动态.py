import streamlit as st
import feedparser
import requests
import re
import time
from datetime import datetime, timezone, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

st.set_page_config(page_title="行业动态", page_icon="📰", layout="wide")

BJT = timezone(timedelta(hours=8))

PRESET_FEEDS = {
    "36氪": "https://36kr.com/feed",
    "少数派": "https://sspai.com/feed",
    "阮一峰博客": "https://www.ruanyifeng.com/blog/atom.xml",
    "Solidot": "https://www.solidot.org/index.rss",
    "InfoQ 中文": "https://www.infoq.cn/feed",
    "IT之家": "https://www.ithome.com/rss",
    "开源中国": "https://www.oschina.net/news/rss",
    "爱范儿": "https://www.ifanr.com/feed",
    "钛媒体": "https://www.tmtpost.com/rss",
    "雷锋网": "https://www.leiphone.com/feed",
    "动点科技": "https://cn.technode.com/feed",
}

CACHE_TTL = 300
HTTP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    )
}

st.title("📰 行业动态")


def strip_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def parse_published(entry) -> datetime | None:
    for attr in ("published_parsed", "updated_parsed"):
        parsed = getattr(entry, attr, None)
        if parsed:
            try:
                return datetime(*parsed[:6], tzinfo=timezone.utc).astimezone(BJT)
            except (TypeError, ValueError):
                pass
    return None


def fetch_single_rss(url: str):
    try:
        resp = requests.get(url, headers=HTTP_HEADERS, timeout=15)
        resp.raise_for_status()
        resp.encoding = "utf-8"
        return feedparser.parse(resp.text)
    except Exception:
        return None


def parse_feed_entries(feed, source_name: str) -> list:
    articles = []
    for entry in feed.entries:
        pub_time = parse_published(entry)
        articles.append({
            "title": entry.get("title", "无标题"),
            "link": entry.get("link", "#"),
            "summary": entry.get("summary", ""),
            "published": pub_time,
            "source": source_name,
        })
    articles.sort(
        key=lambda x: x["published"] or datetime(1970, 1, 1, tzinfo=BJT),
        reverse=True,
    )
    return articles


# ── 侧边栏 ──
with st.sidebar:
    st.header("设置")

    feed_names = list(PRESET_FEEDS.keys())
    mode = st.radio("显示模式", ["单源模式", "聚合模式"], horizontal=True, key="display_mode")

    if mode == "单源模式":
        selected_name = st.selectbox("选择订阅源", feed_names, key="feed_select")
        feed_url = PRESET_FEEDS[selected_name]

        custom_url = st.text_input(
            "或输入自定义 RSS URL",
            placeholder="https://example.com/rss",
            key="custom_rss",
        )
        if custom_url:
            feed_url = custom_url.strip()
            selected_name = custom_url.strip()

        sources_to_fetch = [(selected_name, feed_url)]
    else:
        selected_names = st.multiselect(
            "选择订阅源",
            feed_names,
            default=feed_names[:],
            key="feed_multi",
        )
        sources_to_fetch = [(n, PRESET_FEEDS[n]) for n in selected_names]

    refresh = st.button("🔄 刷新", use_container_width=True, type="primary")

    keyword = st.text_input("🔍 关键词过滤", placeholder="输入关键词...", key="filter_keyword").strip()

# ── 获取数据 ──
now = time.time()
all_articles = []

if mode == "单源模式":
    cache_key = f"rss_{feed_url}"
    last_fetch = st.session_state.get(f"{cache_key}_time", 0)
    should_fetch = refresh or (cache_key not in st.session_state) or (now - last_fetch > CACHE_TTL)

    if should_fetch:
        with st.spinner(f"正在获取 {selected_name}..."):
            feed = fetch_single_rss(feed_url)
            if feed is None:
                st.error(f"获取失败：{selected_name}")
                st.session_state[cache_key] = []
                st.session_state[f"{cache_key}_time"] = now
            elif not feed.entries:
                st.info("该订阅源暂无文章。")
                st.session_state[cache_key] = []
                st.session_state[f"{cache_key}_time"] = now
            else:
                articles = parse_feed_entries(feed, selected_name)
                st.session_state[cache_key] = articles
                st.session_state[f"{cache_key}_time"] = now

    all_articles = st.session_state.get(cache_key, [])
else:
    if not sources_to_fetch:
        st.info("请至少选择一个订阅源。")
    else:
        to_fetch = {}
        for name, url in sources_to_fetch:
            ck = f"rss_{url}"
            last = st.session_state.get(f"{ck}_time", 0)
            if refresh or ck not in st.session_state or now - last > CACHE_TTL:
                to_fetch[(name, url)] = ck

        if to_fetch:
            total = len(to_fetch)
            done = 0
            status_text = st.sidebar.empty()
            with ThreadPoolExecutor(max_workers=8) as executor:
                fut_map = {
                    executor.submit(fetch_single_rss, url): (name, url, ck)
                    for (name, url), ck in to_fetch.items()
                }
                for future in as_completed(fut_map):
                    done += 1
                    status_text.info(f"正在获取订阅源... {done}/{total}")
                    name, url, ck = fut_map[future]
                    feed = future.result()
                    if feed and feed.entries:
                        st.session_state[ck] = parse_feed_entries(feed, name)
                    else:
                        st.session_state[ck] = []
                    st.session_state[f"{ck}_time"] = now
            status_text.empty()

        all_articles = []
        for name, url in sources_to_fetch:
            ck = f"rss_{url}"
            all_articles.extend(st.session_state.get(ck, []))

        all_articles.sort(
            key=lambda x: x["published"] or datetime(1970, 1, 1, tzinfo=BJT),
            reverse=True,
        )

# ── 展示文章 ──
if keyword:
    kw_lower = keyword.lower()
    all_articles = [
        a for a in all_articles
        if kw_lower in a["title"].lower() or kw_lower in strip_html(a["summary"]).lower()
    ]

if not all_articles:
    st.info("暂无匹配文章，请选择订阅源或调整关键词。")
else:
    source_count = len({a["source"] for a in all_articles})
    st.caption(f"共 {len(all_articles)} 篇文章（来自 {source_count} 个订阅源）")

    for article in all_articles:
        summary = strip_html(article["summary"])
        if len(summary) > 200:
            summary = summary[:200] + "…"

        pub_str = article["published"].strftime("%Y-%m-%d %H:%M") if article["published"] else "未知时间"

        with st.container(border=True):
            st.markdown(
                f'<a href="{article["link"]}" target="_blank" '
                f'style="text-decoration:none;color:inherit;font-size:1.1em;font-weight:600;">'
                f'{article["title"]}</a>',
                unsafe_allow_html=True,
            )
            st.caption(f"🕐 {pub_str}　📡 {article['source']}")
            if summary:
                st.markdown(summary)
