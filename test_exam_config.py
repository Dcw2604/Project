#!/usr/bin/env python
"""
Test script for Task 2.2: Exam Configuration API
Tests the creation and retrieval of exam configurations
"""
import os
import sys
import json
import requests
from datetime import datetime, timedelta

# Add project to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

import django
django.setup()

from scheduler.models import User, ExamSession, QuestionBank, ExamConfig, ExamConfigQuestion

BASE_URL = 'http://localhost:8000/api'

def test_exam_config_creation():
    """Test creating an exam configuration via API"""
    
    print("🧪 Testing Exam Configuration Creation")
    
    # Test data - you may need to adjust IDs based on your database
    payload = {
        "exam_session_id": 7,  # Adjust based on existing exam sessions (test n.1)
        "teacher_id": 4,       # Adjust based on existing teachers (teacher1)
        "assigned_student_id": 1,  # Optional - adjust based on existing students (reut)
        "start_time": (datetime.now() + timedelta(hours=1)).isoformat() + "Z",
        "end_time": (datetime.now() + timedelta(hours=3)).isoformat() + "Z",
        "questions": [
            {"question_id": 136, "order_index": 1},  # Adjust based on existing questions
            {"question_id": 133, "order_index": 2}
        ]
    }
    
    try:
        # Test POST /api/exam-configs/
        print(f"📤 POST {BASE_URL}/exam-configs/")
        print(f"📝 Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(
            f"{BASE_URL}/exam-configs/",
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 201:
            print("✅ Success! Exam configuration created")
            data = response.json()
            print(f"📋 Response: {json.dumps(data, indent=2)}")
            
            config_id = data['id']
            
            # Test retrieval
            print(f"\n🔍 Testing retrieval of config {config_id}")
            get_response = requests.get(f"{BASE_URL}/exam-configs/{config_id}/")
            
            if get_response.status_code == 200:
                print("✅ Successfully retrieved exam configuration")
                get_data = get_response.json()
                print(f"📋 Retrieved data: {json.dumps(get_data, indent=2)}")
            else:
                print(f"❌ Failed to retrieve config: {get_response.status_code}")
                print(get_response.text)
                
            # Test listing all configs
            print("\n🔍 Testing listing all configurations")
            list_response = requests.get(f"{BASE_URL}/exam-configs/")
            if list_response.status_code == 200:
                configs = list_response.json()
                print(f"✅ Successfully retrieved {len(configs)} exam configurations")
                if len(configs) > 0:
                    print(f"📋 First config preview: ID {configs[0]['id']} for session '{configs[0]['exam_session']['title']}'")
                else:
                    print("📋 No configurations found")
            else:
                print(f"❌ Failed to list configs: {list_response.status_code}")
                print(list_response.text)
                
        else:
            print(f"❌ Failed to create exam configuration")
            print(f"📝 Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Django server. Is it running on localhost:8000?")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_validation_errors():
    """Test validation scenarios"""
    
    print("\n🧪 Testing Validation Errors")
    
    # Test missing required fields
    invalid_payloads = [
        {
            "description": "Missing exam_session_id",
            "payload": {
                "teacher_id": 1,
                "questions": [{"question_id": 126, "order_index": 1}]
            }
        },
        {
            "description": "Missing teacher_id", 
            "payload": {
                "exam_session_id": 1,
                "questions": [{"question_id": 126, "order_index": 1}]
            }
        },
        {
            "description": "Empty questions list",
            "payload": {
                "exam_session_id": 1,
                "teacher_id": 1,
                "questions": []
            }
        },
        {
            "description": "Invalid order indices",
            "payload": {
                "exam_session_id": 1,
                "teacher_id": 1,
                "questions": [
                    {"question_id": 126, "order_index": 1},
                    {"question_id": 133, "order_index": 3}  # Missing order_index 2
                ]
            }
        },
        {
            "description": "End time before start time",
            "payload": {
                "exam_session_id": 1,
                "teacher_id": 1,
                "start_time": (datetime.now() + timedelta(hours=3)).isoformat() + "Z",
                "end_time": (datetime.now() + timedelta(hours=1)).isoformat() + "Z",
                "questions": [{"question_id": 126, "order_index": 1}]
            }
        }
    ]
    
    for test_case in invalid_payloads:
        print(f"\n🔍 Testing: {test_case['description']}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/exam-configs/",
                json=test_case['payload'],
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 400:
                print("✅ Correctly returned 400 Bad Request")
                data = response.json()
                print(f"📝 Validation errors: {json.dumps(data.get('errors', {}), indent=2)}")
            else:
                print(f"❌ Expected 400, got {response.status_code}")
                print(response.text)
                
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to Django server.")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def check_database_state():
    """Check the current state of the database"""
    
    print("\n📊 Database State Check")
    
    # Check existing data
    exam_sessions = ExamSession.objects.count()
    teachers = User.objects.filter(role='teacher').count()
    students = User.objects.filter(role='student').count()
    questions = QuestionBank.objects.count()
    configs = ExamConfig.objects.count()
    
    print(f"📝 Exam Sessions: {exam_sessions}")
    print(f"👨‍🏫 Teachers: {teachers}")
    print(f"👨‍🎓 Students: {students}")
    print(f"❓ Questions: {questions}")
    print(f"⚙️  Exam Configs: {configs}")
    
    if exam_sessions > 0:
        session = ExamSession.objects.first()
        print(f"📋 Sample Exam Session: {session.id} - {session.title}")
    
    if teachers > 0:
        teacher = User.objects.filter(role='teacher').first()
        print(f"👨‍🏫 Sample Teacher: {teacher.id} - {teacher.username}")
    
    if students > 0:
        student = User.objects.filter(role='student').first()
        print(f"👨‍🎓 Sample Student: {student.id} - {student.username}")
    
    if questions > 0:
        question = QuestionBank.objects.first()
        print(f"❓ Sample Question: {question.id} - {question.question_text[:50]}...")

if __name__ == "__main__":
    print("🚀 Starting Exam Configuration API Tests")
    
    # Check database state first
    check_database_state()
    
    # Run tests
    test_exam_config_creation()
    test_validation_errors()
    
    print("\n✅ Tests completed!")
