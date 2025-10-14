"""
GenericDocumentProcessor — cleaned & refactored to use Gemini Flash 2.0
Now works for ANY academic/technical subject (not just math).
Integrates with document_utils for OCR (PDF/Image handling).
"""

from __future__ import annotations

import os
import json
import re
import logging
from typing import List, Dict, Any, Optional, Protocol
from .topic_extractor import TopicExtractor

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
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
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
            "You are an expert teacher. Generate 5 open-ended questions "
            f"at {difficulty} level (Level {level}) from the following content.\n\n"
            "IMPORTANT: Create questions that require students to write detailed answers, "
            "explain concepts, analyze problems, or demonstrate understanding.\n\n"
            "LANGUAGE: Generate all questions, answers, topics, and keywords in HEBREW language.\n\n"
            "Return ONLY valid JSON in this exact format:\n"
            "{\n"
            '  "questions": [\n'
            '    {\n'
            '      "question_text": "Your open-ended question here?",\n'
            '      "question_type": "open_ended",\n'
            '      "difficulty_level": 3,\n'
            '      "expected_keywords": ["keyword1", "keyword2", "keyword3"],\n'
            '      "sample_answer": "A sample answer that demonstrates the expected response",\n'
            '      "topics": ["Topic1", "Topic2"]\n'  # ADD THIS LINE
            '    }\n'
            '  ]\n'
            "}\n\n"
            "Content:\n" + content[:3000]
        )

        try:
            model = self._genai.GenerativeModel(self.model)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error("Gemini API call failed: %s", e)
            return "{\"questions\": []}"

class GenericDocumentProcessor:
    def __init__(self, provider: Optional[LLMProvider] = None):
        self.provider: LLMProvider = provider or GeminiFlashProvider()
        self.topic_extractor = TopicExtractor()

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


    def process_document(self, text: str, document_id: str) -> Dict[str, Any]:
        try:
            logger.info(f"Processing document {document_id} with text length: {len(text)}")
            logger.info(f"First 200 chars of text: {text[:200]}...")
            
            cleaned = self.clean_text(text)
            logger.info(f"Cleaned text length: {len(cleaned)}")
            
            lvl3 = self.extract_questions_by_level(cleaned, "3", "basic")
            lvl4 = self.extract_questions_by_level(cleaned, "4", "intermediate")
            lvl5 = self.extract_questions_by_level(cleaned, "5", "advanced")
            chunks = self.prepare_rag_chunks(cleaned)

            # add topics to questions
            all_questions = lvl3 + lvl4 + lvl5
            for question_data in all_questions:
                logger.info(f"  Before topic check: q has 'topics' key = {'topics' in question_data}, value = {question_data.get('topics', 'NOT FOUND')[:100] if question_data.get('topics') else 'EMPTY'}") 
                # הוסף נושאים לשאלה
                if not question_data.get("topics"):
                    question_data["topics"] = self.topic_extractor.extract_topics_from_question(
                        question_data["question_text"]
                    )
            
                logger.info(f"  After topic check: topics = {question_data.get('topics', [])}")
            
            return {
                "level_3_questions": lvl3,
                "level_4_questions": lvl4,
                "level_5_questions": lvl5,
                "knowledge_chunks": chunks,
                "total_questions": len(lvl3) + len(lvl4) + len(lvl5),
            }
        except Exception as e:
            logger.error("process_document failed: %s", e)
            return {
                "level_3_questions": [],
                "level_4_questions": [],
                "level_5_questions": [],
                "knowledge_chunks": [],
                "total_questions": 0,
            }

    def extract_questions_by_level(self, text: str, level: str, difficulty: str) -> List[Dict[str, Any]]:
        try:
            logger.info(f"Generating questions for level {level} with content length: {len(text)}")
            raw = self.provider.generate_questions(level=level, difficulty=difficulty, content=text)
            logger.info(f"Raw Gemini response: {raw[:500]}...")
            parsed = self.extract_json_from_response(raw)
            logger.info(f"Parsed JSON: {parsed}")
            questions = [q for q in parsed.get("questions", []) if self.validate_question_data(q)]
            logger.info(f"Valid questions found: {len(questions)}")
            return questions
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
        return [
            " ".join(words[i:i+chunk_size])
            for i in range(0, len(words), chunk_size)
            if len(words[i:i+chunk_size]) > 50
        ]

    def clean_text(self, text: str) -> str:
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"[^\w\s\.,!\?\+\-=\(\)\[\]\{\}\^\*\/\\]", "", text)
        return text.strip()

    def validate_question_data(self, q: Dict[str, Any]) -> bool:
        # For open-ended questions, we need different validation
        required_open_ended = ["question_text", "question_type", "expected_keywords", "sample_answer"]
        required_multiple_choice = ["question_text", "option_a", "option_b", "option_c", "option_d", "correct_answer"]
        
        # Check if it's an open-ended question
        if q.get("question_type") == "open_ended":
            return all((k in q and isinstance(q[k], (str, list)) and (q[k] if isinstance(q[k], list) else q[k].strip())) for k in required_open_ended)
        else:
            # Fallback to multiple choice validation
            return all((k in q and isinstance(q[k], str) and q[k].strip()) for k in required_multiple_choice)

DocumentProcessor = GenericDocumentProcessor