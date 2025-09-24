import json
from scheduler.models import StudentExamSession
from scheduler.adaptive_testing_engine import AdaptiveExamSession, DifficultyProgress, QuestionAttempt
from scheduler.student_results_manager import StudentResultsManager

# Get Daniel's session
session = StudentExamSession.objects.get(id=7)
print(f"Session: {session.id}, Student: {session.student.username}, Exam: {session.exam.title}")

# Load adaptive session from notes
try:
    notes = json.loads(session.notes) if session.notes else {}
    adaptive_data = notes.get('adaptive_session', {})
    
    print("Original adaptive_data keys:", adaptive_data.keys())
    
    # Convert difficulty_progress back to DifficultyProgress objects
    if 'difficulty_progress' in adaptive_data:
        difficulty_progress = {}
        for level, data in adaptive_data['difficulty_progress'].items():
            print(f"Level {level}: {data}")
            difficulty_progress[level] = DifficultyProgress(**data)
        adaptive_data['difficulty_progress'] = difficulty_progress
    
    # Convert question_attempts back to QuestionAttempt objects
    if 'question_attempts' in adaptive_data:
        question_attempts = []
        for attempt_data in adaptive_data['question_attempts']:
            question_attempts.append(QuestionAttempt(**attempt_data))
        adaptive_data['question_attempts'] = question_attempts
    
    adaptive_session = AdaptiveExamSession(**adaptive_data)
    print("Adaptive session loaded successfully")
    
    # Try to save results with detailed error handling
    manager = StudentResultsManager()
    
    # Check what we're working with
    print(f"Session total_questions: {session.total_questions}")
    print(f"Session questions_answered: {session.questions_answered}")
    print(f"Session correct_answers: {session.correct_answers}")
    print(f"Session final_score: {session.final_score}")
    
    result = manager.save_student_results(session, adaptive_session)
    print(f"Save result: {result}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

