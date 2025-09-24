#!/usr/bin/env python
"""
בדיקה מהירה של יצירת שאלות עם ה-API key החדש
"""
import os
import sys
import django

# Setup Django
sys.path.append('c:/myDesktop1/final_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

print("🔍 בודק יצירת שאלות עם Gemini API...")

try:
    from scheduler.gemini_client import gemini_client
    
    print(f"📊 מצב Gemini: {gemini_client.api_version}")
    print(f"📊 Model זמין: {bool(gemini_client.model)}")
    
    # בדיקת יצירת שאלות
    sample_content = """
    מתמטיקה בסיסית:
    חיבור: 2 + 3 = 5
    חילוק: 10 ÷ 2 = 5
    כפל: 4 × 5 = 20
    חיסור: 8 - 3 = 5
    """
    
    print("\n📝 מנסה ליצור שאלות...")
    questions = gemini_client.generate_questions(sample_content, num_questions=2)
    
    print(f"✅ נוצרו {len(questions)} שאלות")
    
    for i, q in enumerate(questions, 1):
        print(f"\n📝 שאלה {i}:")
        print(f"   ID: {q.get('id', 'N/A')}")
        print(f"   טקסט: {q.get('question_text', 'N/A')[:60]}...")
        
        # בדיקה אם זה מ-Gemini או fallback
        if 'gemini' in str(q.get('id', '')).lower():
            print(f"   🤖 מקור: Gemini AI ✅")
        elif 'fallback' in str(q.get('id', '')).lower():
            print(f"   🔧 מקור: Fallback")
        else:
            print(f"   ❓ מקור: לא ברור")

except Exception as e:
    print(f"❌ שגיאה: {e}")

print("\n🎯 סיכום:")
print("אם את רואה 'מקור: Gemini AI' - השאלות נוצרות על ידי Gemini!")
print("אם את רואה 'מקור: Fallback' - השאלות נוצרות על ידי קוד מוכן מראש")
