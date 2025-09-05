"""
Quick test script to verify the exam session listing fix
"""
import os
import sys
import django

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from scheduler.models import ExamSession, User

def test_exam_sessions():
    print("🧪 Testing ExamSession listing...")
    
    # Get all users
    teachers = User.objects.filter(role='teacher')
    students = User.objects.filter(role='student')
    
    print(f"👨‍🏫 Teachers: {teachers.count()}")
    print(f"👨‍🎓 Students: {students.count()}")
    
    # Get all exam sessions
    exam_sessions = ExamSession.objects.all()
    print(f"📝 Total ExamSessions: {exam_sessions.count()}")
    
    for session in exam_sessions:
        print(f"  - {session.title} (Published: {session.is_published}, Created by: {session.created_by.username})")
        print(f"    Questions: {session.num_questions}, Topics: {session.selected_topics.count()}")
    
    # Test student view simulation
    published_sessions = ExamSession.objects.filter(is_published=True)
    print(f"📚 Published sessions available to students: {published_sessions.count()}")
    
    for session in published_sessions:
        print(f"  - {session.title} by {session.created_by.username}")

if __name__ == "__main__":
    test_exam_sessions()
