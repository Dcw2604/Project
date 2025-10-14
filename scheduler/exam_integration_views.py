import logging
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .document_processing import GenericDocumentProcessor
from .document_utils import extract_text_from_file
from .models import Document, Exam, QuestionBank

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@extend_schema(
    description="Upload a document (PDF/Image/Text). The system extracts content and prepares for exam creation.",
        request={
        "multipart/form-data": {
            "type": "object",
            "properties": {
                "file": {
                    "type": "string",
                    "format": "binary",
                    "description": "Upload a PDF, image or text file"
                }
            },
            "required": ["file"],
        }
    },
    responses={200: dict}
)
class DocumentUploadView(APIView):
    def post(self, request):
        try:
            file = request.FILES.get("file")
            if not file:
                return Response({"success": False, "error": "No file uploaded."}, status=400)

            # שמירה במסד נתונים
            doc = Document.objects.create(
                title=file.name,
                file=file,
                processing_status="pending",
            )

            # Extract text from file using the correct function
            extracted_text = extract_text_from_file(doc.file.path)
            
            if not extracted_text:
                return Response({"success": False, "error": "Could not extract text from file."}, status=400)

            # קריאה למנוע העיבוד
            processor = GenericDocumentProcessor()
            result = processor.process_document(extracted_text, str(doc.id))

            doc.extracted_text = extracted_text
            doc.processing_status = "done"
            doc.save()

            return Response({"success": True, "doc_id": doc.id, "result": result})
        except Exception as e:
            logger.error("Document upload failed: %s", e)
            return Response({"success": False, "error": str(e)}, status=500)


@extend_schema(
    description="Create an exam from an uploaded document. Generates questions and stores them.",
    request=dict,
    responses={200: dict}
)
class ExamCreationView(APIView):
    def post(self, request):
        try:
            body = request.data
            doc_id = body.get("document_id")
            if not doc_id:
                return Response({"success": False, "error": "document_id missing."}, status=400)

            document = Document.objects.get(id=doc_id)
            if not document.extracted_text:
                return Response({"success": False, "error": "Document not processed."}, status=400)

            processor = GenericDocumentProcessor()
            result = processor.process_document(document.extracted_text, str(document.id))

            exam = Exam.objects.create(document=document, total_questions=result["total_questions"])
            for lvl, key in [(3, "level_3_questions"), (4, "level_4_questions"), (5, "level_5_questions")]:
                for q in result.get(key, []):
                    logger.info(f"DEBUG: Processing question at level {lvl}, question_text: {q.get('question_text', '')[:100]}")
                    question = QuestionBank.objects.create(
                        exam=exam,
                        document=document,
                        question_text=q.get("question_text"),
                        question_type=q.get("question_type", "open_ended"),
                        expected_keywords=json.dumps(q.get("expected_keywords", [])),
                        sample_answer=q.get("sample_answer", ""),
                        # Keep multiple choice fields for backward compatibility
                        option_a=q.get("option_a", ""),
                        option_b=q.get("option_b", ""),
                        option_c=q.get("option_c", ""),
                        option_d=q.get("option_d", ""),
                        correct_answer=q.get("correct_answer", ""),
                        explanation=q.get("explanation", ""),
                        difficulty_level=lvl,
                 )
                    topics = q.get("topics", [])
                    logger.info(f"DEBUG: Question {question.id} at level {lvl}, has topics: {topics}")   #debug
                    if topics:
                        from .models import Topic, QuestionTopic
                        for topic_name in topics:
                            topic, _ = Topic.objects.get_or_create(name=topic_name)
                            QuestionTopic.objects.get_or_create(question=question, topic=topic)
                            logger.info(f"  Saved topic '{topic_name}' for Question {question.id}")
                    else:
                        logger.info(f"  No topics found in question data!")
            return Response({"success": True, "exam_id": exam.id, "questions": result["total_questions"]})
        except Exception as e:
            logger.error("Exam creation failed: %s", e)
            return Response({"success": False, "error": str(e)}, status=500)
