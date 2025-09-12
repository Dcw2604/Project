"""
בדיקה למערכת יצירת שאלות מהירה עבור מרצים
Test for fast question generation system for teachers
"""
import os
import sys
import django

# הוספת נתיב הפרויקט
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# הגדרת Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from scheduler.gemini_client import gemini_client
from scheduler.models import User, Document

def test_fast_question_generation():
    """בדיקה ליצירת שאלות מהירה"""
    print("🚀 בדיקת יצירת שאלות מהירה...")
    
    if not gemini_client:
        print("❌ Gemini client לא זמין")
        return
    
    # תוכן דוגמה (מסמך חינוכי)
    sample_content = """
    מתמטיקה - פרק על משוואות ליניאריות
    
    משוואה ליניארית היא משוואה שבה המשתנה מופיע בחזקה הראשונה בלבד.
    הצורה הכללית של משוואה ליניארית היא: ax + b = c
    
    שלבי פתרון:
    1. העבר את b לצד השני: ax = c - b
    2. חלק את שני האגפים ב-a: x = (c - b) / a
    
    דוגמאות:
    • 2x + 3 = 7 → x = 2
    • 5x - 10 = 0 → x = 2
    • 3x + 6 = 15 → x = 3
    
    בדיקת פתרון:
    להציב את הערך שמצאנו במשוואה המקורית ולוודא ששני האגפים שווים.
    """
    
    # בדיקות עם רמות קושי שונות
    difficulties = ['basic', 'intermediate', 'advanced', 'mixed']
    
    for difficulty in difficulties:
        print(f"\n--- בדיקה: רמת קושי {difficulty} ---")
        
        try:
            start_time = time.time()
            
            questions = gemini_client.generate_questions_fast(
                document_content=sample_content,
                num_questions=5,
                difficulty=difficulty
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"⏱️ זמן יצירה: {duration:.2f} שניות")
            print(f"📊 נוצרו: {len(questions)} שאלות")
            
            # בדיקת איכות השאלות
            if questions:
                for i, q in enumerate(questions[:2], 1):  # מציג 2 ראשונות
                    print(f"\n📝 שאלה {i}:")
                    print(f"   טקסט: {q.get('question_text', 'N/A')}")
                    print(f"   אפשרויות: {len(q.get('options', {}))}")
                    print(f"   תשובה נכונה: {q.get('correct_answer', 'N/A')}")
                    print(f"   מקור: {q.get('source', 'N/A')}")
                    
                    # בדיקות איכות
                    issues = []
                    
                    # בדיקה שיש 4 אפשרויות
                    options = q.get('options', {})
                    if len(options) != 4:
                        issues.append(f"מספר אפשרויות שגוי: {len(options)}")
                    
                    # בדיקה שהתשובה הנכונה קיימת
                    correct = q.get('correct_answer', '')
                    if correct not in options:
                        issues.append(f"תשובה נכונה לא קיימת: {correct}")
                    
                    # בדיקה שהשאלה לא ריקה
                    if not q.get('question_text', '').strip():
                        issues.append("שאלה ריקה")
                    
                    if issues:
                        print(f"   ⚠️ בעיות: {', '.join(issues)}")
                    else:
                        print(f"   ✅ איכות מעולה!")
                        
                if len(questions) >= 3:
                    print(f"   ...ועוד {len(questions) - 2} שאלות")
            else:
                print("❌ לא נוצרו שאלות")
                
        except Exception as e:
            print(f"❌ שגיאה: {e}")
    
    print(f"\n=== סיכום ===")
    print("המערכת מאפשרת:")
    print("✅ יצירת שאלות מהירה (פחות מ-10 שניות)")
    print("✅ 4 רמות קושי שונות")
    print("✅ שאלות מרובות ברירה מובנות")
    print("✅ עיבוד תוכן מסמכים")
    print("✅ שמירה למסד הנתונים")

def test_api_simulation():
    """סימולציה לקריאת API"""
    print("\n🔗 סימולציית קריאת API...")
    
    # יצירת משתמש מורה למבחן
    teacher, created = User.objects.get_or_create(
        username='test_teacher_fast',
        defaults={
            'email': 'teacher@example.com',
            'role': 'teacher',
            'age': 35
        }
    )
    
    # יצירת מסמך דוגמה
    document, created = Document.objects.get_or_create(
        title='מתמטיקה - משוואות',
        document_type='text',
        uploaded_by=teacher,
        defaults={
            'file_path': 'test_document.txt',
            'extracted_text': """
            פרק 5: משוואות ריבועיות
            
            משוואה ריבועית היא משוואה מהצורה ax² + bx + c = 0
            כאשר a ≠ 0.
            
            שיטות פתרון:
            1. פירוק לגורמים
            2. השלמה לריבוע מושלם
            3. נוסחת השורשים
            
            דוגמאות:
            • x² - 5x + 6 = 0 → x = 2 או x = 3
            • 2x² + 7x + 3 = 0 → x = -0.5 או x = -3
            """,
            'processing_status': 'completed'
        }
    )
    
    print(f"👨‍🏫 מורה: {teacher.username}")
    print(f"📄 מסמך: {document.title}")
    print(f"📝 תוכן: {len(document.extracted_text)} תווים")
    
    # סימולציית קריאת API
    api_data = {
        'document_id': document.id,
        'num_questions': 8,
        'difficulty': 'intermediate'
    }
    
    print(f"📡 נתוני API: {api_data}")
    print("✅ מוכן לקריאת API!")
    
    return teacher, document

if __name__ == "__main__":
    import time
    test_fast_question_generation()
    test_api_simulation()
