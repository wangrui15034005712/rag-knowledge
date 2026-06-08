# config.py — 全局配置（支持通过环境变量覆盖默认值）
import os
from pathlib import Path

# ============================================================
# Ollama（本地 LLM）
# ============================================================
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen2.5:7b")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "bge-m3")

# ============================================================
# vLLM（远程 GPU 服务器，兼容 OpenAI API 格式）
# ============================================================
VLLM_BASE_URL = os.getenv("VLLM_BASE_URL", "http://192.168.2.60:8888/v1")
VLLM_MODEL = os.getenv("VLLM_MODEL", "qwen35-35b-a3b")
VLLM_EMBEDDING_MODEL = os.getenv("VLLM_EMBEDDING_MODEL", "octen-embedding-4b")

# ============================================================
# 默认后端：ollama | vllm
# ============================================================
DEFAULT_BACKEND = os.getenv("DEFAULT_BACKEND", "ollama")

# ============================================================
# 文本分块参数（导入文档时用于切分）
# ============================================================
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "300"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))

# ============================================================
# 检索参数
# ============================================================
TOP_K = int(os.getenv("TOP_K", "4"))

# ============================================================
# 多轮对话记忆窗口
# ============================================================
MEMORY_WINDOW = int(os.getenv("MEMORY_WINDOW", "5"))

# ============================================================
# 日志
# ============================================================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = os.getenv("LOG_FORMAT", "%(asctime)s [%(levelname)s] %(name)s: %(message)s")

# ============================================================
# 目录路径
# ============================================================
BASE_DIR = Path(__file__).parent.parent
CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", str(BASE_DIR / "chroma_db"))
DOCS_DIR = os.getenv("DOCS_DIR", str(BASE_DIR / "docs"))
