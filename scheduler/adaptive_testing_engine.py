"""
Adaptive Testing Engine — Cleaned
----------------------------------
- Manages adaptive exam sessions.
- Selects questions adaptively based on correctness.
- Does not evaluate answers (delegated to views/AnswerEvaluator).
- Provides serialization to/from dict for session storage.
"""

import random
import json
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class AdaptiveExamSession:
    def __init__(self, questions: List[Any]):
        self.questions = questions  # list of QuestionBank objects
        self.answers: Dict[int, Dict[str, Any]] = {}  # {question_id: {"answer": str, "is_correct": bool}}
        self.current_index = 0

    def submit_answer(self, question_id: int, answer: str, is_correct: bool):
        self.answers[question_id] = {"answer": answer, "is_correct": is_correct}
        self.current_index += 1
    
    def get_next_question(self):
        """Get the next question to display"""
        if self.current_index < len(self.questions):
            return self.questions[self.current_index]
        return None

    def is_exam_complete(self):
        """Check if all questions have been answered"""
        return self.current_index >= len(self.questions)

    def current_questions(self, batch_size: int = 1) -> List[Any]:
        # Simple adaptive selection: if last correct → harder, else easier
        if not self.answers:
            return self.questions[:batch_size]

        last_qid = list(self.answers.keys())[-1]
        last_correct = self.answers[last_qid]["is_correct"]
        last_question = next((q for q in self.questions if q.id == last_qid), None)

        if not last_question:
            return []

        current_level = last_question.difficulty_level
        if last_correct:
            target_level = min(5, current_level + 1)
        else:
            target_level = max(3, current_level - 1)

        candidates = [q for q in self.questions if q.difficulty_level == target_level and q.id not in self.answers]
        if not candidates:
            # fallback: return any unanswered question
            candidates = [q for q in self.questions if q.id not in self.answers]

        return random.sample(candidates, min(batch_size, len(candidates))) if candidates else []

    def current_questions_serialized(self, batch_size: int = 1) -> List[Dict[str, Any]]:
        qs = self.current_questions(batch_size=batch_size)
        return [
            {
                "id": q.id,
                "text": q.question_text,
                "options": [q.option_a, q.option_b, q.option_c, q.option_d],
                "difficulty": q.difficulty_level,
            }
            for q in qs
        ]

    def to_dict(self) -> Dict[str, Any]:
        try:
            questions_data = []
            for q in self.questions:
                # Handle expected_keywords safely
                expected_keywords = q.expected_keywords
                if isinstance(expected_keywords, str) and expected_keywords:
                    try:
                        expected_keywords = json.loads(expected_keywords)
                    except:
                        expected_keywords = [expected_keywords]
                elif not expected_keywords:
                    expected_keywords = []
                
                question_dict = {
                    "id": int(q.id),
                    "text": str(q.question_text or ""),
                    "option_a": str(q.option_a or ""),
                    "option_b": str(q.option_b or ""),
                    "option_c": str(q.option_c or ""),
                    "option_d": str(q.option_d or ""),
                    "correct_answer": str(q.correct_answer or ""),
                    "difficulty_level": int(q.difficulty_level or 3),
                    "question_type": str(q.question_type or "multiple_choice"),
                    "expected_keywords": expected_keywords,
                    "sample_answer": str(q.sample_answer or "")
                }
                questions_data.append(question_dict)
            
            result = {
                "answers": self.answers,
                "current_index": int(self.current_index),
                "questions": questions_data,
            }
            
            # Test JSON serialization
            json.dumps(result)
            logger.info(f"Successfully serialized AdaptiveExamSession with {len(questions_data)} questions")
            return result
            
        except Exception as e:
            logger.error(f"Failed to serialize AdaptiveExamSession: {e}")
            return {
                "answers": {},
                "current_index": 0,
                "questions": [],
            }

    @classmethod

    def from_dict(cls, data: Dict[str, Any]):
        try:
            # If data is empty or None, return empty session
            if not data or not isinstance(data, dict):
                logger.warning("Empty or invalid session data, returning empty session")
                return cls(questions=[])
                
            from .models import QuestionBank

            questions = []
            questions_data = data.get("questions", [])
            
            if not questions_data:
                logger.warning("No questions data in session, returning empty session")
                return cls(questions=[])
                
            for qd in questions_data:
                try:
                    q = QuestionBank(
                        id=qd.get("id", 0),
                        question_text=qd.get("text", ""),
                        option_a=qd.get("option_a", ""),
                        option_b=qd.get("option_b", ""),
                        option_c=qd.get("option_c", ""),
                        option_d=qd.get("option_d", ""),
                        correct_answer=qd.get("correct_answer", ""),
                        difficulty_level=qd.get("difficulty_level", 3),
                        question_type=qd.get("question_type", "multiple_choice"),
                        expected_keywords=qd.get("expected_keywords", ""),
                        sample_answer=qd.get("sample_answer", "")
                    )
                    questions.append(q)
                except Exception as q_error:
                    logger.error(f"Failed to create question from data {qd}: {q_error}")
                    continue

            session = cls(questions=questions)
            session.answers = data.get("answers", {})
            session.current_index = data.get("current_index", 0)
            logger.info(f"Successfully deserialized AdaptiveExamSession with {len(questions)} questions")
            return session
            
        except Exception as e:
            logger.error(f"Failed to deserialize AdaptiveExamSession: {e}")
            logger.error(f"Session data was: {data}")
            return cls(questions=[])