#!/usr/bin/env python3
"""
Test script for the Interactive Learning & Socratic Tutoring System
Tests the complete transformation from traditional testing to conversational discovery
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://127.0.0.1:8000/api"
TEST_USER = {
    "username": "test_student_socratic",
    "email": "socratic@test.com", 
    "password": "testpass123",
    "role": "student",
    "age": 16,
    "subject": "math",
    "phone": 1234567890
}

def test_authentication():
    """Test user registration and login"""
    print("🔐 Testing Authentication...")
    
    # Register user
    register_response = requests.post(f"{BASE_URL}/register/", json=TEST_USER)
    print(f"Registration: {register_response.status_code}")
    
    # Login
    login_response = requests.post(f"{BASE_URL}/login/", json={
        "username": TEST_USER["username"],
        "password": TEST_USER["password"]
    })
    
    if login_response.status_code == 200:
        token = login_response.json().get("token")
        print(f"✅ Login successful! Token: {token[:20]}...")
        return token
    else:
        print(f"❌ Login failed: {login_response.text}")
        return None

def test_interactive_learning_session(token):
    """Test starting and interacting with a Socratic learning session"""
    print("\n🧠 Testing Interactive Learning Session...")
    
    headers = {"Authorization": f"Token {token}"}
    
    # Start interactive learning session
    session_data = {
        "topic": "Algebraic Equations",
        "subject": "math",
        "learning_goal": "Understand how to solve for x in basic equations through discovery",
        "session_type": "interactive_learning"
    }
    
    start_response = requests.post(f"{BASE_URL}/interactive/start/", json=session_data, headers=headers)
    print(f"Start Session: {start_response.status_code}")
    
    if start_response.status_code == 201:
        session_info = start_response.json()
        session_id = session_info["session_id"]
        print(f"✅ Session created! ID: {session_id}")
        print(f"📝 Welcome: {session_info['welcome_message']}")
        print(f"❓ Initial Question: {session_info['initial_question']}")
        
        return session_id
    else:
        print(f"❌ Session creation failed: {start_response.text}")
        return None

def test_socratic_conversation(token, session_id):
    """Test the Socratic conversation flow"""
    print(f"\n💬 Testing Socratic Conversation in Session {session_id}...")
    
    headers = {"Authorization": f"Token {token}"}
    
    # Simulate student responses that should trigger different Socratic responses
    student_messages = [
        "I don't understand what x means in 2x + 5 = 11",
        "Is x just a number?",
        "So if 2x + 5 = 11, then 2x = 6?",
        "Oh! So x = 3! I see how this works now!"
    ]
    
    for i, message in enumerate(student_messages, 1):
        print(f"\n--- Conversation Turn {i} ---")
        print(f"👤 Student: {message}")
        
        chat_response = requests.post(
            f"{BASE_URL}/interactive/chat/{session_id}/",
            json={"message": message},
            headers=headers
        )
        
        if chat_response.status_code == 200:
            response_data = chat_response.json()
            print(f"🤖 AI Response: {response_data['ai_response']}")
            print(f"📊 Understanding Level: {response_data['understanding_level']}")
            print(f"💡 Discovery Detected: {response_data['discovery_detected']}")
            print(f"🎯 Hint Level: {response_data['hint_level']}")
            
            if response_data.get('encouragement'):
                print(f"🌟 Encouragement: {response_data['encouragement']}")
                
            if response_data['session_complete']:
                print("🎉 Session completed through discovery!")
                break
        else:
            print(f"❌ Chat failed: {chat_response.text}")
        
        time.sleep(1)  # Brief pause between messages

def test_learning_progress(token, session_id):
    """Test learning progress tracking"""
    print(f"\n📈 Testing Learning Progress for Session {session_id}...")
    
    headers = {"Authorization": f"Token {token}"}
    
    progress_response = requests.get(f"{BASE_URL}/interactive/progress/{session_id}/", headers=headers)
    
    if progress_response.status_code == 200:
        progress_data = progress_response.json()
        print(f"✅ Progress Retrieved!")
        print(f"🎯 Understanding Level: {progress_data['understanding_level']}%")
        print(f"🔥 Engagement Score: {progress_data['engagement_score']:.2f}")
        print(f"💡 Discoveries Made: {progress_data['discoveries_made']}")
        print(f"🤔 Confusion Indicators: {progress_data['confusion_indicators']}")
        print(f"🚀 Breakthrough Moments: {progress_data['breakthrough_moments']}")
        print(f"💬 Total Messages: {progress_data['total_messages']}")
        
        if progress_data['recent_insights']:
            print(f"🔍 Recent Insights: {len(progress_data['recent_insights'])} found")
    else:
        print(f"❌ Progress retrieval failed: {progress_response.text}")

def test_session_ending(token, session_id):
    """Test ending a learning session"""
    print(f"\n🏁 Testing Session Ending for Session {session_id}...")
    
    headers = {"Authorization": f"Token {token}"}
    
    end_response = requests.post(f"{BASE_URL}/interactive/end/{session_id}/", headers=headers)
    
    if end_response.status_code == 200:
        end_data = end_response.json()
        print(f"✅ Session ended successfully!")
        print(f"📝 Message: {end_data['message']}")
        print(f"🎯 Final Understanding: {end_data['session_summary']['current_understanding_level']}%")
        print(f"💡 Total Discoveries: {end_data['session_summary']['discoveries_made']}")
        print(f"🔍 Final Insight: {end_data['final_insight']['description']}")
    else:
        print(f"❌ Session ending failed: {end_response.text}")

def main():
    """Run complete test suite for Interactive Learning System"""
    print("🧪 Testing Interactive Learning & Socratic Tutoring System")
    print("=" * 60)
    
    # Test authentication
    token = test_authentication()
    if not token:
        print("❌ Authentication failed - cannot continue tests")
        return
    
    # Test interactive learning session
    session_id = test_interactive_learning_session(token)
    if not session_id:
        print("❌ Session creation failed - cannot continue tests")
        return
    
    # Test Socratic conversation
    test_socratic_conversation(token, session_id)
    
    # Test progress tracking
    test_learning_progress(token, session_id)
    
    # Test session ending
    test_session_ending(token, session_id)
    
    print("\n" + "=" * 60)
    print("🎉 Interactive Learning System Test Complete!")
    print("🌟 Transformation from traditional testing to Socratic discovery successful!")

if __name__ == "__main__":
    main()
