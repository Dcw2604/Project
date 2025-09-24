#!/usr/bin/env python3
"""
Quick test for the enhanced Interactive Learning system with better progression
"""

import requests
import json

# Configuration
BASE_URL = "http://127.0.0.1:8000/api"

def test_enhanced_algebra_flow():
    """Test the enhanced algebra learning flow"""
    print("🧪 Testing Enhanced Algebra Learning Flow")
    print("=" * 50)
    
    # Login with existing user
    login_response = requests.post(f"{BASE_URL}/login/", json={
        "username": "test_student_socratic",
        "password": "testpass123"
    })
    
    if login_response.status_code != 200:
        print("❌ Login failed")
        return
        
    token = login_response.json().get("token")
    headers = {"Authorization": f"Token {token}"}
    
    # Start algebra session
    session_response = requests.post(f"{BASE_URL}/interactive/start/", json={
        "topic": "Algebraic Equations",
        "subject": "math",
        "learning_goal": "Understand solving for x through discovery",
        "session_type": "interactive_learning"
    }, headers=headers)
    
    if session_response.status_code != 201:
        print("❌ Session creation failed")
        return
        
    session_data = session_response.json()
    session_id = session_data["session_id"]
    
    print(f"✅ Session created! ID: {session_id}")
    print(f"📝 Initial Question: {session_data['initial_question']}")
    
    # Simulate realistic algebra learning conversation
    algebra_conversation = [
        "I think x is like a mystery number",
        "Maybe we subtract 5 from both sides?",
        "So we get 2x = 6",
        "If we divide both sides by 2, we get x = 3!",
        "Let me check: 2(3) + 5 = 6 + 5 = 11. Yes, it works!"
    ]
    
    for i, message in enumerate(algebra_conversation, 1):
        print(f"\n--- Turn {i} ---")
        print(f"👤 Student: {message}")
        
        chat_response = requests.post(
            f"{BASE_URL}/interactive/chat/{session_id}/",
            json={"message": message},
            headers=headers
        )
        
        if chat_response.status_code == 200:
            data = chat_response.json()
            print(f"🤖 AI: {data['ai_response']}")
            print(f"📊 Understanding: {data['understanding_level']}")
            print(f"💡 Discovery: {data['discovery_detected']}")
            
            if data.get('next_question'):
                print(f"➡️ Next Challenge: {data['next_question']}")
                
            if data['session_complete']:
                print("🎉 Session completed through mastery!")
                break
        else:
            print(f"❌ Chat failed: {chat_response.text}")
    
    print("\n" + "=" * 50)
    print("🌟 Enhanced algebra learning flow test complete!")

if __name__ == "__main__":
    test_enhanced_algebra_flow()
