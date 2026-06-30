import streamlit as st
import torch
import torchaudio
import numpy as np
import io
import os
import tempfile
import soundfile as sf
import scipy.io.wavfile

try:
    from transformers import LlamaModel
    import ChatTTS
except ImportError:
    st.error("ChatTTS 依赖异常，请运行: .\\venv\\Scripts\\python.exe -m pip install --force-reinstall transformers ChatTTS")
    st.stop()

st.set_page_config(
    page_title="ChatTTS 语音合成",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

import re as _re

def _sanitize_text(text: str) -> str:
    text = text.replace("\r", "")
    text = _re.sub(r"\s+", " ", text).strip()
    return text

from app.logger import setup_logger

logger = setup_logger(__name__)

st.title("🤖 ChatTTS 语音合成")

device_hint = "GPU (CUDA)" if torch.cuda.is_available() else "CPU"
st.caption(f"⚡ 当前使用 {device_hint}")

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

def load_audio(path: str):
    from pydub import AudioSegment
    e1 = e2 = None
    try:
        return sf.read(path)
    except Exception as ex:
        e1 = ex
        logger.debug(f"load_audio sf.read failed: {e1}")
    try:
        audio = AudioSegment.from_file(path)
        sr = audio.frame_rate
        data = np.array(audio.get_array_of_samples()).astype(np.float32) / 32768.0
        if audio.channels > 1:
            data = data.reshape(-1, audio.channels).mean(axis=1)
        return data, sr
    except Exception as ex:
        e2 = ex
        logger.debug(f"load_audio pydub failed: {e2}")
    try:
        sr, data = scipy.io.wavfile.read(path)
        data = data.astype(np.float32) / 32768.0
        return data, sr
    except Exception as e3:
        raise RuntimeError(
            f"无法解码音频。支持的格式：WAV/MP3/FLAC/OGG。"
            f" sf: {e1}, pydub: {e2}, scipy: {e3}"
        )


@st.cache_resource
def load_model():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    use_compile = torch.cuda.is_available() and torch.cuda.get_device_capability(0) >= (7, 0)
    chat = ChatTTS.Chat()
    try:
        chat.load(source="huggingface", compile=use_compile, force_redownload=False, device=device)
    except Exception as e:
        logger.warning(f"ChatTTS load with default failed: {e}, trying custom path...")
        model_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "chattts_models")
        os.makedirs(model_dir, exist_ok=True)
        chat.load(source="custom", compile=use_compile, custom_path=model_dir, device=device)
    return chat

tab_random, tab_clone, tab_batch = st.tabs(["🎲 随机音色", "🎤 声音克隆", "📝 批量合成"])

with tab_random:
    col_text, col_opts = st.columns([3, 1])

    with col_opts:
        st.markdown("### 🎛️ 参数调节")

        temperature = st.slider("创造性 (Temperature)", 0.01, 1.0, 0.3, 0.05,
            help="越高越随机/有创意，越低越稳定（最小 0.01，避免 CUDA 断言）")

        top_p = st.slider("Top P", 0.5, 1.0, 0.7, 0.05,
            help="核采样，控制多样性")

        top_k = st.slider("Top K", 1, 50, 20, 1,
            help="限制候选词数量")

        st.divider()
        st.markdown("### 🎭 风格标签")

        oral = st.slider("口语化 (0-9)", 0, 9, 2, help="0=正式，9=非常口语")
        laugh = st.slider("笑声 (0-2)", 0, 2, 0, help="0=无笑声，2=较多笑声")
        break_ = st.slider("停顿 (0-9)", 0, 9, 6, help="0=无停顿，9=较多停顿")

        st.divider()
        st.markdown("### 🔢 音色种子")
        seed_input = st.number_input(
            "种子值 (留空=随机)", min_value=0, max_value=999999, value=None,
            placeholder="输入数字固定音色",
            help="相同种子 = 相同音色，空值 = 每次随机"
        )

        col_refresh, col_clear = st.columns(2)
        with col_refresh:
            if st.button("🔄 换一个随机音色", use_container_width=True):
                st.session_state.pop('chat_spk', None)
                st.rerun()
        with col_clear:
            if st.button("🗑️ 清除固定", use_container_width=True):
                st.session_state.pop('chat_spk', None)
                st.session_state.pop('voice_seed', None)
                st.rerun()

    with col_text:
        text = st.text_area(
            "输入文本",
            height=250,
            placeholder="输入要合成的文字...\n\n支持中文，建议每段不超过 100 字",
            label_visibility="collapsed"
        )

        if text.strip():
            st.caption(f"📊 {len(text)} 字符")

        if st.button("🎬 生成语音", type="primary", use_container_width=True, key="btn_random"):
            if text.strip():
                with st.spinner("正在加载模型（首次较慢）..."):
                    chat = load_model()

                with st.spinner("正在合成语音..."):
                    try:
                        if 'chat_spk' not in st.session_state:
                            rng_state = torch.random.get_rng_state()
                            cuda_rng = torch.cuda.get_rng_state() if torch.cuda.is_available() else None
                            if seed_input is not None:
                                torch.manual_seed(int(seed_input))
                            spk = chat.sample_random_speaker()
                            torch.random.set_rng_state(rng_state)
                            if cuda_rng is not None:
                                torch.cuda.set_rng_state(cuda_rng)
                            st.session_state.chat_spk = spk
                            st.session_state.voice_seed = seed_input
                        else:
                            spk = st.session_state.chat_spk

                        params_infer = ChatTTS.Chat.InferCodeParams(
                            spk_emb=spk,
                            temperature=temperature,
                            top_P=top_p,
                            top_K=top_k,
                        )

                        prompt = f'[oral_{oral}][laugh_{laugh}][break_{break_}]'
                        params_refine = ChatTTS.Chat.RefineTextParams(
                            prompt=prompt,
                        )

                        wavs = chat.infer(
                            [_sanitize_text(text)],
                            params_infer_code=params_infer,
                            params_refine_text=params_refine,
                        )

                        if wavs and len(wavs) > 0:
                            audio_np = wavs[0]
                            if not isinstance(audio_np, np.ndarray):
                                audio_np = np.array(audio_np)

                            sr = 24000
                            buf = io.BytesIO()
                            sf.write(buf, audio_np, sr, format='WAV')
                            buf.seek(0)

                            st.audio(buf, format="audio/wav", autoplay=True)

                            st.download_button(
                                "📥 下载 WAV",
                                data=buf.getvalue(),
                                file_name="chattts_output.wav",
                                mime="audio/wav",
                                use_container_width=True
                            )
                            st.success("生成完成！")
                        else:
                            st.error("未生成音频")

                    except Exception as e:
                        st.error(f"失败: {e}")
                        logger.error(f"ChatTTS error: {e}")
            else:
                st.warning("请输入文本")


with tab_clone:
    st.markdown("### 🎤 声音克隆")
    st.caption("上传一段参考音频（建议 3-10 秒），模型会学习音色后生成新语音")

    col_upload, col_text2 = st.columns(2)

    with col_upload:
        ref_audio = st.file_uploader(
            "上传参考音频",
            type=["wav", "mp3", "flac", "ogg"],
            help="建议 3-10 秒清晰人声音频"
        )

        if ref_audio:
            st.audio(ref_audio)
            st.info("✅ 已上传参考音频")

    with col_text2:
        clone_text = st.text_area(
            "输入要合成的文字",
            height=200,
            placeholder="用克隆的声音说...",
            key="clone_text",
            label_visibility="collapsed"
        )

    if ref_audio and clone_text.strip():
        if st.button("🎭 克隆声音并生成", type="primary", use_container_width=True, key="btn_clone"):
            with st.spinner("正在加载模型..."):
                chat = load_model()

            with st.spinner("正在提取音色并合成..."):
                try:
                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                        tmp.write(ref_audio.read())
                        tmp_path = tmp.name

                    logger.info(f"Clone: loading audio from {tmp_path}")
                    ref_audio_data, ref_sr = load_audio(tmp_path)
                    os.unlink(tmp_path)
                    logger.info(f"Clone: loaded audio sr={ref_sr}, shape={ref_audio_data.shape}, dtype={ref_audio_data.dtype}")

                    if ref_audio_data.ndim > 1:
                        ref_audio_data = ref_audio_data.mean(axis=1)

                    ref_audio_data = ref_audio_data.astype(np.float32)

                    if np.any(np.isnan(ref_audio_data)) or np.any(np.isinf(ref_audio_data)):
                        ref_audio_data = np.nan_to_num(ref_audio_data, nan=0.0, posinf=0.0, neginf=0.0)

                    if ref_sr != 16000:
                        logger.info(f"Clone: resampling {ref_sr} -> 16000")
                        ref_tensor = torch.from_numpy(ref_audio_data).float()
                        ref_tensor = torchaudio.functional.resample(ref_tensor, ref_sr, 16000)
                        ref_audio_data = ref_tensor.numpy()
                        logger.info(f"Clone: resampled shape={ref_audio_data.shape}")

                    duration = len(ref_audio_data) / 16000
                    logger.info(f"Clone: audio duration={duration:.2f}s, shape={ref_audio_data.shape}")

                    if duration < 0.3:
                        st.warning("参考音频太短，建议 3-10 秒")

                    logger.info(f"Clone: extracting speaker embedding")
                    spk_emb_str = chat.sample_audio_speaker(ref_audio_data)
                    logger.info(f"Clone: speaker embedding OK")

                    sanitized = _sanitize_text(clone_text)
                    char_count = len(sanitized)
                    max_tok = min(max(1024, char_count * 6), 4096)

                    params_infer = ChatTTS.Chat.InferCodeParams(
                        spk_smp=spk_emb_str,
                        temperature=0.3,
                        top_P=0.7,
                        top_K=20,
                        max_new_token=max_tok,
                    )

                    wavs = chat.infer(
                        [sanitized],
                        params_infer_code=params_infer,
                        skip_refine_text=True,
                        split_text=True,
                    )

                    if wavs and len(wavs) > 0:
                        audio_np = wavs[0]
                        if not isinstance(audio_np, np.ndarray):
                            audio_np = np.array(audio_np)

                        buf = io.BytesIO()
                        sf.write(buf, audio_np, 24000, format='WAV')
                        buf.seek(0)

                        st.audio(buf, format="audio/wav", autoplay=True)
                        st.download_button(
                            "📥 下载克隆语音",
                            data=buf.getvalue(),
                            file_name="cloned_voice.wav",
                            mime="audio/wav",
                            use_container_width=True
                        )
                        st.success("克隆生成完成！")
                    else:
                        st.error("未生成音频")

                except Exception as e:
                    st.error(f"克隆失败: {e}")
                    logger.error(f"Clone error: {e}")
    elif not ref_audio:
        st.info("👈 请先上传参考音频")
    elif not clone_text.strip():
        st.info("👈 请输入要合成的文字")


with tab_batch:
    st.markdown("### 📝 批量合成")
    st.caption("每行一段文本，批量生成语音")

    batch_text = st.text_area(
        "批量文本",
        height=300,
        placeholder="你好，欢迎使用 ChatTTS。\n今天天气真不错。\n我们一起去散步吧。",
        key="batch_text",
        label_visibility="collapsed"
    )

    batch_cols = st.columns(2)
    with batch_cols[0]:
        batch_temp = st.slider("创造性", 0.01, 1.0, 0.3, 0.05, key="batch_temp")
    with batch_cols[1]:
        batch_same_voice = st.checkbox("所有句子使用同一音色", value=True, key="batch_same")

    if batch_text.strip():
        lines = [l.strip() for l in batch_text.strip().split("\n") if l.strip()]
        st.caption(f"📊 {len(lines)} 段文本")

        if st.button("🎬 批量生成", type="primary", use_container_width=True, key="btn_batch"):
            if lines:
                with st.spinner("正在加载模型..."):
                    chat = load_model()

                with st.spinner(f"正在生成 {len(lines)} 段语音..."):
                    try:
                        if batch_same_voice:
                            spk = chat.sample_random_speaker()

                        all_audio = []
                        progress = st.progress(0)

                        for i, line in enumerate(lines):
                            if not batch_same_voice:
                                spk = chat.sample_random_speaker()

                            params_infer = ChatTTS.Chat.InferCodeParams(
                                spk_emb=spk,
                                temperature=batch_temp,
                                top_P=0.7,
                                top_K=20,
                            )

                            wavs = chat.infer(
                                [_sanitize_text(line)],
                                params_infer_code=params_infer,
                                skip_refine_text=True,
                                split_text=False,
                            )

                            if wavs and len(wavs) > 0:
                                audio_np = wavs[0]
                                if not isinstance(audio_np, np.ndarray):
                                    audio_np = np.array(audio_np)

                                buf = io.BytesIO()
                                sf.write(buf, audio_np, 24000, format='WAV')
                                all_audio.append((line, buf.getvalue()))

                            progress.progress((i + 1) / len(lines))

                        if all_audio:
                            st.divider()
                            st.markdown(f"### ✅ 生成完成 ({len(all_audio)} 段)")

                            for i, (line, audio_data) in enumerate(all_audio):
                                with st.expander(f"🔊 {line[:30]}{'...' if len(line) > 30 else ''}"):
                                    st.audio(io.BytesIO(audio_data), format="audio/wav")
                                    st.download_button(
                                        f"📥 下载第 {i+1} 段",
                                        data=audio_data,
                                        file_name=f"batch_{i+1}.wav",
                                        mime="audio/wav",
                                        key=f"dl_batch_{i}"
                                    )

                            combined = b""
                            for _, audio_data in all_audio:
                                combined += audio_data

                            st.divider()
                            st.download_button(
                                "📥 下载全部（合并）",
                                data=combined,
                                file_name="batch_all.wav",
                                mime="audio/wav",
                                use_container_width=True
                            )
                        else:
                            st.error("未生成任何音频")

                    except Exception as e:
                        st.error(f"批量生成失败: {e}")
                        logger.error(f"Batch error: {e}")
    else:
        st.info("👈 输入文本，每行一段")


st.divider()
with st.expander("💡 功能说明", expanded=False):
    st.markdown("""
    **🎲 随机音色** — 每次生成随机音色，可调节创造性、口语化、笑声、停顿等参数

    **🎤 声音克隆** — 上传参考音频（3-10秒），模型学习音色后用你的声音说话

    **📝 批量合成** — 每行一段文本，批量生成语音文件

    **参数说明：**
    - **Temperature** — 越高越随机有创意，越低越稳定
    - **口语化** — 0=正式朗读，9=非常口语化
    - **笑声** — 控制笑声频率
    - **停顿** — 控制停顿频率

    **注意事项：**
    - 首次运行会下载模型（约 1GB），请耐心等待
    - 推荐 GPU 加速，CPU 也能用但较慢
    - 每段文本建议不超过 100 字，效果最佳
    - 声音克隆需要清晰的人声参考音频
    """)
