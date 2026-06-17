# bm25_retriever.py — BM25 关键词检索器（从 ChromaDB 加载全量文档构建索引）

from typing import List
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from app.ingest import get_chroma_client, collection_name_for_backend
from app.config import DEFAULT_BACKEND, RRF_K
from app.logger import setup_logger

logger = setup_logger(__name__)


class BM25RetrieverFromChroma(BaseRetriever):
    """从 ChromaDB 加载文档，使用 jieba 分词 + rank_bm25 构建关键词检索器"""

    texts: List[str]
    metadatas: List[dict]
    k: int = 8
    _bm25 = None

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, texts, metadatas, k=8, **kwargs):
        super().__init__(texts=texts, metadatas=metadatas, k=k, **kwargs)
        self._build_index()

    def _build_index(self):
        import jieba
        from rank_bm25 import BM25Okapi

        logger.info(f"构建 BM25 索引: {len(self.texts)} 个文档块")
        tokenized = [list(jieba.cut(text)) for text in self.texts]
        self._bm25 = BM25Okapi(tokenized)
        logger.info("BM25 索引构建完成")

    def _get_relevant_documents(self, query: str):
        import jieba

        query_tokens = list(jieba.cut(query))
        scores = self._bm25.get_scores(query_tokens)

        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:self.k]

        results = []
        for idx in top_indices:
            if scores[idx] > 0:
                doc = Document(
                    page_content=self.texts[idx],
                    metadata=self.metadatas[idx] if idx < len(self.metadatas) else {},
                )
                results.append(doc)

        logger.info(f"BM25 检索完成: 查询='{query}', 返回 {len(results)} 个结果")
        return results


def get_bm25_retriever(backend: str = DEFAULT_BACKEND, k: int = 8):
    """从 ChromaDB 加载全量文档，构建 BM25 检索器"""
    client = get_chroma_client()
    collection_name = collection_name_for_backend(backend)

    try:
        collection = client.get_collection(collection_name)
    except Exception:
        logger.warning(f"ChromaDB 集合 {collection_name} 不存在，无法构建 BM25 索引")
        return None

    results = collection.get(include=["documents", "metadatas"])
    documents = results.get("documents", [])
    metadatas = results.get("metadatas", [])

    if not documents:
        logger.warning("ChromaDB 中无文档，无法构建 BM25 索引")
        return None

    return BM25RetrieverFromChroma(texts=documents, metadatas=metadatas, k=k)


# ── EnsembleRetriever：融合多个检索器结果（RRF 算法） ──

class EnsembleRetriever(BaseRetriever):
    """融合多个检索器结果，使用 Reciprocal Rank Fusion (RRF) 排序"""

    retrievers: list
    weights: list
    k: int = RRF_K

    class Config:
        arbitrary_types_allowed = True

    def _get_relevant_documents(self, query: str):
        from collections import defaultdict

        scores = defaultdict(float)
        all_docs = {}

        for retriever, weight in zip(self.retrievers, self.weights):
            docs = retriever.invoke(query)
            for rank, doc in enumerate(docs):
                doc_key = doc.page_content[:100]
                scores[doc_key] += weight * (1.0 / (self.k + rank + 1))
                if doc_key not in all_docs:
                    all_docs[doc_key] = doc

        sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        results = [all_docs[key] for key, _ in sorted_docs if key in all_docs]

        logger.info(f"Ensemble 融合完成: 返回 {len(results)} 个结果")
        return results
