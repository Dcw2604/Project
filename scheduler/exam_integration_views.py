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
                },
                "grading_instructions": {
                    "type": "string",
                    "description": "Optional grading criteria for evaluating student answers (e.g., focus on algorithm complexity, clarity, correctness)"
                }
            },
            "required": ["file"],
        }
    },
    responses={200: dict}
)
# scheduler/exam_integration_views.py

class DocumentUploadView(APIView):
    def post(self, request):
        try:
            file = request.FILES.get("file")
            if not file:
                return Response({"success": False, "error": "No file uploaded."}, status=400)
            
            grading_instructions = request.data.get("grading_instructions", "")
            
            # Create document
            doc = Document.objects.create(
                title=file.name,
                file=file,
                processing_status="pending",
                grading_instructions=grading_instructions,
            )

            # Extract text
            extracted_text = extract_text_from_file(doc.file.path)
            if not extracted_text:
                return Response({"success": False, "error": "Could not extract text from file."}, status=400)

            # Generate questions with Gemini (ONCE)
            processor = GenericDocumentProcessor()
            result = processor.process_document(extracted_text, str(doc.id))

            # Save questions to QuestionBank (NOT linked to Exam yet)
            questions_created = 0
            for lvl, key in [(3, "level_3_questions"), (4, "level_4_questions"), (5, "level_5_questions")]:
                for q in result.get(key, []):
                    question = QuestionBank.objects.create(
                        exam=None,  # Not linked to exam yet
                        document=doc,
                        question_text=q.get("question_text"),
                        question_type=q.get("question_type", "open_ended"),
                        expected_keywords=json.dumps(q.get("expected_keywords", [])),
                        sample_answer=q.get("sample_answer", ""),
                        option_a=q.get("option_a", ""),
                        option_b=q.get("option_b", ""),
                        option_c=q.get("option_c", ""),
                        option_d=q.get("option_d", ""),
                        correct_answer=q.get("correct_answer", ""),
                        explanation=q.get("explanation", ""),
                        difficulty_level=lvl,
                    )
                    
                    # Save topics
                    topics = q.get("topics", [])
                    if topics:
                        from .models import Topic, QuestionTopic
                        for topic_name in topics:
                            topic, _ = Topic.objects.get_or_create(name=topic_name)
                            QuestionTopic.objects.get_or_create(question=question, topic=topic)
                    
                    questions_created += 1

            # Update document
            doc.extracted_text = extracted_text
            doc.processing_status = "done"
            doc.questions_generated_count = questions_created
            doc.save()

            return Response({
                "success": True,
                "doc_id": doc.id,
                "questions_generated": questions_created,
                "result": result
            })
            
        except Exception as e:
            logger.error("Document upload failed: %s", e)
            return Response({"success": False, "error": str(e)}, status=500)

@extend_schema(
    description="Create an exam from an uploaded document. Generates questions and stores them.",
    request=dict,
    responses={200: dict}
)
# scheduler/exam_integration_views.py

class ExamCreationView(APIView):
    def post(self, request):
        try:
            doc_id = request.data.get("document_id")
            if not doc_id:
                return Response({"success": False, "error": "document_id missing."}, status=400)

            document = Document.objects.get(id=doc_id)
            
            # Check if questions already exist
            existing_questions = QuestionBank.objects.filter(document=document, exam__isnull=True)
            
            if existing_questions.exists():
                # Reuse existing questions
                logger.info(f"Reusing {existing_questions.count()} existing questions for document {doc_id}")
                
                # Create exam
                exam = Exam.objects.create(
                    document=document, 
                    total_questions=existing_questions.count()
                )
                
                # Link questions to exam
                existing_questions.update(exam=exam)
                
                return Response({
                    "success": True,
                    "exam_id": exam.id,
                    "questions": existing_questions.count(),
                    "reused": True
                })
            
            else:
                # Fallback: Generate questions if they don't exist
                logger.warning(f"No existing questions found for document {doc_id}, generating new ones")
                
                if not document.extracted_text:
                    return Response({"success": False, "error": "Document not processed."}, status=400)

                processor = GenericDocumentProcessor()
                result = processor.process_document(document.extracted_text, str(document.id))

                exam = Exam.objects.create(document=document, total_questions=result["total_questions"])
                
                for lvl, key in [(3, "level_3_questions"), (4, "level_4_questions"), (5, "level_5_questions")]:
                    for q in result.get(key, []):
                        question = QuestionBank.objects.create(
                            exam=exam,
                            document=document,
                            question_text=q.get("question_text"),
                            question_type=q.get("question_type", "open_ended"),
                            expected_keywords=json.dumps(q.get("expected_keywords", [])),
                            sample_answer=q.get("sample_answer", ""),
                            option_a=q.get("option_a", ""),
                            option_b=q.get("option_b", ""),
                            option_c=q.get("option_c", ""),
                            option_d=q.get("option_d", ""),
                            correct_answer=q.get("correct_answer", ""),
                            explanation=q.get("explanation", ""),
                            difficulty_level=lvl,
                        )
                        
                        topics = q.get("topics", [])
                        if topics:
                            from .models import Topic, QuestionTopic
                            for topic_name in topics:
                                topic, _ = Topic.objects.get_or_create(name=topic_name)
                                QuestionTopic.objects.get_or_create(question=question, topic=topic)
                
                return Response({
                    "success": True,
                    "exam_id": exam.id,
                    "questions": result["total_questions"],
                    "reused": False
                })
                
        except Exception as e:
            logger.error("Exam creation failed: %s", e)
            return Response({"success": False, "error": str(e)}, status=500)