"""
Comprehensive Educational Chatbot with RAG (Retrieval-Augmented Generation)
Features:
- Math problem solving (SymPy)
- Document upload and Q&A (PDFPlumber + LangChain)
- Vector search and semantic retrieval (FAISS)
- Conversation memory (LangChain Memory)
- Multi-document support
- Smart model selection
"""
from django.shortcuts import render
from rest_framework import generics, permissions, viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import UserRegistrationSerializer, LessonSerializer
from .models import User, Lesson, ChatInteraction, Document
from .document_utils import document_processor, process_uploaded_document
from sympy import sympify
from sympy.core.sympify import SympifyError
import requests
import json
import os
import tempfile
import time
from datetime import datetime
from django.utils import timezone
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken

# LangChain imports with comprehensive error handling
try:
    from langchain.memory import ConversationBufferMemory
    from langchain.schema import HumanMessage, AIMessage, Document as LangChainDocument
    from langchain_community.llms import Ollama
    from langchain.chains import ConversationChain, RetrievalQA
    from langchain.prompts import PromptTemplate
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_community.vectorstores import FAISS
    from langchain_community.embeddings import OllamaEmbeddings
    LANGCHAIN_AVAILABLE = True
    print("✅ LangChain components loaded successfully")
except ImportError as e:
    LANGCHAIN_AVAILABLE = False
    print(f"❌ LangChain not available: {e}")

# Global storage for user sessions
user_conversation_memories = {}
user_vector_stores = {}

class ComprehensiveRAGProcessor:
    """
    Unified RAG processor handling all document and AI operations
    """
    
    def __init__(self):
        self.text_splitter = None
        self.embeddings = None
        self.llm = None
        self.memory_store = {}
        self.init_components()
    
    def init_components(self):
        """Initialize all LangChain components with robust error handling"""
        if not LANGCHAIN_AVAILABLE:
            print("⚠️  LangChain not available - using fallback mode")
            return
        
        try:
            # Enhanced text splitter for better document chunking
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1500,  # Larger chunks for more context
                chunk_overlap=300,  # More overlap for continuity
                length_function=len,
                separators=["\n\n", "\n", ". ", "! ", "? ", "; ", ", ", " ", ""]
            )
            
            # Embeddings for vector search
            self.embeddings = OllamaEmbeddings(
                model="llama3.2",
                base_url="http://localhost:11434"
            )
            
            # LLM for text generation
            self.llm = Ollama(
                model="llama3.2",
                base_url="http://localhost:11434",
                temperature=0.7
            )
            
            print("✅ RAG components initialized successfully")
            
        except Exception as e:
            print(f"❌ RAG initialization failed: {e}")
            self.text_splitter = None
            self.embeddings = None
            self.llm = None
    
    def create_vector_store(self, text: str, document_id: str):
        """Create FAISS vector store from document text with enhanced processing"""
        if not self.text_splitter or not self.embeddings:
            print(f"❌ Missing components for vector store creation")
            return None
        
        try:
            print(f"📄 Processing document {document_id}, text length: {len(text)}")
            
            # Preprocess text to ensure quality
            if not text or len(text.strip()) < 10:
                print(f"⚠️  Document text too short: {len(text)} characters")
                return None
            
            # Split text into chunks with better parameters
            chunks = self.text_splitter.split_text(text)
            
            if not chunks:
                print(f"⚠️  No chunks created for document {document_id}")
                return None
            
            print(f"📝 Created {len(chunks)} chunks")
            for i, chunk in enumerate(chunks[:3]):  # Show first 3 chunks
                print(f"   Chunk {i}: {len(chunk)} chars - {chunk[:100]}...")
            
            # Create documents with metadata
            documents = []
            for i, chunk in enumerate(chunks):
                if len(chunk.strip()) > 20:  # Only include meaningful chunks
                    doc = LangChainDocument(
                        page_content=chunk,
                        metadata={
                            "document_id": document_id,
                            "chunk_index": i,
                            "chunk_length": len(chunk),
                            "chunk_preview": chunk[:100]
                        }
                    )
                    documents.append(doc)
            
            if not documents:
                print(f"⚠️  No meaningful chunks found")
                return None
            
            # Create vector store
            vectorstore = FAISS.from_documents(documents, self.embeddings)
            
            print(f"✅ Created vector store: {len(documents)} meaningful chunks for doc {document_id}")
            return vectorstore
            
        except Exception as e:
            print(f"❌ Vector store creation failed: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def query_with_rag(self, vectorstore, question: str, conversation_history: str = "") -> str:
        """Enhanced RAG query with improved document retrieval"""
        if not self.llm or not vectorstore:
            return "Document search not available"
        
        try:
            print(f"🔍 Enhanced RAG Query Debug:")
            print(f"   Question: {question[:100]}...")
            print(f"   Vectorstore available: {vectorstore is not None}")
            
            # Test retrieval with multiple search strategies
            retriever = vectorstore.as_retriever(
                search_type="similarity", 
                search_kwargs={"k": 6}  # Get more chunks for better context
            )
            
            # Get relevant documents
            docs = retriever.get_relevant_documents(question)
            print(f"   Retrieved {len(docs)} documents")
            
            if not docs:
                print("   No documents retrieved! Trying fallback search...")
                # Fallback: try with broader keywords
                question_words = question.lower().split()
                broader_query = " OR ".join(question_words[:3])  # Use first 3 words
                docs = retriever.get_relevant_documents(broader_query)
                print(f"   Fallback retrieved {len(docs)} documents")
            
            if docs:
                print(f"   First doc preview: {docs[0].page_content[:200]}...")
                
                # Combine all retrieved content for maximum context
                combined_context = "\n\n---\n\n".join([doc.page_content for doc in docs])
                print(f"   Combined context length: {len(combined_context)}")
                
                # Enhanced prompt that forces the AI to use the document content
                enhanced_prompt = f"""You are an educational AI assistant. I am providing you with specific document content that contains the information needed to answer the student's question.

DOCUMENT CONTENT:
{combined_context}

STUDENT QUESTION: {question}

INSTRUCTIONS:
1. Read through ALL the document content above carefully
2. Look for ANY information that relates to the student's question
3. If you see questions, problems, exercises, or examples in the document, use them to help answer
4. Provide a detailed answer based on what you found in the document
5. If there are specific questions or problems shown in the document, solve or explain them
6. Quote relevant parts from the document when appropriate
7. If the document truly doesn't contain relevant information, say so clearly

ANSWER:"""

                # Use direct LLM call for better control
                print(f"   Sending enhanced prompt to LLM...")
                answer = self.llm(enhanced_prompt)
                
                print(f"   LLM Response length: {len(answer)}")
                print(f"   Answer preview: {answer[:200]}...")
                
                # Add source information
                doc_info = f"\n\n📚 Information found in {len(docs)} document sections"
                return answer + doc_info
                
            else:
                return "I couldn't find any relevant information in the document to answer your question. The document might not contain content related to your query, or the document processing might have failed."
            
        except Exception as e:
            error_msg = f"Document query error: {str(e)}"
            print(f"❌ Enhanced RAG Error: {error_msg}")
            return error_msg
    
    def get_conversation_memory(self, user_id: int):
        """Get or create conversation memory for user"""
        if not LANGCHAIN_AVAILABLE:
            return None
        
        if user_id not in self.memory_store:
            self.memory_store[user_id] = ConversationBufferMemory(
                return_messages=True,
                memory_key="history"
            )
        return self.memory_store[user_id]
    
    def chat_with_memory(self, user_id: int, question: str) -> str:
        """Chat with conversation memory"""
        if not self.llm:
            return get_simple_ollama_response(question)
        
        try:
            memory = self.get_conversation_memory(user_id)
            
            if memory:
                # Create conversation chain with memory
                conversation = ConversationChain(
                    llm=self.llm,
                    memory=memory,
                    prompt=PromptTemplate(
                        input_variables=["history", "input"],
                        template="""You are a helpful educational AI assistant for students.

Previous conversation:
{history}

Student: {input}
AI Assistant:"""
                    )
                )
                
                return conversation.predict(input=question)
            else:
                return get_simple_ollama_response(question)
                
        except Exception as e:
            print(f"❌ Memory chat failed: {e}")
            return get_simple_ollama_response(question)

# Global RAG processor instance
rag_processor = ComprehensiveRAGProcessor()

# Helper functions
def get_simple_ollama_response(question: str) -> str:
    """Fallback Ollama response without LangChain"""
    try:
        data = {
            "model": "llama3.2",
            "prompt": question,
            "stream": False
        }
        response = requests.post("http://localhost:11434/api/generate", json=data, timeout=30)
        if response.status_code == 200:
            response_data = response.json()
            return response_data.get("response", "Sorry, I couldn't understand.")
        else:
            return "AI service temporarily unavailable"
    except Exception as e:
        return f"AI service error: {str(e)}"

def get_conversation_context(user_id: int, limit: int = 3) -> str:
    """Get recent conversation context from database"""
    try:
        recent_chats = ChatInteraction.objects.filter(
            student_id=user_id
        ).order_by('-created_at')[:limit]
        
        context_parts = []
        for chat in reversed(recent_chats):
            context_parts.append(f"Q: {chat.question[:100]}...")
            context_parts.append(f"A: {chat.answer[:100]}...")
        
        return " | ".join(context_parts)
    except:
        return ""

# Main Views
class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]

@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def chat_interaction(request):
    """
    🤖 Main chat endpoint with comprehensive RAG support
    
    Features:
    - Math solving (SymPy)
    - Document upload and Q&A
    - Multi-document querying
    - Conversation memory
    - Smart responses
    """
    if request.method == 'GET':
        return Response({
            "message": "Comprehensive Educational Chat API",
            "features": {
                "math_solving": "✅ SymPy integration",
                "document_qa": "✅ PDF upload and analysis" if LANGCHAIN_AVAILABLE else "❌ LangChain required",
                "vector_search": "✅ Semantic document search" if LANGCHAIN_AVAILABLE else "❌ LangChain required",
                "conversation_memory": "✅ Context-aware responses" if LANGCHAIN_AVAILABLE else "❌ LangChain required",
                "multi_document": "✅ Query multiple documents" if LANGCHAIN_AVAILABLE else "❌ LangChain required"
            },
            "supported_formats": ["PDF", "Text"],
            "langchain_status": "✅ Available" if LANGCHAIN_AVAILABLE else "❌ Not installed"
        })
    
    # Extract request data
    question = request.data.get('question', '').strip()
    uploaded_file = request.FILES.get('document')
    # Handle document_ids - could be a list or single value
    document_ids = request.data.get('document_ids', [])
    if isinstance(document_ids, str):
        document_ids = [document_ids] if document_ids else []
    elif not isinstance(document_ids, list):
        document_ids = []
    user = request.user
    
    if not question:
        return Response({"error": "Missing question"}, status=400)
    
    response_data = {
        "answer": "",
        "source": "",
        "chat_id": None,
        "document_processed": False,
        "documents_used": [],
        "processing_info": {},
        "features_used": []
    }
    
    try:
        # 🔢 STEP 1: Try mathematics first (highest priority)
        try:
            expr = sympify(question)
            result = expr.evalf()
            response_data["answer"] = f"{question} = {result}"
            response_data["source"] = "mathematics"
            response_data["features_used"].append("SymPy Math Solver")
            
        except SympifyError:
            # 📄 STEP 2: Handle document upload
            target_document = None
            
            if uploaded_file:
                doc_result = process_uploaded_document(uploaded_file, user, uploaded_file.name)
                
                if doc_result['success']:
                    # Save document to database
                    document = Document.objects.create(
                        uploaded_by=user,
                        title=doc_result['title'],
                        document_type=doc_result['document_type'],
                        file_path=doc_result['file_path'],
                        extracted_text=doc_result['extraction_result']['text'],
                        metadata=json.dumps(doc_result['extraction_result']['metadata']),
                        processing_status='completed'
                    )
                    target_document = document
                    document_ids = [str(document.id)]
                    
                    response_data["document_processed"] = True
                    response_data["processing_info"] = {
                        "document_id": document.id,
                        "title": document.title,
                        "text_length": len(document.extracted_text),
                        "type": document.document_type
                    }
                    response_data["features_used"].append("Document Upload & Processing")
                else:
                    return Response({"error": f"Document processing failed: {doc_result['error']}"}, status=400)
            
            # 🔍 STEP 3: Document-based Q&A with RAG
            if document_ids:
                documents = Document.objects.filter(
                    id__in=document_ids,
                    uploaded_by=user
                )
                
                if documents.exists():
                    # Create combined vector store
                    combined_texts = []
                    used_docs = []
                    
                    for doc in documents:
                        if doc.extracted_text:
                            combined_texts.append(f"[Document: {doc.title}]\n{doc.extracted_text}")
                            used_docs.append({
                                "id": doc.id,
                                "title": doc.title,
                                "type": doc.document_type
                            })
                    
                    if combined_texts:
                        # Create vector store for combined documents
                        combined_text = "\n\n".join(combined_texts)
                        vectorstore = rag_processor.create_vector_store(
                            combined_text, 
                            f"combined_{user.id}_{int(time.time())}"
                        )
                        
                        if vectorstore:
                            # Get conversation context
                            conversation_context = get_conversation_context(user.id)
                            
                            # Query with RAG
                            answer = rag_processor.query_with_rag(
                                vectorstore, 
                                question, 
                                conversation_context
                            )
                            
                            response_data["answer"] = answer
                            response_data["source"] = "document_rag"
                            response_data["documents_used"] = used_docs
                            response_data["features_used"].extend(["RAG Document Search", "Vector Similarity"])
                            
                        else:
                            # Fallback to simple text search
                            combined_text_lower = combined_text.lower()
                            question_lower = question.lower()
                            
                            if any(word in combined_text_lower for word in question_lower.split()):
                                context_start = max(0, combined_text_lower.find(question_lower.split()[0]) - 300)
                                context_end = min(len(combined_text), context_start + 1000)
                                context = combined_text[context_start:context_end]
                                
                                enhanced_question = f"""
                                Based on these documents: {', '.join([doc['title'] for doc in used_docs])}
                                
                                Document content: {context}
                                
                                Student question: {question}
                                
                                Please answer based on the document content.
                                """
                                
                                answer = get_simple_ollama_response(enhanced_question)
                                response_data["answer"] = answer
                                response_data["source"] = "document_simple"
                                response_data["documents_used"] = used_docs
                                response_data["features_used"].append("Simple Document Search")
                            else:
                                response_data["answer"] = "I couldn't find relevant information in the uploaded documents for your question."
                                response_data["source"] = "no_match"
                    else:
                        return Response({"error": "No text content found in documents"}, status=400)
                else:
                    return Response({"error": "Documents not found or access denied"}, status=404)
            
            # 💬 STEP 4: General conversation with memory
            else:
                if LANGCHAIN_AVAILABLE:
                    answer = rag_processor.chat_with_memory(user.id, question)
                    response_data["features_used"].append("Conversation Memory")
                else:
                    answer = get_simple_ollama_response(question)
                
                response_data["answer"] = answer
                response_data["source"] = "general_chat"
                response_data["features_used"].append("General AI Chat")
        
        # 💾 STEP 5: Save to database
        chat_interaction = ChatInteraction.objects.create(
            student=user,
            question=question,
            answer=response_data["answer"],
            topic=response_data["source"].replace("_", " ").title(),
            document=target_document if 'target_document' in locals() else None,
            notes=json.dumps({
                "features_used": response_data["features_used"],
                "documents_used": response_data.get("documents_used", []),
                "processing_info": response_data.get("processing_info", {}),
                "langchain_available": LANGCHAIN_AVAILABLE
            })
        )
        
        response_data["chat_id"] = chat_interaction.id
        return Response(response_data)
        
    except Exception as e:
        # Error handling with database logging
        error_message = f"System error: {str(e)}"
        
        ChatInteraction.objects.create(
            student=user,
            question=question,
            answer=error_message,
            topic="System Error",
            notes=f"Error details: {str(e)}"
        )
        
        return Response({
            "error": error_message,
            "support_message": "The error has been logged. Please try again or contact support."
        }, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_document(request):
    """📄 Upload and process documents"""
    uploaded_file = request.FILES.get('document')
    title = request.data.get('title', '')
    
    if not uploaded_file:
        return Response({"error": "No file provided"}, status=400)
    
    result = process_uploaded_document(uploaded_file, request.user, title or uploaded_file.name)
    
    if result['success']:
        document = Document.objects.create(
            uploaded_by=request.user,
            title=result['title'],
            document_type=result['document_type'],
            file_path=result['file_path'],
            extracted_text=result['extraction_result']['text'],
            metadata=json.dumps(result['extraction_result']['metadata']),
            processing_status='completed'
        )
        
        return Response({
            "success": True,
            "document_id": document.id,
            "title": document.title,
            "document_type": document.document_type,
            "text_length": len(document.extracted_text),
            "preview": document.extracted_text[:200] + "..." if len(document.extracted_text) > 200 else document.extracted_text
        })
    else:
        return Response({"error": result['error']}, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_documents(request):
    """📚 List user's documents"""
    try:
        print(f"DEBUG: User authenticated: {request.user.is_authenticated}")
        print(f"DEBUG: User: {request.user}")
        print(f"DEBUG: Auth header: {request.headers.get('Authorization', 'Not provided')}")
        
        if not request.user.is_authenticated:
            return Response({
                "error": "Authentication required",
                "documents": [],
                "total": 0
            }, status=401)
        
        documents = Document.objects.filter(uploaded_by=request.user).order_by('-created_at')
        
        doc_list = []
        for doc in documents:
            doc_list.append({
                "id": doc.id,
                "title": doc.title,
                "document_type": doc.document_type,
                "created_at": doc.created_at.isoformat(),
                "text_preview": doc.extracted_text[:150] + "..." if len(doc.extracted_text) > 150 else doc.extracted_text,
                "text_length": len(doc.extracted_text),
                "status": doc.processing_status
            })
        
        return Response({
            "documents": doc_list,
            "total": len(doc_list)
        })
        
    except Exception as e:
        print(f"ERROR in list_documents: {str(e)}")
        return Response({
            "error": f"Failed to load documents: {str(e)}",
            "documents": [],
            "total": 0
        }, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chat_history(request):
    """📜 Get chat history with filtering"""
    limit = int(request.GET.get('limit', 20))
    topic = request.GET.get('topic', '')
    
    chats = ChatInteraction.objects.filter(student=request.user)
    
    if topic:
        chats = chats.filter(topic__icontains=topic)
    
    chats = chats.order_by('-created_at')[:limit]
    
    history = []
    for chat in chats:
        chat_data = {
            "id": chat.id,
            "question": chat.question,
            "answer": chat.answer,
            "topic": chat.topic,
            "created_at": chat.created_at.isoformat(),
        }
        
        if chat.document:
            chat_data["document"] = {
                "id": chat.document.id,
                "title": chat.document.title
            }
        
        if chat.notes:
            try:
                notes_data = json.loads(chat.notes)
                chat_data["features_used"] = notes_data.get("features_used", [])
            except:
                pass
        
        history.append(chat_data)
    
    return Response({
        "history": history,
        "total": ChatInteraction.objects.filter(student=request.user).count()
    })

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clear_conversation_memory(request):
    """🧹 Clear conversation memory and delete all user files"""
    user_id = request.user.id
    files_deleted = 0
    errors = []
    
    try:
        # Get all user documents before deleting them
        user_documents = Document.objects.filter(uploaded_by=request.user)
        
        # Delete physical files from the filesystem
        for doc in user_documents:
            try:
                if doc.file_path and os.path.exists(doc.file_path):
                    os.remove(doc.file_path)
                    files_deleted += 1
                    print(f"✅ Deleted file: {doc.file_path}")
                elif doc.file_path:
                    print(f"⚠️ File not found: {doc.file_path}")
            except Exception as e:
                error_msg = f"Failed to delete file {doc.file_path}: {str(e)}"
                errors.append(error_msg)
                print(f"❌ {error_msg}")
        
        # Delete document records from database
        documents_count = user_documents.count()
        user_documents.delete()
        
        # Clear LangChain memory
        if hasattr(rag_processor, 'memory_store') and user_id in rag_processor.memory_store:
            del rag_processor.memory_store[user_id]
        
        # Clear global memory stores
        if user_id in user_conversation_memories:
            del user_conversation_memories[user_id]
        
        # Clear vector stores for this user
        if user_id in user_vector_stores:
            del user_vector_stores[user_id]
        
        response_data = {
            "message": "Memory and files cleared successfully",
            "details": {
                "documents_deleted": documents_count,
                "files_deleted": files_deleted,
                "memory_cleared": True
            },
            "note": "Database chat history is preserved"
        }
        
        if errors:
            response_data["warnings"] = errors
        
        return Response(response_data)
        
    except Exception as e:
        return Response({
            "error": f"Failed to clear memory and files: {str(e)}",
            "details": {
                "files_deleted": files_deleted,
                "errors": errors
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Custom login view for token authentication
@api_view(['POST'])
@permission_classes([])  # Allow unauthenticated access
def user_login(request):
    """
    Login view that returns authentication token
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({
            'error': 'Username and password are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Authenticate user
    user = authenticate(username=username, password=password)
    
    if user:
        # Get or create token for user
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user': {
                'id': user.id,
                'username': user.username,
                'role': user.role,
                'email': user.email
            }
        })
    else:
        return Response({
            'error': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_logout(request):
    """
    Logout view that deletes the authentication token
    """
    try:
        # Delete the user's token to effectively log them out
        request.user.auth_token.delete()
        return Response({'message': 'Successfully logged out'})
    except:
        return Response({'error': 'Logout failed'}, status=status.HTTP_400_BAD_REQUEST)