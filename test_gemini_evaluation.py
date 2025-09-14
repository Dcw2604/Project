#!/usr/bin/env python3
"""
Test script to verify Gemini evaluation system works
"""

import os
import sys
import django

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from scheduler.models import InteractiveExamQuestion
from scheduler.interactive_exam_views import evaluate_answer_with_gemini

def test_gemini_evaluation():
    """Test the Gemini evaluation system"""
    print("🧪 Testing Gemini Evaluation System...")
    
    # Create a mock question
    class MockQuestion:
        def __init__(self):
            self.question_text = "מה זה סוכן (agent) במערכות מידע?"
            self.correct_answer = "סוכן הוא מערכת אוטונומית שמסוגלת לבצע משימות בשם המשתמש עם מידה גבוהה של עצמאות"
            self.id = 1
    
    question = MockQuestion()
    
    # Test cases
    test_cases = [
        {
            "answer": "סוכן הוא מערכת אוטונומית שמסוגלת לבצע משימות בשם המשתמש עם מידה גבוהה של עצמאות",
            "expected": "correct"
        },
        {
            "answer": "סוכן הוא מערכת שמבצעת משימות אוטומטיות",
            "expected": "partial"
        },
        {
            "answer": "סוכן זה משהו שמעקב אחרי דברים",
            "expected": "incorrect"
        },
        {
            "answer": "מערכת אוטונומית עם עצמאות",
            "expected": "partial"
        }
    ]
    
    print(f"📝 Question: {question.question_text}")
    print(f"✅ Correct Answer: {question.correct_answer}")
    print("\n" + "="*80)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test Case {i}:")
        print(f"📝 Student Answer: {test_case['answer']}")
        print(f"🎯 Expected: {test_case['expected']}")
        
        try:
            result = evaluate_answer_with_gemini(question, test_case['answer'])
            
            print(f"✅ Result:")
            print(f"   Score: {result['score']}")
            print(f"   Is Correct: {result['is_correct']}")
            print(f"   Correctness: {result['correctness']}")
            print(f"   Feedback: {result['feedback']}")
            
            # Check if result makes sense
            if test_case['expected'] == 'correct' and result['score'] >= 0.8:
                print("✅ PASS - Correct answer got high score")
            elif test_case['expected'] == 'partial' and 0.3 <= result['score'] <= 0.8:
                print("✅ PASS - Partial answer got medium score")
            elif test_case['expected'] == 'incorrect' and result['score'] <= 0.3:
                print("✅ PASS - Incorrect answer got low score")
            else:
                print("❌ FAIL - Score doesn't match expectation")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
        
        print("-" * 40)
    
    print("\n🎉 Gemini Evaluation Test Complete!")

if __name__ == "__main__":
    test_gemini_evaluation()

