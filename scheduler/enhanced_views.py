"""
Enhanced Chat Views with RAG Implementation
Integrates document Q&A, conversation memory, and smart model selection
"""
import os
import tempfile
import json
from typing import Dict, Any, Optional

from django.shortcuts import render
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework import generics, permissions, viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .serializers import UserRegistrationSerializer, LessonSerializer
from .models import User, Lesson, ChatInteraction, Document
from .document_processing import document_processor

# LangChain imports
try:
    from langchain.memory import ConversationBufferMemory
    from langchain.schema import HumanMessage, AIMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

# SymPy and requests imports
from sympy import sympify
from sympy.core.sympify import SympifyError
import requests

# Store conversation memory per user (session-based)
user_memories = {}

def get_user_memory(user_id: int) -> Optional[ConversationBufferMemory]:
    """Get or create conversation memory for a specific user"""
    if not LANGCHAIN_AVAILABLE:
        return None
        
    if user_id not in user_memories:
        user_memories[user_id] = ConversationBufferMemory(
            return_messages=True,
            memory_key="chat_history"
        )
    return user_memories[user_id]

def clear_user_memory(user_id: int):
    """Clear conversation memory for a user"""
    if user_id in user_memories:
        del user_memories[user_id]

def detect_question_type(question: str) -> str:
    """Detect the type of question to route to appropriate handler"""
    question_lower = question.lower()
    
    # Math indicators
    math_indicators = [
        'calculate', 'solve', 'derivative', 'integral', 'equation',
        'algebra', 'geometry', 'trigonometry', 'logarithm', 'exponential',
        '+', '-', '*', '/', '^', '=', 'sin', 'cos', 'tan', 'sqrt'
    ]
    
    # Document indicators
    doc_indicators = [
        'document', 'pdf', 'explain this', 'what does this mean',
        'according to', 'in the document', 'summarize', 'based on'
    ]
    
    if any(indicator in question_lower for indicator in math_indicators):
        return 'math'
    elif any(indicator in question_lower for indicator in doc_indicators):
        return 'document'
    else:
        return 'general'

@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def enhanced_chat_interaction(request):
    """
    Enhanced chat with RAG, conversation memory, and smart routing
    """
    if request.method == 'GET':
        return Response({
            "message": "Enhanced AI Chat with RAG and Memory",
            "features": {
                "langchain_available": LANGCHAIN_AVAILABLE,
                "document_qa": True,
                "conversation_memory": True,
                "math_solver": True,
                "smart_routing": True
            }
        })
    
    question = request.data.get('question', '').strip()
    document_id = request.data.get('document_id')  # Optional document to query
    user = request.user
    
    if not question:
        return Response({"error": "Missing question"}, status=400)
    
    # Get conversation memory
    memory = get_user_memory(user.id)
    
    # Detect question type for smart routing
    question_type = detect_question_type(question)
    answer = ""
    method_used = ""
    sources = []
    
    try:
        # 1. Math Problem Solving (highest priority)
        if question_type == 'math':
            try:
                expr = sympify(question)
                result = expr.evalf()
                answer = f"Mathematical solution: {question} = {result}"
                method_used = "sympy_math"
            except SympifyError:
                # Not a direct math expression, try AI math solver
                question_type = 'general'  # Fall through to AI
        
        # 2. Document-specific Q&A with RAG
        if question_type == 'document' or document_id:
            if document_id:
                try:
                    document = Document.objects.get(id=document_id, uploaded_by=user)
                    if document.processing_status == 'completed':
                        rag_result = document_processor.query_document(
                            document, question, memory
                        )
                        answer = rag_result['answer']
                        method_used = f"rag_{rag_result['method']}"
                        sources = rag_result['sources']
                    else:
                        answer = f"Document is still being processed (status: {document.processing_status})"
                        method_used = "document_processing"
                except Document.DoesNotExist:
                    answer = "Document not found or you don't have access to it."
                    method_used = "document_error"
            else:
                # No specific document, but question seems document-related
                # Try to find recent documents by user
                recent_docs = Document.objects.filter(
                    uploaded_by=user, 
                    processing_status='completed'
                ).order_by('-created_at')[:3]
                
                if recent_docs.exists():
                    # Try querying the most recent document
                    rag_result = document_processor.query_document(
                        recent_docs.first(), question, memory
                    )
                    answer = f"Based on your recent document '{recent_docs.first().title}':\n\n{rag_result['answer']}"
                    method_used = f"rag_recent_{rag_result['method']}"
                    sources = rag_result['sources']
                else:
                    # No documents available, fall through to general AI
                    question_type = 'general'
        
        # 3. General AI Chat with Conversation Memory
        if not answer and question_type == 'general':
            if LANGCHAIN_AVAILABLE and memory:
                # Enhanced prompt with conversation context
                chat_history = ""
                if hasattr(memory, 'chat_memory') and memory.chat_memory.messages:
                    recent_messages = memory.chat_memory.messages[-6:]  # Last 3 exchanges
                    for msg in recent_messages:
                        if hasattr(msg, 'content'):
                            role = "Student" if isinstance(msg, HumanMessage) else "AI"
                            chat_history += f"{role}: {msg.content}\n"
                
                enhanced_prompt = f"""You are a helpful educational AI assistant.

Previous conversation:
{chat_history}

Current question: {question}

Please provide a helpful, educational response. If this is a math problem, solve it step by step. If it's a general question, provide clear explanations suitable for students."""
                
                # Add to memory
                memory.chat_memory.add_user_message(question)
            else:
                enhanced_prompt = f"""You are a helpful educational AI assistant. 

Student question: {question}

Please provide a helpful, educational response."""
            
            # Send to Ollama
            data = {
                "model": "llama3.2",
                "prompt": enhanced_prompt,
                "stream": False
            }
            
            try:
                response = requests.post("http://localhost:11434/api/generate", json=data)
                response_data = response.json()
                answer = response_data.get("response", "Sorry, I didn't understand.")
                method_used = "ollama_general"
                
                # Add AI response to memory
                if LANGCHAIN_AVAILABLE and memory:
                    memory.chat_memory.add_ai_message(answer)
                    
            except Exception as e:
                answer = f"Error connecting to AI service: {str(e)}"
                method_used = "ollama_error"
    
    except Exception as e:
        answer = f"An error occurred: {str(e)}"
        method_used = "system_error"
    
    # Save to database with enhanced metadata
    chat_interaction = ChatInteraction.objects.create(
        student=user,
        question=question,
        answer=answer,
        topic=question_type.title(),
        difficulty_estimate=method_used,
        notes=json.dumps({
            'method': method_used,
            'sources_count': len(sources),
            'document_id': document_id,
            'has_memory': LANGCHAIN_AVAILABLE and memory is not None
        }) if sources or document_id else None,
        document_id=document_id if document_id else None
    )
    
    return Response({
        "answer": answer,
        "chat_id": chat_interaction.id,
        "method_used": method_used,
        "question_type": question_type,
        "sources": sources,
        "conversation_context": LANGCHAIN_AVAILABLE and memory is not None,
        "langchain_available": LANGCHAIN_AVAILABLE
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_document(request):
    """
    Upload and process documents for RAG
    """
    if 'document' not in request.FILES:
        return Response({"error": "No document file provided"}, status=400)
    
    uploaded_file = request.FILES['document']
    title = request.data.get('title', uploaded_file.name)
    
    # Validate file type
    allowed_extensions = ['.pdf', '.txt', '.png', '.jpg', '.jpeg']
    file_extension = os.path.splitext(uploaded_file.name)[1].lower()
    
    if file_extension not in allowed_extensions:
        return Response({
            "error": f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        }, status=400)
    
    # Determine document type
    if file_extension == '.pdf':
        doc_type = 'pdf'
    elif file_extension in ['.png', '.jpg', '.jpeg']:
        doc_type = 'image'
    else:
        doc_type = 'text'
    
    try:
        # Save file
        documents_dir = os.path.join('documents', str(request.user.id))
        file_path = default_storage.save(
            os.path.join(documents_dir, uploaded_file.name),
            ContentFile(uploaded_file.read())
        )
        
        # Create document record
        document = Document.objects.create(
            uploaded_by=request.user,
            title=title,
            document_type=doc_type,
            file_path=os.path.join(default_storage.location, file_path),
            processing_status='pending'
        )
        
        # Process document asynchronously (or synchronously for small files)
        if uploaded_file.size < 5 * 1024 * 1024:  # 5MB
            # Process immediately for small files
            success = document_processor.process_document(document)
            
            return Response({
                "document_id": document.id,
                "title": document.title,
                "processing_status": document.processing_status,
                "processing_success": success,
                "message": "Document uploaded and processed successfully" if success 
                          else "Document uploaded but processing failed"
            })
        else:
            # For larger files, queue for background processing
            return Response({
                "document_id": document.id,
                "title": document.title,
                "processing_status": "pending",
                "message": "Document uploaded. Processing will complete shortly."
            })
            
    except Exception as e:
        return Response({"error": f"Upload failed: {str(e)}"}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_documents(request):
    """
    List user's uploaded documents
    """
    documents = Document.objects.filter(uploaded_by=request.user).order_by('-created_at')
    
    document_list = []
    for doc in documents:
        metadata = {}
        if doc.metadata:
            try:
                metadata = json.loads(doc.metadata)
            except:
                pass
        
        document_list.append({
            "id": doc.id,
            "title": doc.title,
            "document_type": doc.document_type,
            "processing_status": doc.processing_status,
            "created_at": doc.created_at.isoformat(),
            "metadata": metadata,
            "has_text": bool(doc.extracted_text),
            "processing_error": doc.processing_error
        })
    
    return Response({
        "documents": document_list,
        "total_count": len(document_list)
    })

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_document(request, document_id):
    """
    Delete a document and its associated files
    """
    try:
        document = Document.objects.get(id=document_id, uploaded_by=request.user)
        
        # Delete physical file
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
        
        # Delete vector store
        vector_path = os.path.join(default_storage.location, 'vectors', f'doc_{document.id}')
        if os.path.exists(vector_path):
            import shutil
            shutil.rmtree(vector_path)
        
        # Delete database record
        document.delete()
        
        return Response({"message": "Document deleted successfully"})
        
    except Document.DoesNotExist:
        return Response({"error": "Document not found"}, status=404)
    except Exception as e:
        return Response({"error": f"Deletion failed: {str(e)}"}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chat_history(request):
    """
    Get user's chat history with enhanced metadata
    """
    limit = int(request.GET.get('limit', 20))
    document_id = request.GET.get('document_id')
    
    queryset = ChatInteraction.objects.filter(student=request.user)
    
    if document_id:
        queryset = queryset.filter(document_id=document_id)
    
    chats = queryset.order_by('-created_at')[:limit]
    
    history = []
    for chat in chats:
        notes = {}
        if chat.notes:
            try:
                notes = json.loads(chat.notes)
            except:
                pass
        
        history.append({
            "id": chat.id,
            "question": chat.question,
            "answer": chat.answer,
            "created_at": chat.created_at.isoformat(),
            "topic": chat.topic,
            "method_used": chat.difficulty_estimate,  # Repurposed field
            "document_id": chat.document.id if chat.document else None,
            "document_title": chat.document.title if chat.document else None,
            "metadata": notes
        })
    
    return Response({
        "history": history,
        "total_conversations": ChatInteraction.objects.filter(student=request.user).count()
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def clear_conversation_memory(request):
    """
    Clear user's conversation memory
    """
    clear_user_memory(request.user.id)
    
    return Response({
        "message": "Conversation memory cleared",
        "langchain_available": LANGCHAIN_AVAILABLE
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def document_summary(request, document_id):
    """
    Get document summary and metadata
    """
    try:
        document = Document.objects.get(id=document_id, uploaded_by=request.user)
        
        metadata = {}
        if document.metadata:
            try:
                metadata = json.loads(document.metadata)
            except:
                pass
        
        # Generate summary if document is processed
        summary = ""
        if document.processing_status == 'completed' and document.extracted_text:
            text_preview = document.extracted_text[:1000]
            summary = f"Document contains {len(document.extracted_text)} characters of text. Preview: {text_preview}..."
        
        return Response({
            "id": document.id,
            "title": document.title,
            "document_type": document.document_type,
            "processing_status": document.processing_status,
            "metadata": metadata,
            "summary": summary,
            "text_length": len(document.extracted_text) if document.extracted_text else 0,
            "created_at": document.created_at.isoformat()
        })
        
    except Document.DoesNotExist:
        return Response({"error": "Document not found"}, status=404)

# Keep existing classes unchanged
class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]

# Legacy endpoint for backward compatibility
@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def chat_interaction(request):
    """
    Legacy chat endpoint - forwards to enhanced version
    """
    return enhanced_chat_interaction(request)
