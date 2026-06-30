# config.py — 全局配置（支持通过环境变量覆盖默认值）
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

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
# SiliconFlow（硅基流动，兼容 OpenAI API 格式）
# ============================================================
SILICONFLOW_BASE_URL = os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1")
SILICONFLOW_LLM_MODEL = os.getenv("SILICONFLOW_LLM_MODEL", "deepseek-ai/DeepSeek-V4-Flash")
SILICONFLOW_EMBEDDING_MODEL = os.getenv("SILICONFLOW_EMBEDDING_MODEL", "Qwen/Qwen3-Embedding-8B")
SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY", "")

# ============================================================
# LM Studio（本地，OpenAI 兼容 API）
# ============================================================
LM_STUDIO_BASE_URL = os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1")
LM_STUDIO_MODEL = os.getenv("LM_STUDIO_MODEL", "qwen2.5-1.5b-instruct")
LM_STUDIO_EMBEDDING_MODEL = os.getenv("LM_STUDIO_EMBEDDING_MODEL", "text-embedding-nomic-embed-text-v1.5")

# ============================================================
# 默认后端：ollama | vllm | siliconflow | lmstudio
# ============================================================
DEFAULT_BACKEND = os.getenv("DEFAULT_BACKEND", "ollama")

# ============================================================
# 文本分块参数（导入文档时用于切分）
# ============================================================
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))

# ============================================================
# 检索参数
# ============================================================
TOP_K = int(os.getenv("TOP_K", "8"))

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
# 重排序（Reranker）
# ============================================================
RERANK_ENABLED = os.getenv("RERANK_ENABLED", "false").lower() == "true"
RERANK_TOP_K = int(os.getenv("RERANK_TOP_K", "4"))
SILICONFLOW_RERANK_MODEL = os.getenv("SILICONFLOW_RERANK_MODEL", "Qwen/Qwen3-Reranker-4B")

# ============================================================
# 混合检索（向量 + BM25 关键词）
# ============================================================
HYBRID_ENABLED = os.getenv("HYBRID_ENABLED", "false").lower() == "true"
BM25_WEIGHT = float(os.getenv("BM25_WEIGHT", "0.5"))
RRF_K = int(os.getenv("RRF_K", "10"))

# ============================================================
# 多查询扩展（MultiQueryRetriever）
# ============================================================
MULTI_QUERY_ENABLED = os.getenv("MULTI_QUERY_ENABLED", "true").lower() == "true"
MULTI_QUERY_COUNT = int(os.getenv("MULTI_QUERY_COUNT", "3"))

# ============================================================
# 目录路径
# ============================================================
BASE_DIR = Path(__file__).parent.parent
CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", str(BASE_DIR / "chroma_db"))
DOCS_DIR = os.getenv("DOCS_DIR", str(BASE_DIR / "docs"))
