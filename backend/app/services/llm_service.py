import time
import logging
from google import genai
from google.genai.errors import ClientError
from app.config import settings

logger = logging.getLogger(__name__)

MODELS = ["gemini-flash-lite-latest", "gemini-3.1-flash-lite", "gemini-3.1-flash-lite-preview"]


class LLMService:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        return cls._instance

    def generate_answer(self, question: str, context: list, metadatas: list = None) -> str:

        # Build context with page labels so Gemini knows where each chunk came from
        context_parts = []
        for i, chunk in enumerate(context):
            if metadatas and i < len(metadatas):
                fn = metadatas[i].get("filename", "document")
                pg = metadatas[i].get("page_number", "?")
                context_parts.append(f"[Source: {fn}, Page {pg}]\n{chunk}")
            else:
                context_parts.append(chunk)

        context_text = "\n\n---\n\n".join(context_parts)

        prompt = f"""You are OpsPilot AI, an intelligent Document Intelligence Assistant.

Your job is to help users understand, search, and extract information from their uploaded PDF documents.

RULES:
1. Answer using ONLY the document context provided below.
2. If the answer is not found in the context, say: "I couldn't find relevant information in the uploaded document."
3. Never hallucinate or invent information.
4. Mention source document name and page number when available.

QUESTION TYPE HANDLING:
- "list skills" / "list all skills" → Extract every skill, technology, tool, or competency mentioned. Return as bullet list.
- "list projects" → Extract all projects mentioned with brief descriptions.
- "list questions" / "all questions" → Extract every question from the document as a numbered list.
- Summary / Key points → Structured bullet points of main topics.
- Definition / Explanation → Explain using the document's own words.
- Specific facts (name, email, phone, date, score, amount) → Extract and state directly.
- Comparison → Compare using only what the document says.
- Analysis / Review → Analyze strictly from document content.
- Counting → Count occurrences in the provided context.
- General greetings (hi, hello, how are you) → Respond warmly and remind user to ask document questions.

FORMAT:
- Use bullet points (•) for lists.
- Use **bold** for important terms.
- Be thorough — do not skip items when listing.
- End with the source document name.

Document Context:
{context_text}

Question: {question}

Answer:"""

        last_error = None
        for model in MODELS:
            for attempt in range(2):
                try:
                    response = self.client.models.generate_content(
                        model=model,
                        contents=prompt
                    )
                    return response.text
                except ClientError as e:
                    last_error = e
                    if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                        logger.warning(f"Quota hit on {model}, attempt {attempt+1}")
                        if attempt == 0:
                            time.sleep(20)
                        else:
                            break  # try next model
                    elif "404" in str(e) or "NOT_FOUND" in str(e):
                        logger.warning(f"Model {model} not available, trying next")
                        break
                    else:
                        raise
        raise Exception(f"All models exhausted. Last error: {last_error}")
