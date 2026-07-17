import chromadb
from chromadb.config import Settings

from app.config import settings
from app.services.embedding_service import EmbeddingService


class VectorService:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.embedding_service = EmbeddingService()
            cls._instance.client = chromadb.Client(Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=settings.VECTOR_DB_PATH,
                anonymized_telemetry=False
            ))
            cls._instance.collection = cls._instance.client.get_or_create_collection(
                name="opspilot"
            )
        return cls._instance

    def document_exists(self, filename: str) -> bool:
        results = self.collection.get(where={"filename": filename}, limit=1)
        return len(results["ids"]) > 0

    def store_chunks(self, chunks: list, filename: str, page_numbers: list = None):
        embeddings = self.embedding_service.generate_embeddings(chunks)
        self._store(chunks, filename, page_numbers, embeddings)

    def store_chunks_with_embeddings(self, chunks: list, filename: str, page_numbers: list, embeddings: list):
        self._store(chunks, filename, page_numbers, embeddings)

    def _store(self, chunks: list, filename: str, page_numbers: list, embeddings: list):
        import uuid
        from datetime import datetime, timezone
        upload_time = datetime.now(timezone.utc).isoformat()
        ids = [str(uuid.uuid4()) for _ in chunks]
        metadatas = [
            {
                "filename": filename,
                "chunk_number": i,
                "page_number": page_numbers[i] if page_numbers and i < len(page_numbers) else 1,
                "upload_time": upload_time
            }
            for i in range(len(chunks))
        ]
        self.collection.add(ids=ids, documents=chunks, embeddings=embeddings, metadatas=metadatas)

    def search(self, question: str, top_k: int = 20) -> dict:
        count = self.collection.count()
        if count == 0:
            return {"documents": [[]], "metadatas": [[]]}
        n = min(top_k, count)
        embedding = self.embedding_service.generate_embedding(question)
        return self.collection.query(
            query_embeddings=[embedding],
            n_results=n
        )

    def delete_document(self, filename: str):
        results = self.collection.get(where={"filename": filename})
        if results["ids"]:
            self.collection.delete(ids=results["ids"])

    def reset_collection(self):
        self.client.reset()
        self.collection = self.client.get_or_create_collection(name="opspilot")

    def keyword_search(self, keyword: str) -> dict:
        """
        Exact keyword search across all stored chunks.
        Returns: { matches: [{filename, page_number, snippet}], total_count: int }
        """
        all_data = self.collection.get()
        if not all_data["documents"]:
            return {"matches": [], "total_count": 0}

        keyword_lower = keyword.lower()
        matches = []
        total_count = 0
        seen_pages = set()  # (filename, page) dedup for page listing

        for doc, meta in zip(all_data["documents"], all_data["metadatas"]):
            count_in_chunk = doc.lower().count(keyword_lower)
            if count_in_chunk > 0:
                total_count += count_in_chunk
                page_key = (meta.get("filename"), meta.get("page_number", 1))
                if page_key not in seen_pages:
                    seen_pages.add(page_key)
                    # Extract a snippet around first occurrence
                    idx = doc.lower().find(keyword_lower)
                    start = max(0, idx - 80)
                    end = min(len(doc), idx + 80)
                    snippet = ("..." if start > 0 else "") + doc[start:end].strip() + ("..." if end < len(doc) else "")
                    matches.append({
                        "filename": meta.get("filename"),
                        "page_number": meta.get("page_number", 1),
                        "snippet": snippet
                    })

        # Sort by filename then page
        matches.sort(key=lambda x: (x["filename"], x["page_number"]))
        return {"matches": matches, "total_count": total_count}

    def list_documents(self) -> list:
        results = self.collection.get()
        if not results["metadatas"]:
            return []
        return list({m["filename"] for m in results["metadatas"]})
