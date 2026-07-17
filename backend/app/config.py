import os
from pathlib import Path
from pydantic_settings import BaseSettings

# Resolve backend root directory (parent of app directory)
BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):

    GEMINI_API_KEY: str

    HF_TOKEN: str = "dummy"

    UPLOAD_FOLDER: str = str(BACKEND_DIR / "uploads")

    VECTOR_DB_PATH: str = str(BACKEND_DIR / "vector_db")

    CHUNK_SIZE: int = 500

    CHUNK_OVERLAP: int = 100

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()