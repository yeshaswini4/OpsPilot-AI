import re
import logging

from fastapi import APIRouter, HTTPException

from app.models.schemas import ChatRequest
from app.services.vector_service import VectorService
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)

router = APIRouter()

vector_service = VectorService()
llm_service = LLMService()

# Patterns that indicate a keyword/search/count/page question
KEYWORD_PATTERNS = [
    r"where is (?:the )?word ['\"]?(.+?)['\"]?\??$",
    r"find (?:the )?word ['\"]?(.+?)['\"]?\??$",
    r"find ['\"]?(.+?)['\"]? in (?:the )?(?:pdf|document)\??$",
    r"(?:search|look) for ['\"]?(.+?)['\"]?\??$",
    r"where (?:is|does) ['\"]?(.+?)['\"]? (?:appear|occur|mentioned|found)\??$",
    r"which pages? (?:contain|mention|discuss|has|have) ['\"]?(.+?)['\"]?\??$",
    r"(?:on )?which pages? is ['\"]?(.+?)['\"]? (?:mentioned|discussed|found)\??$",
    r"how many times (?:is |does )?['\"]?(.+?)['\"]? (?:appear|occur|mentioned|used)\??$",
    r"count (?:of |the )?['\"]?(.+?)['\"]?\??$",
    r"how often (?:is )?['\"]?(.+?)['\"]? (?:mentioned|used)\??$",
]


def detect_keyword_query(question: str):
    """Returns keyword string if question is a keyword/search/count/page query, else None."""
    q = question.strip().lower()
    for pattern in KEYWORD_PATTERNS:
        match = re.search(pattern, q)
        if match:
            return match.group(1).strip().strip("'\"")
    return None


def format_keyword_response(keyword: str, result: dict) -> str:
    matches = result["matches"]
    total = result["total_count"]

    if not matches:
        return f"I couldn't find the word **\"{keyword}\"** in the uploaded document(s)."

    by_file = {}
    for m in matches:
        fn = m["filename"]
        if fn not in by_file:
            by_file[fn] = []
        by_file[fn].append(m)

    lines = [f"🔍 **Keyword Search Result**\n\nThe keyword **\"{keyword}\"** was found **{total} time(s)** across the uploaded document(s).\n"]

    for filename, file_matches in by_file.items():
        lines.append(f"📄 **{filename}**\n")
        for m in file_matches:
            lines.append(f"• Page {m['page_number']}")
            lines.append(f"  *\"{m['snippet']}\"*\n")

    lines.append("\nUse the page references above to locate the keyword in the original document.")
    return "\n".join(lines).strip()


@router.post("/chat")
async def chat(request: ChatRequest):

    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    logger.info(f"Question: {request.question}")

    try:
        # --- Hybrid: keyword/search/count/page detection ---
        keyword = detect_keyword_query(request.question)

        if keyword:
            logger.info(f"Keyword search: '{keyword}'")
            result = vector_service.keyword_search(keyword)
            answer = format_keyword_response(keyword, result)

            sources = []
            seen = set()
            for m in result["matches"]:
                key = (m["filename"], m["page_number"])
                if key not in seen:
                    seen.add(key)
                    sources.append({"filename": m["filename"], "page": m["page_number"]})

            return {
                "success": True,
                "question": request.question,
                "answer": answer,
                "sources": sources
            }

        # --- Semantic search + Gemini for all other questions ---
        results = vector_service.search(request.question)
        documents = results["documents"][0]
        metadatas = results["metadatas"][0]

        if not documents:
            return {
                "success": True,
                "question": request.question,
                "answer": "I couldn't find relevant information in the uploaded document(s). Please ask a question related to the uploaded PDF.",
                "sources": []
            }

        answer = llm_service.generate_answer(request.question, documents, metadatas)

        sources = []
        seen = set()
        for meta in metadatas:
            key = (meta.get("filename"), meta.get("page_number"))
            if key not in seen:
                seen.add(key)
                sources.append({
                    "filename": meta.get("filename"),
                    "page": meta.get("page_number", 1)
                })

        logger.info(f"Answer generated from {len(sources)} source(s)")

        return {
            "success": True,
            "question": request.question,
            "answer": answer,
            "sources": sources
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat failed: {e}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")
