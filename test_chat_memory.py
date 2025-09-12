"""
בדיקה שהצ'אט זוכר שיחות קודמות
Testing chat memory functionality
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

def test_conversation_memory():
    """בדיקה שהצ'אט זוכר שיחות קודמות"""
    print("🧠 בודק זיכרון שיחה...")
    
    client = GeminiClient()
    
    # יצירת משתמש למבחן
    test_user, created = User.objects.get_or_create(
        username='test_memory_user',
        defaults={
            'email': 'memory@example.com',
            'age': 17,
            'role': 'student'
        }
    )
    
    # נקה שיחות קודמות
    ChatInteraction.objects.filter(student=test_user).delete()
    
    print("\n=== בדיקת רצף שיחה ===")
    
    # שיחה מדורגת
    conversation_steps = [
        {
            "message": "קוראים לי דני ואני לומד במתמטיקה",
            "expected_memory": None  # הודעה ראשונה
        },
        {
            "message": "איך אתה קורא לי?",
            "expected_memory": "דני"  # צריך לזכור את השם
        },
        {
            "message": "באיזה נושא אני לומד?",
            "expected_memory": "מתמטיקה"  # צריך לזכור את הנושא
        }
    ]
    
    for i, step in enumerate(conversation_steps, 1):
        print(f"\n--- שלב {i} ---")
        print(f"שאלה: {step['message']}")
        
        try:
            # קבלת היסטוריית שיחה
            chat_history = list(ChatInteraction.objects.filter(
                student=test_user
            ).order_by('created_at').values_list('question', 'answer'))
            
            print(f"היסטוריה: {len(chat_history)} הודעות קודמות")
            
            response = client.chat_response(
                user_message=step['message'],
                context="",
                chat_history=chat_history
            )
            
            print(f"תשובה: {response}")
            
            # שמירת השיחה
            ChatInteraction.objects.create(
                student=test_user,
                question=step['message'],
                answer=response
            )
            
            # בדיקת זיכרון
            if step['expected_memory']:
                if step['expected_memory'].lower() in response.lower():
                    print(f"✅ זוכר את '{step['expected_memory']}'!")
                else:
                    print(f"⚠️ לא זוכר את '{step['expected_memory']}'")
            else:
                print("✅ הודעה ראשונה נשמרה")
                
        except Exception as e:
            print(f"❌ שגיאה: {e}")
    
    # סיכום
    final_count = ChatInteraction.objects.filter(student=test_user).count()
    print(f"\n📊 סה\"כ {final_count} אינטראקציות נשמרו")
    
    # בדיקה נוספת - שאלה על כל השיחה
    print("\n=== בדיקת זיכרון כללי ===")
    try:
        chat_history = list(ChatInteraction.objects.filter(
            student=test_user
        ).order_by('created_at').values_list('question', 'answer'))
        
        final_response = client.chat_response(
            user_message="תזכיר לי איך קוראים לי ומה אני לומד",
            context="",
            chat_history=chat_history
        )
        
        print(f"תשובה סופית: {final_response}")
        
        # בדיקות זיכרון
        remembers_name = "דני" in final_response
        remembers_subject = "מתמטיקה" in final_response
        
        print(f"זוכר שם: {'✅' if remembers_name else '❌'}")
        print(f"זוכר נושא: {'✅' if remembers_subject else '❌'}")
        
    except Exception as e:
        print(f"❌ שגיאה בבדיקה סופית: {e}")

if __name__ == "__main__":
    test_conversation_memory()
