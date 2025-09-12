#!/usr/bin/env python
import requests
import json

def test_interactive_exam():
    # First, login to get a token
    login_data = {
        'username': 'daniel', 
        'password': 'newpassword123'
    }
    
    try:
        # Login
        login_response = requests.post('http://localhost:8000/api/login/', json=login_data)
        print(f"Login status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            token = login_response.json()['token']
            print(f"Login successful! Token: {token[:20]}...")
            
            # Now test the interactive exam start
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Token {token}'
            }
            
            exam_response = requests.post('http://localhost:8000/api/exam/start/', 
                                        json={}, 
                                        headers=headers)
            
            print(f"\nExam start status: {exam_response.status_code}")
            print(f"Response: {json.dumps(exam_response.json(), indent=2)}")
            
        else:
            print(f"Login failed: {login_response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    test_interactive_exam()
