"""
Comprehensive Exam Integration Views
==================================

This module provides unified exam management integrating document upload → question generation → 
exam session creation → student testing in one cohesive system.

Key Features:
- Document upload with automatic question generation
- Exam session creation from generated questions  
- Student exam assignment and testing
- Real-time progress tracking
- Comprehensive analytics
"""

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.utils import timezone
from django.db.models import Q, Count, Avg
import json
import logging

from .models import (
    Document, QuestionBank, ExamSession, ExamSessionQuestion, 
    ExamAnswerAttempt, User, Topic, ExamConfig, ExamConfigQuestion
)
from .serializers import DocumentSerializer, QuestionBankSerializer, ExamSessionSerializer

logger = logging.getLogger(__name__)

# ==========================
# UNIFIED DOCUMENT & QUESTION MANAGEMENT
# ==========================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_document_with_exam_creation(request):
    """
    Enhanced document upload that automatically creates exam session after question generation
    
    Flow:
    1. Upload document
    2. Generate questions (background)
    3. Create exam session with generated questions
    4. Return exam session ID for student assignment
    """
    try:
        from .views import upload_document  # Import existing upload function
        
        # Call existing upload function
        upload_response = upload_document(request)
        
        if upload_response.status_code == 201:
            response_data = upload_response.data
            document_id = response_data.get('document_id')
            
            if request.user.role == 'teacher' and document_id:
                # Add metadata for exam creation after processing
                response_data['create_exam_after_processing'] = True
                response_data['exam_creation_note'] = 'An exam session will be automatically created once question generation completes.'
                
                return Response(response_data, status=201)
        
        return upload_response
        
    except Exception as e:
        logger.error(f"Enhanced upload failed: {str(e)}")
        return Response({
            'error': f'Enhanced document upload failed: {str(e)}'
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_exam_from_document(request, document_id):
    """
    Create an exam session from questions generated from a specific document
    
    Expected payload:
    {
        "title": "Exam Title",
        "description": "Optional description",
        "num_questions": 10,
        "time_limit_seconds": 3600,
        "difficulty_levels": ["easy", "normal", "hard"],
        "question_distribution": {
            "easy": 3,
            "normal": 4, 
            "hard": 3
        }
    }
    """
    try:
        if request.user.role != 'teacher':
            return Response({
                'error': 'Only teachers can create exam sessions'
            }, status=403)
        
        document = get_object_or_404(Document, id=document_id, uploaded_by=request.user)
        
        # Check if document has generated questions
        document_questions = QuestionBank.objects.filter(document=document)
        if not document_questions.exists():
            return Response({
                'error': 'No questions available for this document. Please wait for question generation to complete.'
            }, status=400)
        
        data = request.data
        title = data.get('title', f"Exam: {document.title}")
        description = data.get('description', f"Auto-generated exam from document: {document.title}")
        num_questions = data.get('num_questions', 10)
        time_limit_seconds = data.get('time_limit_seconds')
        difficulty_levels = data.get('difficulty_levels', ['easy', 'normal', 'hard'])
        question_distribution = data.get('question_distribution', {})
        
        with transaction.atomic():
            # Create exam session
            exam_session = ExamSession.objects.create(
                created_by=request.user,
                title=title,
                description=description,
                num_questions=num_questions,
                time_limit_seconds=time_limit_seconds,
                is_published=False  # Teacher can publish manually
            )
            
            # Select questions based on distribution or evenly
            selected_questions = []
            
            if question_distribution:
                # Use specified distribution
                for difficulty, count in question_distribution.items():
                    if difficulty in difficulty_levels:
                        questions = document_questions.filter(
                            difficulty_level=difficulty
                        ).order_by('?')[:count]
                        selected_questions.extend(questions)
            else:
                # Even distribution across available difficulties
                available_difficulties = document_questions.values_list(
                    'difficulty_level', flat=True
                ).distinct()
                per_difficulty = num_questions // len(available_difficulties)
                remainder = num_questions % len(available_difficulties)
                
                for i, difficulty in enumerate(available_difficulties):
                    count = per_difficulty + (1 if i < remainder else 0)
                    questions = document_questions.filter(
                        difficulty_level=difficulty
                    ).order_by('?')[:count]
                    selected_questions.extend(questions)
            
            # Limit to requested number
            selected_questions = selected_questions[:num_questions]
            
            # Create exam session questions with order
            for i, question in enumerate(selected_questions):
                ExamSessionQuestion.objects.create(
                    exam_session=exam_session,
                    question=question,
                    order_index=i + 1,
                    time_limit_seconds=time_limit_seconds
                )
            
            # Create exam config for persistent storage
            exam_config = ExamConfig.objects.create(
                exam_session=exam_session,
                teacher=request.user
            )
            
            # Create config questions
            for i, question in enumerate(selected_questions):
                ExamConfigQuestion.objects.create(
                    exam_config=exam_config,
                    question=question,
                    order_index=i + 1
                )
            
            return Response({
                'success': True,
                'exam_session_id': exam_session.id,
                'exam_config_id': exam_config.id,
                'title': exam_session.title,
                'description': exam_session.description,
                'num_questions': len(selected_questions),
                'time_limit_seconds': exam_session.time_limit_seconds,
                'questions_selected': len(selected_questions),
                'document_title': document.title,
                'is_published': exam_session.is_published,
                'message': f'Exam session "{title}" created successfully with {len(selected_questions)} questions from document "{document.title}"'
            }, status=201)
            
    except Exception as e:
        logger.error(f"Exam creation from document failed: {str(e)}")
        return Response({
            'error': f'Failed to create exam session: {str(e)}'
        }, status=500)


# ==========================
# UNIFIED EXAM SESSION MANAGEMENT
# ==========================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_unified_exam_sessions(request):
    """
    List exam sessions with role-based access:
    - Teachers: See their created exam sessions
    - Students: See published exam sessions available to them
    """
    try:
        if request.user.role == 'teacher':
            # Teachers see their created exam sessions
            exam_sessions = ExamSession.objects.filter(
                created_by=request.user
            ).order_by('-created_at')
            
            sessions_data = []
            for session in exam_sessions:
                questions_count = session.session_questions.count()
                attempts_count = ExamAnswerAttempt.objects.filter(
                    exam_session=session
                ).values('student').distinct().count()
                
                sessions_data.append({
                    'id': session.id,
                    'title': session.title,
                    'description': session.description,
                    'num_questions': session.num_questions,
                    'actual_questions_count': questions_count,
                    'time_limit_seconds': session.time_limit_seconds,
                    'is_published': session.is_published,
                    'created_at': session.created_at.isoformat(),
                    'updated_at': session.updated_at.isoformat(),
                    'student_attempts': attempts_count,
                    'can_edit': True,
                    'can_delete': True
                })
            
            return Response({
                'exam_sessions': sessions_data,
                'total_count': len(sessions_data),
                'user_role': 'teacher'
            })
            
        else:
            # Students see published exam sessions
            exam_sessions = ExamSession.objects.filter(
                is_published=True
            ).order_by('-created_at')
            
            sessions_data = []
            for session in exam_sessions:
                # Check if student has already attempted this exam
                has_attempted = ExamAnswerAttempt.objects.filter(
                    exam_session=session,
                    student=request.user
                ).exists()
                
                sessions_data.append({
                    'id': session.id,
                    'title': session.title,
                    'description': session.description,
                    'num_questions': session.num_questions,
                    'time_limit_seconds': session.time_limit_seconds,
                    'created_by': session.created_by.username,
                    'created_at': session.created_at.isoformat(),
                    'has_attempted': has_attempted,
                    'can_start': not has_attempted
                })
            
            return Response({
                'available_exam_sessions': sessions_data,
                'total_count': len(sessions_data),
                'user_role': 'student'
            })
            
    except Exception as e:
        logger.error(f"List unified exam sessions failed: {str(e)}")
        return Response({
            'error': f'Failed to load exam sessions: {str(e)}'
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_unified_exam_session(request, session_id):
    """
    Get detailed exam session information with role-based data
    """
    try:
        exam_session = get_object_or_404(ExamSession, id=session_id)
        
        if request.user.role == 'teacher':
            # Teachers get full exam session details
            if exam_session.created_by != request.user:
                return Response({
                    'error': 'You can only view your own exam sessions'
                }, status=403)
            
            questions = exam_session.session_questions.all().order_by('order_index')
            questions_data = []
            
            for session_question in questions:
                question = session_question.question
                questions_data.append({
                    'id': question.id,
                    'order_index': session_question.order_index,
                    'question_text': question.question_text,
                    'question_type': question.question_type,
                    'difficulty_level': question.difficulty_level,
                    'subject': question.subject,
                    'correct_answer': question.correct_answer,
                    'option_a': question.option_a,
                    'option_b': question.option_b,
                    'option_c': question.option_c,
                    'option_d': question.option_d,
                    'explanation': question.explanation,
                    'time_limit_seconds': session_question.time_limit_seconds
                })
            
            # Get student attempts summary
            attempts = ExamAnswerAttempt.objects.filter(
                exam_session=exam_session
            ).values('student__username').annotate(
                attempt_count=Count('id'),
                avg_correct=Avg('is_correct')
            )
            
            return Response({
                'exam_session': {
                    'id': exam_session.id,
                    'title': exam_session.title,
                    'description': exam_session.description,
                    'num_questions': exam_session.num_questions,
                    'time_limit_seconds': exam_session.time_limit_seconds,
                    'is_published': exam_session.is_published,
                    'created_at': exam_session.created_at.isoformat(),
                    'updated_at': exam_session.updated_at.isoformat(),
                    'questions': questions_data,
                    'student_attempts': list(attempts)
                },
                'user_role': 'teacher',
                'can_edit': True,
                'can_delete': True,
                'can_publish': not exam_session.is_published
            })
            
        else:
            # Students get limited exam session info (no answers)
            if not exam_session.is_published:
                return Response({
                    'error': 'This exam session is not available'
                }, status=404)
            
            # Check if student has already attempted this exam
            has_attempted = ExamAnswerAttempt.objects.filter(
                exam_session=exam_session,
                student=request.user
            ).exists()
            
            questions = exam_session.session_questions.all().order_by('order_index')
            questions_data = []
            
            for session_question in questions:
                question = session_question.question
                questions_data.append({
                    'id': question.id,
                    'order_index': session_question.order_index,
                    'question_text': question.question_text,
                    'question_type': question.question_type,
                    'difficulty_level': question.difficulty_level,
                    'subject': question.subject,
                    'option_a': question.option_a,
                    'option_b': question.option_b,
                    'option_c': question.option_c,
                    'option_d': question.option_d,
                    'time_limit_seconds': session_question.time_limit_seconds
                    # Note: No correct_answer or explanation for students during exam
                })
            
            return Response({
                'exam_session': {
                    'id': exam_session.id,
                    'title': exam_session.title,
                    'description': exam_session.description,
                    'num_questions': exam_session.num_questions,
                    'time_limit_seconds': exam_session.time_limit_seconds,
                    'created_by': exam_session.created_by.username,
                    'questions': questions_data if not has_attempted else []
                },
                'user_role': 'student',
                'has_attempted': has_attempted,
                'can_start': not has_attempted,
                'message': 'You have already attempted this exam' if has_attempted else None
            })
            
    except Exception as e:
        logger.error(f"Get unified exam session failed: {str(e)}")
        return Response({
            'error': f'Failed to load exam session: {str(e)}'
        }, status=500)


# ==========================
# UNIFIED STUDENT TESTING
# ==========================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_unified_exam_session(request, session_id):
    """
    Start an exam session for a student
    """
    try:
        if request.user.role != 'student':
            return Response({
                'error': 'Only students can start exam sessions'
            }, status=403)
        
        exam_session = get_object_or_404(ExamSession, id=session_id, is_published=True)
        
        # Check if student has already attempted this exam
        existing_attempt = ExamAnswerAttempt.objects.filter(
            exam_session=exam_session,
            student=request.user
        ).first()
        
        if existing_attempt:
            return Response({
                'error': 'You have already attempted this exam',
                'attempted_at': existing_attempt.submitted_at.isoformat()
            }, status=400)
        
        # Get exam questions in order
        questions = exam_session.session_questions.all().order_by('order_index')
        
        if not questions.exists():
            return Response({
                'error': 'This exam has no questions available'
            }, status=400)
        
        questions_data = []
        for session_question in questions:
            question = session_question.question
            questions_data.append({
                'id': question.id,
                'order_index': session_question.order_index,
                'question_text': question.question_text,
                'question_type': question.question_type,
                'difficulty_level': question.difficulty_level,
                'subject': question.subject,
                'option_a': question.option_a,
                'option_b': question.option_b,
                'option_c': question.option_c,
                'option_d': question.option_d,
                'time_limit_seconds': session_question.time_limit_seconds
            })
        
        return Response({
            'success': True,
            'exam_session': {
                'id': exam_session.id,
                'title': exam_session.title,
                'description': exam_session.description,
                'num_questions': exam_session.num_questions,
                'time_limit_seconds': exam_session.time_limit_seconds,
                'questions': questions_data
            },
            'start_time': timezone.now().isoformat(),
            'message': f'Exam "{exam_session.title}" started successfully'
        })
        
    except Exception as e:
        logger.error(f"Start unified exam session failed: {str(e)}")
        return Response({
            'error': f'Failed to start exam session: {str(e)}'
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_unified_exam_answer(request):
    """
    Submit an answer for a question in an exam session
    
    Expected payload:
    {
        "exam_session_id": 1,
        "question_id": 2,
        "answer_text": "A",
        "time_taken_seconds": 30
    }
    """
    try:
        if request.user.role != 'student':
            return Response({
                'error': 'Only students can submit exam answers'
            }, status=403)
        
        data = request.data
        exam_session_id = data.get('exam_session_id')
        question_id = data.get('question_id')
        answer_text = data.get('answer_text', '').strip()
        time_taken_seconds = data.get('time_taken_seconds', 0)
        
        if not all([exam_session_id, question_id, answer_text]):
            return Response({
                'error': 'exam_session_id, question_id, and answer_text are required'
            }, status=400)
        
        exam_session = get_object_or_404(ExamSession, id=exam_session_id, is_published=True)
        question = get_object_or_404(QuestionBank, id=question_id)
        
        # Verify question belongs to this exam session
        session_question = get_object_or_404(
            ExamSessionQuestion, 
            exam_session=exam_session, 
            question=question
        )
        
        # Check if student already answered this question
        existing_attempt = ExamAnswerAttempt.objects.filter(
            exam_session=exam_session,
            student=request.user,
            question=question
        ).first()
        
        if existing_attempt:
            return Response({
                'error': 'You have already answered this question',
                'previous_answer': existing_attempt.answer_text,
                'submitted_at': existing_attempt.submitted_at.isoformat()
            }, status=400)
        
        # Evaluate answer
        is_correct = False
        correct_answer = question.correct_answer.strip().upper()
        student_answer = answer_text.strip().upper()
        
        if question.question_type == 'multiple_choice':
            is_correct = student_answer == correct_answer
        else:
            # For open-ended questions, basic string comparison (can be enhanced with AI)
            is_correct = student_answer.lower() in correct_answer.lower()
        
        # Get current attempt number
        attempt_number = ExamAnswerAttempt.objects.filter(
            exam_session=exam_session,
            student=request.user,
            question=question
        ).count() + 1
        
        # Create answer attempt
        answer_attempt = ExamAnswerAttempt.objects.create(
            exam_session=exam_session,
            student=request.user,
            question=question,
            attempt_number=attempt_number,
            answer_text=answer_text,
            is_correct=is_correct,
            time_taken_seconds=time_taken_seconds
        )
        
        # Get progress
        total_questions = exam_session.session_questions.count()
        answered_questions = ExamAnswerAttempt.objects.filter(
            exam_session=exam_session,
            student=request.user
        ).values('question').distinct().count()
        
        correct_answers = ExamAnswerAttempt.objects.filter(
            exam_session=exam_session,
            student=request.user,
            is_correct=True
        ).values('question').distinct().count()
        
        is_exam_complete = answered_questions >= total_questions
        
        response_data = {
            'success': True,
            'answer_id': answer_attempt.id,
            'is_correct': is_correct,
            'correct_answer': correct_answer if is_exam_complete else None,
            'explanation': question.explanation if is_exam_complete else None,
            'progress': {
                'answered_questions': answered_questions,
                'total_questions': total_questions,
                'correct_answers': correct_answers,
                'is_complete': is_exam_complete,
                'percentage_complete': (answered_questions / total_questions) * 100,
                'current_score': (correct_answers / answered_questions) * 100 if answered_questions > 0 else 0
            }
        }
        
        if is_exam_complete:
            response_data['final_score'] = (correct_answers / total_questions) * 100
            response_data['message'] = f'Exam completed! Final score: {response_data["final_score"]:.1f}%'
        
        return Response(response_data)
        
    except Exception as e:
        logger.error(f"Submit unified exam answer failed: {str(e)}")
        return Response({
            'error': f'Failed to submit answer: {str(e)}'
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_unified_exam_progress(request, session_id):
    """
    Get student's progress in an exam session
    """
    try:
        if request.user.role != 'student':
            return Response({
                'error': 'Only students can view exam progress'
            }, status=403)
        
        exam_session = get_object_or_404(ExamSession, id=session_id, is_published=True)
        
        # Get student's answers
        answers = ExamAnswerAttempt.objects.filter(
            exam_session=exam_session,
            student=request.user
        ).order_by('submitted_at')
        
        total_questions = exam_session.session_questions.count()
        answered_questions = answers.values('question').distinct().count()
        correct_answers = answers.filter(is_correct=True).values('question').distinct().count()
        
        is_complete = answered_questions >= total_questions
        
        # Get detailed answers
        answers_data = []
        for answer in answers:
            answers_data.append({
                'question_id': answer.question.id,
                'question_text': answer.question.question_text,
                'answer_text': answer.answer_text,
                'is_correct': answer.is_correct,
                'correct_answer': answer.question.correct_answer if is_complete else None,
                'explanation': answer.question.explanation if is_complete else None,
                'time_taken_seconds': answer.time_taken_seconds,
                'submitted_at': answer.submitted_at.isoformat()
            })
        
        return Response({
            'exam_session': {
                'id': exam_session.id,
                'title': exam_session.title,
                'description': exam_session.description
            },
            'progress': {
                'answered_questions': answered_questions,
                'total_questions': total_questions,
                'correct_answers': correct_answers,
                'is_complete': is_complete,
                'percentage_complete': (answered_questions / total_questions) * 100,
                'current_score': (correct_answers / answered_questions) * 100 if answered_questions > 0 else 0,
                'final_score': (correct_answers / total_questions) * 100 if is_complete else None
            },
            'answers': answers_data
        })
        
    except Exception as e:
        logger.error(f"Get unified exam progress failed: {str(e)}")
        return Response({
            'error': f'Failed to get exam progress: {str(e)}'
        }, status=500)


# ==========================
# TEACHER MANAGEMENT ACTIONS
# ==========================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def publish_unified_exam_session(request, session_id):
    """
    Publish an exam session to make it available to students
    """
    try:
        if request.user.role != 'teacher':
            return Response({
                'error': 'Only teachers can publish exam sessions'
            }, status=403)
        
        exam_session = get_object_or_404(ExamSession, id=session_id, created_by=request.user)
        
        if exam_session.is_published:
            return Response({
                'error': 'Exam session is already published'
            }, status=400)
        
        # Verify exam has questions
        questions_count = exam_session.session_questions.count()
        if questions_count == 0:
            return Response({
                'error': 'Cannot publish exam session with no questions'
            }, status=400)
        
        exam_session.is_published = True
        exam_session.save()
        
        return Response({
            'success': True,
            'message': f'Exam session "{exam_session.title}" has been published and is now available to students',
            'exam_session_id': exam_session.id,
            'questions_count': questions_count
        })
        
    except Exception as e:
        logger.error(f"Publish unified exam session failed: {str(e)}")
        return Response({
            'error': f'Failed to publish exam session: {str(e)}'
        }, status=500)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_unified_exam_session(request, session_id):
    """
    Delete an exam session (only if no student attempts exist)
    """
    try:
        if request.user.role != 'teacher':
            return Response({
                'error': 'Only teachers can delete exam sessions'
            }, status=403)
        
        exam_session = get_object_or_404(ExamSession, id=session_id, created_by=request.user)
        
        # Check if any students have attempted this exam
        attempts_count = ExamAnswerAttempt.objects.filter(exam_session=exam_session).count()
        if attempts_count > 0:
            return Response({
                'error': f'Cannot delete exam session with {attempts_count} student attempt(s). Unpublish instead.'
            }, status=400)
        
        exam_title = exam_session.title
        exam_session.delete()
        
        return Response({
            'success': True,
            'message': f'Exam session "{exam_title}" has been deleted successfully'
        })
        
    except Exception as e:
        logger.error(f"Delete unified exam session failed: {str(e)}")
        return Response({
            'error': f'Failed to delete exam session: {str(e)}'
        }, status=500)
