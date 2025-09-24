"""
בדיקה מקיפה של מערכת הצ'אט - תשובה יחידה עם זיכרון
Comprehensive chat system test - single response with memory
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
from scheduler.models import User, ChatInteraction

def test_complete_chat_system():
    """בדיקה מקיפה של מערכת הצ'אט"""
    print("🎯 בדיקה מקיפה של מערכת הצ'אט...")
    
    client = GeminiClient()
    
    # יצירת משתמש למבחן
    test_user, created = User.objects.get_or_create(
        username='test_complete_system',
        defaults={
            'email': 'complete@example.com',
            'age': 16,
            'role': 'student'
        }
    )
    
    # נקה שיחות קודמות
    ChatInteraction.objects.filter(student=test_user).delete()
    
    print("\n=== תרחיש למידה מלא ===")
    
    # שיחה שלמה עם תלמיד
    learning_conversation = [
        "שלום, אני תלמיד כיתה י' ושמי ליאור",
        "אני מתקשה עם אלגברה, תוכל לעזור לי?",
        "איך פותרים משוואה מהצורה ax + b = c?",
        "תן לי דוגמה עם המשוואה 3x + 5 = 14",
        "מעולה! איך אני יכול לבדוק שהפתרון נכון?",
        "תודה! איך קוראים לי?"  # בדיקת זיכרון
    ]
    
    responses = []
    
    for i, message in enumerate(learning_conversation, 1):
        print(f"\n--- הודעה {i} ---")
        print(f"תלמיד: {message}")
        
        try:
            # קבלת היסטוריית שיחה
            chat_history = list(ChatInteraction.objects.filter(
                student=test_user
            ).order_by('created_at').values_list('question', 'answer'))
            
            response = client.chat_response(
                user_message=message,
                context="",
                chat_history=chat_history
            )
            
            responses.append(response)
            print(f"AI: {response}")
            
            # בדיקות איכות
            issues = []
            
            # בדיקה שאין תשובות כפולות
            duplicate_patterns = [
                "תשובה נוספת:", "אלטרנטיבה:", "אופציה נוספת:",
                "עוד דרך:", "גם כך:", "כמו כן:", "בנוסף:"
            ]
            
            for pattern in duplicate_patterns:
                if pattern in response:
                    issues.append(f"תשובה כפולה: {pattern}")
            
            # בדיקה שהתשובה לא ארוכה מדי
            if len(response) > 1500:
                issues.append(f"תשובה ארוכה ({len(response)} תווים)")
            
            # בדיקה שהתשובה לא קצרה מדי (פחות מ-10 תווים)
            if len(response) < 10:
                issues.append(f"תשובה קצרה מדי ({len(response)} תווים)")
            
            # דיווח על בעיות
            if issues:
                print(f"⚠️ בעיות: {', '.join(issues)}")
            else:
                print("✅ איכות תשובה מעולה!")
            
            # שמירת השיחה
            ChatInteraction.objects.create(
                student=test_user,
                question=message,
                answer=response
            )
            
        except Exception as e:
            print(f"❌ שגיאה: {e}")
            responses.append(f"ERROR: {e}")
    
    print("\n=== סיכום הבדיקה ===")
    
    # בדיקות זיכרון ספציפיות
    memory_tests = [
        {
            "test": "זיכרון שם",
            "expected": "ליאור",
            "found": any("ליאור" in resp.lower() for resp in responses[-2:])
        },
        {
            "test": "זיכרון נושא",
            "expected": "אלגברה",
            "found": any("אלגברה" in resp.lower() for resp in responses)
        }
    ]
    
    print("\nבדיקות זיכרון:")
    for test in memory_tests:
        status = "✅" if test["found"] else "❌"
        print(f"{status} {test['test']}: מחפש '{test['expected']}'")
    
    # סטטיסטיקות
    total_interactions = ChatInteraction.objects.filter(student=test_user).count()
    avg_response_length = sum(len(r) for r in responses if not r.startswith("ERROR")) / len([r for r in responses if not r.startswith("ERROR")])
    
    print(f"\n📊 סטטיסטיקות:")
    print(f"   💬 סה\"כ אינטראקציות: {total_interactions}")
    print(f"   📏 אורך תשובה ממוצע: {avg_response_length:.1f} תווים")
    print(f"   🔬 שיעור הצלחה: {len([r for r in responses if not r.startswith('ERROR')])}/{len(responses)}")
    
    # הערכה כללית
    success_rate = len([r for r in responses if not r.startswith('ERROR')]) / len(responses)
    memory_success = sum(test["found"] for test in memory_tests) / len(memory_tests)
    
    print(f"\n🎯 ציון כולל:")
    print(f"   📡 יציבות API: {success_rate:.1%}")
    print(f"   🧠 זיכרון: {memory_success:.1%}")
    
    if success_rate >= 0.9 and memory_success >= 0.5:
        print("🏆 המערכת עובדת מעולה!")
    elif success_rate >= 0.7:
        print("👍 המערכת עובדת טוב")
    else:
        print("⚠️ המערכת זקוקה לשיפורים")

if __name__ == "__main__":
    test_complete_chat_system()
