#!/usr/bin/env python3
"""
Test script for the new Document-Based Interactive Learning system
Tests document-based questions with 10-question limit and hint system
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from scheduler.models import Document, QuestionBank, ChatSession, User

def test_document_interactive_learning():
    """Test the complete Document-Based Interactive Learning flow"""
    
    print("🧪 Testing Document-Based Interactive Learning System")
    print("=" * 60)
    
    # Check documents and questions
    documents = Document.objects.all().order_by('-created_at')[:3]
    print(f"📚 Available Documents: {documents.count()}")
    
    for doc in documents:
        question_count = QuestionBank.objects.filter(document=doc).count()
        print(f"  - {doc.title}: {question_count} questions")
    
    if not documents.exists():
        print("❌ No documents found! Upload some documents first.")
        return
    
    # Get a test user
    try:
        user = User.objects.get(username='testuser')
    except User.DoesNotExist:
        print("Creating test user...")
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    print(f"👤 Test User: {user.username}")
    
    # Test 1: Starting Interactive Learning Session
    print("\n🎯 Test 1: Starting Document-Based Interactive Learning Session")
    print("-" * 50)
    
    # Simulate the API call to start learning
    from scheduler.views import start_interactive_learning_session
    from rest_framework.test import APIRequestFactory
    from rest_framework.request import Request
    
    factory = APIRequestFactory()
    request = factory.post('/api/interactive/start/')
    request.user = user
    
    response = start_interactive_learning_session(request)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        session_data = response.data
        session_id = session_data.get('session_id')
        print(f"✅ Session Created: {session_id}")
        print(f"📊 Progress: {session_data.get('progress')}")
        print(f"❓ First Question: {session_data.get('first_question', {}).get('question', 'N/A')[:100]}...")
        
        # Test 2: Testing hint system
        print("\n💡 Test 2: Hint System")
        print("-" * 30)
        
        from scheduler.views import interactive_learning_chat
        
        # Test multiple hint requests
        for hint_num in range(1, 4):
            print(f"\n🔍 Testing hint request #{hint_num}...")
            chat_request = factory.post(f'/api/interactive/chat/{session_id}/', {'message': 'hint'})
            chat_request.user = user
            
            hint_response = interactive_learning_chat(chat_request, session_id)
            print(f"Hint Status: {hint_response.status_code}")
            if hint_response.status_code == 200:
                print(f"💡 Hint #{hint_num}: {hint_response.data.get('ai_response', 'N/A')[:150]}...")
                print(f"🎯 Hints Used: {hint_response.data.get('hints_used', 0)}")
                print(f"🔄 Hints Remaining: {hint_response.data.get('hints_remaining', 0)}")
        
        # Test 4th hint (should be rejected)
        print(f"\n🚫 Testing 4th hint request (should be rejected)...")
        chat_request = factory.post(f'/api/interactive/chat/{session_id}/', {'message': 'hint'})
        chat_request.user = user
        
        hint_response = interactive_learning_chat(chat_request, session_id)
        if hint_response.status_code == 200:
            print(f"⚠️ 4th Hint Response: {hint_response.data.get('ai_response', 'N/A')[:100]}...")
        
        # Test 3: Answer submission
        print("\n📝 Test 3: Answer Submission")
        print("-" * 30)
        
        # Test invalid answer
        print("🔍 Testing invalid answer...")
        answer_request = factory.post(f'/api/interactive/chat/{session_id}/', {'message': 'X'})
        answer_request.user = user
        
        answer_response = interactive_learning_chat(answer_request, session_id)
        print(f"Invalid Answer Status: {answer_response.status_code}")
        if answer_response.status_code == 200:
            print(f"⚠️ Invalid Answer Response: {answer_response.data.get('ai_response', 'N/A')[:100]}...")
        
        # Test valid answer
        print("\n📝 Testing valid answer...")
        answer_request = factory.post(f'/api/interactive/chat/{session_id}/', {'message': 'A'})
        answer_request.user = user
        
        answer_response = interactive_learning_chat(answer_request, session_id)
        print(f"Answer Status: {answer_response.status_code}")
        if answer_response.status_code == 200:
            print(f"✅ Answer Response: {answer_response.data.get('ai_response', 'N/A')[:200]}...")
            print(f"🎯 Is Correct: {answer_response.data.get('is_correct', 'N/A')}")
            print(f"📊 Progress: {answer_response.data.get('progress', {})}")
            
            if answer_response.data.get('next_question'):
                print(f"➡️ Next Question: {answer_response.data.get('next_question', {}).get('question', 'N/A')[:100]}...")
        
        # Test 4: Session persistence and metadata
        print("\n💾 Test 4: Session Persistence")
        print("-" * 30)
        
        session = ChatSession.objects.get(id=session_id)
        metadata = session.get_session_metadata()
        print(f"📱 Session ID: {session.id}")
        print(f"🎯 Current Question: {session.current_question_index}/10")
        print(f"📚 Document Based: {metadata.get('is_document_based', False)}")
        print(f"❓ Question IDs: {len(metadata.get('question_ids', []))} questions")
        print(f"💡 Max Hints Per Question: {metadata.get('max_hints_per_question', 3)}")
        print(f"🔢 Hints Used: {metadata.get('hints_used', {})}")
        
        # Test 5: Complete a few more questions
        print("\n🏁 Test 5: Completing More Questions")
        print("-" * 30)
        
        for i in range(2, 5):  # Answer questions 2, 3, 4
            print(f"\nAnswering question {i}...")
            answer_request = factory.post(f'/api/interactive/chat/{session_id}/', {'message': 'B'})
            answer_request.user = user
            
            answer_response = interactive_learning_chat(answer_request, session_id)
            if answer_response.status_code == 200:
                progress = answer_response.data.get('progress', {})
                print(f"📊 Progress: {progress.get('current', 0)}/{progress.get('total', 10)} ({progress.get('percentage', 0)}%)")
                
                if answer_response.data.get('session_completed'):
                    print("🎉 Session completed!")
                    break
        
        print("\n🎉 Document-Based Interactive Learning Test Completed Successfully!")
        
    else:
        print(f"❌ Failed to start session: {response.data}")

if __name__ == "__main__":
    test_document_interactive_learning()
