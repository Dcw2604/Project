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
        role = models.CharField(max_length=10, choices=ROLE_CHOICES)
        age = models.IntegerField()
        points = models.IntegerField()
        subject = models.CharField(max_length=50)
        phone = models.IntegerField()


class Lesson(models.Model):
    student = models.ForeignKey(User, on_delete= models.SET_NULL, null=True)  # taken from user management
    teacher = models.CharField(max_length=100)  # teacher name
    date = models.DateTimeField()  # date and time of lesson
    duration = models.IntegerField()  # duration of the lesson
    subject = models.CharField(max_length=100)
    phone = models.IntegerField()
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

    #הצגת המשתמש והשעה שבה הוא שלח הודעה
    def __str__(self):
        return f"{self.student.username} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
