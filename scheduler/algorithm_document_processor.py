"""
AlgorithmDocumentProcessor — cleaned & refactored to use Gemini Flash 2.0
Now also integrates with document_utils for OCR (PDF/Image handling).
"""

from __future__ import annotations

import os
import json
import re
import logging
from typing import List, Dict, Any, Optional, Protocol

# OCR/Document utilities
from . import document_utils

# ---------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(levelname)s %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

# ---------------------------------------------------------------------
# LLM Provider Abstraction
# ---------------------------------------------------------------------
class LLMProvider(Protocol):
    def generate_questions(self, *, level: str, difficulty: str, content: str) -> str:
        """Return raw model text for questions JSON given content and difficulty level."""


class GeminiFlashProvider:
    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None):
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        if not self.api_key:
            logger.warning("GEMINI_API_KEY is not set. Calls will fail until configured.")
        try:
            import google.generativeai as genai  # type: ignore
            genai.configure(api_key=self.api_key)
            self._genai = genai
        except Exception as e:
            self._genai = None
            logger.error("Failed to import/configure google.generativeai: %s", e)

    def generate_questions(self, *, level: str, difficulty: str, content: str) -> str:
        if self._genai is None:
            raise RuntimeError("google.generativeai not available.")

        prompt = (
            "You are a precise math teacher who writes JSON.\n\n"
            f"From the following math content, generate 5 multiple-choice questions at {difficulty} level (Level {level}).\n"
            "Return STRICT JSON only. Schema:\n"
            "{\n  \"questions\": [ { ... } ] }\n\n"
            "Content:\n" + content[:3000]
        )

        model = self._genai.GenerativeModel(self.model)
        response = model.generate_content(prompt)
        raw = getattr(response, "text", None)
        if not raw and hasattr(response, "candidates") and response.candidates:
            parts = getattr(response.candidates[0], "content", None)
            if parts and getattr(parts, "parts", None):
                raw = "".join(getattr(p, "text", "") for p in parts.parts)
        return raw or str(response)


class AlgorithmDocumentProcessor:
    def __init__(self, provider: Optional[LLMProvider] = None):
        self.provider: LLMProvider = provider or GeminiFlashProvider()

    # ---------------- JSON extraction ----------------
    def extract_json_from_response(self, content: str) -> Dict[str, Any]:
        try:
            return json.loads(content)
        except Exception:
            pass

        cleaned = re.sub(r"```json\s*", "", content, flags=re.IGNORECASE)
        cleaned = re.sub(r"```\s*", "", cleaned).strip("` ")
        try:
            return json.loads(cleaned)
        except Exception:
            pass

        obj_pattern = r"\{(?:[^{}]|(?:\{[^{}]*\}))*\}"
        matches = re.findall(obj_pattern, cleaned, re.DOTALL)
        for m in matches:
            try:
                parsed = json.loads(m)
                if isinstance(parsed, dict) and "questions" in parsed:
                    return parsed
            except Exception:
                continue

        arr = re.search(r"\[.*\]", cleaned, re.DOTALL)
        if arr:
            try:
                return {"questions": json.loads(arr.group())}
            except Exception:
                pass

        return {"questions": []}

    # ---------------- Math pipeline ----------------
    def process_math_document(self, text: str, document_id: str) -> Dict[str, Any]:
        try:
            cleaned = self.clean_text(text)
            lvl3 = self.extract_questions_by_level(cleaned, "3", "basic")
            lvl4 = self.extract_questions_by_level(cleaned, "4", "intermediate")
            lvl5 = self.extract_questions_by_level(cleaned, "5", "advanced")
            chunks = self.prepare_rag_chunks(cleaned)
            return {
                "level_3_questions": lvl3,
                "level_4_questions": lvl4,
                "level_5_questions": lvl5,
                "knowledge_chunks": chunks,
                "total_questions": len(lvl3) + len(lvl4) + len(lvl5),
            }
        except Exception as e:
            logger.error("process_math_document failed: %s", e)
            return {"level_3_questions": [], "level_4_questions": [], "level_5_questions": [], "knowledge_chunks": [], "total_questions": 0}

    def extract_questions_by_level(self, text: str, level: str, difficulty: str) -> List[Dict[str, Any]]:
        try:
            raw = self.provider.generate_questions(level=level, difficulty=difficulty, content=text)
            parsed = self.extract_json_from_response(raw)
            return [q for q in parsed.get("questions", []) if self.validate_question_data(q)]
        except Exception as e:
            logger.warning("Level %s generation failed (%s).", level, e)
            return []

    # ---------------- OCR / Document entrypoints ----------------
    def extract_pdf_content(self, file_path: str) -> Dict[str, Any]:
        return document_utils.DocumentProcessor().extract_pdf_text(file_path)

    def extract_image_content(self, file_path: str, lang: str = 'en') -> Dict[str, Any]:
        return document_utils.DocumentProcessor().extract_image_text(file_path, lang)

    # ---------------- Helpers ----------------
    def prepare_rag_chunks(self, text: str) -> List[str]:
        words = text.split()
        chunk_size = 500
        return [" ".join(words[i : i+chunk_size]) for i in range(0, len(words), chunk_size) if len(words[i : i+chunk_size]) > 50]

    def clean_text(self, text: str) -> str:
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"[^\w\s\.,!\?\+\-=\(\)\[\]\{\}\^\*\/\\]", "", text)
        return text.strip()

    def validate_question_data(self, q: Dict[str, Any]) -> bool:
        required = ["question_text", "option_a", "option_b", "option_c", "option_d", "correct_answer"]
        return all((k in q and isinstance(q[k], str) and q[k].strip()) for k in required)
