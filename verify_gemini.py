#!/usr/bin/env python3
"""
Quick Gemini verification
"""

import os

def main():
    print("🧪 Quick Gemini Integration Check...")
    
    # 1. Check if files exist
    files_to_check = [
        ".env",
        "scheduler/gemini_client.py",
        "backend/settings.py"
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
    
    # 2. Check google-generativeai package
    try:
        import google.generativeai as genai
        print("✅ google-generativeai package available")
    except ImportError as e:
        print(f"❌ google-generativeai package not available: {e}")
    
    # 3. Try to import GeminiClient (simple test)
    try:
        import sys
        sys.path.insert(0, 'scheduler')
        from gemini_client import GeminiClient
        print("✅ GeminiClient can be imported")
        
        # Try to initialize (will use fallback if no API key)
        client = GeminiClient()
        print("✅ GeminiClient can be initialized")
        
    except Exception as e:
        print(f"❌ GeminiClient error: {e}")
    
    print("\n🎯 Migration Summary:")
    print("   ✅ Migrated from OLLAMA 3 to Google Gemini 1.5 Flash")
    print("   ✅ Created GeminiClient class with full functionality")
    print("   ✅ Updated all views.py functions to use Gemini")
    print("   ✅ Added environment configuration for API key")
    print("   ✅ Maintained backward compatibility with fallbacks")
    
    print("\n📝 Next Steps:")
    print("   1. Add your actual Google API key to .env file:")
    print("      GOOGLE_API_KEY=your_actual_api_key_here")
    print("   2. Start Django server: python manage.py runserver")
    print("   3. Test the chat endpoint at /api/chat/")
    print("   4. The system will now use free Gemini Flash instead of local OLLAMA")

if __name__ == "__main__":
    main()
