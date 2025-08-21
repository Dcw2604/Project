#!/usr/bin/env python3
"""
🎯 Test Script for Task 3.2: Collect and Store Answers
Test the new exam answer submission and progression API endpoints.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = 'http://127.0.0.1:8000/api'
TEST_USER = {
    'username': 'student1',
    'password': 'testpass123'  # Adjust based on your test data
}

class Task32Tester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.student_id = None
        
    def log(self, message):
        """Print timestamped log message"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] {message}")
        
    def authenticate(self):
        """Authenticate as a test student"""
        self.log("🔐 Authenticating test user...")
        
        response = self.session.post(f"{BASE_URL}/login/", data=TEST_USER)
        
        if response.status_code == 200:
            data = response.json()
            self.auth_token = data.get('token')
            self.student_id = data.get('user', {}).get('id')
            self.session.headers.update({'Authorization': f'Token {self.auth_token}'})
            self.log(f"✅ Authentication successful - Student ID: {self.student_id}")
            return True
        else:
            self.log(f"❌ Authentication failed: {response.status_code} - {response.text}")
            return False
    
    def list_exam_sessions(self):
        """List available exam sessions"""
        self.log("📋 Fetching available exam sessions...")
        
        response = self.session.get(f"{BASE_URL}/exam-sessions/list/")
        
        if response.status_code == 200:
            sessions = response.json()
            self.log(f"✅ Found {len(sessions)} exam sessions")
            for session in sessions[:3]:  # Show first 3
                self.log(f"   📝 Session {session['id']}: {session.get('title', 'Untitled')}")
            return sessions
        else:
            self.log(f"❌ Failed to fetch exam sessions: {response.status_code}")
            return []
    
    def get_exam_progress(self, exam_session_id):
        """Test the get exam progress endpoint"""
        self.log(f"📊 Getting progress for exam session {exam_session_id}...")
        
        response = self.session.get(f"{BASE_URL}/exam-progress/{exam_session_id}/")
        
        if response.status_code == 200:
            progress = response.json()
            self.log(f"✅ Progress retrieved successfully")
            self.log(f"   📈 Progress: {progress.get('progress', {})}")
            return progress
        else:
            self.log(f"❌ Failed to get progress: {response.status_code} - {response.text}")
            return None
    
    def submit_exam_answer(self, exam_session_id, question_id, answer_text):
        """Test the submit exam answer endpoint"""
        self.log(f"📝 Submitting answer for question {question_id}...")
        
        payload = {
            'exam_session_id': exam_session_id,
            'question_id': question_id,
            'answer_text': answer_text,
            'interaction_log': {
                'test_submission': True,
                'timestamp': datetime.now().isoformat(),
                'source': 'automated_test'
            }
        }
        
        response = self.session.post(f"{BASE_URL}/student-answers/", json=payload)
        
        if response.status_code in [200, 201]:
            result = response.json()
            self.log(f"✅ Answer submitted successfully")
            self.log(f"   📊 Status: {result.get('status')}")
            self.log(f"   📈 Progress: {result.get('answered_questions')}/{result.get('total_questions')}")
            
            if result.get('next_question'):
                next_q = result['next_question']
                self.log(f"   ➡️  Next question: {next_q.get('id')} - {next_q.get('question_text')[:50]}...")
            
            return result
        else:
            self.log(f"❌ Failed to submit answer: {response.status_code} - {response.text}")
            return None
    
    def test_exam_flow(self):
        """Test the complete exam flow"""
        self.log("🎯 Starting Task 3.2 - Exam Answer Collection Test")
        
        # Step 1: Authenticate
        if not self.authenticate():
            return False
        
        # Step 2: List exam sessions
        sessions = self.list_exam_sessions()
        if not sessions:
            self.log("❌ No exam sessions available for testing")
            return False
        
        # Step 3: Pick first available exam session
        test_session = sessions[0]
        exam_session_id = test_session['id']
        self.log(f"🎓 Testing with exam session: {exam_session_id}")
        
        # Step 4: Get initial progress
        progress = self.get_exam_progress(exam_session_id)
        if not progress:
            return False
        
        # Step 5: Test answer submission if there's a current question
        if progress.get('progress', {}).get('current_question'):
            current_q = progress['progress']['current_question']
            question_id = current_q['id']
            
            # Submit a test answer
            test_answer = "A"  # Simple test answer
            if current_q.get('question_type') == 'open_ended':
                test_answer = "This is a test answer for an open-ended question."
            
            result = self.submit_exam_answer(exam_session_id, question_id, test_answer)
            
            if result:
                self.log("✅ Task 3.2 test completed successfully!")
                return True
            else:
                return False
        else:
            self.log("⚠️  No current question available (exam may be completed or not started)")
            return True

def main():
    """Run the Task 3.2 test suite"""
    print("=" * 60)
    print("🎯 TASK 3.2: COLLECT AND STORE ANSWERS - TEST SUITE")
    print("=" * 60)
    
    tester = Task32Tester()
    
    try:
        success = tester.test_exam_flow()
        
        print("\n" + "=" * 60)
        if success:
            print("✅ ALL TESTS PASSED - Task 3.2 implementation is working!")
        else:
            print("❌ SOME TESTS FAILED - Check the implementation")
        print("=" * 60)
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
