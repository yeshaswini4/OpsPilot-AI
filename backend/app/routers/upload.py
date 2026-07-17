import logging
import traceback
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.concurrency import run_in_threadpool

from app.config import settings
from app.services.pdf_service import PDFService
from app.services.chunk_service import ChunkService
from app.services.vector_service import VectorService

logger = logging.getLogger(__name__)

router = APIRouter()

pdf_service = PDFService(settings.UPLOAD_FOLDER)
chunk_service = ChunkService()
vector_service = VectorService()

MAX_FILE_SIZE = 20 * 1024 * 1024


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    contents = await file.read()

    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File exceeds 20 MB limit.")

    logger.info(f"Uploading: {file.filename}")

    try:
        saved_path = pdf_service.save_pdf_bytes(contents, file.filename)
        safe_name = saved_path.name

        if vector_service.document_exists(safe_name):
            raise HTTPException(status_code=409, detail=f"'{file.filename}' is already uploaded.")

        # Run CPU-heavy extraction+chunking+embedding in thread pool
        def process():
            pages = pdf_service.extract_pages(saved_path)
            if not pages:
                raise ValueError("Could not extract text from this PDF.")
            all_chunks, all_page_numbers = [], []
            for page in pages:
                page_chunks = chunk_service.create_chunks(page["text"])
                all_chunks.extend(page_chunks)
                all_page_numbers.extend([page["page_number"]] * len(page_chunks))
            if not all_chunks:
                raise ValueError("Could not extract text from this PDF.")
            return all_chunks, len(pages), all_page_numbers

        all_chunks, total_pages, all_page_numbers = await run_in_threadpool(process)

        # Generate embeddings in thread pool (CPU-heavy)
        from app.services.embedding_service import EmbeddingService
        embeddings = await run_in_threadpool(
            lambda: EmbeddingService().generate_embeddings(all_chunks)
        )

        # Store in ChromaDB on main thread (SQLite not thread-safe)
        vector_service.store_chunks_with_embeddings(all_chunks, safe_name, all_page_numbers, embeddings)

        logger.info(f"Stored {len(all_chunks)} chunks for {safe_name}")

        return {
            "success": True,
            "message": "PDF uploaded successfully.",
            "filename": safe_name,
            "total_chunks": len(all_chunks),
            "total_pages": total_pages
        }

    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"ValueError during upload: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.exception("Upload failed with unhandled exception")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/documents")
def list_documents():
    try:
        docs = vector_service.list_documents()
        return {"success": True, "documents": docs}
    except Exception as e:
        logger.error(f"Failed to list documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/{filename}")
def delete_document(filename: str):
    try:
        vector_service.delete_document(filename)
        logger.info(f"Deleted: {filename}")
        return {"success": True, "message": f"'{filename}' removed."}
    except Exception as e:
        logger.error(f"Delete failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset")
def reset_all():
    try:
        vector_service.reset_collection()
        logger.info("Collection reset.")
        return {"success": True, "message": "All documents cleared."}
    except Exception as e:
        logger.error(f"Reset failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
