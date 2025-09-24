"""
Adaptive Testing Engine — Cleaned
----------------------------------
- Manages adaptive exam sessions.
- Selects questions adaptively based on correctness.
- Does not evaluate answers (delegated to views/AnswerEvaluator).
- Provides serialization to/from dict for session storage.
"""

import random
from typing import List, Dict, Any


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
        return {
            "answers": self.answers,
            "current_index": self.current_index,
            "questions": [
                {
                    "id": q.id,
                    "text": q.question_text,
                    "option_a": q.option_a,
                    "option_b": q.option_b,
                    "option_c": q.option_c,
                    "option_d": q.option_d,
                    "correct_answer": q.correct_answer,
                    "difficulty_level": q.difficulty_level  # Remove the trailing comma here
                }
                for q in self.questions
            ],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        from .models import QuestionBank

        questions = []
        for qd in data.get("questions", []):
            q = QuestionBank(
                id=qd["id"],
                question_text=qd["text"],
                option_a=qd["option_a"],
                option_b=qd["option_b"],
                option_c=qd["option_c"],
                option_d=qd["option_d"],
                correct_answer=qd["correct_answer"],
                difficulty_level=qd["difficulty_level"],
            )
            questions.append(q)

        session = cls(questions=questions)
        session.answers = data.get("answers", {})
        session.current_index = data.get("current_index", 0)
        return session
    
    def get_next_question(self):
        """Get the next question to display"""
        if self.current_index < len(self.questions):
            return self.questions[self.current_index]
        return None

    def is_exam_complete(self):
        """Check if all questions have been answered"""
        return self.current_index >= len(self.questions)