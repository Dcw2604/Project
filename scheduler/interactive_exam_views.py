"""
Clean Interactive Exam System - Backend APIs

This module provides a focused, clean implementation of the interactive exam system
that sources questions ONLY from teacher-uploaded documents.

Key Features:
- Questions generated only from teacher documents
- 3-attempt system with progressive hints
- Session persistence across page reloads
- Clean REST API endpoints
- Proper error handling and validation
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.db import transaction
from django.shortcuts import get_object_or_404
import json
import logging

from .models import (
    InteractiveExam, InteractiveExamQuestion, StudentExamSession, 
    StudentExamAnswer, StudentExamAttempt, Document, User
)
from .views import generate_questions_with_gemini

logger = logging.getLogger(__name__)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def start_exam(request):
    """
    Start or resume an interactive exam session
    
    GET /api/exam/start?exam_id=...
    
    Returns:
    - If no active session: creates new session with first question
    - If active session exists: resumes from current question
    - If exam completed: returns completion status
    """
    if request.user.role != 'student':
        return Response({'error': 'Only students can start exams'}, status=403)
    
    exam_id = request.GET.get('exam_id')
    
    try:
        # Get or create exam from teacher documents
        if exam_id:
            exam = get_object_or_404(InteractiveExam, id=exam_id, is_active=True)
        else:
            # Auto-select exam from most recent teacher document
            exam = get_or_create_exam_from_documents()
            if not exam:
                return Response({
                    'error': 'No teacher documents available',
                    'message': 'Teachers must upload documents first to create exams'
                }, status=404)
        
        # Check for existing session
        session, created = StudentExamSession.objects.get_or_create(
            student=request.user,
            exam=exam,
            defaults={
                'total_questions': exam.total_questions,
                'status': 'in_progress'
            }
        )
        
        if session.status == 'completed':
            return Response({
                'status': 'completed',
                'message': 'Exam already completed',
                'session_id': session.id,
                'final_score': session.final_score,
                'summary': get_exam_summary(session)
            })
        
        # Get current question
        current_question = get_current_question(session)
        if not current_question:
            # Exam completed
            session.status = 'completed'
            session.completed_at = timezone.now()
            session.final_score = calculate_final_score(session)
            session.save()
            
            return Response({
                'status': 'completed',
                'message': 'Exam completed successfully',
                'session_id': session.id,
                'final_score': session.final_score,
                'summary': get_exam_summary(session)
            })
        
        # Return current question
        return Response({
            'status': 'in_progress',
            'session_id': session.id,
            'exam_title': exam.title,
            'current_question': {
                'index': session.current_question_index + 1,
                'total': session.total_questions,
                'question_id': current_question.id,
                'question_text': current_question.question_text,
                'question_type': current_question.question_type,
                'difficulty': current_question.difficulty
            },
            'progress': {
                'questions_answered': session.questions_answered,
                'correct_answers': session.correct_answers,
                'percentage': (session.questions_answered / session.total_questions) * 100
            },
            'time_limit': exam.time_limit_minutes
        })
        
    except Exception as e:
        logger.error(f"Error starting exam: {e}")
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_answer(request):
    """
    Submit an answer for the current question
    
    POST /api/exam/answer
    {
        "session_id": 123,
        "question_id": 456,
        "answer": "Student's answer text"
    }
    
    Returns:
    - correct: boolean
    - hint: string (if wrong answer and attempts < 3)
    - remaining_attempts: int
    - reveal_answer: string (if 3rd wrong attempt)
    - move_to_next: boolean
    """
    if request.user.role != 'student':
        return Response({'error': 'Only students can submit answers'}, status=403)
    
    session_id = request.data.get('session_id')
    question_id = request.data.get('question_id')
    answer_text = request.data.get('answer', '').strip()
    
    if not all([session_id, question_id, answer_text]):
        return Response({'error': 'Missing required fields'}, status=400)
    
    try:
        # Get session and validate ownership
        session = get_object_or_404(StudentExamSession, id=session_id, student=request.user)
        question = get_object_or_404(InteractiveExamQuestion, id=question_id, exam=session.exam)
        
        if session.status != 'in_progress':
            return Response({'error': 'Session not active'}, status=400)
        
        # Get or create answer record
        answer, created = StudentExamAnswer.objects.get_or_create(
            session=session,
            question=question
        )
        
        # Check if already answered correctly
        if answer.is_correct:
            return Response({
                'correct': True,
                'message': 'Question already answered correctly',
                'remaining_attempts': 0,
                'move_to_next': True
            })
        
        # Check attempt limit
        if answer.attempts_used >= session.exam.max_attempts_per_question:
            return Response({
                'correct': False,
                'message': 'Maximum attempts reached',
                'remaining_attempts': 0,
                'reveal_answer': question.correct_answer,
                'move_to_next': True
            })
        
        # Evaluate answer
        is_correct = evaluate_answer(question, answer_text)
        attempt_number = answer.attempts_used + 1
        
        # Create attempt record
        attempt = StudentExamAttempt.objects.create(
            answer=answer,
            attempt_number=attempt_number,
            answer_text=answer_text,
            is_correct=is_correct
        )
        
        # Update answer record
        answer.attempts_used = attempt_number
        answer.final_answer = answer_text
        answer.is_correct = is_correct
        answer.save()
        
        if is_correct:
            # Correct answer - move to next question
            session.questions_answered += 1
            session.correct_answers += 1
            session.current_question_index += 1
            session.save()
            
            return Response({
                'correct': True,
                'message': 'Correct! Well done.',
                'remaining_attempts': 0,
                'move_to_next': True
            })
        
        else:
            # Wrong answer - check attempts
            remaining_attempts = session.exam.max_attempts_per_question - attempt_number
            
            if remaining_attempts > 0:
                # Show hint
                hint = get_hint(question, attempt_number)
                attempt.hint_shown = hint
                attempt.save()
                
                return Response({
                    'correct': False,
                    'message': f'Not quite right. Attempt {attempt_number} of {session.exam.max_attempts_per_question}',
                    'hint': hint,
                    'remaining_attempts': remaining_attempts,
                    'move_to_next': False
                })
            else:
                # Max attempts reached - reveal answer and move on
                session.questions_answered += 1
                session.current_question_index += 1
                session.save()
                
                return Response({
                    'correct': False,
                    'message': 'Maximum attempts reached',
                    'remaining_attempts': 0,
                    'reveal_answer': question.correct_answer,
                    'move_to_next': True
                })
        
    except Exception as e:
        logger.error(f"Error submitting answer: {e}")
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_exam_state(request):
    """
    Get current exam session state
    
    GET /api/exam/state?session_id=...
    
    Returns current progress and question info
    """
    if request.user.role != 'student':
        return Response({'error': 'Only students can access exam state'}, status=403)
    
    session_id = request.GET.get('session_id')
    if not session_id:
        return Response({'error': 'session_id required'}, status=400)
    
    try:
        session = get_object_or_404(StudentExamSession, id=session_id, student=request.user)
        current_question = get_current_question(session)
        
        return Response({
            'session_id': session.id,
            'status': session.status,
            'exam_title': session.exam.title,
            'progress': {
                'current_question': session.current_question_index + 1,
                'total_questions': session.total_questions,
                'questions_answered': session.questions_answered,
                'correct_answers': session.correct_answers,
                'percentage': (session.questions_answered / session.total_questions) * 100
            },
            'current_question': {
                'question_id': current_question.id if current_question else None,
                'question_text': current_question.question_text if current_question else None,
                'question_type': current_question.question_type if current_question else None,
                'difficulty': current_question.difficulty if current_question else None
            } if current_question else None,
            'time_remaining': get_time_remaining(session)
        })
        
    except Exception as e:
        logger.error(f"Error getting exam state: {e}")
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def finish_exam(request):
    """
    Manually finish an exam session
    
    POST /api/exam/finish
    {
        "session_id": 123
    }
    """
    if request.user.role != 'student':
        return Response({'error': 'Only students can finish exams'}, status=403)
    
    session_id = request.data.get('session_id')
    if not session_id:
        return Response({'error': 'session_id required'}, status=400)
    
    try:
        session = get_object_or_404(StudentExamSession, id=session_id, student=request.user)
        
        if session.status == 'completed':
            return Response({
                'status': 'already_completed',
                'message': 'Exam already completed',
                'summary': get_exam_summary(session)
            })
        
        # Mark as completed
        session.status = 'completed'
        session.completed_at = timezone.now()
        session.final_score = calculate_final_score(session)
        session.save()
        
        return Response({
            'status': 'completed',
            'message': 'Exam finished successfully',
            'summary': get_exam_summary(session)
        })
        
    except Exception as e:
        logger.error(f"Error finishing exam: {e}")
        return Response({'error': str(e)}, status=500)


# ====================
# HELPER FUNCTIONS
# ====================

def get_or_create_exam_from_documents():
    """Get or create an exam from the most recent teacher document"""
    try:
        # Get most recent teacher document with content
        document = Document.objects.filter(
            uploaded_by__role='teacher',
            extracted_text__isnull=False
        ).exclude(extracted_text='').order_by('-created_at').first()
        
        if not document:
            return None
        
        # Check if exam already exists for this document
        exam = InteractiveExam.objects.filter(document=document).first()
        if exam:
            return exam
        
        # Create new exam
        exam = InteractiveExam.objects.create(
            created_by=document.uploaded_by,
            title=f"Interactive Exam: {document.title}",
            description=f"Questions generated from {document.title}",
            document=document,
            total_questions=10,
            max_attempts_per_question=3
        )
        
        # Generate questions using Gemini - start with fewer questions
        questions = generate_questions_with_gemini(
            document.extracted_text,
            document.title,
            count=3  # Start with 3 questions to avoid truncation
        )
        
        print(f"🔍 Generated {len(questions) if questions else 0} questions for exam {exam.id}")
        
        if not questions:
            print("❌ No questions generated, deleting exam")
            exam.delete()
            return None
        
        # Create question records
        created_count = 0
        for i, q_data in enumerate(questions):
            try:
                InteractiveExamQuestion.objects.create(
                    exam=exam,
                    question_text=q_data.get('question', ''),
                    correct_answer=q_data.get('correct_answer', ''),
                    hint_1=q_data.get('hints', [{}])[0] if q_data.get('hints') else '',
                    hint_2=q_data.get('hints', [{}])[1] if len(q_data.get('hints', [])) > 1 else '',
                    hint_3=q_data.get('hints', [{}])[2] if len(q_data.get('hints', [])) > 2 else '',
                    question_type=q_data.get('type', 'open_ended'),
                    difficulty=q_data.get('difficulty', 'medium'),
                    order_index=i + 1
                )
                created_count += 1
            except Exception as e:
                print(f"❌ Error creating question {i+1}: {e}")
        
        print(f"✅ Created {created_count} questions for exam {exam.id}")
        
        if created_count == 0:
            print("❌ No questions created, deleting exam")
            exam.delete()
            return None
        
        return exam
        
    except Exception as e:
        logger.error(f"Error creating exam from documents: {e}")
        return None


def get_current_question(session):
    """Get the current question for a session"""
    try:
        return InteractiveExamQuestion.objects.filter(
            exam=session.exam,
            order_index=session.current_question_index + 1
        ).first()
    except:
        return None


def evaluate_answer(question, answer_text):
    """Evaluate if the student's answer is correct"""
    # Simple text matching - can be enhanced with more sophisticated NLP
    correct_answer = question.correct_answer.lower().strip()
    student_answer = answer_text.lower().strip()
    
    # Exact match
    if correct_answer == student_answer:
        return True
    
    # Check if correct answer contains student answer (partial match)
    if student_answer in correct_answer and len(student_answer) > 3:
        return True
    
    # Check if student answer contains correct answer (partial match)
    if correct_answer in student_answer and len(correct_answer) > 3:
        return True
    
    return False


def get_hint(question, attempt_number):
    """Get appropriate hint based on attempt number"""
    hints = [question.hint_1, question.hint_2, question.hint_3]
    hint_index = min(attempt_number - 1, len(hints) - 1)
    
    hint = hints[hint_index]
    if hint:
        return hint
    
    # Fallback hints
    fallback_hints = [
        "Think about the key concepts mentioned in the question.",
        "Consider the main ideas and relationships discussed.",
        "Review the question carefully and think about what it's really asking."
    ]
    
    return fallback_hints[hint_index] if hint_index < len(fallback_hints) else "Keep trying!"


def calculate_final_score(session):
    """Calculate final score as percentage"""
    if session.total_questions == 0:
        return 0.0
    return (session.correct_answers / session.total_questions) * 100


def get_exam_summary(session):
    """Get comprehensive exam summary"""
    answers = StudentExamAnswer.objects.filter(session=session)
    
    summary = {
        'total_questions': session.total_questions,
        'questions_answered': session.questions_answered,
        'correct_answers': session.correct_answers,
        'final_score': session.final_score,
        'total_time_minutes': session.total_time_minutes,
        'questions': []
    }
    
    for answer in answers:
        question_summary = {
            'question_id': answer.question.id,
            'question_text': answer.question.question_text,
            'is_correct': answer.is_correct,
            'attempts_used': answer.attempts_used,
            'time_taken_seconds': answer.time_taken_seconds
        }
        summary['questions'].append(question_summary)
    
    return summary


def get_time_remaining(session):
    """Calculate remaining time if time limit is set"""
    if not session.exam.time_limit_minutes:
        return None
    
    elapsed = timezone.now() - session.started_at
    elapsed_minutes = elapsed.total_seconds() / 60
    remaining = session.exam.time_limit_minutes - elapsed_minutes
    
    return max(0, remaining)
