import json
import uuid
import math
import os
from datetime import datetime, timezone
from app.config import settings
from app.services.embedding_service import EmbeddingService

DB_FILE = os.path.join(settings.VECTOR_DB_PATH, "vector_store.json")


def _cosine_similarity(a: list, b: list) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def _load() -> list:
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def _save(records: list):
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f)


class VectorService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.embedding_service = EmbeddingService()
        return cls._instance

    def document_exists(self, filename: str) -> bool:
        return any(r["filename"] == filename for r in _load())

    def store_chunks(self, chunks: list, filename: str, page_numbers: list = None):
        embeddings = self.embedding_service.generate_embeddings(chunks)
        self._store(chunks, filename, page_numbers, embeddings)

    def store_chunks_with_embeddings(self, chunks: list, filename: str, page_numbers: list, embeddings: list):
        self._store(chunks, filename, page_numbers, embeddings)

    def _store(self, chunks: list, filename: str, page_numbers: list, embeddings: list):
        records = _load()
        upload_time = datetime.now(timezone.utc).isoformat()
        for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
            records.append({
                "id": str(uuid.uuid4()),
                "document": chunk,
                "embedding": emb,
                "filename": filename,
                "chunk_number": i,
                "page_number": page_numbers[i] if page_numbers and i < len(page_numbers) else 1,
                "upload_time": upload_time,
            })
        _save(records)

    def search(self, question: str, top_k: int = 20) -> dict:
        records = _load()
        if not records:
            return {"documents": [[]], "metadatas": [[]]}
        q_emb = self.embedding_service.generate_embedding(question)
        scored = sorted(records, key=lambda r: _cosine_similarity(q_emb, r["embedding"]), reverse=True)
        top = scored[:top_k]
        return {
            "documents": [[r["document"] for r in top]],
            "metadatas": [[{"filename": r["filename"], "page_number": r["page_number"]} for r in top]],
        }

    def delete_document(self, filename: str):
        _save([r for r in _load() if r["filename"] != filename])

    def reset_collection(self):
        _save([])

    def keyword_search(self, keyword: str) -> dict:
        records = _load()
        keyword_lower = keyword.lower()
        matches = []
        total_count = 0
        seen_pages = set()

        for r in records:
            doc = r["document"]
            count_in_chunk = doc.lower().count(keyword_lower)
            if count_in_chunk > 0:
                total_count += count_in_chunk
                page_key = (r["filename"], r["page_number"])
                if page_key not in seen_pages:
                    seen_pages.add(page_key)
                    idx = doc.lower().find(keyword_lower)
                    start = max(0, idx - 80)
                    end = min(len(doc), idx + 80)
                    snippet = ("..." if start > 0 else "") + doc[start:end].strip() + ("..." if end < len(doc) else "")
                    matches.append({"filename": r["filename"], "page_number": r["page_number"], "snippet": snippet})

        matches.sort(key=lambda x: (x["filename"], x["page_number"]))
        return {"matches": matches, "total_count": total_count}

    def list_documents(self) -> list:
        return list({r["filename"] for r in _load()})
