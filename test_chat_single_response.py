"""
בדיקה שהצ'אט מחזיר תשובה אחת בלבד
Testing that chat returns only single response
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

def test_single_response():
    """בדיקה שהצ'אט מחזיר תשובה אחת"""
    print("🔍 בודק תשובה יחידה מהצ'אט...")
    
    client = GeminiClient()
    
    # יצירת משתמש למבחן
    test_user, created = User.objects.get_or_create(
        username='test_single_response',
        defaults={
            'email': 'test@example.com',
            'age': 16,
            'role': 'student'
        }
    )
    
    # בדיקה עם שאלה פשוטה
    test_questions = [
        "מה זה שטח?",
        "איך מחשבים היקף ריבוע?",
        "תן לי דוגמה לפתרון משוואה ליניארית"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n--- בדיקה {i} ---")
        print(f"שאלה: {question}")
        
        try:
            response = client.chat_response(
                user_message=question,
                context="",
                chat_history=[]
            )
            
            print(f"תשובה: {response[:200]}...")
            
            # בדיקה שאין מספר תשובות
            duplicate_patterns = [
                "תשובה נוספת:",
                "אלטרנטיבה:",
                "אופציה נוספת:",
                "עוד דרך:",
                "גם כך:",
                "כמו כן:"
            ]
            
            found_duplicates = []
            for pattern in duplicate_patterns:
                if pattern in response:
                    found_duplicates.append(pattern)
            
            if found_duplicates:
                print(f"⚠️ נמצאו דפוסי תשובות כפולות: {found_duplicates}")
            else:
                print("✅ תשובה יחידה!")
                
            # בדיקה שהתשובה לא ארוכה מדי
            if len(response) > 2000:
                print(f"⚠️ תשובה ארוכה ({len(response)} תווים)")
            else:
                print(f"✅ אורך תשובה סביר ({len(response)} תווים)")
                
        except Exception as e:
            print(f"❌ שגיאה: {e}")
    
    # ספירת אינטראקציות
    interactions_count = ChatInteraction.objects.filter(student=test_user).count()
    print(f"\n📊 נוצרו {interactions_count} אינטראקציות")

if __name__ == "__main__":
    test_single_response()
