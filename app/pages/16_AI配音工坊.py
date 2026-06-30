import streamlit as st
import edge_tts
import asyncio
import io
import re
import json
import nest_asyncio

nest_asyncio.apply()

st.set_page_config(
    page_title="AI 配音工坊",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

from app.logger import setup_logger

logger = setup_logger(__name__)

st.title("🎬 AI 配音工坊")

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
    .role-tag {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
        margin-right: 6px;
    }
    .role-0 { background: #dbeafe; color: #1e40af; }
    .role-1 { background: #fce7f3; color: #9d174d; }
    .role-2 { background: #d1fae5; color: #065f46; }
    .role-3 { background: #fef3c7; color: #92400e; }
    .role-4 { background: #ede9fe; color: #5b21b6; }
    .role-5 { background: #ffe4e6; color: #9f1239; }
</style>
""", unsafe_allow_html=True)

ALL_VOICES = {
    "中文 - 晓晓 (女)": "zh-CN-XiaoxiaoNeural",
    "中文 - 晓依 (女)": "zh-CN-XiaoyiNeural",
    "中文 - 云健 (男)": "zh-CN-YunjianNeural",
    "中文 - 云希 (男)": "zh-CN-YunxiNeural",
    "中文 - 云夏 (男)": "zh-CN-YunxiaNeural",
    "中文 - 云扬 (男)": "zh-CN-YunyangNeural",
    "中文 - 小北 (女·东北)": "zh-CN-liaoning-XiaobeiNeural",
    "中文 - 小妮 (女·陕西)": "zh-CN-shaanxi-XiaoniNeural",
    "中文 - 粤语晓嘉 (女)": "zh-HK-HiuGaaiNeural",
    "中文 - 粤语云龙 (男)": "zh-HK-WanLungNeural",
    "中文 - 繁体晓臻 (女)": "zh-TW-HsiaoChenNeural",
    "中文 - 繁体云哲 (男)": "zh-TW-YunJheNeural",
    "English - Jenny (F)": "en-US-JennyNeural",
    "English - Guy (M)": "en-US-GuyNeural",
    "English - Aria (F)": "en-US-AriaNeural",
    "English - Brian (M)": "en-US-BrianNeural",
    "English - Emma (F)": "en-US-EmmaNeural",
    "日本語 - 七海 (F)": "ja-JP-NanamiNeural",
    "日本語 - 圭太 (M)": "ja-JP-KeitaNeural",
    "한국어 - 선형 (F)": "ko-KR-SunHiNeural",
    "한국어 - 인준 (M)": "ko-KR-InJoonNeural",
    "Français - Denise (F)": "fr-FR-DeniseNeural",
    "Deutsch - Katja (F)": "de-DE-KatjaNeural",
    "Español - Elvira (F)": "es-ES-ElviraNeural",
    "Русский - Светлана (F)": "ru-RU-SvetlanaNeural",
}

ROLE_COLORS = ["role-0", "role-1", "role-2", "role-3", "role-4", "role-5"]

tab_simple, tab_script, tab_ssml = st.tabs(["📝 单段配音", "🎭 多角色对话", "🔧 SSML 精细控制"])


async def generate_audio(text, voice, rate="+0%", pitch="+0Hz"):
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    audio_data = b""
    duration_ms = 0
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
        elif chunk["type"] == "WordBoundary":
            duration_ms = max(duration_ms, chunk["offset"] + chunk["duration"])
    return audio_data, duration_ms


def run_async(coro):
    loop = asyncio.new_event_loop()
    result = loop.run_until_complete(coro)
    loop.close()
    return result


def seconds_to_srt_time(ms):
    s = ms // 1000
    ms_r = ms % 1000
    m = s // 60
    s = s % 60
    h = m // 60
    m = m % 60
    return f"{h:02d}:{m:02d}:{s:02d},{ms_r:03d}"


with tab_simple:
    col_text, col_opts = st.columns([3, 1])

    with col_opts:
        simple_voice = st.selectbox("音色", list(ALL_VOICES.keys()), index=0, key="simple_voice")
        simple_rate = st.slider("语速", -50, 50, 0, key="simple_rate", format="%+d%%")
        simple_pitch = st.slider("音调", -50, 50, 0, key="simple_pitch", format="%+d%%")

    with col_text:
        simple_text = st.text_area(
            "输入文本",
            height=250,
            placeholder="输入要配音的文字...",
            key="simple_text",
            label_visibility="collapsed"
        )

    if simple_text.strip():
        st.caption(f"📊 {len(simple_text)} 字符")
        if st.button("🎬 生成配音", type="primary", use_container_width=True, key="btn_simple"):
            with st.spinner("正在生成..."):
                try:
                    voice_id = ALL_VOICES[simple_voice]
                    rate_str = f"{simple_rate:+d}%"
                    pitch_str = f"{simple_pitch:+d}Hz"
                    audio, dur = run_async(generate_audio(simple_text, voice_id, rate_str, pitch_str))

                    if audio:
                        st.audio(io.BytesIO(audio), format="audio/mp3", autoplay=True)
                        st.download_button("📥 下载 MP3", audio, "voiceover.mp3", "audio/mpeg", use_container_width=True)
                        st.success("生成完成！")
                    else:
                        st.error("未生成音频")
                except Exception as e:
                    st.error(f"失败: {e}")


with tab_script:
    st.markdown("### 🎭 多角色对话")

    if "script_roles" not in st.session_state:
        st.session_state.script_roles = [
            {"name": "旁白", "voice": "中文 - 云扬 (男)"},
            {"name": "角色A", "voice": "中文 - 晓晓 (女)"},
            {"name": "角色B", "voice": "中文 - 云希 (男)"},
        ]
    if "script_lines" not in st.session_state:
        st.session_state.script_lines = [
            {"role": 0, "text": "在一个阳光明媚的早晨，小明走在上学的路上。"},
            {"role": 1, "text": "早上好！今天天气真不错啊。"},
            {"role": 2, "text": "是啊，要不要一起去学校？"},
            {"role": 1, "text": "好啊，我们走吧！"},
        ]

    with st.expander("👥 角色设置", expanded=True):
        cols = st.columns(len(st.session_state.script_roles) + 1)
        for i, role in enumerate(st.session_state.script_roles):
            with cols[i]:
                role["name"] = st.text_input("角色名", role["name"], key=f"rname_{i}")
                role["voice"] = st.selectbox("音色", list(ALL_VOICES.keys()),
                    index=list(ALL_VOICES.keys()).index(role["voice"]) if role["voice"] in ALL_VOICES else 0,
                    key=f"rvoice_{i}")
        with cols[-1]:
            if st.button("➕ 添加角色", key="add_role"):
                st.session_state.script_roles.append({"name": f"角色{len(st.session_state.script_roles)}", "voice": "中文 - 晓晓 (女)"})
                st.rerun()

    st.markdown("### 📝 剧本")
    st.caption("格式：`角色名：台词内容`，每行一句。未识别的角色名默认使用「旁白」")

    script_text = st.text_area(
        "剧本内容",
        height=300,
        value="\n".join([f"{st.session_state.script_roles[l['role']]['name']}：{l['text']}" for l in st.session_state.script_lines]),
        key="script_text",
        label_visibility="collapsed",
        placeholder="旁白：在一个阳光明媚的早晨...\n小明：早上好！\n小红：你好啊！"
    )

    if st.button("🎬 生成对话配音", type="primary", use_container_width=True, key="btn_script"):
        lines = [l.strip() for l in script_text.strip().split("\n") if l.strip()]
        role_names = {r["name"]: i for i, r in enumerate(st.session_state.script_roles)}
        parsed = []
        for line in lines:
            match = re.match(r"^(.+?)[：:](.+)$", line)
            if match:
                rname = match.group(1).strip()
                text = match.group(2).strip()
                role_idx = role_names.get(rname, 0)
                parsed.append({"role": role_idx, "text": text})

        if not parsed:
            st.error("未识别到有效台词，请检查格式")
        else:
            with st.spinner(f"正在生成 {len(parsed)} 段对话..."):
                try:
                    all_audio = []
                    srt_entries = []
                    current_ms = 0

                    for i, line in enumerate(parsed):
                        role = st.session_state.script_roles[line["role"]]
                        voice_id = ALL_VOICES[role["voice"]]
                        audio, dur = run_async(generate_audio(line["text"], voice_id))

                        if audio:
                            all_audio.append(audio)
                            srt_entries.append({
                                "index": len(srt_entries) + 1,
                                "start": current_ms,
                                "end": current_ms + dur,
                                "text": line["text"],
                                "role": role["name"]
                            })
                            current_ms += dur + 500

                    if all_audio:
                        combined = b"".join(all_audio)
                        st.audio(io.BytesIO(combined), format="audio/mp3", autoplay=True)

                        c1, c2 = st.columns(2)
                        with c1:
                            st.download_button("📥 下载音频", combined, "dialogue.mp3", "audio/mpeg", use_container_width=True)
                        with c2:
                            srt_content = ""
                            for e in srt_entries:
                                srt_content += f"{e['index']}\n"
                                srt_content += f"{seconds_to_srt_time(e['start'])} --> {seconds_to_srt_time(e['end'])}\n"
                                srt_content += f"[{e['role']}] {e['text']}\n\n"
                            st.download_button("📥 下载字幕 (SRT)", srt_content, "dialogue.srt", "text/plain", use_container_width=True)

                        st.success(f"生成完成！共 {len(parsed)} 段对话")
                    else:
                        st.error("未生成音频")
                except Exception as e:
                    st.error(f"失败: {e}")


with tab_ssml:
    st.markdown("### 🔧 SSML 精细控制")
    st.caption("使用 SSML 标签精确控制语音效果：停顿、重音、语速、音调等")

    col_ssml, col_preview = st.columns([3, 1])

    with col_preview:
        ssml_voice = st.selectbox("音色", list(ALL_VOICES.keys()), index=0, key="ssml_voice")
        st.markdown("**可用标签：**")
        st.code("""<!-- 停顿 -->
<speak>
  你好<break time="1s"/>世界
</speak>

<!-- 重音 -->
<speak>
  这很<emphasis level="strong">重要</emphasis>
</speak>

<!-- 语速 -->
<speak>
  <prosody rate="slow">慢慢说</prosody>
  <prosody rate="fast">快快说</prosody>
</speak>

<!-- 音调 -->
<speak>
  <prosody pitch="+20%">高音</prosody>
  <prosody pitch="-20%">低音</prosody>
</speak>

<!-- 换人 -->
<speak>
  <voice name="zh-CN-YunxiNeural">我是云希</voice>
  <voice name="zh-CN-XiaoxiaoNeural">我是晓晓</voice>
</speak>""", language="xml")

    with col_ssml:
        ssml_text = st.text_area(
            "SSML 内容",
            height=400,
            value='<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="zh-CN">\n  <voice name="zh-CN-XiaoxiaoNeural">\n    你好，欢迎使用<emphasis level="strong">AI 配音工坊</emphasis>！<break time="500ms"/>\n    这里支持<prosody rate="slow">慢速</prosody>和<prosody rate="fast">快速</prosody>朗读。\n  </voice>\n</speak>',
            key="ssml_text",
            label_visibility="collapsed"
        )

    if st.button("🎬 生成 SSML 配音", type="primary", use_container_width=True, key="btn_ssml"):
        with st.spinner("正在生成..."):
            try:
                voice_id = ALL_VOICES[ssml_voice]
                communicate = edge_tts.Communicate(ssml_text, voice_id)
                audio = b""
                loop = asyncio.new_event_loop()
                async def collect(communicate):
                    data = b""
                    async for chunk in communicate.stream():
                        if chunk["type"] == "audio":
                            data += chunk["data"]
                    return data
                audio = loop.run_until_complete(collect(communicate))
                loop.close()

                if audio:
                    st.audio(io.BytesIO(audio), format="audio/mp3", autoplay=True)
                    st.download_button("📥 下载 MP3", audio, "ssml_voice.mp3", "audio/mpeg", use_container_width=True)
                    st.success("生成完成！")
                else:
                    st.error("未生成音频")
            except Exception as e:
                st.error(f"失败: {e}")


st.divider()
with st.expander("💡 功能说明", expanded=False):
    st.markdown("""
    **📝 单段配音** — 简单文本转语音，支持语速和音调调节

    **🎭 多角色对话** — 剧本格式，不同角色自动分配不同音色，生成后可导出 SRT 字幕

    **🔧 SSML 精细控制** — 使用 SSML 标签精确控制：
    - `<break time="1s"/>` — 插入停顿
    - `<emphasis level="strong">` — 重音强调
    - `<prosody rate="slow">` — 语速控制
    - `<prosody pitch="+20%">` — 音调控制
    - `<voice name="...">` — 切换音色
    """)
