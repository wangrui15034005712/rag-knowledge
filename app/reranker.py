# reranker.py — 重排序（Reranker）抽象层，当前仅实现 SiliconFlow 后端

from typing import List
from pathlib import Path
import requests
import json
from langchain_core.documents import Document

from app.config import (
    SILICONFLOW_BASE_URL, SILICONFLOW_API_KEY, SILICONFLOW_RERANK_MODEL,
    RERANK_TOP_K,
)
from app.logger import setup_logger

logger = setup_logger(__name__)


class SiliconFlowReranker:
    def __init__(self):
        self.model = SILICONFLOW_RERANK_MODEL
        self.top_n = RERANK_TOP_K
        self.url = f"{SILICONFLOW_BASE_URL}/rerank"
        msg = f"[Reranker] SiliconFlowReranker 初始化: model={self.model}, top_n={self.top_n}"
        logger.info(msg)
        print(f"\n{'=' * 60}\n{msg}\n{'=' * 60}", flush=True)

    def rerank(self, query: str, documents: List[Document]) -> List[Document]:
        if not documents:
            return documents

        texts = [d.page_content for d in documents]

        payload = {
            "model": self.model,
            "query": query,
            "documents": texts,
            "top_n": self.top_n,
            "return_documents": False,
        }
        headers = {
            "Authorization": f"Bearer {SILICONFLOW_API_KEY}",
            "Content-Type": "application/json",
        }

        logger.debug(f"Reranker 请求: query={query[:60]}..., documents={len(texts)}个, top_n={self.top_n}")

        try:
            resp = requests.post(self.url, headers=headers, json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            logger.warning(f"Reranker 调用失败: {e}，退回原始排序")
            return documents

        results = data.get("results", [])
        logger.debug(f"Reranker 返回: {len(results)} 个结果")

        # 按 relevance_score 降序排列
        results.sort(key=lambda r: r.get("relevance_score", 0), reverse=True)

        reranked = []
        original_indices = []
        for r in results:
            idx = r.get("index")
            score = r.get("relevance_score", 0)
            if idx is not None and 0 <= idx < len(documents):
                doc = documents[idx]
                doc.metadata["relevance_score"] = score
                reranked.append(doc)
                original_indices.append(idx)

        # ---- 统一表格日志 ----
        kept = set(original_indices)
        lines = []
        lines.append(f"  Reranker: {len(documents)} \u2192 {len(reranked)}")
        lines.append(f"  {'#':<3} {'score':<7} {'原#':<5} {'来源':<18} 内容")
        for i, (d, oi) in enumerate(zip(reranked, original_indices)):
            src = Path(d.metadata.get("source", "?")).name
            s = d.metadata.get("relevance_score", 0)
            preview = d.page_content[:300].replace("\n", " ")
            lines.append(f"  {i:<3} {s:.4f}  ({oi:<2}) {src:<18} {preview}")
        lines.append(f"  {'\u2500' * 70}")
        removed = [(i, d) for i, d in enumerate(documents) if i not in kept]
        if removed:
            lines.append(f"  移除: {len(removed)} 个")
            for oi, d in removed:
                src = Path(d.metadata.get("source", "?")).name
                preview = d.page_content[:300].replace("\n", " ")
                lines.append(f"    ({oi}) {src:<18} {preview}")
        print("\n".join(lines), flush=True)
        return reranked


def get_reranker(backend: str):
    if backend == "siliconflow":
        return SiliconFlowReranker()
    return None
