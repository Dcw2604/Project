"""
Django Models — Cleaned
-----------------------
- Defines User (teacher/student), Document, QuestionBank, Exam, ExamSession, StudentAnswer, ChatSession, ChatInteraction.
- Replaced JSONField with TextField for SQLite compatibility.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = (
        ("teacher", "Teacher"),
        ("student", "Student"),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="student")


class Document(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to="documents/")
    extracted_text = models.TextField(blank=True, null=True)
    metadata = models.TextField(blank=True, null=True)       # JSON as text
    rag_chunks = models.TextField(blank=True, null=True)     # JSON as text
    processing_status = models.CharField(max_length=20, default="pending")
    questions_generated_count = models.IntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)


class Exam(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="exams")
    total_questions = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)


class QuestionBank(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="questions")
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="questions")
    question_text = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_answer = models.CharField(max_length=1)
    explanation = models.TextField(blank=True, null=True)
    difficulty_level = models.IntegerField(default=3)


class ExamSession(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="sessions")
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="exam_sessions")
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    score = models.IntegerField(default=0)


class StudentAnswer(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(QuestionBank, on_delete=models.CASCADE, related_name="answers")
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="answers")
    answer = models.CharField(max_length=10)
    is_correct = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)


class ChatSession(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chat_sessions")
    created_at = models.DateTimeField(auto_now_add=True)


SENDER_CHOICES = (
    ("teacher", "Teacher"),
    ("student", "Student"),
)

class ChatInteraction(models.Model):
    chat_session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name="interactions")
    sender = models.CharField(max_length=20, choices=SENDER_CHOICES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
