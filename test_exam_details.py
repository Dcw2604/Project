#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import RequestFactory
from scheduler.views import get_exam_session_details
from scheduler.models import ExamSession

User = get_user_model()

def test_exam_details_endpoint():
    print("🧪 Testing exam details endpoint...")
    
    # Get a teacher user
    teacher = User.objects.filter(role='teacher').first()
    if not teacher:
        print("❌ No teacher found")
        return
    
    # Get an exam session created by this teacher
    exam_session = ExamSession.objects.filter(created_by=teacher).first()
    if not exam_session:
        print("❌ No exam session found for teacher")
        return
    
    print(f"👨‍🏫 Testing with teacher: {teacher.username}")
    print(f"📝 Testing exam: {exam_session.title} (ID: {exam_session.id})")
    
    # Create a request
    factory = RequestFactory()
    request = factory.get(f'/api/exam-sessions/{exam_session.id}/details/')
    request.user = teacher
    
    # Call the view
    try:
        response = get_exam_session_details(request, exam_session.id)
        print(f"📊 Response status: {response.status_code}")
        if response.status_code == 200:
            data = response.data
            print(f"✅ Exam details loaded successfully!")
            print(f"📋 Title: {data['exam_session']['title']}")
            print(f"📝 Questions found: {len(data['questions'])}")
            print(f"🎯 Total questions expected: {data['exam_session']['total_questions']}")
            
            if len(data['questions']) > 0:
                print(f"📄 First question: {data['questions'][0]['question_text'][:100]}...")
            else:
                print("⚠️ No questions found in exam!")
        else:
            print(f"❌ Error: {response.data}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_exam_details_endpoint()
