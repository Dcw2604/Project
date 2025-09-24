from django.contrib import admin
<<<<<<< HEAD

# Register your models here.
=======
from .models import User, Lesson, ChatInteraction, Document, QuestionBank, TestSession, StudentAnswer, Topic, ExamSession, ExamSessionTopic, ExamSessionQuestion, ExamConfig, ExamConfigQuestion

# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'age', 'points', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    list_editable = ('role',)

admin.site.register(Lesson)
admin.site.register(ChatInteraction)
admin.site.register(Document)
admin.site.register(QuestionBank)
admin.site.register(TestSession)
admin.site.register(StudentAnswer)

# Topic admin
@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)

# ExamSession admin
@admin.register(ExamSession)
class ExamSessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'num_questions', 'time_limit_seconds', 'is_published', 'created_at')
    list_filter = ('is_published', 'random_topic_distribution', 'created_at')
    search_fields = ('title', 'description', 'created_by__username')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('selected_topics', 'manually_selected_questions')

# ExamSessionTopic admin
@admin.register(ExamSessionTopic)
class ExamSessionTopicAdmin(admin.ModelAdmin):
    list_display = ('exam_session', 'topic', 'num_questions')
    list_filter = ('topic',)
    search_fields = ('exam_session__title', 'topic__name')

# ExamSessionQuestion admin
@admin.register(ExamSessionQuestion)
class ExamSessionQuestionAdmin(admin.ModelAdmin):
    list_display = ('exam_session', 'question', 'order_index')
    list_filter = ('exam_session',)
    search_fields = ('exam_session__title', 'question__question_text')
    ordering = ('exam_session', 'order_index')


# ====================
# TASK 2.2: EXAM CONFIG ADMIN
# ====================

# ExamConfig admin
@admin.register(ExamConfig)
class ExamConfigAdmin(admin.ModelAdmin):
    list_display = ('id', 'exam_session', 'teacher', 'assigned_student', 'start_time', 'end_time', 'created_at')
    list_filter = ('teacher', 'assigned_student', 'created_at', 'start_time', 'end_time')
    search_fields = ('exam_session__title', 'teacher__username', 'assigned_student__username')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('exam_session', 'teacher', 'assigned_student')
        }),
        ('Scheduling', {
            'fields': ('start_time', 'end_time')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

# ExamConfigQuestion admin
@admin.register(ExamConfigQuestion)
class ExamConfigQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'exam_config', 'question', 'order_index')
    list_filter = ('exam_config__exam_session', 'exam_config__teacher')
    search_fields = ('exam_config__exam_session__title', 'question__question_text')
    ordering = ('exam_config', 'order_index')
    
    def exam_session_title(self, obj):
        """Display exam session title for easier identification"""
        return obj.exam_config.exam_session.title
    exam_session_title.short_description = 'Exam Session'
    
    list_display = ('id', 'exam_config', 'exam_session_title', 'question', 'order_index')
>>>>>>> daniel
