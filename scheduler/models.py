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
