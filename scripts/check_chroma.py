import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from app.ingest import get_chroma_client, collection_name_for_backend
client = get_chroma_client()
collection = client.get_collection("rag_knowledge_lmstudio")
results = collection.get(include=["documents", "metadatas"])
docs = results.get("documents", [])
metas = results.get("metadatas", [])
print(f"总 chunk 数: {len(docs)}")
for i, (doc, meta) in enumerate(zip(docs, metas)):
    filename = meta.get("filename", "?")
    print(f"[{i}] {filename} -> {doc[:200]}")
