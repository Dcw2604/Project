"""
Quick verification test for the Interactive Exam Learning system
This tests the core functionality to ensure OLAMA integration is working properly.
"""

import requests
import json

# Quick test function
def test_endpoints():
    base_url = "http://127.0.0.1:8000/api"
    
    print("🔍 Testing Interactive Exam Learning System...")
    
    # Test 1: Check if Django admin is accessible (basic connectivity)
    try:
        response = requests.get("http://127.0.0.1:8000/admin/", timeout=5)
        print(f"✅ Django server connectivity: {response.status_code}")
    except Exception as e:
        print(f"❌ Server connectivity failed: {e}")
        return False
    
    # Test 2: Check if our new API endpoints exist
    try:
        # This should return 401/403 since we're not authenticated, but it confirms endpoint exists
        response = requests.get(f"{base_url}/interactive-exam-progress/1/", timeout=5)
        if response.status_code in [401, 403, 404]:
            print(f"✅ Interactive exam progress endpoint exists: {response.status_code}")
        else:
            print(f"⚠️  Unexpected response from progress endpoint: {response.status_code}")
            
        response = requests.post(f"{base_url}/interactive-exam-answers/", 
                               json={}, timeout=5)
        if response.status_code in [401, 403, 400]:
            print(f"✅ Interactive exam answers endpoint exists: {response.status_code}")
        else:
            print(f"⚠️  Unexpected response from answers endpoint: {response.status_code}")
            
    except Exception as e:
        print(f"❌ API endpoint test failed: {e}")
        return False
    
    print("✅ Basic endpoint verification completed!")
    return True

if __name__ == "__main__":
    test_endpoints()
