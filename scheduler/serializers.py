"""
Serializers — Cleaned
---------------------
- Serializers for core models: User, Document, Exam, QuestionBank, ExamSession, StudentAnswer.
- Removed unused/duplicate serializers (Lesson, TestSession, etc.).
"""

from rest_framework import serializers
from .models import User, Document, Exam, QuestionBank, ExamSession, StudentAnswer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "role"]


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ["id", "title", "file", "extracted_text", "metadata", "processing_status", "questions_generated_count", "uploaded_at"]


class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = ["id", "document", "total_questions", "created_at"]


class QuestionBankSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionBank
        fields = [
            "id",
            "exam",
            "document",
            "question_text",
            "correct_answer",
            "explanation",
            "difficulty_level",
        ]


class ExamSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamSession
        fields = ["id", "exam", "student", "started_at", "completed_at", "score"]


class StudentAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAnswer
        fields = ["id", "exam", "question", "student", "answer", "is_correct", "submitted_at"]