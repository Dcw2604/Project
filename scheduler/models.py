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


class Lesson(models.Model):
        student = models.ForeignKey(User, related_name='student_lessons', on_delete=models.CASCADE)
        teacher = models.ForeignKey(User, related_name='teacher_lessons', on_delete=models.CASCADE)
        date = models.DateField()
        start_time = models.TimeField()
        end_time = models.TimeField()
        status = models.CharField(max_length=10, choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('declined', 'Declined')
        ])
