import logging
import random 
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .models import Exam, ExamSession, QuestionBank, StudentAnswer, User, QuestionAttempt
from .adaptive_testing_engine import AdaptiveExamSession
from .answer_evaluator import AnswerEvaluator


logger = logging.getLogger(__name__)


@extend_schema(
    description="Start an exam session for a student.",
    request=dict,
    responses={200: dict}
)
class StartExamView(APIView):
    def post(self, request, exam_id):
        try:
            student_id = request.data.get("student_id")
            student = User.objects.get(id=student_id, role="student")

            exam = Exam.objects.get(id=exam_id)
            session = ExamSession.objects.create(exam=exam, student=student)

            # Get questions by difficulty level
            level_3_questions = list(QuestionBank.objects.filter(exam=exam, difficulty_level=3))
            level_4_questions = list(QuestionBank.objects.filter(exam=exam, difficulty_level=4))
            level_5_questions = list(QuestionBank.objects.filter(exam=exam, difficulty_level=5))
            
            # Select random questions with the specified distribution
            selected_questions = []
            
            # 30% from Level 3 (3 questions)
            if len(level_3_questions) >= 3:
                selected_questions.extend(random.sample(level_3_questions, 3))
            else:
                selected_questions.extend(level_3_questions)  # Take all if less than 3
            
            # 30% from Level 4 (3 questions)
            if len(level_4_questions) >= 3:
                selected_questions.extend(random.sample(level_4_questions, 3))
            else:
                selected_questions.extend(level_4_questions)  # Take all if less than 3
            
            # 40% from Level 5 (4 questions)
            if len(level_5_questions) >= 4:
                selected_questions.extend(random.sample(level_5_questions, 4))
            else:
                selected_questions.extend(level_5_questions)  # Take all if less than 4
            
            # Shuffle the selected questions for random order
            random.shuffle(selected_questions)
            
            # Store only essential data in session (not the full object)
            request.session["adaptive_exam"] = {
                "exam_session_id": session.id,
                "current_index": 0,
                "answers": {},
                "exam_id": exam_id,
                "selected_question_ids": [q.id for q in selected_questions],  # Store selected question IDs
                "total_selected_questions": len(selected_questions)
            }
            request.session.modified = True

            return Response({
                "success": True,
                "session_id": session.id,
                "total_questions": len(selected_questions),
                "question_distribution": {
                    "level_3_selected": len([q for q in selected_questions if q.difficulty_level == 3]),
                    "level_4_selected": len([q for q in selected_questions if q.difficulty_level == 4]),
                    "level_5_selected": len([q for q in selected_questions if q.difficulty_level == 5])
                }
            })
        except Exception as e:
            logger.error("Start exam failed: %s", e)
            return Response({"success": False, "error": str(e)}, status=500)

@extend_schema(
    description="Submit an answer to a question. Evaluates correctness, updates session, and returns next question.",
    request=dict,
    responses={200: dict}
)
@extend_schema(
    description="Submit an answer for a question in an exam.",
    request=dict,
    responses={200: dict}
)

class SubmitAnswerView(APIView):
    def post(self, request, exam_id):
        try:
            # Get raw body first (before Django processes it)
            raw_body = request.body.decode('utf-8', errors='ignore')
            
            # Try to parse JSON normally first
            import json
            try:
                request_data = json.loads(raw_body)
                session_id = request_data.get("exam_session_id")
                question_id = request_data.get("question_id")
                answer_text = request_data.get("answer")
            except json.JSONDecodeError:
                # If JSON parsing fails, clean the raw body and try again
                cleaned_body = raw_body.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
                request_data = json.loads(cleaned_body)
                session_id = request_data.get("exam_session_id")
                question_id = request_data.get("question_id")
                answer_text = request_data.get("answer")

            # Clean the answer text
            if answer_text:
                answer_text = str(answer_text).replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
                answer_text = ' '.join(answer_text.split())

            exam_session = ExamSession.objects.get(id=session_id)
            question = QuestionBank.objects.get(id=question_id)
            
            # Get selected questions from session
            #session_data = request.session.get("adaptive_exam", {})
            session_data = dict(request.session.get("adaptive_exam", {}))
            selected_question_ids = session_data.get("selected_question_ids", [])
            total_selected_questions = session_data.get("total_selected_questions", 10)
            
            # Calculate points per question (100 divided by selected questions)
            points_per_question = 100.0 / total_selected_questions if total_selected_questions > 0 else 10.0

            # Use improved evaluator with calculated points
            evaluator = AnswerEvaluator()
            is_correct, score = evaluator.evaluate_answer(
                question_text=question.question_text,
                correct_answer=question.correct_answer,
                student_answer=answer_text,
                question_type=question.question_type,
                sample_answer=question.sample_answer,
                max_points=points_per_question
            )

            # Store the answer with score
            StudentAnswer.objects.create(
                exam=exam_session.exam,
                question=question,
                student=exam_session.student,
                answer=answer_text,
                is_correct=is_correct,
                score=score
            )

            # Update session data
            session_data["answers"] = session_data.get("answers", {})
            session_data["answers"][question_id] = {
                "answer": answer_text, 
                "is_correct": is_correct,
                "score": score
            }
            
            # Track attempts per question (DB-backed with session cache)
            try:
                # Get or create attempt record from DB
                attempt_record, created = QuestionAttempt.objects.get_or_create(
                    exam_session=exam_session,
                    question=question,
                    defaults={'attempt_count': 0}
                )
                
                # Increment attempt count
                attempt_record.attempt_count += 1
                attempt_record.save()
                
                # Also update session cache
                session_data["attempts"] = session_data.get("attempts", {})
                session_data["attempts"][str(question_id)] = attempt_record.attempt_count
                
                current_attempts = attempt_record.attempt_count
                should_advance = is_correct or current_attempts >= 3
                
                print(f"DEBUG: question_id={question_id}, current_attempts={current_attempts}")
                print(f"DEBUG: is_correct={is_correct}, should_advance={should_advance}")
                
                if should_advance:
                    if "current_index" not in session_data:
                        session_data["current_index"] = 0
                    session_data["current_index"] = session_data.get("current_index", 0) + 1
                    print(f"DEBUG: Advanced to index {session_data['current_index']}")
                
                request.session["adaptive_exam"] = session_data
                request.session.modified = True
                
            except Exception as attempt_error:
                print(f"DEBUG: Error in attempt tracking: {attempt_error}")
                current_attempts = 1
                should_advance = False

            # Get next question from selected questions
            current_index = session_data.get("current_index", 0)
            has_more_questions = current_index < len(selected_question_ids)
            
            next_question_data = None
            if has_more_questions:
                next_question_id = selected_question_ids[current_index]
                next_question = QuestionBank.objects.get(id=next_question_id)
                next_question_data = {
                    "id": next_question.id,
                    "question_text": next_question.question_text,
                    "option_a": next_question.option_a,
                    "option_b": next_question.option_b,
                    "option_c": next_question.option_c,
                    "option_d": next_question.option_d,
                    "difficulty_level": next_question.difficulty_level,
                    "question_number": current_index + 1,
                    "total_questions": len(selected_question_ids),
                    "question_type": next_question.question_type,
                    "points_per_question": round(points_per_question, 2)
                }

            return Response({
                "success": True,
                "is_correct": is_correct,
                "score": round(score, 2),
                "max_score": round(points_per_question, 2),
                "attempts_used": current_attempts,
                "attempts_remaining": max(0, 3 - current_attempts),
                "should_advance": should_advance,
                "next_question": next_question_data,
                "has_more_questions": has_more_questions,
                "message": f"Answer submitted successfully. Score: {round(score, 2)}/{round(points_per_question, 2)}"
            })
        except Exception as e:
            logger.error("Submit answer failed: %s", e)
            return Response({"success": False, "error": str(e)}, status=500)

@extend_schema(
    description="Finish an exam session and return results summary.",
    request=dict,
    responses={200: dict}
)
class FinishExamView(APIView):
    def post(self, request, exam_id):
        try:
            session_id = request.data.get("exam_session_id")
            exam_session = ExamSession.objects.get(id=session_id)

            # Get all answers for this student in this exam
            answers = StudentAnswer.objects.filter(exam=exam_session.exam, student=exam_session.student)
            
            # Count unique questions answered correctly
            correct_question_ids = answers.filter(is_correct=True).values_list('question_id', flat=True).distinct()
            correct_answers = len(correct_question_ids)
            
            # Get total questions in the exam from the database
            total_questions_in_exam = QuestionBank.objects.filter(exam=exam_session.exam).count()
            
            # Count total questions actually answered
            questions_answered = answers.values_list('question_id', flat=True).distinct().count()

            return Response({
                "success": True,
                "exam_session_id": session_id,
                "questions_answered": questions_answered,
                "total_questions_in_exam": total_questions_in_exam,
                "correct_answers": correct_answers,
                "total_score_earned": correct_answers,  # Simple count
                "max_possible_score": total_questions_in_exam,
                "percentage_of_exam_completed": round((questions_answered / total_questions_in_exam) * 100, 2) if total_questions_in_exam > 0 else 0,
                "percentage_of_answered_correct": round((correct_answers / questions_answered) * 100, 2) if questions_answered > 0 else 0
            })
        except Exception as e:
            logger.error("Finish exam failed: %s", e)
            return Response({"success": False, "error": str(e)}, status=500)
            
@extend_schema(
    description="Get questions for an exam.",
    responses={200: dict}
)
class GetExamQuestionsView(APIView):
    def get(self, request, exam_id):
        try:
            exam = Exam.objects.get(id=exam_id)
            questions = QuestionBank.objects.filter(exam=exam)
            
            questions_data = []
            for q in questions:
                questions_data.append({
                    "id": q.id,
                    "question_text": q.question_text,
                    #"option_a": q.option_a,
                    #"option_b": q.option_b,
                    #"option_c": q.option_c,
                    #"option_d": q.option_d,
                    "difficulty_level": q.difficulty_level
                })

            print(f"DEBUG: Returning {len(questions_data)} questions")
            print(f"DEBUG: First question: {questions_data[0] if questions_data else 'No questions'}")
            
            
            return Response({
                "success": True,
                "exam_id": exam_id,
                "questions": questions_data
            })
        except Exception as e:
            print(f"DEBUG: Error in GetExamQuestionsView: {e}")
            return Response({"success": False, "error": str(e)}, status=500)
    
@extend_schema(
    description="Get the next question in an interactive exam session.",
    responses={200: dict}
)
class GetNextQuestionView(APIView):
    def get(self, request, exam_id):
        try:
            session_id = request.data.get("exam_session_id")
            exam_session = ExamSession.objects.get(id=session_id)
            
            # Get session data (simplified approach)
            session_data = request.session.get("adaptive_exam", {})
            current_index = session_data.get("current_index", 0)
            
            # Get questions from database
            questions = QuestionBank.objects.filter(exam=exam_session.exam).order_by('difficulty_level')
            questions_list = list(questions)
            
            has_more_questions = current_index < len(questions_list)
            
            if has_more_questions:
                next_question = questions_list[current_index]
                question_data = {
                    "id": next_question.id,
                    "question_text": next_question.question_text,
                    "option_a": next_question.option_a,
                    "option_b": next_question.option_b,
                    "option_c": next_question.option_c,
                    "option_d": next_question.option_d,
                    "difficulty_level": next_question.difficulty_level,
                    "question_number": current_index + 1,
                    "total_questions": len(questions_list)
                }
                
                return Response({
                    "success": True,
                    "question": question_data,
                    "has_more_questions": True
                })
            else:
                return Response({
                    "success": True,
                    "question": None,
                    "has_more_questions": False,
                    "message": "No more questions. You can finish the exam."
                })
                
        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=500)

@extend_schema(
    description="Get list of all exams",
    responses={200: dict}
)
class GetExamsView(APIView):
    def get(self, request):
        try:
            exams = Exam.objects.all().order_by('-created_at')
            
            exam_list = []
            for exam in exams:
                # Get question count for each exam
                question_count = QuestionBank.objects.filter(exam=exam).count()
                
                exam_list.append({
                    "id": exam.id,
                    "title": f"Exam {exam.id}",  # You can add a title field to Exam model later
                    "document_title": exam.document.title if exam.document else "Unknown Document",
                    "total_questions": question_count,
                    "created_at": exam.created_at.isoformat()
                })
            
            return Response({
                "success": True,
                "exams": exam_list
            })
        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=500)

@extend_schema(
    description="Get exam results for teachers",
    responses={200: dict}
)
class GetExamResultsView(APIView):
    def get(self, request, exam_id):
        try:
            exam = Exam.objects.get(id=exam_id)
            
            # Get all exam sessions for this exam
            sessions = ExamSession.objects.filter(exam=exam)
            
            results = []
            for session in sessions:
                # Get student's answers (same logic as FinishExamView)
                answers = StudentAnswer.objects.filter(exam=session.exam, student=session.student)
                
                # Get session data to determine selected questions
                # Note: We'll use a fallback since we don't have access to the original session
                total_questions_in_exam = QuestionBank.objects.filter(exam=exam).count()
                
                # Calculate scores using the same logic as FinishExamView
                total_score_earned = sum(answer.score for answer in answers)
                total_questions_answered = answers.count()
                
                # Calculate points per question (same as FinishExamView)
                points_per_question = 100.0 / total_questions_in_exam if total_questions_in_exam > 0 else 10.0
                
                # Count correct answers using the same logic as FinishExamView
                correct_question_ids = answers.filter(is_correct=True).values_list('question_id', flat=True).distinct()
                correct_answers = len(correct_question_ids)
                
                # Get individual scores for each question (same as FinishExamView)
                individual_scores = []
                for answer in answers:
                    individual_scores.append({
                        "question_id": answer.question.id,
                        "question_text": answer.question.question_text,
                        "student_answer": answer.answer,
                        "is_correct": answer.is_correct,
                        "score": answer.score,
                        "max_score": points_per_question,
                        "submitted_at": answer.submitted_at.isoformat()
                    })
                
                results.append({
                    "student_name": session.student.username,
                    "student_id": session.student.id,
                    "score": correct_answers,  # Count of correct questions
                    "total_questions": total_questions_in_exam,
                    "questions_answered": total_questions_answered,
                    "total_score_earned": round(total_score_earned, 2),
                    "max_possible_score": 100.0,
                    "percentage_of_exam_completed": round((total_questions_answered / total_questions_in_exam) * 100, 2) if total_questions_in_exam > 0 else 0,
                    "percentage_of_answered_correct": round((correct_answers / total_questions_answered) * 100, 2) if total_questions_answered > 0 else 0,
                    "points_per_question": round(points_per_question, 2),
                    "individual_scores": individual_scores,
                    "completed_at": session.completed_at,
                    "started_at": session.started_at
                })
            
            return Response({
                "success": True,
                "exam_id": exam_id,
                "results": results
            })
        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=500)
