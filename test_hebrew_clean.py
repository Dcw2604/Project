"""
בדיקה שהצ'אט מחזיר תשובות בעברית נקייה בלי ערבוב שפות
Testing that chat returns clean Hebrew responses without language mixing
"""
import os
import sys
import django

# הוספת נתיב הפרויקט
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# הגדרת Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from scheduler.gemini_client import GeminiClient

def test_hebrew_responses():
    """בדיקה שהתשובות בעברית נקייה"""
    print("🔤 בדיקת תשובות עברית נקייה...")
    
    client = GeminiClient()
    
    # שאלות שבדרך כלל גורמות לערבוב שפות
    test_questions = [
        "איך פותרים משוואה ליניארית?",
        "מה ההבדל בין חיבור לכפל?", 
        "תן לי דוגמה למשוואה ופתרון שלה",
        "איך מחשבים שטח מלבן?",
        "מה זה פונקציה במתמטיקה?"
    ]
    
    # מילים באנגלית שלא צריכות להופיע
    english_words = [
        'answer', 'solution', 'step', 'example', 'equation', 
        'algebra', 'math', 'calculation', 'result', 'problem',
        'formula', 'let', 'so', 'therefore', 'because', 'where', 'then'
    ]
    
    results = []
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n--- בדיקה {i} ---")
        print(f"שאלה: {question}")
        
        try:
            response = client.chat_response(
                user_message=question,
                context="",
                chat_history=[]
            )
            
            print(f"תשובה: {response}")
            
            # בדיקת ערבוב שפות
            issues = []
            
            # חיפוש מילים באנגלית
            found_english = []
            for word in english_words:
                if word.lower() in response.lower():
                    found_english.append(word)
            
            if found_english:
                issues.append(f"מילים באנגלית: {found_english}")
            
            # בדיקת כותרות מיותרות
            if any(prefix in response for prefix in ['תשובה:', 'Answer:', 'פתרון:', 'Solution:']):
                issues.append("כותרות מיותרות")
            
            # בדיקת טקסט מעורב (לטינית + עברית באותה מילה)
            import re
            mixed_words = re.findall(r'[a-zA-Z]+[א-ת]+|[א-ת]+[a-zA-Z]+', response)
            if mixed_words:
                issues.append(f"מילים מעורבות: {mixed_words}")
            
            # דיווח על בעיות
            if issues:
                print(f"⚠️ בעיות שפה: {', '.join(issues)}")
                results.append({'question': question, 'clean': False, 'issues': issues})
            else:
                print("✅ עברית נקייה!")
                results.append({'question': question, 'clean': True, 'issues': []})
                
        except Exception as e:
            print(f"❌ שגיאה: {e}")
            results.append({'question': question, 'clean': False, 'issues': [f'שגיאה: {e}']})
    
    # סיכום
    print("\n=== סיכום בדיקת שפה ===")
    clean_responses = len([r for r in results if r['clean']])
    total_responses = len(results)
    
    print(f"📊 תשובות נקיות: {clean_responses}/{total_responses}")
    print(f"🎯 אחוז הצלחה: {clean_responses/total_responses:.1%}")
    
    # פירוט בעיות
    problematic = [r for r in results if not r['clean']]
    if problematic:
        print("\n🔍 בעיות שנמצאו:")
        for result in problematic:
            print(f"   • {result['question'][:50]}... - {', '.join(result['issues'])}")
    else:
        print("🏆 כל התשובות בעברית נקייה!")
        
    return clean_responses == total_responses

if __name__ == "__main__":
    success = test_hebrew_responses()
    print(f"\n{'✅ המערכת עוברת בדיקת עברית!' if success else '⚠️ יש לשפר את העברית'}")
