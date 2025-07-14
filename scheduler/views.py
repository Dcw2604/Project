from django.shortcuts import render

# Create your views here.

from rest_framework import viewsets, permissions
from .models import Lesson
from .serializers import LessonSerializer

# ViewSet that provides CRUD operations (Create, Read, Update, Delete)
# for Lesson objects through the API
class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()  # All lessons from the database
    serializer_class = LessonSerializer  # Use the serializer we defined
    permission_classes = [permissions.IsAuthenticated]  # Require login for access
