import base64
import re
from openai import OpenAI

from app.config import (
    SILICONFLOW_BASE_URL, SILICONFLOW_API_KEY,
    VLLM_BASE_URL, VLLM_MODEL,
)
from app.logger import setup_logger

logger = setup_logger(__name__)

OCR_MODEL_SILICONFLOW = "Qwen/Qwen3.5-35B-A3B"
OCR_PROMPT = (
    "请完整识别图片中的所有文字，以 Markdown 格式输出。"
    "保留原文的段落结构、标题层级和列表格式。"
    "仅输出识别到的文字，不要添加额外说明。"
)


def _clean_thinking(text: str) -> str:
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    text = re.sub(r'<reasoning>.*?</reasoning>', '', text, flags=re.DOTALL)
    return text.strip()


def ocr_image(image_bytes: bytes, backend: str, mime_type: str = "image/png") -> str:
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    data_url = f"data:{mime_type};base64,{b64}"

    if backend == "siliconflow":
        if not SILICONFLOW_API_KEY:
            raise ValueError("SiliconFlow API Key 未设置，请在 .env 中配置 SILICONFLOW_API_KEY")
        client = OpenAI(base_url=SILICONFLOW_BASE_URL, api_key=SILICONFLOW_API_KEY)
        model = OCR_MODEL_SILICONFLOW
    elif backend == "vllm":
        client = OpenAI(base_url=VLLM_BASE_URL, api_key="none")
        model = VLLM_MODEL
    else:
        raise ValueError(f"不支持的 OCR 后端: {backend}")

    logger.info(f"OCR 请求: backend={backend}, model={model}")

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": data_url}},
                    {"type": "text", "text": OCR_PROMPT},
                ],
            }
        ],
        max_tokens=8192,
        temperature=0.1,
    )

    text = response.choices[0].message.content or ""
    text = _clean_thinking(text)

    logger.info(f"OCR 完成: {len(text)} 字符")
    return text
