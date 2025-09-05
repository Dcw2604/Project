#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import RequestFactory
from scheduler.views import list_exam_sessions
from django.contrib.auth.models import AnonymousUser

User = get_user_model()

def test_student_api():
    print("🧪 Testing student exam session API...")
    
    # Get a student user
    student = User.objects.filter(role='student').first()
    if not student:
        print("❌ No student found")
        return
    
    print(f"👨‍🎓 Testing with student: {student.username}")
    
    # Create a request
    factory = RequestFactory()
    request = factory.get('/api/exam-sessions/list/')
    request.user = student
    
    # Call the view
    try:
        response = list_exam_sessions(request)
        print(f"📊 Response status: {response.status_code}")
        print(f"📝 Response data: {response.data}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_student_api()
