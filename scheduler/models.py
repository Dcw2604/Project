from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser

# יצירת מודל של USER מוכן והוספת אופצית תפקיד 
class User(AbstractUser):
        ROLE_CHOICES = (
        ('student' , 'student'),
        ('teacher', 'teacher'),

        )
        role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
        age = models.IntegerField(default=18)
        points = models.IntegerField(default=0)
        subject = models.CharField(max_length=50, blank=True, null=True)
        phone = models.IntegerField(default=0)


class Lesson(models.Model):
    student = models.ForeignKey(User, on_delete= models.SET_NULL, null=True)  # taken from user management
    teacher = models.CharField(max_length=100, default='TBD')  # teacher name
    date = models.DateTimeField(null=True, blank=True)  # date and time of lesson
    duration = models.IntegerField(default=60)  # duration of the lesson
    subject = models.CharField(max_length=100, default='General')
    phone = models.IntegerField(default=0)
    status_CHOICES = (
        ('approved' , 'approved'),
        ('pending', 'pending'),
        ('cancelled','cancelled')

        )
    status = models.CharField(max_length=10, choices=status_CHOICES, default='pending')

#שמירה השיחות עם הצאט
class ChatInteraction(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role':'student'})
    question = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

  # ניתוח עתידי
    topic = models.CharField(max_length=100, blank=True, null=True)  # למשל: "אלגברה", "גיאומטריה"
    difficulty_estimate = models.CharField(max_length=50, blank=True, null=True)  # למשל: "קל", "בינוני", "קשה"
    notes = models.TextField(blank=True, null=True)  # למשל תובנות מהצ'אט
    # Link to document if the question was about a document
    document = models.ForeignKey('Document', on_delete=models.SET_NULL, blank=True, null=True)

    #הצגת המשתמש והשעה שבה הוא שלח הודעה
    def __str__(self):
        return f"{self.student.username} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"

# Document storage for PDF files and other study materials
class Document(models.Model):
    DOCUMENT_TYPES = (
        ('pdf', 'PDF'),
        ('image', 'Image'), 
        ('text', 'Text'),
    )
    
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    document_type = models.CharField(max_length=10, choices=DOCUMENT_TYPES)
    file_path = models.CharField(max_length=500)  # Store file path
    extracted_text = models.TextField(blank=True, null=True)  # Extracted text content
    metadata = models.TextField(blank=True, null=True)  # Store PDF metadata as JSON string
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Processing status
    PROCESSING_STATUS = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    processing_status = models.CharField(max_length=15, choices=PROCESSING_STATUS, default='pending')
    processing_error = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.title} - {self.uploaded_by.username}"
    
    class Meta:
        ordering = ['-created_at']

# Question Bank for storing generated questions from documents
class QuestionBank(models.Model):
    QUESTION_TYPES = (
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('short_answer', 'Short Answer'),
        ('essay', 'Essay'),
    )
    
    DIFFICULTY_LEVELS = (
        ('3', 'Level 3 - Basic'),
        ('4', 'Level 4 - Intermediate'),
        ('5', 'Level 5 - Advanced'),
    )
    
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='multiple_choice')
    difficulty_level = models.CharField(max_length=2, choices=DIFFICULTY_LEVELS)
    subject = models.CharField(max_length=100, default='math')
    
    # For multiple choice questions
    option_a = models.TextField(blank=True, null=True)
    option_b = models.TextField(blank=True, null=True)
    option_c = models.TextField(blank=True, null=True)
    option_d = models.TextField(blank=True, null=True)
    
    correct_answer = models.TextField()  # Store the correct answer or option letter
    explanation = models.TextField(blank=True, null=True)  # RAG-generated explanation
    
    # Auto-generated or teacher-modified
    is_approved = models.BooleanField(default=True)
    created_by_ai = models.BooleanField(default=True)
    modified_by_teacher = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Q{self.id} - Level {self.difficulty_level} - {self.question_text[:50]}..."
    
    class Meta:
        ordering = ['difficulty_level', '-created_at']

# Test Sessions for students
class TestSession(models.Model):
    TEST_TYPES = (
        ('level_test', 'Level Test'),
        ('practice_test', 'Practice Test'),
    )
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_sessions')
    test_type = models.CharField(max_length=20, choices=TEST_TYPES)
    difficulty_level = models.CharField(max_length=2, choices=QuestionBank.DIFFICULTY_LEVELS)
    subject = models.CharField(max_length=100, default='math')
    
    # Test configuration
    total_questions = models.IntegerField(default=10)
    time_limit_minutes = models.IntegerField(null=True, blank=True)  # Null for practice tests
    
    # Test status
    is_completed = models.BooleanField(default=False)
    score = models.FloatField(null=True, blank=True)
    passed = models.BooleanField(default=False)
    
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.student.username} - {self.test_type} - Level {self.difficulty_level}"
    
    class Meta:
        ordering = ['-started_at']

# Individual answers for each question in a test session
class StudentAnswer(models.Model):
    test_session = models.ForeignKey(TestSession, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(QuestionBank, on_delete=models.CASCADE)
    student_answer = models.TextField()
    is_correct = models.BooleanField()
    time_taken_seconds = models.IntegerField(null=True, blank=True)
    
    answered_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.test_session.student.username} - Q{self.question.id} - {'✓' if self.is_correct else '✗'}"
    
    class Meta:
        ordering = ['answered_at']
