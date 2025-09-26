import logging
import random 
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .models import Exam, ExamSession, QuestionBank, StudentAnswer, User
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
            session_data = request.session.get("adaptive_exam", {})
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
            session_data["current_index"] = session_data.get("current_index", 0) + 1
            request.session["adaptive_exam"] = session_data
            request.session.modified = True

            # Get next question from selected questions
            current_index = session_data["current_index"]
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

            answers = StudentAnswer.objects.filter(exam=exam_session.exam, student=exam_session.student)
            
            # ✅ FIX: Get the actual selected questions from session, not from database
            session_data = request.session.get("adaptive_exam", {})
            total_selected_questions = session_data.get("total_selected_questions", 10)
            
            # Calculate scores based on ACTUAL selected questions (10), not total created (15)
            total_score_earned = sum(answer.score for answer in answers)
            total_questions_answered = answers.count()
            
            # Calculate points per question based on selected questions (10), not total created (15)
            points_per_question = 100.0 / total_selected_questions if total_selected_questions > 0 else 10.0
            
            # Calculate what the maximum possible score would be if all selected questions were answered perfectly
            max_possible_if_all_answered = 100.0  # Always 100 points total
            max_possible_with_answered_questions = total_questions_answered * points_per_question
            
            correct_answers = answers.filter(is_correct=True).count()

            return Response({
                "success": True,
                "exam_session_id": session_id,
                "questions_answered": total_questions_answered,
                "total_questions_in_exam": total_selected_questions,  # ✅ Show actual selected questions (10)
                "correct_answers": correct_answers,
                "total_score_earned": round(total_score_earned, 2),
                "max_possible_score": max_possible_if_all_answered,
                "percentage_of_exam_completed": round((total_questions_answered / total_selected_questions) * 100, 2),  # ✅ Based on selected questions
                "percentage_of_answered_correct": round((correct_answers / total_questions_answered) * 100, 2) if total_questions_answered > 0 else 0,
                "points_per_question": round(points_per_question, 2),
                "individual_scores": [{"question_id": answer.question.id, "score": answer.score, "max_score": points_per_question} for answer in answers]
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
                    "option_a": q.option_a,
                    "option_b": q.option_b,
                    "option_c": q.option_c,
                    "option_d": q.option_d,
                    "difficulty_level": q.difficulty_level
                })
            
            return Response({
                "success": True,
                "exam_id": exam_id,
                "questions": questions_data
            })
        except Exception as e:
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
