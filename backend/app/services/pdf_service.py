import re
from pathlib import Path
from pypdf import PdfReader

from app.utils.helpers import clean_text


class PDFService:

    def __init__(self, upload_folder: str):
        self.upload_folder = Path(upload_folder)
        self.upload_folder.mkdir(parents=True, exist_ok=True)

    def _safe_filename(self, filename: str) -> str:
        filename = re.sub(r"[^\w\-_\. ]", "_", filename)
        return filename.strip()

    def save_pdf_bytes(self, contents: bytes, filename: str) -> Path:
        safe_name = self._safe_filename(filename)
        file_path = self.upload_folder / safe_name
        with open(file_path, "wb") as f:
            f.write(contents)
        return file_path

    def extract_pages(self, pdf_path: Path) -> list[dict]:
        """Returns list of {page_number, text} for each page."""
        reader = PdfReader(pdf_path)
        pages = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text and text.strip():
                pages.append({
                    "page_number": i + 1,
                    "text": clean_text(text)
                })
        return pages

    def extract_text(self, pdf_path: Path) -> str:
        pages = self.extract_pages(pdf_path)
        return " ".join(p["text"] for p in pages)

    def get_total_pages(self, pdf_path: Path) -> int:
        return len(PdfReader(pdf_path).pages)
