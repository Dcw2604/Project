from django.contrib import admin
from .models import User, Lesson, ChatInteraction, Document, QuestionBank, TestSession, StudentAnswer

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
