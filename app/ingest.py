# ingest.py — 文档入库流水线：解析 → 分块 → 嵌入向量 → 存储到 ChromaDB（支持增量去重）

import hashlib
from pathlib import Path
from typing import List, Dict

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_ollama import OllamaEmbeddings
from app.config import (
    DOCS_DIR, CHROMA_DB_DIR, EMBEDDING_MODEL, OLLAMA_BASE_URL,
    VLLM_BASE_URL, VLLM_EMBEDDING_MODEL, DEFAULT_BACKEND,
    CHUNK_SIZE, CHUNK_OVERLAP,
)
import chromadb
from app.logger import setup_logger

logger = setup_logger(__name__)


# ── 工具函数：计算文件 SHA256 哈希，用于去重判断 ──

def get_file_hash(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    file_hash = h.hexdigest()
    logger.debug(f"计算文件 hash: {filepath} -> {file_hash[:12]}...")
    return file_hash


# ── 文档解析：支持 PDF / TXT / DOCX 三种格式 ──

def load_document(filepath: str) -> List[Document]:
    ext = Path(filepath).suffix.lower()
    logger.info(f"解析文件: {filepath}, 类型={ext}")
    if ext == ".pdf":
        loader = PyPDFLoader(filepath)
        docs = loader.load()
        logger.info(f"  PDF 解析完成: {len(docs)} 页")
    elif ext == ".txt":
        loader = TextLoader(filepath, encoding="utf-8")
        docs = loader.load()
        logger.info(f"  TXT 解析完成: {len(docs)} 段")
    elif ext == ".docx":
        import docx2txt
        text = docx2txt.process(filepath)
        docs = [Document(page_content=text, metadata={"source": filepath})]
        logger.info(f"  DOCX 解析完成: {len(text)} 字符")
    else:
        raise ValueError(f"Unsupported file type: {ext}")
    for d in docs:
        d.metadata["source"] = filepath
    return docs


# ── 文本分块：将长文档切分成小块，便于向量检索 ──

def split_documents(docs: List[Document]) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", "。", "！", "？", "，", " ", ""],
    )
    chunks = splitter.split_documents(docs)
    logger.info(f"文本分块: {len(docs)} 文档 -> {len(chunks)} 个块 (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")
    for i, chunk in enumerate(chunks[:10]):
        logger.info(f"  chunk[{i}]: {chunk.page_content[:500]}...")
    return chunks


# ── 嵌入模型选择：Ollama（本地）/ vLLM（远程） ──

def get_embedding(backend: str = DEFAULT_BACKEND):
    if backend == "vllm":
        from langchain_openai import OpenAIEmbeddings
        logger.info(f"初始化嵌入模型(vLLM): {VLLM_EMBEDDING_MODEL} @ {VLLM_BASE_URL}")
        return OpenAIEmbeddings(
            model=VLLM_EMBEDDING_MODEL,
            base_url=VLLM_BASE_URL,
            api_key="none",
        )
    logger.debug(f"初始化嵌入模型(Ollama): {EMBEDDING_MODEL} @ {OLLAMA_BASE_URL}")
    return OllamaEmbeddings(
        model=EMBEDDING_MODEL,
        base_url=OLLAMA_BASE_URL,
    )


# ── ChromaDB 客户端连接 ──

def get_chroma_client():
    logger.debug(f"连接 ChromaDB: {CHROMA_DB_DIR}")
    return chromadb.PersistentClient(path=CHROMA_DB_DIR)


# ── 获取已索引文件的哈希表（用于增量跳过） ──

def get_indexed_hashes(client) -> Dict[str, str]:
    try:
        collection = client.get_collection("rag_knowledge")
        results = collection.get(include=["metadatas"])
        hashes = {}
        if results["metadatas"]:
            for meta in results["metadatas"]:
                if meta and "file_hash" in meta and "source" in meta:
                    hashes[meta["source"]] = meta["file_hash"]
        logger.debug(f"已索引文件数: {len(hashes)}")
        return hashes
    except Exception:
        logger.debug("ChromaDB 集合尚不存在，返回空索引")
        return {}


# ── 文档导入主流程：解析 → 分块 → 嵌入 → 去重 → 写入 ChromaDB ──

def ingest_documents(filepaths: List[str], backend: str = DEFAULT_BACKEND) -> Dict[str, str]:
    logger.info(f"开始导入 {len(filepaths)} 个文档 (backend={backend})")
    chroma_client = get_chroma_client()
    collection = chroma_client.get_or_create_collection("rag_knowledge")
    indexed = get_indexed_hashes(chroma_client)

    embedding_fn = get_embedding(backend)
    results = {}

    for fp in filepaths:
        fpath = Path(fp)
        filename = fpath.name
        logger.info(f"处理文件: {filename}")

        # 文件不存在则跳过
        if not fpath.exists():
            logger.warning(f"文件不存在: {fp}")
            results[fp] = "文件不存在"
            continue

        # 计算文件 hash，对比已索引的 hash，内容没变则跳过
        file_hash = get_file_hash(fp)
        if fp in indexed and indexed[fp] == file_hash:
            logger.info(f"跳过（内容无变化）: {filename}")
            results[fp] = "跳过（内容无变化）"
            continue

        try:
            # 1) 解析原始文档
            raw_docs = load_document(fp)
            # 2) 切分成小块
            chunks = split_documents(raw_docs)

            # 3) 提取文本 + 元数据 + 生成唯一 ID（基于文件 hash）
            texts = [d.page_content for d in chunks]
            metadatas = []
            for d in chunks:
                m = dict(d.metadata)
                m["file_hash"] = file_hash
                m["filename"] = filename
                metadatas.append(m)

            ids = [f"{file_hash}_{i}" for i in range(len(chunks))]

            # 4) 生成嵌入向量（只有这一步走 embedding 模型，不走大 LLM）
            logger.debug(f"生成嵌入向量: {len(texts)} 个文本块")
            embeddings = embedding_fn.embed_documents(texts)

            # 5) 去重：检查哪些块已经存在
            existing_ids = set()
            try:
                existing = collection.get(ids=ids, include=[])
                if existing["ids"]:
                    existing_ids = set(existing["ids"])
            except Exception:
                pass

            # 6) 只添加不存在的块
            new_ids = []
            new_texts = []
            new_metadatas = []
            new_embeddings = []
            for i in range(len(ids)):
                if ids[i] not in existing_ids:
                    new_ids.append(ids[i])
                    new_texts.append(texts[i])
                    new_metadatas.append(metadatas[i])
                    new_embeddings.append(embeddings[i])

            # 7) 写入 ChromaDB
            if new_ids:
                collection.add(
                    ids=new_ids,
                    documents=new_texts,
                    metadatas=new_metadatas,
                    embeddings=new_embeddings,
                )
                logger.info(f"导入成功: {filename} -> {len(new_ids)} 个新文本块")
                results[fp] = f"导入成功（{len(new_ids)} 个文本块）"
            else:
                logger.info(f"跳过（已是最新）: {filename}")
                results[fp] = "跳过（已是最新）"

        except Exception as e:
            logger.error(f"导入失败: {filename} -> {e}")
            results[fp] = f"失败：{e}"

    logger.info(f"导入完成: {sum(1 for v in results.values() if '成功' in v)} 成功, "
                f"{sum(1 for v in results.values() if '失败' in v)} 失败")
    return results
