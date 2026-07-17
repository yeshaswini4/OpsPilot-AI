from google import genai
from app.config import settings


class EmbeddingService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        return cls._instance

    def generate_embedding(self, text: str) -> list:
        response = self.client.models.embed_content(
            model="gemini-embedding-001",
            contents=text,
        )
        return response.embeddings[0].values

    def generate_embeddings(self, chunks: list) -> list:
        import time
        embeddings = []
        for i, chunk in enumerate(chunks):
            response = self.client.models.embed_content(
                model="gemini-embedding-001",
                contents=chunk,
            )
            embeddings.append(response.embeddings[0].values)
            if (i + 1) % 10 == 0:
                time.sleep(1)
        return embeddings
