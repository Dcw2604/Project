"""
Math Document Processor — Cleaned
---------------------------------
- Splits text into chunks.
- Sends chunks to Gemini for question generation.
- Returns structured questions by difficulty level.
"""

import logging
from .gemini_client import generate_questions_from_text

logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(levelname)s %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)


class MathDocumentProcessor:
    def __init__(self, chunk_size: int = 1000):
        self.chunk_size = chunk_size

    def split_into_chunks(self, text: str):
        """Split text into smaller chunks for processing."""
        return [text[i:i + self.chunk_size] for i in range(0, len(text), self.chunk_size)]

    def process_math_document(self, text: str, document_id: int):
        """
        Process a math document:
        - Split into chunks
        - Generate questions with Gemini
        - Return structured dictionary with levels
        """
        try:
            chunks = self.split_into_chunks(text)
            all_questions = []

            for chunk in chunks:
                qset = generate_questions_from_text(chunk, num_questions=5)
                all_questions.extend(qset)

            # Group by difficulty
            result = {
                "total_questions": len(all_questions),
                "level_3_questions": [q for q in all_questions if q.get("difficulty_level") == 3],
                "level_4_questions": [q for q in all_questions if q.get("difficulty_level") == 4],
                "level_5_questions": [q for q in all_questions if q.get("difficulty_level") == 5],
            }

            logger.info("Processed document %s → %s questions", document_id, result["total_questions"])
            return result

        except Exception as e:
            logger.error("Math document processing failed: %s", e)
            return {"total_questions": 0, "level_3_questions": [], "level_4_questions": [], "level_5_questions": []}
