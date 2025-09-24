#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from scheduler.models import User
from scheduler.views import _generate_exam_questions_from_docs

def test_question_generation():
    # Get daniel user  
    daniel = User.objects.get(username='daniel')
    print(f'Testing question generation for: {daniel.username} (role: {daniel.role})')

    # Test the question generation function directly
    result = _generate_exam_questions_from_docs(daniel, 5)
    print(f'Generation result keys: {list(result.keys())}')

    if 'error' in result:
        print(f'Error: {result["error"]}')
    else:
        print(f'Success! Generated {len(result.get("questions", []))} questions')
        print(f'Source documents: {result.get("source_documents", [])}')
        print(f'Generation method: {result.get("generation_method", "unknown")}')
        print(f'Teacher documents used: {result.get("teacher_documents_used", 0)}')
        
        # Show first question as example
        questions = result.get('questions', [])
        if questions:
            first_q = questions[0]
            print(f'\nExample question:')
            print(f'  Text: {first_q.get("question_text", "N/A")}')
            print(f'  Type: {first_q.get("question_type", "N/A")}')  
            print(f'  Answer: {first_q.get("correct_answer", "N/A")}')

if __name__ == '__main__':
    test_question_generation()
