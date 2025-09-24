#!/usr/bin/env python3
"""
Test Ollama connectivity and response time
"""
import requests
import time

def test_ollama_connection():
    """Test if Ollama is working properly"""
    print("🔍 Testing Ollama Connection...")
    
    try:
        start_time = time.time()
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2",
                "prompt": "Just say 'Hello' in one word.",
                "stream": False
            },
            timeout=30
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        print(f"⏱️ Response time: {response_time:.2f} seconds")
        
        if response.status_code == 200:
            data = response.json()
            ollama_response = data.get('response', '').strip()
            print(f"✅ Ollama Response: '{ollama_response}'")
            print(f"📊 Status: Working properly")
            return True
        else:
            print(f"❌ Ollama returned status code: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Ollama timeout - taking too long to respond")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama - server not running?")
        return False
    except Exception as e:
        print(f"❌ Ollama error: {e}")
        return False

def test_hint_generation():
    """Test hint generation like in the real system"""
    print("\n💡 Testing Hint Generation...")
    
    try:
        prompt = """Provide a gentle hint for this question without giving away the answer:

Question: What is 2 + 2?

Options:
A) 3
B) 4  
C) 5
D) 6

Correct answer: B

Provide a subtle hint that guides thinking but doesn't reveal the answer. Keep it brief and encouraging."""

        start_time = time.time()
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2",
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        print(f"⏱️ Hint generation time: {response_time:.2f} seconds")
        
        if response.status_code == 200:
            data = response.json()
            hint = data.get('response', '').strip()
            print(f"💡 Generated Hint: {hint[:200]}...")
            print(f"✅ Hint generation: Working")
            return True
        else:
            print(f"❌ Hint generation failed with status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Hint generation error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Ollama Testing Suite")
    print("=" * 40)
    
    # Test basic connection
    basic_test = test_ollama_connection()
    
    # Test hint generation
    hint_test = test_hint_generation()
    
    print("\n📋 Summary:")
    print(f"  Basic Connection: {'✅ Pass' if basic_test else '❌ Fail'}")
    print(f"  Hint Generation: {'✅ Pass' if hint_test else '❌ Fail'}")
    
    if basic_test and hint_test:
        print("\n🎉 Ollama is ready for Interactive Learning!")
    else:
        print("\n⚠️ Ollama needs attention before using hints.")
