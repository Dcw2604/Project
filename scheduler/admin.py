from django.contrib import admin
from .models import (
    User, Document, Exam, QuestionBank,
    ExamSession, StudentAnswer, ChatSession, ChatInteraction
)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "role", "is_active")
    list_filter = ("role", "is_active")
    search_fields = ("username", "email")


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "uploaded_at", "processing_status", "questions_generated_count")
    search_fields = ("title",)


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ("id", "document", "total_questions", "created_at")


@admin.register(QuestionBank)
class QuestionBankAdmin(admin.ModelAdmin):
    list_display = ("id", "question_text", "difficulty_level", "exam")
    search_fields = ("question_text",)


@admin.register(ExamSession)
class ExamSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "exam", "student", "started_at", "completed_at", "score")
    list_filter = ("exam", "student")


@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ("id", "exam", "question", "student", "is_correct", "submitted_at")
    list_filter = ("exam", "student", "is_correct")


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "created_at")


@admin.register(ChatInteraction)
class ChatInteractionAdmin(admin.ModelAdmin):
    list_display = ("id", "chat_session", "sender", "message", "created_at")
    search_fields = ("message",)
