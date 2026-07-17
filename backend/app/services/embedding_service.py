import os
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"
os.environ["HF_HUB_OFFLINE"] = "1"

# Prevent PyTorch/OpenMP multithreading deadlocks/crashes in uvicorn threadpools
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

from sentence_transformers import SentenceTransformer


class EmbeddingService:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.model = SentenceTransformer(
                "sentence-transformers/all-MiniLM-L6-v2"
            )
        return cls._instance

    def generate_embedding(self, text: str) -> list:
        return self.model.encode(text).tolist()

    def generate_embeddings(self, chunks: list) -> list:
        return self.model.encode(chunks).tolist()
