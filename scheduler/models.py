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

