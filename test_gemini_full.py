#!/usr/bin/env python
"""
🔍 בדיקה מקיפה של Gemini AI
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from scheduler.gemini_client import gemini_client

print('🔍 בודק מצב Gemini client...')
print(f'API Version: {gemini_client.api_version}')
print(f'Model זמין: {bool(gemini_client.model)}')

print('\n📝 בדיקה 1: יצירת שאלות מתוכן ספציפי...')
sample_content = """
מתמטיקה בסיסית:
- חיבור: 2+2=4, 5+3=8
- כפל: 3×5=15, 4×6=24  
- חלוקה: 10÷2=5, 12÷3=4
- שברים: 1/2 = 0.5
"""

questions = gemini_client.generate_questions(sample_content, num_questions=3)
print(f'נוצרו {len(questions)} שאלות')

for i, q in enumerate(questions, 1):
    print(f'\n📋 שאלה {i}:')
    print(f'   ID: {q.get("id", "N/A")}')
    print(f'   טקסט: {q.get("question_text", "N/A")[:100]}')
    
    # בדיקה אם זה מ-Gemini או fallback
    question_id = str(q.get("id", ""))
    if "gemini" in question_id.lower():
        print(f'   🤖 מקור: Gemini AI')
    elif "fallback" in question_id.lower():
        print(f'   🔧 מקור: Fallback (לא Gemini)')
    else:
        print(f'   ❓ מקור: לא ברור')
    
    # הצגת אפשרויות התשובה
    options = q.get("options", {})
    if options:
        print(f'   אפשרויות: A) {options.get("A", "N/A")[:30]}...')

print('\n💬 בדיקה 2: שיחה בעברית...')
chat_response = gemini_client.chat_response('מה זה 4×3? תסביר לי איך לחשב')
print(f'שאלה: "מה זה 4×3? תסביר לי איך לחשב"')
print(f'תשובה: {chat_response[:200]}{"..." if len(chat_response) > 200 else ""}')

print('\n💬 בדיקה 3: שאלה כללית...')
general_response = gemini_client.chat_response('שלום, איך אתה יכול לעזור לי בלימודים?')
print(f'שאלה: "שלום, איך אתה יכול לעזור לי בלימודים?"')
print(f'תשובה: {general_response[:200]}{"..." if len(general_response) > 200 else ""}')

print('\n🎯 סיכום:')
if gemini_client.api_version == "fallback":
    print('❌ המערכת במצב Fallback - השאלות נוצרות על ידי קוד מוכן מראש')
elif "gemini" in str(questions[0].get("id", "")).lower():
    print('✅ המערכת משתמשת ב-Gemini AI לייצור שאלות!')
else:
    print('❓ לא ברור איך השאלות נוצרות')
