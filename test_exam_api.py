#!/usr/bin/env python3
import os
import sys
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()

print("🧪 Testing Interactive Exam API")
print("=" * 40)

# Get student user and token
try:
    student = User.objects.get(username='daniel')
    token, created = Token.objects.get_or_create(user=student)
    print(f"✅ Student: {student.username} (role: {student.role})")
    print(f"✅ Token: {token.key[:10]}...")
except User.DoesNotExist:
    print("❌ Student 'daniel' not found")
    sys.exit(1)

# Test the API endpoint
url = "http://127.0.0.1:8000/api/exam/start/"
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Token {token.key}'
}
data = {}

print(f"\n🌐 Testing API: {url}")
print(f"📤 Headers: {headers}")
print(f"📤 Data: {data}")

try:
    response = requests.post(url, headers=headers, json=data, timeout=30)
    print(f"\n📊 Response Status: {response.status_code}")
    print(f"📊 Response Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Success! Response:")
        print(json.dumps(result, indent=2))
    else:
        print(f"❌ Error! Response:")
        print(response.text)
        
except requests.exceptions.RequestException as e:
    print(f"❌ Request failed: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
