import streamlit as st
import edge_tts
import asyncio
import io
import nest_asyncio

nest_asyncio.apply()

st.set_page_config(
    page_title="文字转语音",
    page_icon="🔊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

from app.logger import setup_logger

logger = setup_logger(__name__)

st.title("🔊 文字转语音")

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

VOICES = {
    "中文 - 晓晓 (女)": "zh-CN-XiaoxiaoNeural",
    "中文 - 晓依 (女)": "zh-CN-XiaoyiNeural",
    "中文 - 云健 (男)": "zh-CN-YunjianNeural",
    "中文 - 云希 (男)": "zh-CN-YunxiNeural",
    "中文 - 云夏 (男)": "zh-CN-YunxiaNeural",
    "中文 - 云扬 (男)": "zh-CN-YunyangNeural",
    "中文 - 小北 (女·东北)": "zh-CN-liaoning-XiaobeiNeural",
    "中文 - 小妮 (女·陕西)": "zh-CN-shaanxi-XiaoniNeural",
    "中文 - 粤语晓嘉 (女)": "zh-HK-HiuGaaiNeural",
    "中文 - 粤语晓曼 (女)": "zh-HK-HiuMaanNeural",
    "中文 - 粤语云龙 (男)": "zh-HK-WanLungNeural",
    "中文 - 繁体晓臻 (女)": "zh-TW-HsiaoChenNeural",
    "中文 - 繁体云哲 (男)": "zh-TW-YunJheNeural",
    "中文 - 繁体晓雨 (女)": "zh-TW-HsiaoYuNeural",
    "English - Jenny (F)": "en-US-JennyNeural",
    "English - Guy (M)": "en-US-GuyNeural",
    "English - Aria (F)": "en-US-AriaNeural",
    "English - Ava (F)": "en-US-AvaNeural",
    "English - Brian (M)": "en-US-BrianNeural",
    "English - Andrew (M)": "en-US-AndrewNeural",
    "English - Emma (F)": "en-US-EmmaNeural",
    "English - Roger (M)": "en-US-RogerNeural",
    "English - Liz (F)": "en-US-LizNeural",
    "English - GB Libby (F)": "en-GB-LibbyNeural",
    "English - GB Ryan (M)": "en-GB-RyanNeural",
    "English - AU Natasha (F)": "en-AU-NatashaNeural",
    "日本語 - 七海 (F)": "ja-JP-NanamiNeural",
    "日本語 - 圭太 (M)": "ja-JP-KeitaNeural",
    "한국어 - 선형 (F)": "ko-KR-SunHiNeural",
    "한국어 - 인준 (M)": "ko-KR-InJoonNeural",
    "Français - Denise (F)": "fr-FR-DeniseNeural",
    "Français - Henri (M)": "fr-FR-HenriNeural",
    "Deutsch - Katja (F)": "de-DE-KatjaNeural",
    "Deutsch - Conrad (M)": "de-DE-ConradNeural",
    "Español - Elvira (F)": "es-ES-ElviraNeural",
    "Español - Alvaro (M)": "es-ES-AlvaroNeural",
    "Português - Francisca (F)": "pt-BR-FranciscaNeural",
    "Português - Antonio (M)": "pt-BR-AntonioNeural",
    "Italiano - Isabella (F)": "it-IT-IsabellaNeural",
    "Italiano - Diego (M)": "it-IT-DiegoNeural",
    "Русский - Светлана (F)": "ru-RU-SvetlanaNeural",
    "Русский - Дмитрий (M)": "ru-RU-DmitryNeural",
    "हिंदी - स्वरा (F)": "hi-IN-SwaraNeural",
    "हिंदी - मधुर (M)": "hi-IN-MadhurNeural",
    "ภาษาไทย - พรวดี (F)": "th-TH-PremwadeeNeural",
    "Tiếng Việt - Hoài My (F)": "vi-VN-HoaiMyNeural",
    "Bahasa - Gadis (F)": "id-ID-GadisNeural",
}

RATE_OPTIONS = {
    "慢速 (-30%)": "-30%",
    "较慢 (-15%)": "-15%",
    "正常": "+0%",
    "较快 (+15%)": "+15%",
    "快速 (+30%)": "+30%",
}

async def generate_audio(text, voice, rate):
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
    return audio_data

col_text, col_settings = st.columns([3, 1])

with col_settings:
    voice_name = st.selectbox("音色", list(VOICES.keys()), index=0)
    rate_label = st.selectbox("语速", list(RATE_OPTIONS.keys()), index=2)

with col_text:
    text = st.text_area(
        "输入文本",
        height=300,
        placeholder="在这里输入要朗读的文字...\n\n支持中文、英文、日文、韩文等多种语言",
        label_visibility="collapsed"
    )

if text.strip():
    char_count = len(text)
    st.caption(f"📊 {char_count} 字符")

    if st.button("🔊 生成语音", type="primary", use_container_width=True):
        with st.spinner("正在生成语音..."):
            try:
                voice = VOICES[voice_name]
                rate = RATE_OPTIONS[rate_label]

                loop = asyncio.new_event_loop()
                audio_bytes = loop.run_until_complete(generate_audio(text, voice, rate))
                loop.close()

                if audio_bytes and len(audio_bytes) > 0:
                    audio_io = io.BytesIO(audio_bytes)
                    st.audio(audio_io, format="audio/mp3", autoplay=True)

                    st.download_button(
                        label="📥 下载 MP3",
                        data=audio_bytes,
                        file_name="speech.mp3",
                        mime="audio/mpeg",
                        use_container_width=True
                    )

                    st.success("语音生成完成！")
                else:
                    st.error("未生成音频数据，请检查文本或网络连接")

            except Exception as e:
                st.error(f"生成失败: {e}")
                logger.error(f"TTS error: {e}")

else:
    st.info("👈 输入文字，选择音色，点击生成语音")

with st.expander("💡 使用技巧", expanded=False):
    st.markdown("""
    - **中文**：14 种音色（含东北/陕西方言、粤语、繁体）
    - **多语言**：支持中/英/日/韩/法/德/西/葡/意/俄/印/泰/越/印尼
    - **语速调节**：5 档语速，从慢到快
    - **下载**：生成后可下载 MP3 文件离线播放
    - **质量**：基于微软 Edge TTS，音质自然流畅
    """)
