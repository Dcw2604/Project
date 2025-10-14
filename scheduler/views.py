"""
API Views — Cleaned + Swagger Ready
-----------------------------------
- All endpoints use DRF APIView (so Swagger can detect them).
- Added @extend_schema for request/response documentation.
"""

import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .document_processing import DocumentProcessor
from .math_document_processor import MathDocumentProcessor
from .models import Document, Exam, QuestionBank, ExamSession, StudentAnswer, User
from .adaptive_testing_engine import AdaptiveExamSession
from .answer_evaluator import AnswerEvaluator
from .topic_extractor import TopicExtractor
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import TopicPerformance, StudentAnalytics


logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(levelname)s %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)


# ✅ Health check
@extend_schema(
    description="Simple health check endpoint",
    responses={200: {"status": "ok", "message": "Service is running."}}
)
class HealthCheckView(APIView):
    def get(self, request):
        return Response({"status": "ok", "message": "Service is running."})


# ✅ Document upload
@extend_schema(
    description="Upload a document for processing",
    request={"multipart/form-data": {"file": {"type": "string", "format": "binary"}}},
    responses={200: {"success": "boolean", "document_id": "integer"}}
)
class DocumentUploadView(APIView):
    def post(self, request):
        try:
            file = request.FILES.get("file")
            if not file:
                return Response({"success": False, "error": "No file uploaded."}, status=400)

            doc = Document.objects.create(
                title=file.name,
                file=file,
                processing_status="pending",
            )

            processor = DocumentProcessor()
            result = processor.process_document_unified(
                doc.file.path, doc.id, file_type=file.content_type.split("/")[0]
            )
            return Response({"success": True, "document_id": doc.id, "result": result})
        except Exception as e:
            logger.error("Document upload failed: %s", e)
            return Response({"success": False, "error": str(e)}, status=500)


# ✅ Exam creation
@extend_schema(
    description="Create an exam from a processed document",
    request={"application/json": {"document_id": "integer"}},
    responses={200: {"success": "boolean", "exam_id": "integer"}}
)
class ExamCreationView(APIView):
    def post(self, request):
        try:
            doc_id = request.data.get("document_id")
            if not doc_id:
                return Response({"success": False, "error": "document_id missing."}, status=400)

            document = Document.objects.get(id=doc_id)
            if not document.extracted_text:
                return Response({"success": False, "error": "Document not processed."}, status=400)

            math_proc = MathDocumentProcessor()
            result = math_proc.process_math_document(document.extracted_text, document.id)

            exam = Exam.objects.create(document=document, total_questions=result["total_questions"])
            for lvl, key in [(3, "level_3_questions"), (4, "level_4_questions"), (5, "level_5_questions")]:
                for q in result.get(key, []):
                    QuestionBank.objects.create(
                        exam=exam,
                        document=document,
                        question_text=q.get("question_text"),
                        option_a=q.get("option_a"),
                        option_b=q.get("option_b"),
                        option_c=q.get("option_c"),
                        option_d=q.get("option_d"),
                        correct_answer=q.get("correct_answer"),
                        explanation=q.get("explanation", ""),
                        difficulty_level=lvl,
                    )
            from .topic_extractor import TopicExtractor
            topic_extractor = TopicExtractor()
            
            # קבל את כל השאלות שנשמרו
            saved_questions = QuestionBank.objects.filter(exam=exam)
            
            # הקצה נושאים לכל שאלה
            for question_obj in saved_questions:
                topic_extractor.assign_topics_to_question(question_obj)
            
            logger.info(f"Assigned topics to {saved_questions.count()} questions")
            
            return Response({"success": True, "exam_id": exam.id, "questions": result["total_questions"]})

        except Exception as e:
            logger.error("Exam creation failed: %s", e)
            return Response({"success": False, "error": str(e)}, status=500)


# ✅ Start exam
@extend_schema(
    description="Start a new exam session for a student",
    request={"application/json": {"student_id": "integer"}},
    responses={200: {"success": "boolean", "exam_session_id": "integer"}}
)
class StartExamView(APIView):
    def post(self, request, exam_id):
        try:
            student_id = request.data.get("student_id")
            student = User.objects.get(id=student_id, role="student")

            exam = Exam.objects.get(id=exam_id)
            session = ExamSession.objects.create(exam=exam, student=student)

            adaptive = AdaptiveExamSession()
            request.session["adaptive_exam"] = adaptive.to_dict()
            request.session.modified = True

            return Response({
                "success": True,
                "exam_session_id": session.id,
                "message": "Exam started."
            })
        except Exception as e:
            logger.error("Start exam failed: %s", e)
            return Response({"success": False, "error": str(e)}, status=500)


# ✅ Submit answer
@extend_schema(
    description="Submit an answer and receive next question",
    request={"application/json": {
        "exam_session_id": "integer",
        "question_id": "integer",
        "answer": "string"
    }},
    responses={200: {"success": "boolean", "is_correct": "boolean", "next_question": "object|null"}}
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
            adaptive.record_answer(question_id, is_correct)
            request.session["adaptive_exam"] = adaptive.to_dict()
            request.session.modified = True

            next_q = adaptive.select_next_question(list(QuestionBank.objects.filter(exam=exam_session.exam)))
            next_q_data = None
            if next_q:
                next_q_data = {
                    "id": next_q.id,
                    "text": next_q.question_text,
                    "options": {
                        "A": next_q.option_a,
                        "B": next_q.option_b,
                        "C": next_q.option_c,
                        "D": next_q.option_d,
                    },
                    "difficulty": next_q.difficulty_level
                }

            return Response({
                "success": True,
                "is_correct": is_correct,
                "score": score,
                "next_question": next_q_data
            })

        except Exception as e:
            logger.error("Submit answer failed: %s", e)
            return Response({"success": False, "error": str(e)}, status=500)


# ✅ Finish exam
@extend_schema(
    description="Finish an exam session and calculate final score",
    request={"application/json": {"exam_session_id": "integer"}},
    responses={200: {"success": "boolean", "final_score": "integer"}}
)
class FinishExamView(APIView):
    def post(self, request, exam_id):
        try:
            session_id = request.data.get("exam_session_id")
            exam_session = ExamSession.objects.get(id=session_id)

            answers = StudentAnswer.objects.filter(exam=exam_session.exam, student=exam_session.student)
            final_score = sum(1 for a in answers if a.is_correct)

            return Response({"success": True, "final_score": final_score})
        except Exception as e:
            logger.error("Finish exam failed: %s", e)
            return Response({"success": False, "error": str(e)}, status=500)
