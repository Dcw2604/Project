"""
Answer Evaluator
----------------
- Evaluates student answers.
- Supports both exact MCQ answers and free-text similarity.
- Returns: (is_correct, score)
"""

import difflib


class AnswerEvaluator:
    def evaluate_answer(self, question_text, correct_answer, student_answer):
        """
        Evaluate student's answer.
        Args:
            question_text (str): The original question (optional use for context).
            correct_answer (str): The expected correct answer (letter or text).
            student_answer (str): The student's submitted answer.

        Returns:
            tuple: (is_correct: bool, score: float)
        """
        if not student_answer:
            return False, 0.0

        # Normalize inputs
        correct = str(correct_answer).strip().lower()
        student = str(student_answer).strip().lower()

        # Case 1: exact match (for multiple choice A/B/C/D)
        if student == correct:
            return True, 1.0

        # Case 2: similarity check (for free text answers)
        similarity = difflib.SequenceMatcher(None, correct, student).ratio()

        if similarity > 0.85:  # very close → full credit
            return True, 1.0
        elif similarity > 0.6:  # somewhat close → partial credit
            return False, 0.5
        else:  # wrong
            return False, 0.0
