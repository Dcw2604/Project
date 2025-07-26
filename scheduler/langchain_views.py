"""
Enhanced RAG (Retrieval-Augmented Generation) Chat System with LangChain
Supports document upload, vector search, conversation memory, and smart AI responses
"""
from django.shortcuts import render
from rest_framework import generics, permissions, viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import UserRegistrationSerializer, LessonSerializer
from .models import User, Lesson, ChatInteraction, Document
from sympy import sympify
from sympy.core.sympify import SympifyError
import requests
import json
import os
import tempfile
import hashlib
import time
from datetime import datetime
from django.utils import timezone

# PDF processing
import pdfplumber
from PIL import Image

# LangChain imports with error handling
try:
    from langchain.memory import ConversationBufferMemory
    from langchain.schema import HumanMessage, AIMessage
    from langchain_community.llms import Ollama
    from langchain.chains import ConversationChain, RetrievalQA
    from langchain.prompts import PromptTemplate
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_community.vectorstores import FAISS
    from langchain_community.embeddings import OllamaEmbeddings
    from langchain.schema import Document as LangChainDocument
    LANGCHAIN_AVAILABLE = True
except ImportError as e:
    print(f"LangChain not available: {e}")
    LANGCHAIN_AVAILABLE = False

# Global storage for user memories and vector stores
user_memories = {}
user_vector_stores = {}
document_vector_stores = {}

class RAGProcessor:
    """
    Comprehensive RAG (Retrieval-Augmented Generation) processor
    """
    
    def __init__(self):
        self.text_splitter = None
        self.embeddings = None
        self.llm = None
        self.init_components()
    
    def init_components(self):
        """Initialize LangChain components"""
        if not LANGCHAIN_AVAILABLE:
            return
        
        try:
            # Text splitter for chunking documents
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
                separators=["\n\n", "\n", ".", "!", "?", ";", " ", ""]
            )
            
            # Embeddings for vector storage
            self.embeddings = OllamaEmbeddings(
                model="llama3.2",
                base_url="http://localhost:11434"
            )
            
            # LLM for generating responses
            self.llm = Ollama(
                model="llama3.2",
                base_url="http://localhost:11434",
                temperature=0.7
            )
            
            print("RAG components initialized successfully")
            
        except Exception as e:
            print(f"RAG initialization failed: {e}")
            self.text_splitter = None
            self.embeddings = None
            self.llm = None
    
    def process_pdf(self, file_path: str) -> dict:
        """Extract text and metadata from PDF"""
        result = {
            'text': '',
            'metadata': {},
            'pages': 0,
            'tables': 0,
            'errors': []
        }
        
        try:
            with pdfplumber.open(file_path) as pdf:
                # Extract metadata
                if pdf.metadata:
                    result['metadata'] = {
                        'title': pdf.metadata.get('Title', ''),
                        'author': pdf.metadata.get('Author', ''),
                        'subject': pdf.metadata.get('Subject', ''),
                        'pages': len(pdf.pages)
                    }
                
                # Extract text from all pages
                text_parts = []
                table_count = 0
                
                for page_num, page in enumerate(pdf.pages, 1):
                    try:
                        # Extract text
                        page_text = page.extract_text()
                        if page_text:
                            text_parts.append(f"[Page {page_num}]\n{page_text}")
                        
                        # Count tables
                        tables = page.extract_tables()
                        if tables:
                            table_count += len(tables)
                            # Add table content as text
                            for table in tables:
                                table_text = "\n".join(["\t".join(str(cell) for cell in row if cell) for row in table if row])
                                text_parts.append(f"[Table from Page {page_num}]\n{table_text}")
                                
                    except Exception as e:
                        result['errors'].append(f"Page {page_num}: {str(e)}")
                
                result['text'] = "\n\n".join(text_parts)
                result['pages'] = len(pdf.pages)
                result['tables'] = table_count
                
        except Exception as e:
            result['errors'].append(f"PDF processing error: {str(e)}")
        
        return result
    
    def create_vector_store(self, text: str, document_id: str) -> object:
        """Create FAISS vector store from document text"""
        if not self.text_splitter or not self.embeddings:
            return None
        
        try:
            # Split text into chunks
            chunks = self.text_splitter.split_text(text)
            
            if not chunks:
                return None
            
            # Create LangChain documents
            documents = [
                LangChainDocument(
                    page_content=chunk,
                    metadata={"document_id": document_id, "chunk_index": i}
                )
                for i, chunk in enumerate(chunks)
            ]
            
            # Create vector store
            vectorstore = FAISS.from_documents(documents, self.embeddings)
            
            print(f"Created vector store with {len(chunks)} chunks for document {document_id}")
            return vectorstore
            
        except Exception as e:
            print(f"Vector store creation failed: {e}")
            return None
    
    def query_documents(self, vectorstore, question: str, k: int = 4) -> str:
        """Query documents using RAG"""
        if not self.llm or not vectorstore:
            return "Document search not available"
        
        try:
            # Create RAG chain
            qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=vectorstore.as_retriever(search_kwargs={"k": k}),
                return_source_documents=True,
                chain_type_kwargs={
                    "prompt": PromptTemplate(
                        template="""Use the following context to answer the question. If you don't know the answer based on the context, say so.

Context: {context}

Question: {question}

Answer:""",
                        input_variables=["context", "question"]
                    )
                }
            )
            
            # Get response
            response = qa_chain({"query": question})
            return response.get("result", "No answer found in documents")
            
        except Exception as e:
            return f"Document query error: {str(e)}"

# Global RAG processor instance
rag_processor = RAGProcessor()

def get_user_memory(user_id):
    """Get or create conversation memory for a specific user"""
    if not LANGCHAIN_AVAILABLE:
        return None
    
    if user_id not in user_memories:
        user_memories[user_id] = ConversationBufferMemory(
            return_messages=True,
            memory_key="history",
            input_key="input"
        )
    return user_memories[user_id]

@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def rag_chat_interaction(request):
    """
    Advanced RAG-powered chat with document support and memory
    """
    if request.method == 'GET':
        return Response({
            "message": "RAG Chat API with LangChain",
            "features": [
                "Document upload and processing",
                "Vector-based document search",
                "Conversation memory",
                "Math problem solving",
                "Multi-document querying"
            ],
            "langchain_available": LANGCHAIN_AVAILABLE
        })
    
    question = request.data.get('question', '').strip()
    uploaded_file = request.FILES.get('document')
    document_ids = request.data.getlist('document_ids', [])  # Support multiple documents
    user = request.user
    
    if not question:
        return Response({"error": "Missing question"}, status=400)
    
    response_data = {
        "answer": "",
        "source": "",
        "document_processed": False,
        "documents_used": [],
        "processing_info": {}
    }
    
    try:
        # 1. Try math first (highest priority)
        try:
            expr = sympify(question)
            result = expr.evalf()
            response_data["answer"] = f"{question} = {result}"
            response_data["source"] = "mathematics"
            
        except SympifyError:
            # 2. Handle document upload
            if uploaded_file:
                result = process_uploaded_document(uploaded_file, user)
                if result['success']:
                    document = result['document']
                    response_data["document_processed"] = True
                    response_data["processing_info"] = result['processing_info']
                    document_ids = [str(document.id)]
                else:
                    return Response({"error": result['error']}, status=400)
            
            # 3. RAG with documents
            if document_ids:
                # Get documents
                documents = Document.objects.filter(
                    id__in=document_ids,
                    uploaded_by=user
                ).select_related('uploaded_by')
                
                if documents:
                    # Create combined vector store if needed
                    combined_vectorstore = None
                    used_docs = []
                    
                    for doc in documents:
                        doc_key = f"doc_{doc.id}"
                        
                        # Create vector store for document if not exists
                        if doc_key not in document_vector_stores:
                            if doc.extracted_text:
                                vectorstore = rag_processor.create_vector_store(
                                    doc.extracted_text,
                                    str(doc.id)
                                )
                                if vectorstore:
                                    document_vector_stores[doc_key] = vectorstore
                        
                        # Combine vector stores
                        if doc_key in document_vector_stores:
                            if combined_vectorstore is None:
                                combined_vectorstore = document_vector_stores[doc_key]
                            else:
                                # Merge vector stores (simplified approach)
                                try:
                                    combined_vectorstore.merge_from(document_vector_stores[doc_key])
                                except:
                                    # Fallback: use the first available store
                                    pass
                            
                            used_docs.append({
                                "id": doc.id,
                                "title": doc.title,
                                "type": doc.document_type
                            })
                    
                    # Query documents
                    if combined_vectorstore:
                        # Add conversation context if available
                        memory = get_user_memory(user.id)
                        context_question = question
                        
                        if memory and LANGCHAIN_AVAILABLE:
                            try:
                                history = memory.load_memory_variables({})
                                if history.get('history'):
                                    context_question = f"""
                                    Previous conversation context:
                                    {history['history'][-200:]}  # Last 200 chars
                                    
                                    Current question: {question}
                                    """
                            except:
                                pass
                        
                        answer = rag_processor.query_documents(combined_vectorstore, context_question)
                        response_data["answer"] = answer
                        response_data["source"] = "documents"
                        response_data["documents_used"] = used_docs
                        
                        # Update conversation memory
                        if memory:
                            try:
                                memory.save_context({"input": question}, {"output": answer})
                            except:
                                pass
                    else:
                        response_data["answer"] = "No searchable content found in documents"
                        response_data["source"] = "error"
                else:
                    return Response({"error": "Documents not found"}, status=404)
            
            # 4. General conversation with memory
            else:
                if LANGCHAIN_AVAILABLE and rag_processor.llm:
                    memory = get_user_memory(user.id)
                    
                    # Create conversation chain
                    conversation = ConversationChain(
                        llm=rag_processor.llm,
                        memory=memory,
                        prompt=PromptTemplate(
                            input_variables=["history", "input"],
                            template="""You are a helpful educational AI assistant.

Previous conversation:
{history}

Student: {input}
AI Assistant:"""
                        )
                    )
                    
                    answer = conversation.predict(input=question)
                    response_data["answer"] = answer
                    response_data["source"] = "general_ai"
                else:
                    # Fallback to simple Ollama
                    answer = get_simple_ollama_response(question)
                    response_data["answer"] = answer
                    response_data["source"] = "simple_ai"
        
        # Save to database
        chat_interaction = ChatInteraction.objects.create(
            student=user,
            question=question,
            answer=response_data["answer"],
            topic=response_data["source"].title(),
            notes=json.dumps({
                "documents_used": response_data.get("documents_used", []),
                "processing_info": response_data.get("processing_info", {}),
                "langchain_used": LANGCHAIN_AVAILABLE
            })
        )
        
        response_data["chat_id"] = chat_interaction.id
        return Response(response_data)
        
    except Exception as e:
        error_msg = f"Chat processing error: {str(e)}"
        
        # Save error to database
        ChatInteraction.objects.create(
            student=user,
            question=question,
            answer=error_msg,
            topic="Error",
            notes=f"System error: {str(e)}"
        )
        
        return Response({"error": error_msg}, status=500)

def process_uploaded_document(uploaded_file, user):
    """Process uploaded document and save to database"""
    try:
        # Create unique filename
        timestamp = int(time.time())
        filename = f"user_{user.id}_{timestamp}_{uploaded_file.name}"
        file_path = os.path.join('media', 'documents', filename)
        
        # Save file
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'wb') as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)
        
        # Determine document type
        file_ext = os.path.splitext(uploaded_file.name)[1].lower()
        if file_ext == '.pdf':
            doc_type = 'pdf'
            processing_result = rag_processor.process_pdf(file_path)
        else:
            doc_type = 'text'
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            processing_result = {
                'text': content,
                'metadata': {'filename': uploaded_file.name},
                'pages': 1,
                'tables': 0,
                'errors': []
            }
        
        # Save to database
        document = Document.objects.create(
            uploaded_by=user,
            title=uploaded_file.name,
            document_type=doc_type,
            file_path=file_path,
            extracted_text=processing_result['text'],
            metadata=json.dumps(processing_result['metadata']),
            processing_status='completed'
        )
        
        return {
            'success': True,
            'document': document,
            'processing_info': {
                'pages': processing_result['pages'],
                'tables': processing_result['tables'],
                'text_length': len(processing_result['text']),
                'errors': processing_result['errors']
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def get_simple_ollama_response(question: str) -> str:
    """Fallback Ollama response without LangChain"""
    try:
        data = {
            "model": "llama3.2",
            "prompt": question,
            "stream": False
        }
        response = requests.post("http://localhost:11434/api/generate", json=data, timeout=30)
        response_data = response.json()
        return response_data.get("response", "Sorry, I couldn't understand.")
    except Exception as e:
        return f"AI service error: {str(e)}"

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_user_documents(request):
    """List user's uploaded documents"""
    documents = Document.objects.filter(uploaded_by=request.user).order_by('-created_at')
    
    doc_list = []
    for doc in documents:
        metadata = json.loads(doc.metadata) if doc.metadata else {}
        doc_list.append({
            "id": doc.id,
            "title": doc.title,
            "document_type": doc.document_type,
            "created_at": doc.created_at.isoformat(),
            "pages": metadata.get('pages', 1),
            "text_preview": doc.extracted_text[:200] + "..." if len(doc.extracted_text) > 200 else doc.extracted_text,
            "processing_status": doc.processing_status
        })
    
    return Response({
        "documents": doc_list,
        "total": len(doc_list),
        "langchain_available": LANGCHAIN_AVAILABLE
    })

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clear_user_memory(request):
    """Clear user's conversation memory and vector stores"""
    user_id = request.user.id
    
    # Clear conversation memory
    if user_id in user_memories:
        del user_memories[user_id]
    
    # Clear user's vector stores
    user_stores = [key for key in document_vector_stores.keys() if key.startswith(f"user_{user_id}_")]
    for key in user_stores:
        del document_vector_stores[key]
    
    return Response({
        "message": "Memory and vector stores cleared",
        "cleared_items": len(user_stores) + (1 if user_id in user_memories else 0)
    })

# Keep existing classes for compatibility
class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]
