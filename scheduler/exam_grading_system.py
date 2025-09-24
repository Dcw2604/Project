"""
Exam Grading System
-------------------
- Computes final score for an ExamSession.
- Aggregates StudentAnswer correctness.
- Extendable for partial credit, weighted difficulty, etc.
"""

from django.utils import timezone
from .models import StudentAnswer


class ExamGradingSystem:
    def grade_exam(self, exam_session):
        """
        Calculate the final score for a given exam session.
        Currently: percentage of correct answers.
        """
        answers = StudentAnswer.objects.filter(
            exam=exam_session.exam,
            student=exam_session.student
        )

        total = answers.count()
        if total == 0:
            return 0

        correct = answers.filter(is_correct=True).count()
        score_percentage = round((correct / total) * 100, 2)

        return score_percentage

    def now(self):
        """Return current timestamp (for marking exam completion)."""
        return timezone.now()
