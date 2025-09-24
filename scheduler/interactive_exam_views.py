import logging
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

            # Get questions for this exam
            questions = QuestionBank.objects.filter(exam=exam).order_by('difficulty_level')
            questions_list = list(questions)

            # Pass questions to AdaptiveExamSession
            adaptive = AdaptiveExamSession(questions_list)
            request.session["adaptive_exam"] = adaptive.to_dict()
            request.session.modified = True

            # Add this return statement back
            return Response({
                "success": True,
                "session_id": session.id,
                "total_questions": len(questions_list)
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
            session_id = request.data.get("exam_session_id")
            question_id = request.data.get("question_id")
            answer_text = request.data.get("answer")

            exam_session = ExamSession.objects.get(id=session_id)
            question = QuestionBank.objects.get(id=question_id)

            evaluator = AnswerEvaluator()
            is_correct, score = evaluator.evaluate_answer(
                question_text=question.question_text,
                correct_answer=question.correct_answer,
                student_answer=answer_text
            )

            StudentAnswer.objects.create(
                exam=exam_session.exam,
                question=question,
                student=exam_session.student,
                answer=answer_text,
                is_correct=is_correct
            )

            adaptive = AdaptiveExamSession.from_dict(request.session.get("adaptive_exam", {}))
            adaptive.submit_answer(question_id, answer_text, is_correct)
            request.session["adaptive_exam"] = adaptive.to_dict()
            request.session.modified = True

            # Get next question
            next_question = adaptive.get_next_question()
            next_question_data = None
            
            if next_question:
                next_question_data = {
                    "id": next_question.id,
                    "question_text": next_question.question_text,
                    "option_a": next_question.option_a,
                    "option_b": next_question.option_b,
                    "option_c": next_question.option_c,
                    "option_d": next_question.option_d,
                    "difficulty_level": next_question.difficulty_level,
                    "question_number": adaptive.current_index + 1,
                    "total_questions": len(adaptive.questions)
                }

            return Response({
                "success": True,
                "is_correct": is_correct,
                "score": score,
                "next_question": next_question_data,
                "has_more_questions": not adaptive.is_exam_complete(),
                "message": "Answer submitted successfully."
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
            correct = answers.filter(is_correct=True).count()
            total = answers.count()

            return Response({
                "success": True,
                "exam_session_id": session_id,
                "correct": correct,
                "total": total,
                "score_percent": (correct / total * 100) if total else 0
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
            
            # Get the adaptive session
            adaptive = AdaptiveExamSession.from_dict(request.session.get("adaptive_exam", {}))
            
            # Get next question
            next_question = adaptive.get_next_question()
            
            if next_question:
                question_data = {
                    "id": next_question.id,
                    "question_text": next_question.question_text,
                    "option_a": next_question.option_a,
                    "option_b": next_question.option_b,
                    "option_c": next_question.option_c,
                    "option_d": next_question.option_d,
                    "difficulty_level": next_question.difficulty_level,
                    "question_number": adaptive.current_index + 1,
                    "total_questions": len(adaptive.questions)
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