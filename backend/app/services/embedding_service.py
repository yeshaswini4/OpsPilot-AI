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
            model="text-embedding-004",
            contents=text,
        )
        return response.embeddings[0].values

    def generate_embeddings(self, chunks: list) -> list:
        embeddings = []
        for chunk in chunks:
            response = self.client.models.embed_content(
                model="text-embedding-004",
                contents=chunk,
            )
            embeddings.append(response.embeddings[0].values)
        return embeddings
