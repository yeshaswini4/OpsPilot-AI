import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.upload import router as upload_router
from app.routers.chat import router as chat_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

app = FastAPI(
    title="OpsPilot",
    version="1.0.0",
    description="AI Document Intelligence Assistant"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router, tags=["Upload"])
app.include_router(chat_router, tags=["Chat"])


@app.get("/")
def home():
    return {"message": "Welcome to OpsPilot 🚀", "status": "Running"}


@app.get("/health")
def health():
    return {"status": "ok"}
