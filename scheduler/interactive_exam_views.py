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
from django.core.exceptions import PermissionDenied
import json
import logging

from .models import (
    InteractiveExam, InteractiveExamQuestion, StudentExamSession, 
    StudentExamAnswer, StudentExamAttempt, Document, User
)
from .views import generate_questions_with_gemini, generate_questions_in_batches
from .adaptive_testing_engine import adaptive_engine, AdaptiveExamSession, DifficultyProgress, QuestionAttempt
from .exam_grading_system import exam_grading_system
from .student_results_manager import student_results_manager
from .results_access_modes import results_access_modes
from .secure_data_handler import secure_data_handler

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
        
        # Initialize adaptive session if new
        if created:
            adaptive_session = adaptive_engine.create_adaptive_session(
                session_id=session.id,
                student_id=request.user.id,
                exam_id=exam.id
            )
            # Store adaptive session data
            session.notes = json.dumps({'adaptive_session': adaptive_session.to_dict()}, ensure_ascii=False)
            session.save()
        else:
            # Load existing adaptive session
            try:
                notes = json.loads(session.notes) if session.notes else {}
                adaptive_data = notes.get('adaptive_session', {})
                # Convert difficulty_progress back to DifficultyProgress objects
                if 'difficulty_progress' in adaptive_data:
                    difficulty_progress = {}
                    for level, data in adaptive_data['difficulty_progress'].items():
                        difficulty_progress[level] = DifficultyProgress(**data)
                    adaptive_data['difficulty_progress'] = difficulty_progress
                
                # Convert question_attempts back to QuestionAttempt objects
                if 'question_attempts' in adaptive_data:
                    question_attempts = []
                    for attempt_data in adaptive_data['question_attempts']:
                        question_attempts.append(QuestionAttempt(**attempt_data))
                    adaptive_data['question_attempts'] = question_attempts
                
                adaptive_session = AdaptiveExamSession(**adaptive_data)
            except Exception as e:
                print(f"Error loading adaptive session: {e}")
                # Create new adaptive session if loading fails
                adaptive_session = adaptive_engine.create_adaptive_session(
                    session_id=session.id,
                    student_id=request.user.id,
                    exam_id=exam.id
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
        
        # Load adaptive session
        try:
            notes = json.loads(session.notes) if session.notes else {}
            adaptive_data = notes.get('adaptive_session', {})
            # Convert difficulty_progress back to DifficultyProgress objects
            if 'difficulty_progress' in adaptive_data:
                difficulty_progress = {}
                for level, data in adaptive_data['difficulty_progress'].items():
                    difficulty_progress[level] = DifficultyProgress(**data)
                adaptive_data['difficulty_progress'] = difficulty_progress
            
            # Convert question_attempts back to QuestionAttempt objects
            if 'question_attempts' in adaptive_data:
                question_attempts = []
                for attempt_data in adaptive_data['question_attempts']:
                    question_attempts.append(QuestionAttempt(**attempt_data))
                adaptive_data['question_attempts'] = question_attempts
            
            adaptive_session = AdaptiveExamSession(**adaptive_data)
        except Exception as e:
            print(f"Error loading adaptive session: {e}")
            # Create new adaptive session if loading fails
            adaptive_session = adaptive_engine.create_adaptive_session(
                session_id=session.id,
                student_id=request.user.id,
                exam_id=session.exam.id
            )
        
        # Evaluate answer with intelligent scoring
        evaluation_result = evaluate_answer(question, answer_text)
        is_correct = evaluation_result['is_correct']
        score = evaluation_result['score']
        feedback = evaluation_result['feedback']
        attempt_number = answer.attempts_used + 1
        
        # Get hints used (if any)
        hints_used = []
        if attempt_number > 1:
            # Get hints from previous attempts
            previous_attempts = StudentExamAttempt.objects.filter(answer=answer)
            for prev_attempt in previous_attempts:
                if prev_attempt.hint_shown:
                    hints_used.append(prev_attempt.hint_shown)
        
        # Record answer in adaptive engine
        should_advance, next_difficulty, completion_status = adaptive_engine.record_answer(
            session=adaptive_session,
            question_id=question.id,
            question_text=question.question_text,
            student_answer=answer_text,
            correct_answer=question.correct_answer,
            is_correct=is_correct,
            partial_score=score,
            hints_used=hints_used,
            time_spent=0.0  # Could be calculated if needed
        )
        
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
        answer.partial_score = score
        
        # Save Gemini evaluation results
        if 'correctness' in evaluation_result:
            answer.correctness = evaluation_result['correctness']
        if 'feedback' in evaluation_result:
            answer.feedback = evaluation_result['feedback']
        if 'gemini_response' in evaluation_result:
            answer.gemini_response = evaluation_result['gemini_response']
        
        answer.save()
        
        # Save adaptive session
        session.notes = json.dumps({'adaptive_session': adaptive_session.to_dict()}, ensure_ascii=False)
        session.save()
        
        if is_correct:
            # Correct answer - move to next question
            session.questions_answered += 1
            session.correct_answers += 1
            session.current_question_index += 1
            session.save()
            
            response_data = {
                'correct': True,
                'message': feedback,
                'score': score,
                'remaining_attempts': 0,
                'move_to_next': True,
                'adaptive_data': {
                    'current_difficulty': adaptive_session.current_difficulty,
                    'difficulty_advanced': should_advance,
                    'next_difficulty': next_difficulty
                }
            }
            
            if completion_status:
                # Mark session as completed
                session.status = 'completed'
                session.completed_at = timezone.now()
                session.final_score = adaptive_session.final_score
                session.save()
                
                # Generate comprehensive grade report
                grade_report = exam_grading_system.generate_grade_report(adaptive_session)
                
                # Save student results to JSON file
                try:
                    results_saved = student_results_manager.save_student_results(session, adaptive_session)
                    if results_saved:
                        print(f"✅ Student results saved for student {session.student.id} in exam {session.exam.id}")
                    else:
                        print(f"❌ Failed to save student results for student {session.student.id}")
                except Exception as e:
                    print(f"❌ Error saving student results: {e}")
                
                response_data['exam_completed'] = True
                response_data['final_score'] = adaptive_session.final_score
                response_data['summary'] = adaptive_engine.get_session_summary(adaptive_session)
                response_data['grade_report'] = grade_report
            
            return Response(response_data)
        
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
                    'message': feedback,
                    'score': score,
                    'hint': hint,
                    'remaining_attempts': remaining_attempts,
                    'move_to_next': False,
                    'adaptive_data': {
                        'current_difficulty': adaptive_session.current_difficulty,
                        'difficulty_advanced': should_advance,
                        'next_difficulty': next_difficulty
                    }
                })
            else:
                # Max attempts reached - reveal answer and move on
                session.questions_answered += 1
                session.current_question_index += 1
                session.save()
                
                response_data = {
                    'correct': False,
                    'message': f'{feedback} הגעת למספר הניסיונות המקסימלי.',
                    'score': score,
                    'remaining_attempts': 0,
                    'reveal_answer': question.correct_answer,
                    'move_to_next': True,
                    'adaptive_data': {
                        'current_difficulty': adaptive_session.current_difficulty,
                        'difficulty_advanced': should_advance,
                        'next_difficulty': next_difficulty
                    }
                }
                
                if completion_status:
                    # Mark session as completed
                    session.status = 'completed'
                    session.completed_at = timezone.now()
                    session.final_score = adaptive_session.final_score
                    session.save()
                    
                    # Generate comprehensive grade report
                    grade_report = exam_grading_system.generate_grade_report(adaptive_session)
                    
                    # Save student results to JSON file
                    try:
                        results_saved = student_results_manager.save_student_results(session, adaptive_session)
                        if results_saved:
                            print(f"✅ Student results saved for student {session.student.id} in exam {session.exam.id}")
                        else:
                            print(f"❌ Failed to save student results for student {session.student.id}")
                    except Exception as e:
                        print(f"❌ Error saving student results: {e}")
                    
                    response_data['exam_completed'] = True
                    response_data['final_score'] = adaptive_session.final_score
                    response_data['summary'] = adaptive_engine.get_session_summary(adaptive_session)
                    response_data['grade_report'] = grade_report
                
                return Response(response_data)
        
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
        
        # Load adaptive session for comprehensive grading
        try:
            notes = json.loads(session.notes) if session.notes else {}
            adaptive_data = notes.get('adaptive_session', {})
            # Convert difficulty_progress back to DifficultyProgress objects
            if 'difficulty_progress' in adaptive_data:
                difficulty_progress = {}
                for level, data in adaptive_data['difficulty_progress'].items():
                    difficulty_progress[level] = DifficultyProgress(**data)
                adaptive_data['difficulty_progress'] = difficulty_progress
            
            # Convert question_attempts back to QuestionAttempt objects
            if 'question_attempts' in adaptive_data:
                question_attempts = []
                for attempt_data in adaptive_data['question_attempts']:
                    question_attempts.append(QuestionAttempt(**attempt_data))
                adaptive_data['question_attempts'] = question_attempts
            
            adaptive_session = AdaptiveExamSession(**adaptive_data)
        except Exception as e:
            print(f"Error loading adaptive session: {e}")
            # Create basic adaptive session if loading fails
            adaptive_session = adaptive_engine.create_adaptive_session(
                session_id=session.id,
                student_id=request.user.id,
                exam_id=session.exam.id
            )
        
        # Mark as completed
        session.status = 'completed'
        session.completed_at = timezone.now()
        session.final_score = calculate_final_score(session)
        session.save()
        
        # Generate comprehensive grade report
        grade_report = exam_grading_system.generate_grade_report(adaptive_session)
        
        # Save student results to secure JSON file
        try:
            # First save to regular location for compatibility
            results_saved = student_results_manager.save_student_results(session, adaptive_session)
            
            # Then save to secure location
            all_results = student_results_manager.get_all_results()
            secure_saved = secure_data_handler.save_secure_results(all_results)
            
            if results_saved and secure_saved:
                print(f"✅ Student results saved securely for student {session.student.id} in exam {session.exam.id}")
            else:
                print(f"❌ Failed to save student results for student {session.student.id}")
        except Exception as e:
            print(f"❌ Error saving student results: {e}")
        
        return Response({
            'status': 'completed',
            'message': 'המבחן הושלם בהצלחה!',
            'summary': get_exam_summary(session),
            'grade_report': grade_report
        })
        
    except Exception as e:
        logger.error(f"Error finishing exam: {e}")
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_student_results(request):
    """
    Get student results for teachers
    
    GET /api/exam/results/
    GET /api/exam/results/?student_id=123
    GET /api/exam/results/?exam_id=456
    """
    if request.user.role not in ['teacher', 'admin']:
        return Response({'error': 'Only teachers can access results'}, status=403)
    
    try:
        student_id = request.GET.get('student_id')
        exam_id = request.GET.get('exam_id')
        
        if student_id:
            results = student_results_manager.get_student_results(int(student_id))
            return Response({
                'student_id': int(student_id),
                'results': results
            })
        elif exam_id:
            results = student_results_manager.get_exam_results(int(exam_id))
            return Response({
                'exam_id': int(exam_id),
                'results': results
            })
        else:
            # Get all results
            all_results = student_results_manager.get_all_results()
            return Response(all_results)
            
    except Exception as e:
        logger.error(f"Error getting student results: {e}")
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_teacher_analytics(request):
    """
    Get comprehensive analytics for teachers
    
    GET /api/exam/analytics/
    """
    if request.user.role not in ['teacher', 'admin']:
        return Response({'error': 'Only teachers can access analytics'}, status=403)
    
    try:
        analytics = student_results_manager.get_teacher_analytics()
        return Response(analytics)
        
    except Exception as e:
        logger.error(f"Error getting teacher analytics: {e}")
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_teacher_dashboard(request):
    """
    Teacher Mode: Comprehensive dashboard with all student data
    
    GET /api/exam/teacher-dashboard/
    
    Security Rules:
    - Only teachers and admins can access
    - Returns full dataset
    - Includes all student data
    - Comprehensive analytics provided
    """
    try:
        dashboard_data = secure_data_handler.get_teacher_data(
            user_id=request.user.id,
            user_role=request.user.role
        )
        return Response(dashboard_data)
        
    except PermissionDenied as e:
        return Response({'error': str(e)}, status=403)
    except Exception as e:
        logger.error(f"Error getting teacher dashboard: {e}")
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_teacher_summary_report(request):
    """
    Teacher Mode: Generate comprehensive summary report
    
    GET /api/exam/teacher-summary-report/
    """
    if request.user.role not in ['teacher', 'admin']:
        return Response({'error': 'Only teachers can access summary report'}, status=403)
    
    try:
        summary_report = results_access_modes.get_teacher_summary_report()
        return Response(summary_report)
        
    except Exception as e:
        logger.error(f"Error getting teacher summary report: {e}")
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_student_personal_results(request, student_id):
    """
    Student Mode: Personal results only
    
    GET /api/exam/student-results/<int:student_id>/
    
    Security Rules:
    - Students can only access their own data
    - Teachers can access any student's data
    - Strict filtering by student_id
    - No access to other students' data
    """
    try:
        student_data = secure_data_handler.get_student_data(
            user_id=request.user.id,
            user_role=request.user.role,
            requested_student_id=student_id
        )
        return Response(student_data)
        
    except PermissionDenied as e:
        return Response({'error': str(e)}, status=403)
    except Exception as e:
        logger.error(f"Error getting student personal results: {e}")
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_security_audit_log(request):
    """
    Security Audit Log (Teachers and Admins only)
    
    GET /api/exam/security-audit/
    
    Security Rules:
    - Only teachers and admins can access
    - Provides security monitoring capabilities
    - Tracks data access patterns
    """
    try:
        audit_data = secure_data_handler.get_security_audit_log(
            user_id=request.user.id,
            user_role=request.user.role
        )
        return Response(audit_data)
        
    except PermissionDenied as e:
        return Response({'error': str(e)}, status=403)
    except Exception as e:
        logger.error(f"Error getting security audit log: {e}")
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
        
        # Generate questions using Gemini - generate 10 questions in smaller batches for Hebrew
        questions = generate_questions_in_batches(
            document.extracted_text,
            document.title,
            total_count=10,
            batch_size=3  # Generate 3 questions at a time to avoid Hebrew truncation
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
    """
    Intelligent answer evaluation system using Gemini LLM
    Returns: dict with 'score' (0.0-1.0), 'is_correct' (bool), 'feedback' (str)
    """
    try:
        # Use Gemini for evaluation
        result = evaluate_answer_with_gemini(question, answer_text)
        return result
        
    except Exception as e:
        print(f"❌ Gemini evaluation failed: {e}")
        # Fallback to simple evaluation
        return evaluate_answer_simple(question, answer_text)


def evaluate_answer_with_gemini(question, answer_text):
    """
    Evaluate student answer using Gemini LLM
    """
    try:
        # Import Gemini client
        from .views import gemini_client
        
        if not gemini_client:
            raise Exception("Gemini client not available")
        
        # Create prompt for Gemini
        prompt = f"""Compare the following two answers:
Expected answer: {question.correct_answer}
Student's answer: {answer_text}
Task: Determine if the student's answer is correct, partially correct, or incorrect. 
If partially correct, suggest a partial score (e.g., 0.25, 0.5, 0.75).
Output a JSON object with fields: {{ "correctness": "correct/partial/incorrect", "score": number between 0 and 1, "explanation": "short explanation in Hebrew" }}."""

        # Get response from Gemini
        response = gemini_client.generate_content(prompt)
        
        if not response or not hasattr(response, 'text'):
            raise Exception("No response from Gemini")
        
        response_text = response.text.strip()
        
        # Parse JSON response
        try:
            # Clean up response text
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            # Parse JSON
            import json
            result = json.loads(response_text)
            
            # Extract values
            correctness = result.get('correctness', 'incorrect')
            score = float(result.get('score', 0.0))
            explanation = result.get('explanation', 'לא ניתן להעריך את התשובה')
            
            # Determine if correct based on score
            is_correct = score >= 0.5  # Consider 50%+ as correct
            
            return {
                'score': score,
                'is_correct': is_correct,
                'feedback': explanation,
                'correctness': correctness,
                'gemini_response': response_text
            }
            
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse Gemini JSON response: {e}")
            print(f"Raw response: {response_text}")
            
            # Fallback: try to extract score from text
            score = extract_score_from_text(response_text)
            return {
                'score': score,
                'is_correct': score >= 0.5,
                'feedback': 'תשובה הוערכה על ידי Gemini',
                'correctness': 'partial' if 0 < score < 1 else ('correct' if score >= 1 else 'incorrect'),
                'gemini_response': response_text
            }
        
    except Exception as e:
        print(f"❌ Gemini evaluation error: {e}")
        raise e


def extract_score_from_text(text):
    """
    Try to extract a score from Gemini's text response
    """
    import re
    
    # Look for numbers between 0 and 1
    score_patterns = [
        r'(\d+\.?\d*)\s*/\s*1',  # "0.75/1"
        r'score[:\s]*(\d+\.?\d*)',  # "score: 0.75"
        r'(\d+\.?\d*)\s*out\s*of\s*1',  # "0.75 out of 1"
        r'(\d+\.?\d*)\s*%',  # "75%"
    ]
    
    for pattern in score_patterns:
        match = re.search(pattern, text.lower())
        if match:
            score = float(match.group(1))
            if '%' in pattern:
                score = score / 100.0  # Convert percentage to decimal
            return min(max(score, 0.0), 1.0)  # Clamp between 0 and 1
    
    # Look for keywords
    if 'correct' in text.lower() and 'incorrect' not in text.lower():
        return 1.0
    elif 'incorrect' in text.lower() and 'correct' not in text.lower():
        return 0.0
    elif 'partial' in text.lower():
        return 0.5
    
    return 0.0


def evaluate_answer_simple(question, answer_text):
    """
    Simple fallback evaluation system
    """
    correct_answer = question.correct_answer.lower().strip()
    student_answer = answer_text.lower().strip()
    
    # Remove extra whitespace and normalize
    correct_answer = ' '.join(correct_answer.split())
    student_answer = ' '.join(student_answer.split())
    
    # Exact match - full credit
    if correct_answer == student_answer:
        return {
            'score': 1.0,
            'is_correct': True,
            'feedback': 'תשובה נכונה לחלוטין! מעולה!'
        }
    
    # Check for key concepts and synonyms
    score, feedback = evaluate_answer_intelligently(correct_answer, student_answer, question)
    
    return {
        'score': score,
        'is_correct': score >= 0.5,  # Consider 50%+ as "correct"
        'feedback': feedback
    }


def evaluate_answer_intelligently(correct_answer, student_answer, question):
    """
    Intelligent evaluation using multiple criteria
    Returns: (score, feedback)
    """
    # Extract key concepts from correct answer
    key_concepts = extract_key_concepts(correct_answer)
    
    # Check how many key concepts are present in student answer
    concepts_found = 0
    total_concepts = len(key_concepts)
    
    for concept in key_concepts:
        if concept in student_answer:
            concepts_found += 1
    
    # Calculate base score based on concept coverage
    if total_concepts > 0:
        concept_score = concepts_found / total_concepts
    else:
        concept_score = 0
    
    # Check for synonyms and alternative phrasings
    synonym_score = check_synonyms_and_alternatives(correct_answer, student_answer)
    
    # Check for partial matches
    partial_score = check_partial_matches(correct_answer, student_answer)
    
    # Combine scores (weighted average)
    final_score = (concept_score * 0.4 + synonym_score * 0.3 + partial_score * 0.3)
    
    # Generate feedback based on score
    if final_score >= 0.9:
        feedback = 'תשובה מצוינת! כל המושגים החשובים מופיעים.'
    elif final_score >= 0.7:
        feedback = 'תשובה טובה! רוב המושגים החשובים מופיעים.'
    elif final_score >= 0.5:
        feedback = 'תשובה חלקית נכונה. חסרים כמה מושגים חשובים.'
    elif final_score >= 0.3:
        feedback = 'תשובה חלקית. יש כמה מושגים נכונים אבל חסרים רבים.'
    else:
        feedback = 'תשובה לא נכונה. נסה לחשוב על המושגים העיקריים.'
    
    return final_score, feedback


def extract_key_concepts(text):
    """Extract key concepts from text"""
    # Simple keyword extraction - can be enhanced with NLP
    # Remove common words and extract meaningful terms
    common_words = {'הוא', 'היא', 'זה', 'זו', 'של', 'את', 'על', 'ב', 'ל', 'מ', 'כ', 'אל', 'עם', 'או', 'אבל', 'כי', 'אם', 'כאשר', 'אשר', 'כל', 'כלל', 'יותר', 'פחות', 'גם', 'רק', 'אפילו', 'במיוחד', 'בעיקר', 'בדרך', 'כלל', 'בדרך כלל'}
    
    words = text.split()
    key_concepts = []
    
    for word in words:
        # Remove punctuation
        clean_word = ''.join(c for c in word if c.isalnum() or c in 'אבגדהוזחטיכלמנסעפצקרשת')
        if len(clean_word) > 2 and clean_word not in common_words:
            key_concepts.append(clean_word)
    
    return key_concepts


def check_synonyms_and_alternatives(correct_answer, student_answer):
    """Check for synonyms and alternative phrasings"""
    # Simple synonym checking - can be enhanced with a proper thesaurus
    synonyms = {
        'מערכת': ['מערכת', 'מנגנון', 'מבנה', 'ארכיטקטורה'],
        'נתונים': ['נתונים', 'מידע', 'דאטה', 'מקורות'],
        'תהליך': ['תהליך', 'מהלך', 'שלב', 'שלבים'],
        'פתרון': ['פתרון', 'פתרונות', 'מענה', 'תשובה'],
        'בעיה': ['בעיה', 'בעיות', 'קושי', 'אתגר'],
        'שיטה': ['שיטה', 'דרך', 'אופן', 'גישה'],
        'כלי': ['כלי', 'כלים', 'מכשיר', 'מכשירים'],
        'תכונה': ['תכונה', 'תכונות', 'מאפיין', 'מאפיינים'],
        'פונקציה': ['פונקציה', 'פונקציות', 'תפקיד', 'תפקידים'],
        'תוצאה': ['תוצאה', 'תוצאות', 'התוצאה', 'התוצאות']
    }
    
    score = 0
    total_checks = 0
    
    for concept, syn_list in synonyms.items():
        if concept in correct_answer:
            total_checks += 1
            found_synonym = False
            for syn in syn_list:
                if syn in student_answer:
                    found_synonym = True
                    break
            if found_synonym:
                score += 1
    
    return score / total_checks if total_checks > 0 else 0


def check_partial_matches(correct_answer, student_answer):
    """Check for partial matches and word order variations"""
    # Split into words
    correct_words = correct_answer.split()
    student_words = student_answer.split()
    
    if not correct_words or not student_words:
        return 0
    
    # Check word overlap
    correct_set = set(correct_words)
    student_set = set(student_words)
    
    overlap = len(correct_set.intersection(student_set))
    total_words = len(correct_set)
    
    return overlap / total_words if total_words > 0 else 0


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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def grade_answer(request):
    """
    Grade a student's answer using semantic grading
    POST /api/grade
    """
    try:
        data = request.data
        attempt_id = data.get('attempt_id')
        question_id = data.get('question_id')
        answer_text = data.get('answer_text')
        
        if not all([attempt_id, question_id, answer_text]):
            return Response({
                'error': 'Missing required fields: attempt_id, question_id, answer_text'
            }, status=400)
        
        # Get the question
        try:
            question = InteractiveExamQuestion.objects.get(id=question_id)
        except InteractiveExamQuestion.DoesNotExist:
            return Response({
                'error': 'Question not found'
            }, status=404)
        
        # Import semantic grader
        from .semantic_grading import semantic_grader
        
        # Grade the answer
        result = semantic_grader.grade_free_text(answer_text, question)
        
        # Store the result (optional - for audit trail)
        # You can save this to a new model if needed
        
        return Response({
            'score': result.score,
            'is_correct': result.is_correct,
            'confidence': result.confidence,
            'reasons': result.reasons,
            'matched_key_points': result.matched_key_points,
            'missing_key_points': result.missing_key_points,
            'strategy_used': result.strategy_used
        })
        
    except Exception as e:
        return Response({
            'error': f'Grading failed: {str(e)}'
        }, status=500)


def get_time_remaining(session):
    """Calculate remaining time if time limit is set"""
    if not session.exam.time_limit_minutes:
        return None
    
    elapsed = timezone.now() - session.started_at
    elapsed_minutes = elapsed.total_seconds() / 60
    remaining = session.exam.time_limit_minutes - elapsed_minutes
    
    return max(0, remaining)
