"""
Document Utils — Cleaned (No OCR)
---------------------------------
- Provides utilities for extracting text from uploaded documents.
- Supports plain text (.txt) and PDF (.pdf).
- No OCR (image support removed).
"""

import logging
from pathlib import Path

try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None

logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(levelname)s %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)


def extract_text_from_file(file_path: str) -> str:
    """
    Extract text from .txt or .pdf files.
    """
    path = Path(file_path)
    if not path.exists():
        logger.error("File not found: %s", file_path)
        return ""

    try:
        if path.suffix.lower() == ".txt":
            return path.read_text(encoding="utf-8")

        elif path.suffix.lower() == ".pdf" and PdfReader:
            reader = PdfReader(str(path))
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text

        else:
            logger.warning("Unsupported file type: %s", path.suffix)
            return ""

    except Exception as e:
        logger.error("Failed to extract text from %s: %s", file_path, e)
        return ""
