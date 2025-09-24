<<<<<<< HEAD
from django.shortcuts import render
from rest_framework import generics, permissions
from .serializers import UserRegistrationSerializer
from .models import User, Lesson, ChatInteraction 
from rest_framework import viewsets, permissions
from .serializers import LessonSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from sympy import sympify # type: ignore
from sympy.core.sympify import SympifyError
import requests

=======
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
from .serializers import (
    UserRegistrationSerializer, LessonSerializer, DocumentSerializer, 
    DocumentUploadSerializer, QuestionBankSerializer, QuestionBankCreateSerializer, 
    TestSessionSerializer, TestSessionCreateSerializer, StudentAnswerSerializer,
    TopicSerializer, ExamSessionSerializer, ExamSessionCreateSerializer, ExamConfigSerializer
)
from .models import (
    User, Lesson, ChatInteraction, Document, LearningSession, QuestionResponse,
    QuestionBank, Topic, ExamSession, ExamSessionTopic, ExamSessionQuestion, ExamConfig, ExamConfigQuestion,
    StudentAnswer, ExamAnswerAttempt
)
from .structured_learning import StructuredLearningManager
# Temporarily disable imports to get server running
try:
    from .document_processing import DocumentProcessor
    document_processor = DocumentProcessor()
    print("✅ Document processor initialized successfully")
except ImportError:
    print("⚠️ Document processing not available")
    document_processor = None

try:
    from sympy import sympify
    from sympy.core.sympify import SympifyError
    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False
    print("⚠️ SymPy not available - math processing disabled")

import requests
import json
import os
import tempfile
import time
import uuid
import traceback
import random
import re
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

# Import Gemini Client
try:
    from .gemini_client import GeminiClient
    GEMINI_AVAILABLE = True
    print("✅ Gemini client loaded successfully")
except ImportError as e:
    GEMINI_AVAILABLE = False
    print(f"❌ Gemini client not available: {e}")

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
                model="llama3.2",  # Use llama3.2 model
                base_url="http://localhost:11434"
            )
            
            # LLM for text generation
            self.llm = Ollama(
                model="llama3.2",  # Use llama3.2 model
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

# Global Gemini client instance
gemini_client = None
if GEMINI_AVAILABLE:
    try:
        gemini_client = GeminiClient()
        print("✅ Gemini client initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize Gemini client: {e}")
        gemini_client = None

class QuestionVariationGenerator:
    """
    Advanced Question Variation Generator
    Creates mathematical and contextual variations of exam questions to prevent duplicates
    """
    
    def __init__(self):
        self.used_questions = set()
        self.variation_cache = {}
    
    def generate_question_variations(self, base_question, num_variations=3):
        """
        Generate multiple variations of a question by changing numbers and contexts
        """
        variations = []
        
        try:
            # Extract numbers from the question
            numbers = re.findall(r'\b\d+(?:\.\d+)?\b', base_question.question_text)
            
            for i in range(num_variations):
                varied_question = self._create_numerical_variation(base_question, numbers, i + 1)
                if varied_question:
                    variations.append(varied_question)
        
        except Exception as e:
            print(f"❌ Question variation failed: {e}")
        
        return variations
    
    def _create_numerical_variation(self, base_question, numbers, variation_seed):
        """Create a variation by modifying numbers in the question"""
        try:
            # Set random seed for consistent variations
            random.seed(hash(base_question.question_text) + variation_seed)
            
            question_text = base_question.question_text
            correct_answer = base_question.correct_answer
            
            # Track answer modifications for mathematical consistency
            answer_modifications = {}
            
            # Replace each number with a variation
            for original_num in numbers:
                if original_num in question_text:
                    # Create varied number (±20-50% change)
                    original_val = float(original_num)
                    variation_factor = random.uniform(0.5, 1.5)  # 50% to 150% of original
                    
                    # Round to appropriate precision
                    if '.' in original_num:
                        # Decimal number
                        varied_val = round(original_val * variation_factor, 2)
                    else:
                        # Integer
                        varied_val = max(1, int(original_val * variation_factor))
                    
                    # Store modification for answer calculation
                    answer_modifications[original_val] = varied_val
                    
                    # Replace in question text (only first occurrence to avoid double replacement)
                    question_text = question_text.replace(original_num, str(varied_val), 1)
            
            # Calculate new correct answer
            new_correct_answer = self._calculate_varied_answer(
                base_question, answer_modifications
            )
            
            # Create variation object
            variation = {
                'question_text': question_text,
                'correct_answer': str(new_correct_answer),
                'option_a': self._vary_option(base_question.option_a, answer_modifications, new_correct_answer),
                'option_b': self._vary_option(base_question.option_b, answer_modifications, new_correct_answer),
                'option_c': self._vary_option(base_question.option_c, answer_modifications, new_correct_answer),
                'option_d': self._vary_option(base_question.option_d, answer_modifications, new_correct_answer),
                'question_type': base_question.question_type,
                'difficulty_level': base_question.difficulty_level,
                'subject': base_question.subject,
                'explanation': self._vary_explanation(base_question.explanation, answer_modifications),
                'is_variation': True,
                'base_question_id': base_question.id
            }
            
            return variation
            
        except Exception as e:
            print(f"❌ Numerical variation failed: {e}")
            return None
    
    def _calculate_varied_answer(self, base_question, modifications):
        """Calculate the correct answer for the varied question"""
        try:
            original_answer = base_question.correct_answer.strip()
            
            # If answer is a number, apply the same modifications
            if re.match(r'^\d+(?:\.\d+)?$', original_answer):
                original_val = float(original_answer)
                
                # For simple cases, apply direct scaling
                if len(modifications) == 1:
                    old_val, new_val = list(modifications.items())[0]
                    scale_factor = new_val / old_val if old_val != 0 else 1
                    return round(original_val * scale_factor, 2)
                
                # For complex cases, try to maintain mathematical relationships
                elif len(modifications) == 2:
                    vals = list(modifications.values())
                    # Common patterns: addition, multiplication, etc.
                    if '+' in base_question.question_text.lower():
                        return sum(vals)
                    elif 'multiply' in base_question.question_text.lower() or '×' in base_question.question_text:
                        return vals[0] * vals[1] if len(vals) >= 2 else vals[0]
                    elif 'subtract' in base_question.question_text.lower() or '-' in base_question.question_text:
                        return abs(vals[0] - vals[1]) if len(vals) >= 2 else vals[0]
                    elif 'divide' in base_question.question_text.lower() or '÷' in base_question.question_text:
                        return round(vals[0] / vals[1], 2) if len(vals) >= 2 and vals[1] != 0 else vals[0]
                
                # Default: scale by average modification
                avg_scale = sum(new/old for old, new in modifications.items() if old != 0) / len(modifications)
                return round(original_val * avg_scale, 2)
            
            # For non-numeric answers, return original
            return original_answer
            
        except Exception as e:
            print(f"❌ Answer calculation failed: {e}")
            return base_question.correct_answer
    
    def _vary_option(self, option, modifications, new_correct_answer):
        """Vary multiple choice options to match the new question"""
        if not option:
            return option
        
        try:
            # Check if option contains numbers that need variation
            numbers = re.findall(r'\b\d+(?:\.\d+)?\b', option)
            varied_option = option
            
            for num in numbers:
                original_val = float(num)
                # Apply modifications if this number was changed in the question
                for old_val, new_val in modifications.items():
                    if abs(original_val - old_val) < 0.01:  # Match found
                        varied_option = varied_option.replace(num, str(new_val), 1)
                        break
                else:
                    # If no direct match, apply random variation
                    scale_factor = random.uniform(0.7, 1.3)
                    if '.' in num:
                        new_val = round(original_val * scale_factor, 2)
                    else:
                        new_val = max(1, int(original_val * scale_factor))
                    varied_option = varied_option.replace(num, str(new_val), 1)
            
            return varied_option
            
        except Exception as e:
            print(f"❌ Option variation failed: {e}")
            return option
    
    def _vary_explanation(self, explanation, modifications):
        """Update explanation to reflect the new numbers"""
        if not explanation:
            return explanation
        
        try:
            varied_explanation = explanation
            for old_val, new_val in modifications.items():
                # Replace numbers in explanation
                varied_explanation = re.sub(
                    r'\b' + str(old_val) + r'\b',
                    str(new_val),
                    varied_explanation
                )
            return varied_explanation
        except Exception as e:
            print(f"❌ Explanation variation failed: {e}")
            return explanation
    
    def select_varied_questions(self, exam, required_count):
        """
        Select questions ensuring no duplicates and creating variations when needed
        """
        from .models import QuestionBank  # Import here to avoid circular imports
        
        print(f"🎯 Selecting {required_count} varied questions for exam {exam.id}")
        
        selected_questions = []
        self.used_questions.clear()  # Reset for this exam
        
        # Get base questions
        base_pool = list(exam.questions.all())
        
        # If not enough base questions, expand pool
        if len(base_pool) < required_count:
            # Get additional questions from the same subject/difficulty
            additional_pool = QuestionBank.objects.filter(
                is_approved=True,
                subject=exam.subject,
                difficulty_level=exam.difficulty_level
            ).exclude(
                id__in=[q.id for q in base_pool]
            )
            
            # Add teacher's questions for consistency
            if exam.created_by:
                teacher_questions = additional_pool.filter(
                    document__uploaded_by=exam.created_by
                )
                base_pool.extend(list(teacher_questions))
            
            # If still not enough, add any approved questions
            if len(base_pool) < required_count:
                remaining = additional_pool.exclude(
                    id__in=[q.id for q in base_pool]
                )
                base_pool.extend(list(remaining))
        
        # Shuffle the pool
        random.shuffle(base_pool)
        
        # Select base questions first
        questions_needed = required_count
        for question in base_pool:
            if questions_needed <= 0:
                break
                
            # Add original question
            selected_questions.append({
                'type': 'original',
                'question': question,
                'data': {
                    'id': question.id,
                    'question_text': question.question_text,
                    'correct_answer': question.correct_answer,
                    'option_a': question.option_a,
                    'option_b': question.option_b,
                    'option_c': question.option_c,
                    'option_d': question.option_d,
                    'question_type': question.question_type,
                    'difficulty_level': question.difficulty_level,
                    'subject': question.subject,
                    'explanation': question.explanation
                }
            })
            self.used_questions.add(question.question_text.lower())
            questions_needed -= 1
        
        # Generate variations if we need more questions
        while questions_needed > 0 and base_pool:
            # Pick a random base question to vary
            base_question = random.choice(base_pool)
            
            # Generate variations
            variations = self.generate_question_variations(base_question, questions_needed)
            
            for variation in variations:
                if questions_needed <= 0:
                    break
                
                # Check if this variation is too similar to existing questions
                variation_text = variation['question_text'].lower()
                if variation_text not in self.used_questions:
                    selected_questions.append({
                        'type': 'variation',
                        'base_question': base_question,
                        'data': variation
                    })
                    self.used_questions.add(variation_text)
                    questions_needed -= 1
        
        print(f"✅ Selected {len(selected_questions)} varied questions ({required_count - questions_needed} original + {questions_needed} variations)")
        
        return selected_questions[:required_count]

# Global question variation generator
question_generator = QuestionVariationGenerator()

def start_background_processing(document_id, file_path, document_type):
    import threading, time
    def task():
        time.sleep(0.5)
        process_document_background(document_id, file_path, document_type)
    threading.Thread(target=task, daemon=True).start()

def process_document_background(document_id, file_path, document_type):
    from django.utils import timezone
    from .document_processing import DocumentProcessor, OllamaUnavailableError, InsufficientQuestionsError
    
    document = Document.objects.get(id=document_id)
    try:
        # If extracted_text is empty/suspiciously short, try re-extracting here
        txt = (document.extracted_text or "").strip()
        if len(txt) < 500:
            res = None
            if document_type == 'pdf':
                res = document_processor.extract_pdf_content(file_path)
                # Optional OCR fallback for scanned PDFs
                try:
                    from pdf2image import convert_from_path
                    import pytesseract
                    if document_type == 'pdf' and len(txt) < 500:
                        pages = convert_from_path(file_path, dpi=200)
                        ocr_text = "\n\n".join(pytesseract.image_to_string(p) for p in pages[:10])  # cap for safety
                        if len(ocr_text.strip()) > len(txt):
                            txt = ocr_text
                            document.extracted_text = txt
                            document.processed_content = txt
                            document.save(update_fields=['extracted_text','processed_content','updated_at'])
                except Exception:
                    pass  # keep non-OCR behavior if libs not installed
            elif document_type == 'image':
                res = document_processor.extract_image_text(file_path)
            else:
                # leave txt as-is for plain text
                pass
            if res:
                txt = res.get('text', '') if isinstance(res, dict) else str(res or '')
                document.extracted_text = txt
                document.processed_content = txt
                document.save(update_fields=['extracted_text','processed_content','updated_at'])

        # Not enough content? Mark failed clearly.
        if len((document.extracted_text or '').strip()) < 500:
            document.processing_status = 'failed'
            document.processing_error = 'INSUFFICIENT_TEXT'
            document.save(update_fields=['processing_status','processing_error','updated_at'])
            return

        # ✅ Proceed to generation (your existing call)
        result = DocumentProcessor().generate_questions_from_document(
            document_id=document.id,
            difficulty_levels=['3','4','5'],
            require_llm=True,     # your strict policy
            min_per_level=10
        )

        # Recompute and mark completed only on success
        total = QuestionBank.objects.filter(document_id=document.id).count()
        document.questions_generated_count = total
        document.processing_status = 'completed'
        document.processing_error = ''
        document.save(update_fields=['questions_generated_count','processing_status','processing_error','updated_at'])

    except OllamaUnavailableError:
        document.processing_status = 'failed'
        document.processing_error = 'AI_UNAVAILABLE'  # Updated from OLLAMA_UNAVAILABLE
        document.save(update_fields=['processing_status','processing_error','updated_at'])
    except InsufficientQuestionsError as e:
        document.processing_status = 'failed'
        document.processing_error = str(e) or 'INSUFFICIENT_QUESTIONS'
        document.save(update_fields=['processing_status','processing_error','updated_at'])
    except Exception as e:
        document.processing_status = 'failed'
        document.processing_error = f'GENERATION_ERROR: {e}'
        document.save(update_fields=['processing_status','processing_error','updated_at'])

# Helper functions
def get_simple_gemini_response(question: str, user=None) -> str:
    """Fallback Gemini response for simple questions with memory support"""
    print(f"DEBUG: get_simple_gemini_response called with question: '{question[:100]}...'")
    try:
        global gemini_client
        if not gemini_client:
            return "AI service temporarily unavailable - Gemini not connected"
        
        # אם יש משתמש, נקרא את ההיסטוריה
        chat_history = []
        if user:
            try:
                recent_chats = ChatInteraction.objects.filter(
                    student=user
                ).order_by('-created_at')[:3]  # 3 שיחות אחרונות
                
                for chat in reversed(recent_chats):
                    chat_history.append({
                        'user': chat.question,
                        'assistant': chat.answer
                    })
                print(f"DEBUG: Simple response with {len(chat_history)} history items")
            except Exception as e:
                print(f"DEBUG: Failed to retrieve history in simple response: {e}")
        
        response = gemini_client.chat_response(question, chat_history=chat_history)
        
        if response:
            print(f"DEBUG: Gemini API success, answer length: {len(response)}")
            print(f"DEBUG: Gemini API answer preview: {response[:100]}...")
            return response
        else:
            print(f"DEBUG: Gemini API returned empty response")
            return "Sorry, I couldn't understand your question. Please try rephrasing it."
            
    except Exception as e:
        print(f"DEBUG: Gemini API exception: {e}")
        return f"AI service error: {str(e)}"

def get_simple_ollama_response(question: str) -> str:
    """Legacy Ollama response - now redirects to Gemini"""
    print(f"DEBUG: Legacy OLLAMA function called, redirecting to Gemini")
    return get_simple_gemini_response(question, user=None)

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

def handle_exam_command(user, command, session, notes):
    """Handle special commands during exam (help, status, progress, time)"""
    try:
        from django.utils import timezone
        
        question_sequence = notes.get('question_sequence', [])
        current_index = notes.get('current_question_index', 0)
        total_questions = len(question_sequence)
        
        if command == 'help':
            help_message = """📋 **Exam Help**

**Available Commands:**
- Type your answer (A, B, C, D for multiple choice)
- `status` - See your current progress
- `time` - Check elapsed time
- `progress` - View completion percentage

**Remember:** You cannot go back to previous questions in exam mode."""
            
            ChatInteraction.objects.create(
                student=user,
                question=f"[EXAM COMMAND] {command}",
                answer=help_message,
                topic="Exam Help",
                notes=json.dumps({
                    "exam_mode": True,
                    "command": command,
                    "test_session_id": session.id
                })
            )
            
            return Response({
                'success': True,
                'exam_complete': False,
                'chatbot_message': help_message,
                'command_response': True
            })
        
        elif command in ['status', 'progress']:
            progress_percentage = (current_index / total_questions) * 100
            answered_count = current_index
            
            status_message = f"""📊 **Exam Progress**

**Current Status:**
- Question: {current_index + 1} of {total_questions}
- Progress: {progress_percentage:.1f}% complete
- Questions answered: {answered_count}
- Questions remaining: {total_questions - answered_count}

Continue with the current question when ready."""
            
            ChatInteraction.objects.create(
                student=user,
                question=f"[EXAM COMMAND] {command}",
                answer=status_message,
                topic="Exam Status",
                notes=json.dumps({
                    "exam_mode": True,
                    "command": command,
                    "progress": progress_percentage,
                    "test_session_id": session.id
                })
            )
            
            return Response({
                'success': True,
                'exam_complete': False,
                'chatbot_message': status_message,
                'command_response': True,
                'progress': {
                    'current_question': current_index + 1,
                    'total_questions': total_questions,
                    'percentage': progress_percentage
                }
            })
        
        elif command == 'time':
            exam_start_time_str = notes.get('exam_start_time')
            time_message = "⏰ **Time Information**\n\n"
            
            if exam_start_time_str:
                try:
                    from datetime import datetime
                    current_time = timezone.now()
                    exam_start_time = datetime.fromisoformat(exam_start_time_str.replace('Z', '+00:00'))
                    time_elapsed = (current_time - exam_start_time).total_seconds()
                    minutes_elapsed = int(time_elapsed // 60)
                    seconds_elapsed = int(time_elapsed % 60)
                    
                    time_message += f"Time elapsed: {minutes_elapsed}:{seconds_elapsed:02d}\n"
                    
                    # Show remaining time if limit exists
                    exam = session.exam
                    if exam and exam.exam_time_limit_minutes:
                        remaining_minutes = exam.exam_time_limit_minutes - minutes_elapsed
                        if remaining_minutes > 0:
                            time_message += f"Time remaining: {remaining_minutes} minutes\n"
                        else:
                            time_message += "⚠️ **Time limit exceeded!**\n"
                    
                    if exam and exam.per_question_time_seconds:
                        time_message += f"Suggested time per question: {exam.per_question_time_seconds} seconds"
                        
                except Exception as e:
                    time_message += "Unable to calculate time information."
            else:
                time_message += "Time tracking not available."
            
            ChatInteraction.objects.create(
                student=user,
                question=f"[EXAM COMMAND] {command}",
                answer=time_message,
                topic="Exam Time",
                notes=json.dumps({
                    "exam_mode": True,
                    "command": command,
                    "test_session_id": session.id
                })
            )
            
            return Response({
                'success': True,
                'exam_complete': False,
                'chatbot_message': time_message,
                'command_response': True
            })
        
        else:
            return Response({'error': 'Unknown command'}, status=400)
            
    except Exception as e:
        print(f"Error in exam command handler: {e}")
        return Response({'error': f'Command error: {str(e)}'}, status=500)

def handle_exam_chat_interaction(user, student_answer, test_session_id):
    """
    Handle interactive exam flow via Ollama (OLLaMA) + LangChain, with RAG over teacher-uploaded documents.
    Generates 10-question exam dynamically from teacher's documents only (no static QuestionBank).
    """
    try:
        from .models import TestSession, ExamAnswerAttempt, Document
        
        print(f"🎯 Interactive Exam Flow - Student: {user.username}, Answer: '{student_answer[:50]}...'")
        
        # Get the test session
        session = TestSession.objects.get(id=test_session_id, student=user, test_type='exam')
        
        # Parse session notes to get current state
        notes = {}
        if session.notes:
            try:
                notes = json.loads(session.notes)
            except json.JSONDecodeError:
                notes = {}
        
        # Initialize session state if needed
        if 'question_index' not in notes:
            notes['question_index'] = 0
            notes['attempts_for_current'] = 0
            notes['score_correct'] = 0
            notes['level'] = notes.get('level', 'intermediate')  # Default difficulty
            notes['exam_start_time'] = timezone.now().isoformat()
        
        current_index = notes['question_index']
        attempts_for_current = notes['attempts_for_current']
        
        # 1) Generate questions if not already done
        if 'questions' not in notes or not notes['questions']:
            print("📚 Generating questions from teacher documents...")
            result = _generate_exam_questions_from_docs(user, notes.get('level', 'intermediate'))
            if 'error' in result:
                return Response(result, status=400)
            
            notes['questions'] = result['questions']
            notes['vector_store_id'] = result.get('vector_store_id', '')
            session.notes = json.dumps(notes)
            session.save()
            print(f"✅ Generated {len(notes['questions'])} questions")
        
        # 2) Check if exam completed
        if current_index >= 10:
            return _handle_exam_completion(session, notes)
        
        # 3) Get current question
        current_question = notes['questions'][current_index]
        
        # 4) Evaluate student answer using LLM with RAG
        print(f"📝 Evaluating answer for question {current_index + 1}")
        evaluation_result = _eval_answer_with_llm(current_question, student_answer, notes['vector_store_id'])
        
        # 5) Create attempt record
        attempt = ExamAnswerAttempt.objects.create(
            test_session=session,
            student=user,
            question_id=current_question['id'],
            attempt_number=attempts_for_current + 1,
            answer_text=student_answer,
            is_correct=evaluation_result['is_correct'],
            time_taken_seconds=None,  # Could be calculated if needed
            notes=json.dumps({
                'llm_feedback': evaluation_result.get('feedback_short', ''),
                'canonical_answer': evaluation_result.get('canonical_answer', ''),
                'source_doc_ids': evaluation_result.get('source_doc_ids', []),
                'question_text': current_question['text'],
                'question_type': current_question.get('type', 'open')
            })
        )
        
        # 6) Handle correct vs incorrect responses
        if evaluation_result['is_correct']:
            # Correct answer - advance to next question
            print(f"✅ Correct answer for question {current_index + 1}")
            notes['question_index'] = current_index + 1
            notes['attempts_for_current'] = 0
            notes['score_correct'] += 1
            session.notes = json.dumps(notes)
            session.save()
            
            # Return success response
            if notes['question_index'] >= 10:
                return _handle_exam_completion(session, notes)
            else:
                next_question = notes['questions'][notes['question_index']]
                return Response({
                    'status': 'correct',
                    'question': {
                        'id': next_question['id'],
                        'text': next_question['text'],
                        'type': next_question.get('type', 'open'),
                        'options': next_question.get('options')
                    },
                    'progress': {
                        'current': notes['question_index'] + 1,
                        'total': 10,
                        'attempts_for_current': 0,
                        'score_correct': notes['score_correct']
                    },
                    'canonical_answer': evaluation_result.get('canonical_answer', ''),
                    'sources': evaluation_result.get('source_doc_ids', []),
                    'session_id': session.id
                })
        else:
            # Incorrect answer
            print(f"❌ Incorrect answer for question {current_index + 1}, attempt {attempts_for_current + 1}")
            notes['attempts_for_current'] = attempts_for_current + 1
            
            if notes['attempts_for_current'] <= 3:
                # Generate hint
                hint_text = _make_hint(current_question, student_answer, notes['vector_store_id'], notes['attempts_for_current'])
                session.notes = json.dumps(notes)
                session.save()
                
                return Response({
                    'status': 'hint',
                    'question': {
                        'id': current_question['id'],
                        'text': current_question['text'],
                        'type': current_question.get('type', 'open'),
                        'options': current_question.get('options')
                    },
                    'progress': {
                        'current': current_index + 1,
                        'total': 10,
                        'attempts_for_current': notes['attempts_for_current'],
                        'score_correct': notes['score_correct']
                    },
                    'hint': hint_text,
                    'sources': evaluation_result.get('source_doc_ids', []),
                    'session_id': session.id
                })
            else:
                # 4th attempt - reveal answer and advance
                explanation = _make_reveal(current_question, notes['vector_store_id'])
                notes['question_index'] = current_index + 1
                notes['attempts_for_current'] = 0
                session.notes = json.dumps(notes)
                session.save()
                
                if notes['question_index'] >= 10:
                    return _handle_exam_completion(session, notes)
                else:
                    next_question = notes['questions'][notes['question_index']]
                    return Response({
                        'status': 'reveal',
                        'question': {
                            'id': next_question['id'],
                            'text': next_question['text'],
                            'type': next_question.get('type', 'open'),
                            'options': next_question.get('options')
                        },
                        'progress': {
                            'current': notes['question_index'] + 1,
                            'total': 10,
                            'attempts_for_current': 0,
                            'score_correct': notes['score_correct']
                        },
                        'explanation': explanation,
                        'canonical_answer': evaluation_result.get('canonical_answer', ''),
                        'sources': evaluation_result.get('source_doc_ids', []),
                        'session_id': session.id
                    })
    
    except Exception as e:
        print(f"❌ Exam interaction error: {e}")
        import traceback
        traceback.print_exc()
        return Response({'error': str(e)}, status=500)


def _generate_exam_questions_from_docs(user, num_questions=10):
    """Generate exam questions using Gemini AI over TEACHER documents (not student documents)"""
    try:
        from .models import Document
        import time
        import random
        
        print(f"🎯 Generating {num_questions} exam questions for student {user.username} using Gemini AI")
        print(f"DEBUG: Looking for TEACHER documents, not student documents")
        
        # Get TEACHER documents only (not student documents)
        teacher_documents = Document.objects.filter(
            uploaded_by__role='teacher',  # Only teachers' documents
            processing_status='completed',
            extracted_text__isnull=False
        ).exclude(extracted_text='').order_by('-created_at')[:5]  # Get recent teacher documents
        
        print(f"DEBUG: Found {teacher_documents.count()} teacher documents for question generation")
        
        if not teacher_documents.exists():
            print("❌ No teacher documents found!")
            return {'error': 'No teacher documents available for generating questions. Teachers must upload course materials first.'}
        
        # Show which teacher documents we're using
        for doc in teacher_documents:
            print(f"DEBUG: Using teacher document: '{doc.title}' by teacher {doc.uploaded_by.username}")
        
        # Use global Gemini client
        global gemini_client
        if not gemini_client:
            print("❌ Gemini client not available")
            return {'error': 'Gemini AI service not available'}
        
        # Combine all teacher documents
        combined_texts = []
        source_docs = []
        
        for doc in teacher_documents:
            if doc.extracted_text and len(doc.extracted_text.strip()) > 100:
                combined_texts.append(f"[Teacher Document: {doc.title}]\n{doc.extracted_text}")
                source_docs.append({
                    'id': doc.id,
                    'title': doc.title,
                    'teacher': doc.uploaded_by.username
                })
        
        if not combined_texts:
            return {'error': 'No suitable teacher documents found with sufficient content'}
        
        # Create context from teacher documents
        combined_text = "\n\n===DOCUMENT SEPARATOR===\n\n".join(combined_texts)
        
        print(f"✅ Prepared context from {len(combined_texts)} teacher documents")
        
        # Generate questions using Gemini
        try:
            questions = gemini_client.generate_questions(
                context=combined_text,
                num_questions=num_questions,
                topic="course_content",
                difficulty_mix=True
            )
            
            if questions:
                print(f"✅ Generated {len(questions)} questions using Gemini AI")
                
                return {
                    'questions': questions[:num_questions],  # Ensure we don't exceed requested number
                    'source_documents': source_docs,
                    'generation_method': 'gemini_ai_teacher_documents',
                    'teacher_documents_used': len(source_docs)
                }
            else:
                # Fallback if Gemini fails
                print("⚠️ Gemini generation failed, creating fallback questions...")
                questions = []
                
                # Create sample questions based on teacher documents
                for i in range(min(num_questions, len(combined_texts))):
                    doc_text = combined_texts[i]
                    
                    # Extract first meaningful sentence from document
                    sentences = doc_text.split('.')[:3]
                    content_preview = '. '.join(sentences).strip()
                    if len(content_preview) > 300:
                        content_preview = content_preview[:300] + "..."
                    
                    # Create question based on actual document content
                    if i % 2 == 0:  # Multiple choice
                        questions.append({
                            'id': f"teacher_doc_q_{i+1}",
                            'question_text': f"Based on the course material: {content_preview} - What is the main concept being discussed?",
                            'question_type': 'multiple_choice',
                            'difficulty_level': random.choice(['easy', 'medium', 'hard']),
                            'subject': 'course_content',
                            'options': {
                                'A': f"Concept A related to the material",
                                'B': f"Concept B related to the material", 
                                'C': f"Concept C related to the material",
                                'D': f"Concept D related to the material"
                            },
                            'correct_answer': 'B',
                            'explanation': f"Based on the teacher's document: {source_docs[i % len(source_docs)]['title']}"
                        })
                    else:  # Open-ended
                        questions.append({
                            'id': f"teacher_doc_q_{i+1}",
                            'question_text': f"Explain the concept discussed in: {content_preview}",
                            'question_type': 'open_ended',
                            'difficulty_level': random.choice(['medium', 'hard']),
                            'subject': 'course_content',
                            'correct_answer': f"Answer should be based on the content from {source_docs[i % len(source_docs)]['title']}",
                            'explanation': f"This question tests understanding of material from teacher document: {source_docs[i % len(source_docs)]['title']}"
                        })
                
                # Fill remaining questions if needed
                while len(questions) < num_questions:
                    doc_idx = len(questions) % len(source_docs)
                    questions.append({
                        'id': f"teacher_doc_q_{len(questions)+1}",
                        'question_text': f"Question {len(questions)+1}: According to the teacher's course material '{source_docs[doc_idx]['title']}', explain a key concept covered.",
                        'question_type': 'open_ended',
                        'difficulty_level': 'medium',
                        'subject': 'course_content',
                        'correct_answer': f"Answer should reference content from {source_docs[doc_idx]['title']}",
                        'explanation': f"Based on teacher document: {source_docs[doc_idx]['title']}"
                    })
                
                print(f"✅ Generated {len(questions)} fallback questions from teacher documents")
                
                return {
                    'questions': questions[:num_questions],
                    'source_documents': source_docs,
                    'generation_method': 'fallback_teacher_documents',
                    'teacher_documents_used': len(source_docs)
                }
        
        except Exception as gemini_error:
            print(f"❌ Gemini question generation error: {gemini_error}")
            return {'error': f'Failed to generate questions with Gemini: {str(gemini_error)}'}
        
        print(f"📚 Source documents: {[doc['title'] for doc in source_docs]}")
        
    except Exception as e:
        print(f"❌ Question generation error: {e}")
        import traceback
        traceback.print_exc()
        return {'error': f'Failed to generate questions from teacher documents: {str(e)}'}


def _eval_answer_with_llm(question_data, student_answer, attempt_num):
    """Evaluate student answer using Gemini AI"""
    try:
        global gemini_client
        if not gemini_client:
            return {'correct': False, 'explanation': 'Evaluation system unavailable - Gemini not connected'}
        
        # Use Gemini to evaluate the answer
        evaluation = gemini_client.evaluate_answer(
            question=question_data['question_text'],
            correct_answer=question_data['correct_answer'],
            student_answer=student_answer,
            attempt_number=attempt_num
        )
        
        if evaluation:
            return evaluation
        else:
            # Fallback evaluation
            return {
                'correct': False,
                'score': 0.0,
                'explanation': 'Could not evaluate answer with Gemini AI',
                'feedback': 'Please review with your teacher',
                'canonical_answer': question_data['correct_answer']
            }
        
    except Exception as e:
        print(f"❌ Answer evaluation error: {e}")
        return {
            'correct': False, 
            'score': 0.0,
            'explanation': f'Evaluation error: {e}',
            'feedback': 'Please review with your teacher',
            'canonical_answer': question_data['correct_answer']
        }


def _make_hint(question_data, attempt_num):
    """Generate a hint for the current question using Gemini AI"""
    try:
        global gemini_client
        if not gemini_client:
            return "Hint system unavailable. Try reviewing the course materials."
        
        hint_level = "gentle" if attempt_num == 1 else "moderate" if attempt_num == 2 else "strong"
        
        hint_text = gemini_client.generate_hint(
            question=question_data['question_text'],
            correct_answer=question_data['correct_answer'],
            attempt_number=attempt_num,
            hint_level=hint_level
        )
        
        return hint_text or f"💡 Hint {attempt_num}: Review the key concepts related to this topic in your course materials."
        
    except Exception as e:
        print(f"❌ Hint generation error: {e}")
        return f"💡 Hint {attempt_num}: Consider the main concepts covered in class for this topic."


def _make_reveal(question_data):
    """Generate explanation when revealing the correct answer using Gemini AI"""
    try:
        global gemini_client
        if not gemini_client:
            return f"The correct answer is: {question_data['correct_answer']}\n\n{question_data.get('explanation', 'No explanation available.')}"
        
        explanation = gemini_client.explain_answer(
            question=question_data['question_text'],
            correct_answer=question_data['correct_answer']
        )
        
        if explanation:
            return f"📚 **Correct Answer:** {question_data['correct_answer']}\n\n**Explanation:**\n{explanation}"
        else:
            return f"📚 **Correct Answer:** {question_data['correct_answer']}\n\n{question_data.get('explanation', 'This is the correct answer based on the course materials.')}"
        
    except Exception as e:
        print(f"❌ Explanation generation error: {e}")
        return f"📚 **Correct Answer:** {question_data['correct_answer']}\n\n{question_data.get('explanation', 'This is the correct answer.')}"


def _handle_exam_completion(session, questions_data):
    """Handle exam completion and generate final results"""
    try:
        # Get all exam attempts for this session
        attempts = ExamAnswerAttempt.objects.filter(test_session=session).order_by('question_number', 'attempt_number')
        
        total_questions = len(questions_data)
        correct_count = 0
        
        # Count correct answers (only best attempt per question)
        for q_num in range(1, total_questions + 1):
            question_attempts = attempts.filter(question_number=q_num)
            if question_attempts.filter(is_correct=True).exists():
                correct_count += 1
        
        # Calculate score
        score_percentage = (correct_count / total_questions) * 100 if total_questions > 0 else 0
        
        # Generate performance message
        if score_percentage >= 90:
            performance_msg = "🌟 Excellent work! Outstanding performance!"
        elif score_percentage >= 80:
            performance_msg = "👏 Great job! You did very well!"
        elif score_percentage >= 70:
            performance_msg = "📚 Good work! You have a solid understanding!"
        elif score_percentage >= 60:
            performance_msg = "💪 Not bad! Keep studying to improve further!"
        else:
            performance_msg = "📖 Keep practicing! There's room for improvement!"
        
        # Calculate time spent
        time_spent = "N/A"
        if session.created_at and session.updated_at:
            duration = session.updated_at - session.created_at
            minutes = int(duration.total_seconds() // 60)
            seconds = int(duration.total_seconds() % 60)
            time_spent = f"{minutes}:{seconds:02d}"
        
        completion_message = f"""🎯 **Exam Completed!**

**Final Results:**
- Questions: {total_questions}
- Correct: {correct_count}
- Score: {score_percentage:.1f}%
- Time: {time_spent}

{performance_msg}

Your results have been saved. Great work on completing the exam!"""
        
        return {
            'message': completion_message,
            'total_questions': total_questions,
            'correct_answers': correct_count,
            'score_percentage': score_percentage,
            'time_spent': time_spent
        }
        
    except Exception as e:
        print(f"❌ Exam completion error: {e}")
        return {
            'message': "Exam completed with errors. Please contact your teacher.",
            'total_questions': 0,
            'correct_answers': 0,
            'score_percentage': 0,
            'time_spent': "N/A"
        }


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]


# Main Views
>>>>>>> daniel
class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

<<<<<<< HEAD

# ViewSet that provides CRUD operations (Create, Read, Update, Delete)
# for Lesson objects through the API
class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()  # All lessons from the database
    serializer_class = LessonSerializer  # Use the serializer we defined
    permission_classes = [permissions.IsAuthenticated]  # Require login for access
=======
class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]
>>>>>>> daniel

@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def chat_interaction(request):
<<<<<<< HEAD
    if request.method == 'GET':
        return Response({"message": "ה-API הזה מקבל שאלות ב-POST בלבד."})
    question = request.data.get('question', '').strip()
    user = request.user

    if not question:
        return Response({"error": "Missing question"}, status=400)

    # ניתוח מתמטי
    try:
        expr = sympify(question)
        result = expr.evalf()
        answer = f"{question} = {result}"

    except SympifyError:
        # שליחה ל־LLM
        data = {
            "model": "llama2",
            "prompt": question,
            "stream": False
        }
        try:
            response = requests.post("http://localhost:11434/api/generate", json=data)
            response_data = response.json()
            answer = response_data.get("response", "Sorry, I didn’t understand.")
        except:
            answer = "Error connecting to AI service."

    # שמירה ב-DB
    ChatInteraction.objects.create(
        student=user,
        question=question,
        answer=answer
    )

    return Response({"answer": answer})
=======
    """
    🤖 Main chat endpoint with Gemini AI + comprehensive features
    
    Features:
    - Gemini AI responses
    - Math solving (SymPy)
    - Document upload and Q&A
    - Image OCR processing
    - Multi-document querying
    - Conversation memory
    - Smart responses
    """
    print(f"🔍 DEBUG: chat_interaction called - Method: {request.method}")
    print(f"🔍 DEBUG: Content-Type: {request.content_type}")
    print(f"🔍 DEBUG: User authenticated: {request.user.is_authenticated}")
    
    if request.method == 'GET':
        return Response({
            "message": "Comprehensive Educational Chat API with Gemini 2.5 Flash AI + Image Support",
            "features": {
                "gemini_ai": "✅ Google Gemini 2.5 Flash (Latest)" if GEMINI_AVAILABLE else "❌ Gemini not available",
                "thinking_capabilities": "✅ Adaptive thinking and reasoning",
                "math_solving": "✅ SymPy integration",
                "document_qa": "✅ PDF upload and analysis with Gemini 2.5",
                "image_ocr": "✅ Image text extraction with OCR",
                "context_awareness": "✅ Document context analysis with Gemini",
                "conversation_memory": "✅ Chat history support",
                "multi_document": "✅ Query multiple documents with Gemini",
                "fallback_rag": "✅ LangChain RAG fallback" if LANGCHAIN_AVAILABLE else "❌ No fallback available"
            },
            "supported_formats": ["PDF", "Text", "Images (JPG, PNG, GIF, BMP)"],
            "ai_provider": "Google Gemini 2.5 Flash (Latest)" if GEMINI_AVAILABLE else "Not available",
            "langchain_status": "✅ Available for fallback" if LANGCHAIN_AVAILABLE else "❌ Not installed"
        })
    
    # Extract request data - Handle both form data (with images) and JSON
    try:
        if request.content_type and request.content_type.startswith('multipart/form-data'):
            # Form data with potential image upload
            question = request.POST.get('question', '').strip()  # Changed from 'message' to 'question'
            uploaded_file = request.FILES.get('document')
            uploaded_image = request.FILES.get('image')
            document_ids = request.POST.getlist('document_ids') or []
            use_rag = request.POST.get('use_rag', 'true').lower() == 'true'
            # Exam mode parameters
            exam_mode = request.POST.get('exam_mode', 'false').lower() == 'true'
            test_session_id = request.POST.get('test_session_id', '')
            
            print(f"🔍 DEBUG Form Data: question='{question[:50]}...', image={uploaded_image is not None}, use_rag={use_rag}, exam_mode={exam_mode}")
            if uploaded_image:
                print(f"🔍 DEBUG Image: name={uploaded_image.name}, size={uploaded_image.size}, content_type={getattr(uploaded_image, 'content_type', 'unknown')}")
        else:
            # JSON data
            question = request.data.get('question', '').strip()
            uploaded_file = request.FILES.get('document') if hasattr(request, 'FILES') else None
            uploaded_image = request.FILES.get('image') if hasattr(request, 'FILES') else None
            document_ids = request.data.get('document_ids', [])
            use_rag = request.data.get('use_rag', True)
            # Exam mode parameters
            exam_mode = request.data.get('exam_mode', False)
            test_session_id = request.data.get('test_session_id', '')
            
            print(f"🔍 DEBUG JSON Data: question='{question[:50]}...', image={uploaded_image is not None}, use_rag={use_rag}, exam_mode={exam_mode}")
            
    except Exception as e:
        print(f"❌ ERROR extracting request data: {e}")
        return Response({
            "error": f"Failed to parse request data: {str(e)}",
            "content_type": request.content_type,
            "help": "Please ensure you're sending either JSON data or proper multipart form data"
        }, status=400)
    
    # Handle document_ids - could be a list or single value
    if isinstance(document_ids, str):
        document_ids = [document_ids] if document_ids else []
    elif not isinstance(document_ids, list):
        document_ids = []
    user = request.user
    
    print(f"🔍 DEBUG: Final validation - question: '{question[:30]}...', image: {uploaded_image is not None}, exam_mode: {exam_mode}")
    
    # 🎓 EXAM MODE: Handle exam chat interaction first
    if exam_mode and test_session_id:
        print(f"🎓 DEBUG: Processing exam mode chat - session: {test_session_id}")
        return handle_exam_chat_interaction(user, question, test_session_id)
    
    if not question and not uploaded_image:
        print(f"❌ DEBUG: Validation failed - no question or image provided")
        return Response({
            "error": "Please provide either a question or upload an image",
            "received_question": f"'{question}'" if question else "empty",
            "received_image": uploaded_image is not None,
            "help": "You can send text, upload an image, or both"
        }, status=400)
    
    response_data = {
        "answer": "",
        "source": "",
        "chat_id": None,
        "document_processed": False,
        "image_processed": False,
        "extracted_text": "",
        "ocr_metadata": {},  # Changed from "image_metadata" to "ocr_metadata"
        "documents_used": [],
        "processing_info": {},
        "features_used": [],
        "exam_mode": exam_mode,
        "test_session_id": test_session_id if exam_mode else None
    }
    
    try:
        # �️ STEP 1: Process uploaded image first if present
        if uploaded_image:
            # Validate image file
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
            file_extension = os.path.splitext(uploaded_image.name)[1].lower()
            
            if file_extension not in valid_extensions:
                return Response({
                    "error": f"Invalid image format. Supported: {', '.join(valid_extensions)}"
                }, status=400)
            
            # Save image temporarily and process with OCR
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
                for chunk in uploaded_image.chunks():
                    temp_file.write(chunk)
                temp_image_path = temp_file.name
            
            try:
                # Extract text from image using OCR
                print(f"DEBUG: Processing image with OCR: {temp_image_path}")
                print(f"DEBUG: Image file exists: {os.path.exists(temp_image_path)}")
                print(f"DEBUG: Image file size: {os.path.getsize(temp_image_path) if os.path.exists(temp_image_path) else 'N/A'} bytes")
                
                ocr_result = document_processor.extract_image_text(temp_image_path)
                print(f"DEBUG: OCR result keys: {list(ocr_result.keys())}")
                print(f"DEBUG: OCR text length: {len(ocr_result.get('text', ''))}")
                print(f"DEBUG: OCR text content: '{ocr_result.get('text', '')}'")
                print(f"DEBUG: OCR errors: {ocr_result.get('processing_errors', [])}")
                print(f"DEBUG: OCR text quality: {ocr_result.get('text_quality', 'unknown')}")
                
                extracted_text = ocr_result.get('text', '').strip()
                print(f"DEBUG: Extracted text after strip: '{extracted_text}'")
                print(f"DEBUG: OCR check: {extracted_text != 'OCR not available - PaddleOCR not installed. Please install PaddleOCR to enable image text extraction.'}")
                
                if extracted_text and not extracted_text.startswith("OCR not available"):
                    print(f"DEBUG: Processing successful text extraction")
                    response_data["image_processed"] = True
                    response_data["extracted_text"] = extracted_text
                    response_data["ocr_metadata"] = ocr_result.get('metadata', {})
                    response_data["features_used"].append("Image OCR")
                    
                    # Combine user question with extracted text
                    if question:
                        combined_question = f"{question}\n\nText extracted from image:\n{extracted_text}"
                    else:
                        combined_question = f"Please help me understand this text from the image:\n{extracted_text}"
                    
                    question = combined_question
                    print(f"DEBUG: Combined question length: {len(combined_question)}")
                    
                    # Save OCR result as a temporary document for potential future reference
                    try:
                        temp_document = Document.objects.create(
                            uploaded_by=user,
                            title=f"OCR_{uploaded_image.name}_{int(time.time())}",
                            document_type='image',
                            file_path=temp_image_path,
                            extracted_text=extracted_text,
                            metadata=json.dumps(ocr_result.get('metadata', {})),
                            processing_status='completed'
                        )
                        response_data["documents_used"].append({
                            "id": temp_document.id,
                            "title": temp_document.title,
                            "type": "image_ocr"
                        })
                        print(f"DEBUG: Saved OCR document with ID: {temp_document.id}")
                    except Exception as e:
                        print(f"Warning: Could not save OCR document: {e}")
                    
                else:
                    # Handle case where OCR is not available or failed
                    print(f"DEBUG: OCR failed or no text extracted")
                    
                    if extracted_text.startswith("OCR not available"):
                        error_message = "OCR is not available. PaddleOCR is not installed on this server. Please contact the administrator to enable image text extraction."
                        print(f"DEBUG: PaddleOCR not installed error")
                    elif ocr_result.get('processing_errors'):
                        error_message = f"Could not extract text from the image. {'; '.join(ocr_result['processing_errors'])}"
                        print(f"DEBUG: OCR processing errors: {ocr_result['processing_errors']}")
                    else:
                        error_message = "No readable text was found in the image. Please try with a clearer image containing text, or ensure the text is not handwritten or too stylized."
                        print(f"DEBUG: No processing errors but no text extracted - likely image quality issue")
                    
                    # Instead of returning error, let's continue with the question if provided
                    if question:
                        print(f"DEBUG: No OCR text but user provided question, continuing with: '{question}'")
                        response_data["image_processed"] = False
                        response_data["extracted_text"] = ""
                        response_data["ocr_metadata"] = ocr_result.get('metadata', {})
                        response_data["processing_errors"] = ocr_result.get('processing_errors', [])
                        response_data["ocr_feedback"] = error_message  # Add feedback for user
                        # Continue with the original question
                    else:
                        print(f"DEBUG: No OCR text and no question, returning error")
                        return Response({
                            "error": error_message,
                            "ocr_metadata": ocr_result.get('metadata', {}),
                            "processing_errors": ocr_result.get('processing_errors', []),
                            "suggestion": "Try uploading a clearer image with printed text, or include a text question along with your image."
                        }, status=400)
                    
            finally:
                # Clean up temporary file
                if os.path.exists(temp_image_path):
                    try:
                        os.unlink(temp_image_path)
                    except Exception as e:
                        print(f"Warning: Could not delete temp image file: {e}")
        
        # 🔢 STEP 2: Try mathematics (highest priority for math expressions)
        print(f"DEBUG: About to process question for math: '{question[:100]}...' (length: {len(question)})")
        try:
            expr = sympify(question)
            result = expr.evalf()
            response_data["answer"] = f"{question} = {result}"
            response_data["source"] = "mathematics"
            response_data["features_used"].append("SymPy Math Solver")
            print(f"DEBUG: Math processing successful: {response_data['answer']}")
            
        except SympifyError:
            print(f"DEBUG: Not a math expression, continuing to other processing")
            target_document = None
            
            # Note: File upload is now handled by upload_document function
            if uploaded_file:
                print("DEBUG: File upload detected but not processed in chat endpoint")
                # Legacy upload processing commented out - use upload_document endpoint instead
                pass
                
                # if doc_result['success']:
                #     # Save document to database
                #     document = Document.objects.create(
                #         uploaded_by=user,
                #         title=doc_result['title'],
                #         document_type=doc_result['document_type'],
                #         file_path=doc_result['file_path'],
                #         extracted_text=doc_result['extraction_result']['text'],
                #         metadata=json.dumps(doc_result['extraction_result']['metadata']),
                #         processing_status='completed'
                #     )
                #     target_document = document
                #     document_ids = [str(document.id)]
                #     
                #     response_data["document_processed"] = True
                #     response_data["processing_info"] = {
                #         "document_id": document.id,
                #         "title": document.title,
                #         "text_length": len(document.extracted_text),
                #         "type": document.document_type
                #     }
                #     response_data["features_used"].append("Document Upload & Processing")
                # else:
                #     return Response({"error": f"Document processing failed: {doc_result['error']}"}, status=400)
            
            # 🔍 STEP 3: Document-based Q&A with RAG
            if document_ids:
                # Students can access their own documents + teacher documents
                # Teachers can only access their own documents
                if user.role == 'teacher':
                    documents = Document.objects.filter(
                        id__in=document_ids,
                        uploaded_by=user
                    )
                else:
                    # Students can access their own documents and teacher documents
                    from django.db.models import Q
                    documents = Document.objects.filter(
                        id__in=document_ids
                    ).filter(
                        Q(uploaded_by=user) | Q(uploaded_by__role='teacher')
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
                        
                        # Use Gemini for document-based Q&A instead of RAG
                        if combined_texts:
                            # Get conversation context
                            conversation_context = get_conversation_context(user.id)
                            
                            # Create enhanced prompt with document context for Gemini
                            enhanced_prompt = f"""Based on the following documents: {', '.join([doc['title'] for doc in used_docs])}

Document Content:
{combined_text}

Previous conversation context:
{conversation_context}

User Question: {question}

Please provide a comprehensive answer based on the document content above. Focus on information that is explicitly mentioned in the documents."""
                            
                            if GEMINI_AVAILABLE and gemini_client:
                                # קריאת היסטוריית השיחה למסמכים
                                try:
                                    recent_chats = ChatInteraction.objects.filter(
                                        student=user
                                    ).order_by('-created_at')[:5]
                                    
                                    chat_history = []
                                    for chat in reversed(recent_chats):
                                        chat_history.append({
                                            'user': chat.question,
                                            'assistant': chat.answer
                                        })
                                    
                                    print(f"DEBUG: Document analysis with {len(chat_history)} conversation history items")
                                except Exception as e:
                                    print(f"DEBUG: Failed to retrieve chat history for documents: {e}")
                                    chat_history = []
                                
                                answer = gemini_client.chat_response(
                                    enhanced_prompt,
                                    context="",
                                    chat_history=chat_history
                                )
                                response_data["features_used"].extend(["Gemini Document Analysis", "Context Awareness", "Conversation Memory"])
                            else:
                                # Fallback to RAG if Gemini unavailable
                                vectorstore = rag_processor.create_vector_store(
                                    combined_text, 
                                    f"combined_{user.id}_{int(time.time())}"
                                )
                                if vectorstore:
                                    answer = rag_processor.query_with_rag(
                                        vectorstore, 
                                        question, 
                                        conversation_context
                                    )
                                    response_data["features_used"].extend(["RAG Document Search", "Vector Similarity"])
                                else:
                                    answer = "Sorry, I couldn't process the documents to answer your question."
                            
                            response_data["answer"] = answer
                            response_data["source"] = "document_analysis"
                            response_data["documents_used"] = used_docs
                            
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
            
            # 💬 STEP 4: General conversation with memory OR auto-document detection
            else:
                print(f"DEBUG: Processing as general conversation")
                print(f"DEBUG: Question: '{question[:100]}...'")
                print(f"DEBUG: LANGCHAIN_AVAILABLE: {LANGCHAIN_AVAILABLE}")
                
                # Check if user has any recent documents that might be relevant
                # Include both user's documents and teacher documents (for students)
                if user.role == 'student':
                    from django.db.models import Q
                    recent_documents = Document.objects.filter(
                        Q(uploaded_by=user) | Q(uploaded_by__role='teacher'),
                        processing_status='completed',
                        extracted_text__isnull=False
                    ).exclude(extracted_text='').order_by('-created_at')[:5]
                else:
                    recent_documents = Document.objects.filter(
                        uploaded_by=user,
                        processing_status='completed',
                        extracted_text__isnull=False
                    ).exclude(extracted_text='').order_by('-created_at')[:3]
                
                # If user has recent documents, try to find relevant content
                document_context = ""
                auto_selected_doc = None
                
                if recent_documents.exists():
                    print(f"DEBUG: Found {recent_documents.count()} recent documents, checking for relevance")
                    question_words = set(question.lower().split())
                    relevant_docs = []
                    
                    for doc in recent_documents:
                        doc_words = set(doc.extracted_text.lower().split())
                        # Check for word overlap or document name mention
                        overlap = len(question_words.intersection(doc_words))
                        
                        # Enhanced document name detection
                        doc_title_lower = doc.title.lower()
                        question_lower = question.lower()
                        
                        # Check various ways the document might be mentioned
                        doc_name_mentioned = (
                            any(word in doc_title_lower for word in question_words) or
                            doc_title_lower in question_lower or
                            any(part in question_lower for part in doc_title_lower.split('.')[0].split()) or  # Check filename without extension
                            any(f'"{word}"' in question_lower for word in doc_title_lower.split('.')[0].split())  # Check quoted mentions
                        )
                        
                        # Consider document relevant if:
                        # 1. There's word overlap with content
                        # 2. Document name/title is mentioned in question
                        # 3. Question asks about "document", "file", "pdf", etc.
                        # 4. Question mentions "first", "1", "question" etc. and we have documents
                        general_doc_words = {'document', 'file', 'pdf', 'questions', 'problems', 'inside', 'from', 'content', 'answer', 'solve'}
                        question_ref_words = {'first', '1st', '1', 'question', 'problem', 'equation'}
                        
                        has_general_doc_reference = bool(question_words.intersection(general_doc_words))
                        has_question_reference = bool(question_words.intersection(question_ref_words))
                        
                        # Higher scoring for direct name mentions
                        score = overlap
                        if doc_name_mentioned:
                            score += 20
                        if has_general_doc_reference:
                            score += 5
                        if has_question_reference and doc.extracted_text:
                            score += 10
                        
                        if score > 0 or doc_name_mentioned or has_general_doc_reference:
                            relevant_docs.append((doc, score))
                            print(f"DEBUG: Document '{doc.title}' considered relevant (score: {score}, overlap: {overlap}, name_mentioned: {doc_name_mentioned}, general_ref: {has_general_doc_reference})")
                    
                    if relevant_docs:
                        # Sort by relevance and use the most relevant document
                        relevant_docs.sort(key=lambda x: x[1], reverse=True)
                        best_doc = relevant_docs[0][0]
                        auto_selected_doc = best_doc
                        
                        # If score is high enough, redirect to document processing
                        if relevant_docs[0][1] >= 15:  # High confidence threshold
                            print(f"DEBUG: HIGH CONFIDENCE - Redirecting to document RAG processing for '{best_doc.title}'")
                            document_ids = [str(best_doc.id)]
                            
                            # Jump back to document processing logic
                            documents = Document.objects.filter(id=best_doc.id)
                            
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
                                        f"auto_selected_{user.id}_{int(time.time())}"
                                    )
                                    
                                    # Use Gemini for auto-selected document analysis
                                    if combined_texts:
                                        # Get conversation context
                                        conversation_context = get_conversation_context(user.id)
                                        
                                        # Create enhanced prompt with document context for Gemini
                                        enhanced_prompt = f"""Based on the auto-selected document: {best_doc.title}

Document Content:
{combined_text}

Previous conversation context:
{conversation_context}

User Question: {question}

Please provide a comprehensive answer based on the document content above. The system automatically selected this document as relevant to the user's question."""
                                        
                                        if GEMINI_AVAILABLE and gemini_client:
                                            answer = gemini_client.chat_response(enhanced_prompt)
                                            response_data["features_used"].extend(["Gemini Document Analysis", "Auto Document Detection", "Context Awareness"])
                                        else:
                                            # Fallback to RAG if Gemini unavailable
                                            vectorstore = rag_processor.create_vector_store(
                                                combined_text, 
                                                f"auto_selected_{user.id}_{int(time.time())}"
                                            )
                                            if vectorstore:
                                                answer = rag_processor.query_with_rag(
                                                    vectorstore, 
                                                    question, 
                                                    conversation_context
                                                )
                                                response_data["features_used"].extend(["RAG Document Search", "Vector Similarity", "Auto Document Detection"])
                                            else:
                                                answer = "Sorry, I couldn't process the auto-selected document to answer your question."
                                        
                                        response_data["answer"] = answer
                                        response_data["source"] = "document_auto_analysis"
                                        response_data["documents_used"] = used_docs
                                        
                                        # Skip to the end
                                        print(f"DEBUG: Successfully processed with auto-selected document using Gemini")
                                        
                                    else:
                                        # Fallback to simple text search
                                        combined_text_lower = combined_text.lower()
                                        question_lower = question.lower()
                                        
                                        if any(word in combined_text_lower for word in question_lower.split()):
                                            context_start = max(0, combined_text_lower.find(question_lower.split()[0]) - 300)
                                            context_end = min(len(combined_text), context_start + 1000)
                                            context = combined_text[context_start:context_end]
                                            
                                            enhanced_question = f"""
                                            Based on this document: {best_doc.title}
                                            
                                            Document content: {context}
                                            
                                            Student question: {question}
                                            
                                            Please answer based on the document content.
                                            """
                                            
                                            answer = get_simple_ollama_response(enhanced_question)
                                            response_data["answer"] = answer
                                            response_data["source"] = "document_simple"
                                            response_data["documents_used"] = used_docs
                                            response_data["features_used"].extend(["Simple Document Search", "Auto Document Detection"])
                                        else:
                                            response_data["answer"] = "I found the document you mentioned but couldn't find relevant information for your specific question."
                                            response_data["source"] = "no_match"
                        else:
                            # Lower confidence - use as context for general chat
                            doc_text = best_doc.extracted_text
                            document_context = f"\n\nDOCUMENT CONTENT from '{best_doc.title}':\n{doc_text}"
                            print(f"DEBUG: Using document '{best_doc.title}' for context (full text length: {len(doc_text)})")
                    else:
                        print(f"DEBUG: No relevant documents found based on question content")
                
                # Only do general chat if we didn't redirect to document processing
                if response_data["source"] == "":
                    # Enhance the question with document context if available
                    enhanced_question = question
                    if document_context:
                        enhanced_question = f"""The user has uploaded a document and is asking about it. Here is the question: "{question}"

{document_context}

IMPORTANT: Use the document content above to answer the user's question. If they ask about "questions" or "problems" in the document, look for mathematical equations, problems, or questions in the document content and solve/explain them. Do not make up generic answers - use only what's actually in the document."""
                    
                    # Use Gemini for chat responses (with memory support)
                    if GEMINI_AVAILABLE and gemini_client:
                        print(f"DEBUG: Using Gemini AI chat response with conversation history")
                        
                        # קריאת היסטוריית השיחה האחרונה
                        try:
                            recent_chats = ChatInteraction.objects.filter(
                                student=user
                            ).order_by('-created_at')[:5]  # 5 שיחות אחרונות
                            
                            chat_history = []
                            for chat in reversed(recent_chats):
                                chat_history.append({
                                    'user': chat.question,
                                    'assistant': chat.answer
                                })
                            
                            print(f"DEBUG: Retrieved {len(chat_history)} previous conversations for context")
                        except Exception as e:
                            print(f"DEBUG: Failed to retrieve chat history: {e}")
                            chat_history = []
                        
                        # קריאה ל-Gemini עם היסטוריה
                        answer = gemini_client.chat_response(
                            enhanced_question, 
                            context=document_context or "", 
                            chat_history=chat_history
                        )
                        response_data["features_used"].append("Gemini AI Chat")
                        response_data["features_used"].append("Conversation Memory")
                        if document_context:
                            response_data["features_used"].append("Automatic Document Context")
                    elif LANGCHAIN_AVAILABLE:
                        print(f"DEBUG: Fallback to LangChain memory chat")
                        answer = rag_processor.chat_with_memory(user.id, enhanced_question)
                        response_data["features_used"].append("Conversation Memory")
                        if document_context:
                            response_data["features_used"].append("Automatic Document Context")
                    else:
                        print(f"DEBUG: Using simple fallback response")
                        answer = get_simple_gemini_response(enhanced_question, user)
                        if document_context:
                            response_data["features_used"].append("Automatic Document Context")
                    
                    print(f"DEBUG: Generated answer length: {len(answer)}")
                    print(f"DEBUG: Generated answer preview: {answer[:100]}...")
                    
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
        
        print(f"DEBUG: Final response data:")
        print(f"  - answer length: {len(response_data.get('answer', ''))}")
        print(f"  - answer preview: {response_data.get('answer', '')[:100]}...")
        print(f"  - source: {response_data.get('source', 'none')}")
        print(f"  - image_processed: {response_data.get('image_processed', False)}")
        print(f"  - extracted_text length: {len(response_data.get('extracted_text', ''))}")
        print(f"  - features_used: {response_data.get('features_used', [])}")
        
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
    Uses username-only authentication for both students and teachers
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({
            'error': 'Username and password are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    print(f"DEBUG: Login attempt - username: {username}")
    
    # Simple username/password authentication only
    user = authenticate(username=username, password=password)
    
    print(f"DEBUG: Authentication result - user: {user}")
    if user:
        print(f"DEBUG: User details - username: {user.username}, role: {user.role}, active: {user.is_active}")
    
    if user and user.is_active:
        # Get or create token for user
        token, created = Token.objects.get_or_create(user=user)
        
        print(f"DEBUG: Login successful for user: {user.username}, role: {user.role}")
        
        return Response({
            'token': token.key,
            'user': {
                'id': user.id,
                'username': user.username,
                'role': user.role,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        })
    else:
        print(f"DEBUG: Login failed for username: {username}")
        if user:
            print(f"DEBUG: User found but not active: {user.is_active}")
        else:
            print(f"DEBUG: No user found with username: {username}")
        
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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_image_upload(request):
    """🧪 Test endpoint for debugging image uploads"""
    try:
        print(f"DEBUG: Content-Type: {request.content_type}")
        print(f"DEBUG: POST data keys: {list(request.POST.keys())}")
        print(f"DEBUG: FILES data keys: {list(request.FILES.keys())}")
        
        # Check what we received
        question = request.POST.get('question', '')
        image = request.FILES.get('image')
        
        response_data = {
            "received_question": question,
            "received_image": image is not None,
            "image_name": image.name if image else None,
            "image_size": image.size if image else None,
            "content_type": request.content_type,
            "post_keys": list(request.POST.keys()),
            "files_keys": list(request.FILES.keys())
        }
        
        if image:
            print(f"DEBUG: Image received - {image.name}, {image.size} bytes")
            # Try to process the image
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                for chunk in image.chunks():
                    temp_file.write(chunk)
                temp_path = temp_file.name
            
            # Test OCR
            try:
                from .document_processing import document_processor
                ocr_result = document_processor.extract_image_text(temp_path)
                response_data["ocr_result"] = {
                    "text_length": len(ocr_result.get('text', '')),
                    "text_preview": ocr_result.get('text', '')[:100] + "..." if len(ocr_result.get('text', '')) > 100 else ocr_result.get('text', ''),
                    "errors": ocr_result.get('processing_errors', []),
                    "metadata": ocr_result.get('metadata', {})
                }
            except Exception as e:
                response_data["ocr_error"] = str(e)
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
        
        return Response(response_data)
        
    except Exception as e:
        return Response({
            "error": str(e),
            "error_type": type(e).__name__
        }, status=500)

# ===== NEW VIEWS FOR DOCUMENT UPLOAD AND QUESTION MANAGEMENT =====

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_document(request):
    """Handle document upload for teachers (question generation) and students (AI chat)"""
    try:
        # Handle file upload - check multiple possible field names
        uploaded_file = request.FILES.get('document') or request.FILES.get('file') or request.FILES.get('upload')
        title = request.data.get('title', '') or request.POST.get('title', '')
        
        print(f"DEBUG: Upload attempt by user '{request.user.username}' (role: {request.user.role})")
        print(f"DEBUG: Available FILES keys: {list(request.FILES.keys())}")
        print(f"DEBUG: Available POST keys: {list(request.POST.keys())}")
        print(f"DEBUG: Available data keys: {list(request.data.keys()) if hasattr(request, 'data') else 'No data'}")
        print(f"DEBUG: File found: {uploaded_file.name if uploaded_file else 'None'}")
        print(f"DEBUG: Title: '{title}'")
        print(f"DEBUG: Content-Type: {request.content_type}")
        
        if not uploaded_file:
            # If no file found, try to get the first available file
            if request.FILES:
                first_file_key = list(request.FILES.keys())[0]
                uploaded_file = request.FILES[first_file_key]
                print(f"DEBUG: Using first available file from key '{first_file_key}': {uploaded_file.name}")
            else:
                print("ERROR: No file provided - FILES is empty")
                return Response({
                    'error': 'No file provided',
                    'debug_info': {
                        'files_keys': list(request.FILES.keys()),
                        'post_keys': list(request.POST.keys()),
                        'content_type': request.content_type
                    }
                }, status=400)
        
        # Import required modules with error handling
        try:
            from .document_processing import document_processor
            from django.conf import settings
            print("DEBUG: Successfully imported required modules")
        except ImportError as import_error:
            print(f"ERROR: Import failed: {import_error}")
            return Response({'error': f'System modules not available: {str(import_error)}'}, status=500)
        
        # Determine document type from file extension
        file_extension = uploaded_file.name.lower().split('.')[-1]
        document_type = 'pdf' if file_extension == 'pdf' else 'image' if file_extension in ['jpg', 'jpeg', 'png'] else 'text'
        print(f"DEBUG: Detected document type: {document_type}")
        
        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join(settings.BASE_DIR, 'media', 'documents')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}_{uploaded_file.name}"
        file_path = os.path.join(upload_dir, unique_filename)
        print(f"DEBUG: Saving file to: {file_path}")
        
        # Save file to disk
        try:
            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            print("DEBUG: File saved successfully")
        except Exception as file_error:
            print(f"ERROR: File save failed: {file_error}")
            return Response({'error': f'Failed to save file: {str(file_error)}'}, status=500)
        
        # Create document record
        try:
            document = Document.objects.create(
                uploaded_by=request.user,
                title=title or uploaded_file.name,
                document_type=document_type,
                file_path=file_path,
                processing_status='processing'
            )
            print(f"DEBUG: Created document record with ID: {document.id}")
        except Exception as db_error:
            print(f"ERROR: Database creation failed: {db_error}")
            # Clean up file if database creation fails
            if os.path.exists(file_path):
                os.unlink(file_path)
            return Response({'error': f'Failed to create document record: {str(db_error)}'}, status=500)
        
        # Extract text from document
        extracted_text = ""
        try:
            if document_type == 'pdf':
                print("DEBUG: Processing PDF document")
                try:
                    res = document_processor.extract_pdf_content(file_path)
                    extracted_text = res.get('text', '') if isinstance(res, dict) else (str(res or ''))
                    print(f"DEBUG: PDF extracted {len(extracted_text)} characters")
                except Exception as e:
                    print(f"ERROR: PDF extraction failed: {e}")
                    document.processing_status = 'failed'
                    document.processing_error = f'PDF_EXTRACT_ERROR: {e}'
                    document.extracted_text = ''
                    document.processed_content = ''
                    document.save(update_fields=['processing_status','processing_error','extracted_text','processed_content','updated_at'])
                    return Response({
                        "error": "Failed to extract PDF",
                        "detail": str(e),
                        "code": "PDF_EXTRACT_ERROR",
                        "document_id": document.id
                    }, status=422)
                    
            elif document_type == 'image':
                print("DEBUG: Processing image with OCR")
                if document_processor:
                    ocr_result = document_processor.extract_image_text(file_path)
                    extracted_text = ocr_result.get('text', '') if isinstance(ocr_result, dict) else str(ocr_result)
                    print(f"DEBUG: OCR extracted {len(extracted_text)} characters")
                else:
                    extracted_text = "Image processing temporarily unavailable"
                
            else:
                print("DEBUG: Processing text file")
                try:
                    with open(file_path, 'r', encoding='utf-8') as text_file:
                        extracted_text = text_file.read()
                except UnicodeDecodeError:
                    # Try with different encoding
                    with open(file_path, 'r', encoding='latin-1') as text_file:
                        extracted_text = text_file.read()
                print(f"DEBUG: Text file extracted {len(extracted_text)} characters")
            
            # Update document with extracted text
            document.extracted_text = extracted_text
            document.processed_content = extracted_text
            document.processing_status = 'processing'  # Update status
            document.save(update_fields=['extracted_text','processed_content','processing_status','updated_at'])
            print("DEBUG: Updated document with extracted text and saved to database")
            
        except Exception as extraction_error:
            print(f"ERROR: Text extraction failed: {extraction_error}")
            document.processing_status = 'failed'
            document.save()
            return Response({
                'success': False,
                'error': f'Text extraction failed: {str(extraction_error)}',
                'document_id': document.id,
                'processing_status': 'failed'
            }, status=400)
        
        # Process based on user role
        questions_generated = 0
        try:
            if request.user.role == 'teacher':
                print("DEBUG: Processing for teacher - generating questions")
                print(f"DEBUG: Document {document.id} has extracted_text length: {len(document.extracted_text)}")
                
                # For teachers: ALWAYS start background thread and report that to the client
                start_background_processing(document.id, file_path, document_type)
                return Response({
                    "document_id": document.id,
                    "processing_status": document.processing_status,
                    "background_processing": True,
                    "questions_generated": 0
                }, status=201)
                    
            else:
                print("DEBUG: Processing for student - no question generation")
                # Students: Just process for RAG and chat
                document.processing_status = 'completed'
                document.questions_generated_count = 0
                
        except Exception as processing_error:
            print(f"ERROR: Role-based processing failed: {processing_error}")
            # Continue with basic processing even if advanced features fail
            document.processing_status = 'completed'
            
        # Save all changes
        document.save()
        print(f"DEBUG: Document processing completed. Status: {document.processing_status}")
        
        # Return appropriate response based on user role
        if request.user.role == 'teacher':
            # Check if background processing was started
            is_processing = document.processing_status == 'processing' and questions_generated == 0
            
            response_data = {
                'success': True,
                'document_id': document.id,
                'message': 'Document uploaded successfully!' if is_processing else 'Document uploaded and processed for question generation!',
                'background_processing_note': 'Complete document processing and question generation continues in background. Check back in a few minutes.' if is_processing else None,
                'title': document.title,
                'document_type': document.document_type,
                'questions_generated': questions_generated,
                'text_length': len(extracted_text),
                'processing_result': {
                    'questions_generated': questions_generated,
                    'processing_status': document.processing_status,
                    'background_processing': is_processing
                }
            }
            print(f"DEBUG: Returning teacher response: {questions_generated} questions generated, background_processing: {is_processing}")
            return Response(response_data, status=201)
        else:
            response_data = {
                'success': True,
                'document_id': document.id,
                'message': 'Document uploaded successfully for AI chat!',
                'title': document.title,
                'document_type': document.document_type,
                'text_length': len(extracted_text),
                'preview': extracted_text[:200] + "..." if len(extracted_text) > 200 else extracted_text,
                'processing_status': document.processing_status
            }
            print(f"DEBUG: Returning student response")
            return Response(response_data, status=201)
            
    except Exception as e:
        print(f"ERROR: Upload function failed: {str(e)}")
        import traceback
        print(f"ERROR: Full traceback: {traceback.format_exc()}")
        return Response({
            'error': f'Document upload failed: {str(e)}',
            'error_type': type(e).__name__
        }, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_documents(request):
    """List documents - SEPARATED by role: teachers see only their own, students see only their own"""
    try:
        from .serializers import DocumentSerializer
        
        user = request.user
        print(f"DEBUG: User '{user.username}' (role: {user.role}) requesting documents")
        
        # SEPARATE DOCUMENT VISIBILITY BY ROLE
        if user.role == 'teacher':
            # Teachers only see their own uploaded documents
            documents = Document.objects.filter(uploaded_by=user).order_by('-created_at')
            print(f"DEBUG: Teacher sees {documents.count()} of their own documents")
        else:
            # Students only see their own uploaded documents (NOT teacher documents)
            documents = Document.objects.filter(uploaded_by=user).order_by('-created_at')
            print(f"DEBUG: Student sees {documents.count()} of their own documents")
        
        serializer = DocumentSerializer(documents, many=True)
        return Response({'documents': serializer.data})
        
    except Exception as e:
        print(f"ERROR in list_documents: {str(e)}")
        return Response({
            'error': 'Failed to load documents'
        }, status=500)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_document(request, document_id):
    """Delete a document and all its associated questions"""
    try:
        # Users can only delete their own documents
        document = Document.objects.get(id=document_id, uploaded_by=request.user)
        
        # Delete associated file if it exists
        try:
            if document.file_path and os.path.exists(document.file_path):
                os.unlink(document.file_path)
        except Exception as file_error:
            print(f"Warning: Could not delete file {document.file_path}: {file_error}")
        
        # Delete document (questions will be cascade deleted)
        document_title = document.title
        document.delete()
        
        return Response({
            'success': True, 
            'message': f'Document "{document_title}" deleted successfully'
        })
        
    except Document.DoesNotExist:
        return Response({'error': 'Document not found or not owned by you'}, status=404)
    except Exception as e:
        print(f"Error deleting document {document_id}: {str(e)}")
        return Response({'error': f'Failed to delete document: {str(e)}'}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def document_status(request, document_id):
    """Get the processing status of a document"""
    try:
        document = Document.objects.get(id=document_id, uploaded_by=request.user)
        
        # Return document processing status
        return Response({
            'id': document.id,
            'title': document.title,
            'processing_status': getattr(document, 'processing_status', 'completed'),
            'processing_progress': getattr(document, 'processing_progress', 100),
            'upload_date': document.upload_date,
            'file_size': getattr(document, 'file_size', 0)
        })
        
    except Document.DoesNotExist:
        return Response({'error': 'Document not found or not owned by you'}, status=404)
    except Exception as e:
        print(f"Error getting document status {document_id}: {str(e)}")
        return Response({'error': f'Failed to get document status: {str(e)}'}, status=500)

@api_view(['GET'])
@permission_classes([])  # Allow anonymous access for development
def list_questions(request):
    """List all chat-generated questions, optionally filtered by difficulty level and topics"""
    # Remove teacher role check for development
    # if request.user.role != 'teacher':
    #     return Response({'error': 'Only teachers can view questions'}, status=403)
    
    try:
        from .models import QuestionBank
        from .serializers import QuestionBankSerializer
        
        # Get query parameters
        difficulty_level = request.GET.get('difficulty_level')
        document_id = request.GET.get('document_id')
        topic_ids = request.GET.get('topic_ids')  # Comma-separated topic IDs
        search = request.GET.get('search')
        is_generated = request.GET.get('is_generated', 'true')  # Default to chat-generated only
        limit = request.GET.get('limit')
        offset = request.GET.get('offset', '0')
        
        # Filter questions - ONLY chat-generated questions by default
        # For development, get all questions if no user is authenticated
        if hasattr(request, 'user') and request.user.is_authenticated:
            questions = QuestionBank.objects.filter(
                document__uploaded_by=request.user,
                is_generated=(is_generated.lower() == 'true')  # Filter by chat-generated origin
            )
        else:
            # For anonymous access, return all chat-generated questions
            questions = QuestionBank.objects.filter(
                is_generated=(is_generated.lower() == 'true')
            )
        
        if difficulty_level:
            questions = questions.filter(difficulty_level=difficulty_level)
        if document_id:
            questions = questions.filter(document_id=document_id)
        
        # Filter by topics if provided
        if topic_ids:
            try:
                topic_id_list = [int(tid.strip()) for tid in topic_ids.split(',') if tid.strip()]
                questions = questions.filter(topic_id__in=topic_id_list)
            except ValueError:
                return Response({'error': 'Invalid topic_ids format'}, status=400)
        
        # Search functionality
        if search:
            questions = questions.filter(question_text__icontains=search)
        
        # Pagination
        total_count = questions.count()
        try:
            offset = int(offset)
            if limit:
                limit = int(limit)
                questions = questions[offset:offset + limit]
            else:
                questions = questions[offset:]
        except ValueError:
            return Response({'error': 'Invalid limit or offset'}, status=400)
        
        # Add debug logging
        print(f"Found {total_count} chat-generated questions for user {request.user.username}")
        
        serializer = QuestionBankSerializer(questions, many=True)
        
        # Add debug info to response
        response_data = {
            'questions': serializer.data,
            'total_count': total_count,
            'filter_applied': {
                'difficulty_level': difficulty_level,
                'document_id': document_id,
                'topic_ids': topic_ids,
                'search': search,
                'is_generated': is_generated,
                'limit': limit,
                'offset': offset
            }
        }
        
        print(f"Returning response: {len(serializer.data)} questions")
        return Response(response_data)
        
    except Exception as e:
        print(f"Error in list_questions: {e}")
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_test_questions(request):
    """Create test questions for demonstration - DELETE THIS in PRODUCTION"""
    if request.user.role != 'teacher':
        return Response({'error': 'Only teachers can create questions'}, status=403)
    
    try:
        from .models import QuestionBank, Document
        
        # Get the first document for this user, or create a test document
        try:
            document = Document.objects.filter(uploaded_by=request.user).first()
            if not document:
                # Create a test document
                document = Document.objects.create(
                    uploaded_by=request.user,
                    title="Test Document",
                    document_type="pdf",
                    file_path="/test/path.pdf",
                    extracted_text="This is test content for mathematics questions.",
                    processing_status="completed"
                )
        except Exception as doc_error:
            return Response({'error': f'Document error: {str(doc_error)}'}, status=500)
        
        # Create test questions
        test_questions = [
            {
                'question_text': 'What is 2 + 2?',
                'difficulty_level': '3',
                'option_a': '3',
                'option_b': '4',
                'option_c': '5',
                'option_d': '6',
                'correct_answer': 'B',
                'explanation': 'Basic addition: 2 + 2 = 4'
            },
            {
                'question_text': 'Solve for x: 2x + 5 = 11',
                'difficulty_level': '4',
                'option_a': 'x = 2',
                'option_b': 'x = 3',
                'option_c': 'x = 4',
                'option_d': 'x = 5',
                'correct_answer': 'B',
                'explanation': '2x + 5 = 11, so 2x = 6, therefore x = 3'
            },
            {
                'question_text': 'What is the derivative of x²?',
                'difficulty_level': '5',
                'option_a': 'x',
                'option_b': '2x',
                'option_c': 'x²',
                'option_d': '2x²',
                'correct_answer': 'B',
                'explanation': 'Using the power rule: d/dx(x²) = 2x'
            }
        ]
        
        created_questions = []
        for q_data in test_questions:
            question = QuestionBank.objects.create(
                document=document,
                question_text=q_data['question_text'],
                question_type='multiple_choice',
                difficulty_level=q_data['difficulty_level'],
                subject='math',
                option_a=q_data['option_a'],
                option_b=q_data['option_b'],
                option_c=q_data['option_c'],
                option_d=q_data['option_d'],
                correct_answer=q_data['correct_answer'],
                explanation=q_data['explanation'],
                is_approved=True,
                created_by_ai=False  # These are manually created test questions
            )
            created_questions.append(question.id)
        
        return Response({
            'success': True,
            'message': f'Created {len(created_questions)} test questions',
            'question_ids': created_questions,
            'document_id': document.id
        })
        
    except Exception as e:
        print(f"Error creating test questions: {e}")
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_question(request):
    """Create a new question manually"""
    if request.user.role != 'teacher':
        return Response({'error': 'Only teachers can create questions'}, status=403)
    
    try:
        from .models import QuestionBank
        from .serializers import QuestionBankCreateSerializer
        
        serializer = QuestionBankCreateSerializer(data=request.data)
        if serializer.is_valid():
            question = serializer.save(created_by_ai=False, modified_by_teacher=True)
            
            response_serializer = QuestionBankSerializer(question)
            return Response({
                'success': True,
                'question': response_serializer.data
            })
        else:
            return Response({'error': serializer.errors}, status=400)
            
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_question(request, question_id):
    """Update an existing question"""
    if request.user.role != 'teacher':
        return Response({'error': 'Only teachers can update questions'}, status=403)
    
    try:
        from .models import QuestionBank
        from .serializers import QuestionBankSerializer
        
        question = QuestionBank.objects.get(
            id=question_id, 
            document__uploaded_by=request.user
        )
        
        serializer = QuestionBankSerializer(question, data=request.data, partial=True)
        if serializer.is_valid():
            question = serializer.save(modified_by_teacher=True)
            
            return Response({
                'success': True,
                'question': serializer.data
            })
        else:
            return Response({'error': serializer.errors}, status=400)
            
    except QuestionBank.DoesNotExist:
        return Response({'error': 'Question not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_question(request, question_id):
    """Delete a question"""
    if request.user.role != 'teacher':
        return Response({'error': 'Only teachers can delete questions'}, status=403)
    
    try:
        from .models import QuestionBank
        
        question = QuestionBank.objects.get(
            id=question_id, 
            document__uploaded_by=request.user
        )
        question.delete()
        
        return Response({'success': True, 'message': 'Question deleted successfully'})
        
    except QuestionBank.DoesNotExist:
        return Response({'error': 'Question not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_test(request):
    """Start a new test session for a student"""
    if request.user.role != 'student':
        return Response({'error': 'Only students can start tests'}, status=403)
    
    try:
        from .models import QuestionBank, TestSession
        from .serializers import TestSessionCreateSerializer, TestSessionSerializer
        
        serializer = TestSessionCreateSerializer(data=request.data)
        if serializer.is_valid():
            test_session = serializer.save(student=request.user)
            
            # Get random questions for this test
            questions = QuestionBank.objects.filter(
                difficulty_level=test_session.difficulty_level,
                subject=test_session.subject,
                is_approved=True
            ).order_by('?')[:test_session.total_questions]
            
            if len(questions) < test_session.total_questions:
                return Response({
                    'error': f'Not enough questions available for level {test_session.difficulty_level}. Found {len(questions)}, need {test_session.total_questions}'
                }, status=400)
            
            # Return test session with questions
            response_serializer = TestSessionSerializer(test_session)
            return Response({
                'success': True,
                'test_session': response_serializer.data,
                'questions': [
                    {
                        'id': q.id,
                        'question_text': q.question_text,
                        'question_type': q.question_type,
                        'option_a': q.option_a,
                        'option_b': q.option_b,
                        'option_c': q.option_c,
                        'option_d': q.option_d,
                    } for q in questions
                ]
            })
        else:
            return Response({'error': serializer.errors}, status=400)
            
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_answer(request):
    """Submit an answer for a test question"""
    if request.user.role != 'student':
        return Response({'error': 'Only students can submit answers'}, status=403)
    
    try:
        from .models import TestSession, QuestionBank, StudentAnswer
        
        test_session_id = request.data.get('test_session_id')
        question_id = request.data.get('question_id')
        student_answer = request.data.get('answer')
        time_taken = request.data.get('time_taken_seconds')
        
        # Validate test session belongs to student
        test_session = TestSession.objects.get(id=test_session_id, student=request.user)
        question = QuestionBank.objects.get(id=question_id)
        
        # Check if answer is correct
        is_correct = student_answer.lower().strip() == question.correct_answer.lower().strip()
        
        # Create student answer record
        answer_record = StudentAnswer.objects.create(
            test_session=test_session,
            question=question,
            student_answer=student_answer,
            is_correct=is_correct,
            time_taken_seconds=time_taken
        )
        
        # For practice tests, enable interactive chat mode instead of immediate explanation
        response_data = {
            'success': True,
            'is_correct': is_correct,
            'answer_id': answer_record.id
        }
        
        if test_session.test_type == 'practice_test':
            # For practice tests, enable chat mode for hints and guidance
            response_data.update({
                'practice_mode': True,
                'chat_enabled': True,
                'question_id': question.id,
                'test_session_id': test_session.id,
                'show_chat': True,
                'tutor_available': True
            })
            
            # Provide different messages based on correctness
            if is_correct:
                response_data.update({
                    'feedback': "🎉 Excellent work! You got it right!",
                    'message': "Great job! You can ask me about different solution methods, or try the next question. What would you like to explore?",
                    'correct_answer': question.correct_answer,
                    'explanation': question.explanation
                })
            else:
                response_data.update({
                    'feedback': "🤔 Not quite right, but that's okay!",
                    'message': "That's not the correct answer, but don't worry! Ask me for hints and I'll guide you step by step to understand this problem better.",
                    'hint_available': True
                })
        else:
            # For level tests, don't show answers immediately
            response_data.update({
                'practice_mode': False,
                'message': 'Answer submitted for grading.'
            })
        
        return Response(response_data)
        
    except (TestSession.DoesNotExist, QuestionBank.DoesNotExist):
        return Response({'error': 'Test session or question not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_test(request):
    """Complete a test session and calculate score"""
    if request.user.role != 'student':
        return Response({'error': 'Only students can complete tests'}, status=403)
    
    try:
        from .models import TestSession, StudentAnswer
        
        test_session_id = request.data.get('test_session_id')
        test_session = TestSession.objects.get(id=test_session_id, student=request.user)
        
        # Calculate score
        total_answers = test_session.answers.count()
        correct_answers = test_session.answers.filter(is_correct=True).count()
        
        if total_answers > 0:
            score = (correct_answers / total_answers) * 100
            passed = score >= 70  # 70% passing threshold
        else:
            score = 0
            passed = False
        
        # Update test session
        test_session.is_completed = True
        test_session.score = score
        test_session.passed = passed
        test_session.completed_at = timezone.now()
        test_session.save()
        
        # Update student points if passed and it's a level test
        if passed and test_session.test_type == 'level_test':
            request.user.points += int(test_session.difficulty_level) * 10
            request.user.save()
        
        return Response({
            'success': True,
            'score': score,
            'passed': passed,
            'correct_answers': correct_answers,
            'total_questions': total_answers,
            'points_earned': int(test_session.difficulty_level) * 10 if passed and test_session.test_type == 'level_test' else 0
        })
        
    except TestSession.DoesNotExist:
        return Response({'error': 'Test session not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def practice_chat(request):
    """
    Interactive chat for practice questions - provides hints without revealing answers
    """
    if request.user.role != 'student':
        return Response({'error': 'Only students can use practice chat'}, status=403)
    
    try:
        from .models import TestSession, QuestionBank, StudentAnswer
        
        test_session_id = request.data.get('test_session_id')
        question_id = request.data.get('question_id')
        student_question = request.data.get('question', '').strip()
        
        if not student_question:
            return Response({'error': 'Please ask a question'}, status=400)
        
        # Validate test session and question
        test_session = TestSession.objects.get(
            id=test_session_id, 
            student=request.user,
            test_type='practice_test'  # Only for practice tests
        )
        question = QuestionBank.objects.get(id=question_id)
        
        # Get the student's answer if they've already attempted this question
        try:
            student_answer = StudentAnswer.objects.get(
                test_session=test_session,
                question=question
            )
            student_already_answered = True
            is_correct = student_answer.is_correct
        except StudentAnswer.DoesNotExist:
            student_already_answered = False
            is_correct = False
        
        print(f"DEBUG: Practice chat - Question: '{student_question}'")
        print(f"DEBUG: Student answered: {student_already_answered}, Correct: {is_correct}")
        
        # Create sophisticated tutor prompt that gives hints without revealing answers
        tutor_prompt = f"""
You are a helpful mathematics tutor in a practice session. A student is working on this problem:

PROBLEM: {question.question_text}
CORRECT ANSWER (DO NOT REVEAL): {question.correct_answer}
STUDENT ALREADY ANSWERED: {student_already_answered}
ANSWER WAS CORRECT: {is_correct}

STUDENT'S QUESTION/REQUEST: "{student_question}"

TUTOR INSTRUCTIONS:
1. NEVER directly give the answer ({question.correct_answer})
2. If student asks for the answer directly, redirect them to think through the problem
3. Provide hints, ask guiding questions, or suggest problem-solving approaches
4. If they ask about a specific step or concept, explain that concept without solving the whole problem
5. If they're stuck, give them the first step or a similar example
6. If they already answered correctly, you can discuss the solution method and alternative approaches
7. If they answered incorrectly and ask for help, guide them toward the right thinking process
8. Be encouraging and supportive
9. Use mathematical reasoning appropriate for the difficulty level
10. If they ask "is this right?" about their approach, give feedback on the method, not the final answer

Example responses:
- "That's a good start! What do you think the next step would be?"
- "Let me give you a hint: consider what type of mathematical operation this problem is asking for"
- "You're on the right track. What happens if you try to simplify that expression?"
- "Instead of giving you the answer, let me ask: what's the first thing you notice about this problem?"

Respond as a supportive tutor in 2-3 sentences maximum.
"""
        
        try:
            # Generate tutor response using Ollama
            tutor_response = get_simple_ollama_response(tutor_prompt)
            
            # Clean up the response and ensure it doesn't contain the answer
            if question.correct_answer.lower() in tutor_response.lower():
                # If the answer somehow got included, provide a safe fallback
                tutor_response = f"Let me guide you through this step by step. What's your approach to solving this type of problem? Think about the mathematical concepts involved and try to break it down into smaller steps."
            
            # Add some personalization
            if not student_already_answered:
                tutor_response += " Remember, you can take your time to think through this!"
            elif is_correct:
                tutor_response += " Since you got it right, we can explore different solution methods if you're curious!"
            
        except Exception as e:
            print(f"Tutor response generation failed: {e}")
            # Fallback responses
            if "hint" in student_question.lower() or "help" in student_question.lower():
                tutor_response = "Let me give you a hint: break this problem down into smaller steps. What's the first mathematical operation you think you need to perform?"
            elif "answer" in student_question.lower():
                tutor_response = "I can't give you the answer directly - that would spoil the learning! But I can guide you through the thinking process. What approach do you want to try?"
            else:
                tutor_response = "That's a great question! Let me help you think through this step by step. What part of the problem are you finding challenging?"
        
        return Response({
            'success': True,
            'tutor_response': tutor_response,
            'question_context': {
                'question_text': question.question_text,
                'difficulty_level': question.difficulty_level,
                'already_answered': student_already_answered,
                'is_correct': is_correct if student_already_answered else None
            },
            'chat_continues': True
        })
        
    except (TestSession.DoesNotExist, QuestionBank.DoesNotExist):
        return Response({'error': 'Test session or question not found'}, status=404)
    except Exception as e:
        print(f"Practice chat error: {e}")
        return Response({'error': f'Chat error: {str(e)}'}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_test_history(request):
    """Get test history for the current student"""
    if request.user.role != 'student':
        return Response({'error': 'Only students can view test history'}, status=403)
    
    try:
        from .models import TestSession
        from .serializers import TestSessionSerializer
        
        test_sessions = TestSession.objects.filter(student=request.user).order_by('-started_at')
        serializer = TestSessionSerializer(test_sessions, many=True)
        
        return Response({'test_history': serializer.data})
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_exam(request):
    """Teacher creates an exam"""
    if request.user.role != 'teacher':
        return Response({'error': 'Only teachers can create exams'}, status=403)
    try:
        from .models import Exam, QuestionBank
        from .serializers import ExamCreateSerializer
        data = request.data.copy()
        serializer = ExamCreateSerializer(data=data)
        if not serializer.is_valid():
            return Response({'error': serializer.errors}, status=400)
        v = serializer.validated_data
        
        # Parse selection_rules JSON if provided
        selection_rules = None
        if v.get('selection_rules'):
            try:
                import json
                selection_rules = json.loads(v['selection_rules'])
            except json.JSONDecodeError:
                return Response({'error': 'Invalid JSON in selection_rules'}, status=400)
        
        exam = Exam.objects.create(
            created_by=request.user,
            title=v['title'],
            description=v.get('description', ''),
            subject=v.get('subject') or 'math',
            difficulty_level=v.get('difficulty_level'),
            total_questions=v['total_questions'],
            exam_time_limit_minutes=v.get('exam_time_limit_minutes'),
            per_question_time_seconds=v.get('per_question_time_seconds'),
            start_at=v.get('start_at'),
            end_at=v.get('end_at'),
            is_published=v.get('is_published', False),
            selection_rules=v.get('selection_rules')
        )
        # Assign students
        for sid in v.get('assigned_student_ids', []) or []:
            try:
                s = User.objects.get(id=sid, role='student')
                exam.assigned_students.add(s)
            except User.DoesNotExist:
                continue
        # Attach questions if provided
        for qid in v.get('question_ids', []) or []:
            try:
                q = QuestionBank.objects.get(id=qid, document__uploaded_by=request.user)
                exam.questions.add(q)
            except QuestionBank.DoesNotExist:
                continue
        return Response({'success': True, 'exam_id': exam.id})
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_exams(request):
    """List exams for the teacher or assigned exams for students"""
    try:
        from .models import Exam
        from .serializers import ExamSerializer
        if request.user.role == 'teacher':
            exams = Exam.objects.filter(created_by=request.user).order_by('-created_at')
        else:
            exams = Exam.objects.filter(is_published=True, assigned_students=request.user).order_by('-created_at')
        data = []
        for ex in exams:
            selection_rules_parsed = None
            if ex.selection_rules:
                try:
                    import json
                    selection_rules_parsed = json.loads(ex.selection_rules)
                except json.JSONDecodeError:
                    selection_rules_parsed = None
            
            data.append({
                'id': ex.id,
                'title': ex.title,
                'description': ex.description or '',
                'subject': ex.subject,
                'difficulty_level': ex.difficulty_level,
                'total_questions': ex.total_questions,
                'exam_time_limit_minutes': ex.exam_time_limit_minutes,
                'per_question_time_seconds': ex.per_question_time_seconds,
                'start_at': ex.start_at,
                'end_at': ex.end_at,
                'is_published': ex.is_published,
                'assigned_students': [s.username for s in ex.assigned_students.all()],
                'question_ids': list(ex.questions.values_list('id', flat=True)),
                'selection_rules': selection_rules_parsed,
                'created_at': ex.created_at,
            })
        return Response({'exams': data})
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_exam(request, exam_id):
    """Get single exam details"""
    try:
        from .models import Exam
        ex = Exam.objects.get(id=exam_id)
        if request.user.role == 'teacher' and ex.created_by != request.user:
            return Response({'error': 'Not allowed'}, status=403)
        if request.user.role == 'student' and (not ex.is_published or request.user not in ex.assigned_students.all()):
            return Response({'error': 'Not allowed'}, status=403)
        
        selection_rules_parsed = None
        if ex.selection_rules:
            try:
                import json
                selection_rules_parsed = json.loads(ex.selection_rules)
            except json.JSONDecodeError:
                selection_rules_parsed = None
        
        data = {
            'id': ex.id,
            'title': ex.title,
            'description': ex.description or '',
            'subject': ex.subject,
            'difficulty_level': ex.difficulty_level,
            'total_questions': ex.total_questions,
            'exam_time_limit_minutes': ex.exam_time_limit_minutes,
            'per_question_time_seconds': ex.per_question_time_seconds,
            'start_at': ex.start_at,
            'end_at': ex.end_at,
            'is_published': ex.is_published,
            'assigned_students': [s.username for s in ex.assigned_students.all()],
            'question_ids': list(ex.questions.values_list('id', flat=True)),
            'selection_rules': selection_rules_parsed,
            'created_at': ex.created_at,
        }
        return Response({'exam': data})
    except Exam.DoesNotExist:
        return Response({'error': 'Exam not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assign_students_to_exam(request, exam_id):
    """Teacher assigns students to exam"""
    if request.user.role != 'teacher':
        return Response({'error': 'Only teachers can assign students'}, status=403)
    try:
        from .models import Exam
        ex = Exam.objects.get(id=exam_id, created_by=request.user)
        student_ids = request.data.get('student_ids', []) or []
        action = request.data.get('action', 'add')
        for sid in student_ids:
            try:
                s = User.objects.get(id=sid, role='student')
                if action == 'remove':
                    ex.assigned_students.remove(s)
                else:
                    ex.assigned_students.add(s)
            except User.DoesNotExist:
                continue
        return Response({'success': True})
    except Exam.DoesNotExist:
        return Response({'error': 'Exam not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def publish_exam(request, exam_id):
    """Teacher publishes/unpublishes exam"""
    if request.user.role != 'teacher':
        return Response({'error': 'Only teachers can publish exams'}, status=403)
    try:
        from .models import Exam
        ex = Exam.objects.get(id=exam_id, created_by=request.user)
        is_published = bool(request.data.get('is_published', True))
        ex.is_published = is_published
        ex.save()
        return Response({'success': True, 'is_published': ex.is_published})
    except Exam.DoesNotExist:
        return Response({'error': 'Exam not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_exam(request, exam_id):
    """Student starts an assigned, published exam → creates TestSession and returns questions"""
    if request.user.role != 'student':
        return Response({'error': 'Only students can start exams'}, status=403)
    try:
        from django.utils import timezone
        from .models import Exam, TestSession, QuestionBank
        ex = Exam.objects.get(id=exam_id, is_published=True)
        now = timezone.now()
        if ex.start_at and now < ex.start_at:
            return Response({'error': 'Exam has not started yet'}, status=400)
        if ex.end_at and now > ex.end_at:
            return Response({'error': 'Exam has ended'}, status=400)
        if request.user not in ex.assigned_students.all():
            return Response({'error': 'You are not assigned to this exam'}, status=403)
        # Create session
        session = TestSession.objects.create(
            student=request.user,
            test_type='exam',
            difficulty_level=ex.difficulty_level or '3',
            subject=ex.subject,
            exam=ex,
            total_questions=ex.total_questions,
            time_limit_minutes=ex.exam_time_limit_minutes
        )
        # Collect questions: explicit list first
        selected = list(ex.questions.all())
        # If not enough, sample using selection_rules
        if len(selected) < ex.total_questions:
            rules = {}
            if ex.selection_rules:
                try:
                    import json
                    rules = json.loads(ex.selection_rules)
                except json.JSONDecodeError:
                    rules = {}
            difficulty_map = (rules.get('difficulty') or rules.get('difficulties') or {})
            subject = rules.get('subject') or ex.subject
            # If rule map provided, sample per difficulty
            pool = QuestionBank.objects.filter(is_approved=True, subject=subject)
            # Limit to teacher's questions for consistency
            pool = pool.filter(document__uploaded_by=ex.created_by)
            import random
            needed = ex.total_questions - len(selected)
            if isinstance(difficulty_map, dict) and difficulty_map:
                for level, count in difficulty_map.items():
                    qs = list(pool.filter(difficulty_level=str(level)))
                    random.shuffle(qs)
                    selected.extend(qs[: int(count)])
            # If still not enough, fill with any pool
            if len(selected) < ex.total_questions:
                remaining_pool = [q for q in pool if q not in selected]
                random.shuffle(remaining_pool)
                selected.extend(remaining_pool[:needed])
        # Enforce size
        selected = selected[: ex.total_questions]
        if len(selected) < ex.total_questions:
            return Response({'error': f'Not enough questions to start this exam. Found {len(selected)}, need {ex.total_questions}.'}, status=400)
        # Return payload
        return Response({
            'success': True,
            'test_session': {
                'id': session.id,
                'time_limit_minutes': session.time_limit_minutes,
                'test_type': session.test_type,
                'subject': session.subject,
                'exam_id': ex.id,
            },
            'questions': [
                {
                    'id': q.id,
                    'question_text': q.question_text,
                    'question_type': q.question_type,
                    'option_a': q.option_a,
                    'option_b': q.option_b,
                    'option_c': q.option_c,
                    'option_d': q.option_d,
                } for q in selected
            ]
        })
    except Exam.DoesNotExist:
        return Response({'error': 'Exam not found or not available'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_exam_chat(request, exam_id):
    """🎓 Phase 3: Start an Exam Session with Chat Interaction
    
    When the student starts the exam:
    - The chatbot greets the student
    - Sends only the first question to the student (no answer or hints)  
    - Waits for a student response
    """
    if request.user.role != 'student':
        return Response({'error': 'Only students can start exams'}, status=403)
    
    try:
        from django.utils import timezone
        from .models import Exam, TestSession, QuestionBank
        
        # Validate exam availability
        ex = Exam.objects.get(id=exam_id, is_published=True)
        now = timezone.now()
        
        if ex.start_at and now < ex.start_at:
            return Response({'error': 'Exam has not started yet'}, status=400)
        if ex.end_at and now > ex.end_at:
            return Response({'error': 'Exam has ended'}, status=400)
        if request.user not in ex.assigned_students.all():
            return Response({'error': 'You are not assigned to this exam'}, status=403)
        
        # Check if student already has an active exam session
        existing_session = TestSession.objects.filter(
            student=request.user,
            exam=ex,
            test_type='exam',
            is_completed=False
        ).first()
        
        if existing_session:
            return Response({'error': 'You already have an active exam session for this exam'}, status=400)
        
        # Create new exam session
        session = TestSession.objects.create(
            student=request.user,
            test_type='exam',
            difficulty_level=ex.difficulty_level or '3',
            subject=ex.subject,
            exam=ex,
            total_questions=ex.total_questions,
            time_limit_minutes=ex.exam_time_limit_minutes
        )
        
        # 🎯 NEW: Use advanced question variation system for diverse questions
        print(f"🔄 Generating varied questions for exam {ex.title}")
        
        # Use the question variation generator to get diverse questions
        varied_questions = question_generator.select_varied_questions(ex, ex.total_questions)
        
        if len(varied_questions) < ex.total_questions:
            return Response({'error': f'Not enough questions to start this exam. Found {len(varied_questions)}, need {ex.total_questions}.'}, status=400)
        
        # Convert varied questions to a format we can work with
        question_data = []
        actual_questions = []  # For the sequence
        
        for i, varied_q in enumerate(varied_questions):
            q_data = varied_q['data']
            
            # Create a pseudo-question object for variations
            if varied_q['type'] == 'variation':
                # This is a generated variation
                class VariationQuestion:
                    def __init__(self, data):
                        self.id = f"var_{varied_q['base_question'].id}_{i}"
                        self.question_text = data['question_text']
                        self.correct_answer = data['correct_answer']
                        self.option_a = data['option_a']
                        self.option_b = data['option_b']
                        self.option_c = data['option_c']
                        self.option_d = data['option_d']
                        self.question_type = data['question_type']
                        self.difficulty_level = data['difficulty_level']
                        self.subject = data['subject']
                        self.explanation = data['explanation']
                        self.is_variation = True
                        self.base_question_id = data['base_question_id']
                
                question_obj = VariationQuestion(q_data)
                question_data.append(q_data)
                actual_questions.append(question_obj)
            else:
                # This is an original question
                original_q = varied_q['question']
                question_data.append(q_data)
                actual_questions.append(original_q)
        
        # Store enhanced question sequence with variation info
        question_sequence = []
        for i, q in enumerate(actual_questions):
            if hasattr(q, 'is_variation') and q.is_variation:
                question_sequence.append({
                    'type': 'variation',
                    'id': q.id,
                    'base_id': q.base_question_id,
                    'data': question_data[i]
                })
            else:
                question_sequence.append({
                    'type': 'original',
                    'id': q.id,
                    'data': None  # Use database query for original questions
                })
        
        session.notes = json.dumps({
            'question_sequence': question_sequence,
            'current_question_index': 0,
            'exam_chat_mode': True,
            'exam_start_time': now.isoformat(),
            'variation_info': f'Generated {len([q for q in varied_questions if q["type"] == "variation"])} variations'
        })
        session.save()
        
        # Get the first question (either original or variation)
        first_question = actual_questions[0]
        
        # Format first question for chat display
        question_text = first_question.question_text
        
        # Add multiple choice options if available
        options = []
        if first_question.option_a:
            options.append(f"A) {first_question.option_a}")
        if first_question.option_b:
            options.append(f"B) {first_question.option_b}")
        if first_question.option_c:
            options.append(f"C) {first_question.option_c}")
        if first_question.option_d:
            options.append(f"D) {first_question.option_d}")
        
        if options:
            question_display = f"{question_text}\n\n" + "\n".join(options)
        else:
            question_display = question_text
        
        # Create greeting message with first question
        greeting_message = f"""🎓 **Welcome to your {ex.subject} exam!** 

**Exam:** {ex.title}
**Questions:** {ex.total_questions}
**Time Limit:** {ex.exam_time_limit_minutes} minutes
{f"**Per Question Time:** {ex.per_question_time_seconds} seconds" if ex.per_question_time_seconds else ""}

Let's begin! Here's your first question:

**Question 1 of {ex.total_questions}:**

{question_display}

Please provide your answer. You can type the letter (A, B, C, D) for multiple choice questions, or write your complete answer for open-ended questions."""
        
        # Save the greeting and question as a chat interaction
        ChatInteraction.objects.create(
            student=request.user,
            question=f"[EXAM START] {ex.title}",
            answer=greeting_message,
            topic="Exam Start",
            notes=json.dumps({
                "exam_mode": True,
                "exam_id": ex.id,
                "test_session_id": session.id,
                "question_id": first_question.id,
                "question_number": 1,
                "total_questions": ex.total_questions
            })
        )
        
        return Response({
            'success': True,
            'exam_session': {
                'test_session_id': session.id,
                'exam_id': ex.id,
                'exam_title': ex.title,
                'total_questions': ex.total_questions,
                'time_limit_minutes': ex.exam_time_limit_minutes,
                'per_question_time_seconds': ex.per_question_time_seconds,
                'current_question': 1,
                'exam_chat_mode': True
            },
            'chatbot_message': greeting_message,
            'first_question': {
                'id': first_question.id,
                'question_number': 1,
                'question_text': question_text,
                'question_type': first_question.question_type,
                'has_options': len(options) > 0,
                'options': options
            },
            'instruction': 'The exam has started! Please respond with your answer to Question 1.'
        })
        
    except Exam.DoesNotExist:
        return Response({'error': 'Exam not found or not available'}, status=404)
    except Exception as e:
        print(f"Error starting exam chat: {e}")
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_exam_results(request, test_session_id):
    """📊 Get detailed exam results for a completed exam session"""
    if request.user.role != 'student':
        return Response({'error': 'Only students can view exam results'}, status=403)
    
    try:
        from .models import TestSession, StudentAnswer
        from django.utils import timezone
        
        # Get the test session
        session = TestSession.objects.get(
            id=test_session_id, 
            student=request.user, 
            test_type='exam'
        )
        
        if not session.session_complete:
            return Response({'error': 'Exam session is not yet complete'}, status=400)
        
        # Get all answers for this session
        answers = StudentAnswer.objects.filter(test_session=session).order_by('answered_at')
        
        # Calculate statistics
        total_questions = answers.count()
        correct_answers = answers.filter(is_correct=True).count()
        score_percentage = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        
        # Parse session notes for timing
        notes = {}
        if session.notes:
            try:
                notes = json.loads(session.notes)
            except json.JSONDecodeError:
                notes = {}
        
        # Calculate total time
        exam_start_time_str = notes.get('exam_start_time')
        total_time = "Unknown"
        
        if exam_start_time_str and answers.exists():
            try:
                from datetime import datetime
                exam_start_time = datetime.fromisoformat(exam_start_time_str.replace('Z', '+00:00'))
                last_answer_time = answers.last().answered_at
                time_elapsed = (last_answer_time - exam_start_time).total_seconds()
                minutes_elapsed = int(time_elapsed // 60)
                seconds_elapsed = int(time_elapsed % 60)
                total_time = f"{minutes_elapsed}:{seconds_elapsed:02d}"
            except Exception as e:
                print(f"Time calculation error: {e}")
        
        # Prepare detailed answer breakdown
        question_details = []
        for i, answer in enumerate(answers, 1):
            question_details.append({
                'question_number': i,
                'question_id': answer.question.id,
                'question_text': answer.question.question_text,
                'student_answer': answer.student_answer,
                'correct_answer': answer.question.correct_answer,
                'is_correct': answer.is_correct,
                'answered_at': answer.answered_at.isoformat(),
                'question_type': answer.question.question_type,
                'difficulty_level': answer.question.difficulty_level
            })
        
        # Get exam info
        exam_info = {}
        if session.exam:
            exam_info = {
                'exam_id': session.exam.id,
                'exam_title': session.exam.title,
                'subject': session.exam.subject,
                'difficulty_level': session.exam.difficulty_level,
                'time_limit_minutes': session.exam.exam_time_limit_minutes
            }
        
        return Response({
            'success': True,
            'exam_results': {
                'test_session_id': session.id,
                'exam_info': exam_info,
                'summary': {
                    'total_questions': total_questions,
                    'correct_answers': correct_answers,
                    'incorrect_answers': total_questions - correct_answers,
                    'score_percentage': round(score_percentage, 1),
                    'total_time': total_time,
                    'completed_at': session.updated_at.isoformat() if hasattr(session, 'updated_at') else 'Unknown'
                },
                'question_breakdown': question_details,
                'performance_analysis': {
                    'grade': 'A' if score_percentage >= 90 else 'B' if score_percentage >= 80 else 'C' if score_percentage >= 70 else 'D' if score_percentage >= 60 else 'F',
                    'passed': score_percentage >= 60,
                    'strengths': [q for q in question_details if q['is_correct']],
                    'areas_for_improvement': [q for q in question_details if not q['is_correct']]
                }
            }
        })
        
    except TestSession.DoesNotExist:
        return Response({'error': 'Test session not found'}, status=404)
    except Exception as e:
        print(f"Error getting exam results: {e}")
        return Response({'error': str(e)}, status=500)

# ===================================================================
# 🎯 INTERACTIVE EXAM LEARNING WITH OLAMA INTEGRATION
# ===================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_interactive_exam_answer(request):
    """
    🎯 Interactive Exam Answer Submission with 3-Attempt System and Hints
    
    This function handles both ChatSession-based and ExamSession-based interactive exams.
    
    Flow:
    1. Student submits answer
    2. Check if answer is correct
    3. If correct: Store answer, move to next question
    4. If incorrect: 
       - Track attempt count
       - If attempts < MAX_ATTEMPTS: Generate hint
       - If attempts >= MAX_ATTEMPTS: Reveal answer, move to next
    """
    if request.user.role != 'student':
        return Response({'error': 'Only students can submit exam answers'}, status=403)
    
    # Configuration
    MAX_ATTEMPTS = 3  # Allow 3 attempts per question
    
    try:
        import json
        from .models import ChatSession, ExamSession
        
        # Get request data
        exam_session_id = request.data.get('exam_session_id')
        question_id = request.data.get('question_id')
        answer_text = request.data.get('answer_text', '').strip()
        time_taken = request.data.get('time_taken_seconds')
        
        if not exam_session_id or not answer_text:
            return Response({
                'status': 'error',
                'message': 'exam_session_id and answer_text are required'
            }, status=400)
        
        # Try to get as ChatSession first (new interactive exam format)
        try:
            session = ChatSession.objects.get(id=exam_session_id, student=request.user)
            metadata = session.get_session_metadata()
            
            if metadata.get('is_interactive_exam'):
                # This is a chat-based interactive exam
                return handle_chat_session_answer(session, metadata, question_id, answer_text, time_taken, MAX_ATTEMPTS)
            else:
                return Response({
                    'status': 'error',
                    'message': 'This is not an interactive exam session'
                }, status=400)
                
        except ChatSession.DoesNotExist:
            # Fall back to ExamSession (legacy format)
            try:
                exam_session = ExamSession.objects.get(id=exam_session_id)
                return handle_exam_session_answer(exam_session, question_id, answer_text, time_taken, MAX_ATTEMPTS, request.user)
                
            except ExamSession.DoesNotExist:
                return Response({
                    'status': 'error',
                    'message': 'Exam session not found'
                }, status=404)
        
    except Exception as e:
        print(f"Error in interactive exam answer submission: {e}")
        return Response({
            'status': 'error',
            'message': f'Failed to process answer: {str(e)}'
        }, status=500)


def handle_chat_session_answer(session, metadata, question_id, answer_text, time_taken, max_attempts):
    """Handle answer submission for ChatSession-based interactive exams"""
    import json
    from .models import Document
    
    try:
        # Restore exam session
        exam_session = InteractiveExamSession.from_dict(metadata['exam_session'])
        
        # Get current question
        current_question = exam_session.questions[exam_session.current_question_index]
        question_key = str(exam_session.current_question_index)
        question_state = exam_session.question_states.get(question_key, {})
        
        # Get current attempt count
        attempts = question_state.get('answers', [])
        attempt_number = len(attempts) + 1
        
        # Evaluate answer correctness
        is_correct = evaluate_chat_answer_correctness(current_question, answer_text)
        
        # Store the attempt
        attempt_data = {
            'answer': answer_text,
            'is_correct': is_correct,
            'timestamp': timezone.now().isoformat(),
            'time_taken': time_taken
        }
        
        if is_correct:
            # ✅ CORRECT ANSWER: Move to next question
            attempts.append(attempt_data)
            question_state['answers'] = attempts
            question_state['isCorrect'] = True
            exam_session.question_states[question_key] = question_state
            exam_session.total_correct += 1
            
            # Move to next question
            exam_session.current_question_index += 1
            
            # Update session metadata
            metadata['exam_session'] = exam_session.to_dict()
            session.set_session_metadata(metadata)
            session.save()
            
            if exam_session.current_question_index >= len(exam_session.questions):
                # Exam completed
                final_score = calculate_chat_exam_score(exam_session)
                return Response({
                    'status': 'completed',
                    'message': 'Congratulations! You have completed the exam.',
                    'final_score': final_score,
                    'progress': {
                        'answered_questions': exam_session.current_question_index,
                        'total_questions': len(exam_session.questions),
                        'progress_percentage': 100.0,
                        'is_completed': True
                    }
                })
            else:
                # Get next question
                next_question = exam_session.questions[exam_session.current_question_index]
                return Response({
                    'status': 'correct',
                    'message': 'Correct! Well done. Moving to the next question.',
                    'next_question': {
                        'id': exam_session.current_question_index,
                        'question_text': next_question['question'],
                        'question_type': 'short_answer',
                        'correct_answer': next_question['correct_answer']
                    },
                    'progress': {
                        'answered_questions': exam_session.current_question_index,
                        'total_questions': len(exam_session.questions),
                        'progress_percentage': (exam_session.current_question_index / len(exam_session.questions)) * 100,
                        'is_completed': False
                    }
                })
        
        else:
            # ❌ INCORRECT ANSWER: Check attempt count
            attempts.append(attempt_data)
            question_state['answers'] = attempts
            exam_session.question_states[question_key] = question_state
            
            if attempt_number < max_attempts:
                # Generate hint
                hint = generate_chat_hint(current_question, answer_text, attempt_number, metadata)
                attempt_data['hint'] = hint
                
                # Update session metadata
                metadata['exam_session'] = exam_session.to_dict()
                session.set_session_metadata(metadata)
                session.save()
                
                return Response({
                    'status': 'hint',
                    'message': f'Not quite right. Here\'s a hint to help you:',
                    'hint': hint,
                    'attempt_number': attempt_number,
                    'max_attempts': max_attempts,
                    'attempts_remaining': max_attempts - attempt_number
                })
            
            else:
                # Max attempts reached - reveal answer and move on
                exam_session.current_question_index += 1
                
                # Update session metadata
                metadata['exam_session'] = exam_session.to_dict()
                session.set_session_metadata(metadata)
                session.save()
                
                if exam_session.current_question_index >= len(exam_session.questions):
                    # Exam completed
                    final_score = calculate_chat_exam_score(exam_session)
                    return Response({
                        'status': 'completed',
                        'message': f'Exam completed! The correct answer to the last question was: {current_question["correct_answer"]}',
                        'correct_answer': current_question['correct_answer'],
                        'final_score': final_score,
                        'progress': {
                            'answered_questions': exam_session.current_question_index,
                            'total_questions': len(exam_session.questions),
                            'progress_percentage': 100.0,
                            'is_completed': True
                        }
                    })
                else:
                    # Get next question
                    next_question = exam_session.questions[exam_session.current_question_index]
                    return Response({
                        'status': 'reveal',
                        'message': f'Maximum attempts reached. The correct answer was: {current_question["correct_answer"]}',
                        'correct_answer': current_question['correct_answer'],
                        'next_question': {
                            'id': exam_session.current_question_index,
                            'question_text': next_question['question'],
                            'question_type': 'short_answer',
                            'correct_answer': next_question['correct_answer']
                        },
                        'progress': {
                            'answered_questions': exam_session.current_question_index,
                            'total_questions': len(exam_session.questions),
                            'progress_percentage': (exam_session.current_question_index / len(exam_session.questions)) * 100,
                            'is_completed': False
                        }
                    })
                    
    except Exception as e:
        print(f"Error handling chat session answer: {e}")
        return Response({
            'status': 'error',
            'message': f'Failed to process answer: {str(e)}'
        }, status=500)


def handle_exam_session_answer(exam_session, question_id, answer_text, time_taken, max_attempts, student):
    """Handle answer submission for ExamSession-based interactive exams (legacy)"""
    import json
    from .models import QuestionBank, ExamAnswerAttempt, StudentAnswer
    
    try:
        # Get question
        try:
            question = QuestionBank.objects.get(id=question_id)
        except QuestionBank.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Question not found'
            }, status=404)
        
        # Get current attempt count
        existing_attempts = ExamAnswerAttempt.objects.filter(
            exam_session=exam_session,
            student=student,
            question=question
        ).count()
        
        attempt_number = existing_attempts + 1
        
        # Evaluate answer correctness
        is_correct = evaluate_answer_correctness(question, answer_text)
        
        # Create the attempt record
        attempt = ExamAnswerAttempt.objects.create(
            exam_session=exam_session,
            student=student,
            question=question,
            attempt_number=attempt_number,
            answer_text=answer_text,
            is_correct=is_correct,
            time_taken_seconds=time_taken,
            olama_context=json.dumps({
                'question_text': question.question_text,
                'correct_answer': question.correct_answer,
                'attempt_number': attempt_number,
                'student_answer': answer_text
            })
        )
        
        if is_correct:
            # ✅ CORRECT ANSWER: Store final answer and move to next question
            StudentAnswer.objects.create(
                exam_session=exam_session,
                question=question,
                student=student,
                answer_text=answer_text,
                is_correct=True,
                time_taken_seconds=time_taken,
                interaction_log=json.dumps({
                    'attempt_count': attempt_number,
                    'interactive_mode': True,
                    'olama_hints_used': attempt_number - 1
                })
            )
            
            # Get next question
            next_question_data = get_next_exam_question(exam_session, student)
            
            if next_question_data:
                return Response({
                    'status': 'correct',
                    'message': f'Correct! Well done. Moving to the next question.',
                    'attempt_number': attempt_number,
                    'next_question': next_question_data,
                    'progress': get_exam_progress_data(exam_session, student)
                })
            else:
                # Exam completed
                final_score = calculate_final_exam_score(exam_session, student)
                return Response({
                    'status': 'completed',
                    'message': 'Congratulations! You have completed the exam.',
                    'exam_completed': True,
                    'final_score': final_score,
                    'progress': get_exam_progress_data(exam_session, student)
                })
        
        else:
            # ❌ INCORRECT ANSWER: Check attempt count and decide next action
            if attempt_number < max_attempts:
                # Generate hint
                hint = generate_olama_hint(question, answer_text, attempt_number)
                
                # Store hint in attempt record
                attempt.hint_provided = hint
                attempt.save()
                
                return Response({
                    'status': 'hint',
                    'message': f'Not quite right. Here\'s a hint to help you:',
                    'hint': hint,
                    'attempt_number': attempt_number,
                    'max_attempts': max_attempts,
                    'attempts_remaining': max_attempts - attempt_number
                })
            
            else:
                # Max attempts reached - reveal answer and move on
                StudentAnswer.objects.create(
                    exam_session=exam_session,
                    question=question,
                    student=student,
                    answer_text=answer_text,
                    is_correct=False,
                    time_taken_seconds=time_taken,
                    interaction_log=json.dumps({
                        'attempt_count': attempt_number,
                        'interactive_mode': True,
                        'max_attempts_reached': True,
                        'olama_hints_used': attempt_number - 1
                    })
                )
                
                # Get next question
                next_question_data = get_next_exam_question(exam_session, student)
                
                if next_question_data:
                    return Response({
                        'status': 'reveal',
                        'message': f'Maximum attempts reached. The correct answer was: {question.correct_answer}',
                        'correct_answer': question.correct_answer,
                        'attempt_number': attempt_number,
                        'next_question': next_question_data,
                        'progress': get_exam_progress_data(exam_session, student)
                    })
                else:
                    # Exam completed
                    final_score = calculate_final_exam_score(exam_session, student)
                    return Response({
                        'status': 'completed',
                        'message': f'Exam completed! The correct answer to the last question was: {question.correct_answer}',
                        'correct_answer': question.correct_answer,
                        'exam_completed': True,
                        'final_score': final_score,
                        'progress': get_exam_progress_data(exam_session, student)
                    })
                    
    except Exception as e:
        print(f"Error handling exam session answer: {e}")
        return Response({
            'status': 'error',
            'message': f'Failed to process answer: {str(e)}'
        }, status=500)


def evaluate_chat_answer_correctness(question_data, answer_text):
    """Evaluate if the student's answer is correct for chat-based questions"""
    answer_text = answer_text.strip().lower()
    correct_answer = question_data['correct_answer'].strip().lower()
    
    # Simple text matching - can be enhanced with more sophisticated matching
    if answer_text == correct_answer:
        return True
    
    # Check if answer contains key parts of the correct answer
    correct_words = set(correct_answer.split())
    answer_words = set(answer_text.split())
    
    # If 70% of correct words are present, consider it correct
    if len(correct_words) > 0:
        overlap = len(correct_words.intersection(answer_words))
        if overlap / len(correct_words) >= 0.7:
            return True
    
    return False


def generate_chat_hint(question_data, answer_text, attempt_number, metadata):
    """Generate a hint for chat-based questions"""
    try:
        # Use pre-computed hints if available
        if 'hints' in question_data and attempt_number <= len(question_data['hints']):
            return question_data['hints'][attempt_number - 1]
        
        # Generate contextual hint using Ollama
        from .models import Document
        
        document = Document.objects.get(id=metadata['document_id'])
        
        prompt = f"""Based on this document content and the question, provide a helpful hint for attempt {attempt_number}.

Document: {document.title}
Question: {question_data['question']}
Correct Answer: {question_data['correct_answer']}
Student's Answer: {answer_text}

Provide a hint that:
1. Gently guides the student toward the correct answer
2. Doesn't give away the answer directly
3. Is appropriate for attempt {attempt_number} of 3
4. References the document content when relevant

Hint:"""

        try:
            # Use Gemini 2.0 Flash for hint generation
            global gemini_client
            if not gemini_client:
                return f"Hint {attempt_number}: Consider the main concepts from the document."
            
            response = gemini_client.generate_content(prompt)
            if response:
                response_text = response.text if hasattr(response, 'text') else str(response)
                if response_text:
                    return response_text.strip()
            
            return f"Hint {attempt_number}: Consider the main concepts from the document."
                
        except Exception as e:
            print(f"Error generating hint with Gemini: {e}")
            return f"Hint {attempt_number}: Consider the main concepts from the document."
            
    except Exception as e:
        print(f"Error in generate_chat_hint: {e}")
        return f"Hint {attempt_number}: Consider the main concepts from the document."


def calculate_chat_exam_score(exam_session):
    """Calculate final score for chat-based exam"""
    total_questions = len(exam_session.questions)
    correct_answers = exam_session.total_correct
    
    score_percentage = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    
    # Calculate efficiency score based on attempts
    total_attempts = sum(len(state.get('answers', [])) for state in exam_session.question_states.values())
    efficiency_score = max(0, 100 - (total_attempts - total_questions) * 10) if total_questions > 0 else 0
    
    return {
        'correct_answers': correct_answers,
        'total_questions': total_questions,
        'score_percentage': round(score_percentage, 1),
        'efficiency_score': round(efficiency_score, 1),
        'total_attempts': total_attempts
    }


def generate_questions_in_batches(document_content, document_title, total_count=10, batch_size=5):
    """Generate questions in batches to avoid response truncation"""
    try:
        all_questions = []
        remaining_count = total_count
        
        while remaining_count > 0:
            current_batch_size = min(batch_size, remaining_count)
            
            print(f"🔄 Generating batch of {current_batch_size} questions (remaining: {remaining_count})")
            
            batch_questions = generate_questions_with_gemini(
                document_content, 
                document_title, 
                count=current_batch_size
            )
            
            if batch_questions:
                all_questions.extend(batch_questions)
                remaining_count -= len(batch_questions)
                print(f"✅ Generated {len(batch_questions)} questions in this batch")
            else:
                print(f"❌ Failed to generate questions in batch, stopping")
                break
        
        print(f"🎯 Total questions generated: {len(all_questions)}")
        return all_questions[:total_count]  # Return exactly the requested count
        
    except Exception as e:
        print(f"❌ Batch question generation failed: {e}")
        return []


def generate_questions_with_gemini(document_content, document_title, count=10):
    """Generate questions from document using Gemini 2.0 Flash"""
    try:
        global gemini_client
        if not gemini_client:
            raise Exception("Gemini client not available")
        
        prompt = f"""תבסס על תוכן המסמך הבא, צור בדיוק {count} שאלות חינוכיות עם תשובות פתוחות (לא בחירה מרובה).

כותרת המסמך: {document_title}
תוכן המסמך: {document_content[:4000]}...

עבור כל שאלה, ספק:
1. שאלה ברורה וספציפית
2. התשובה הנכונה בהתבסס על המסמך
3. 3 רמזים הולכים ומתמקדים יותר
4. מילות מפתח שצריכות להיות בתשובה נכונה
5. סוג השאלה (מספרי, טקסט, מושג, וכו')
6. רמת קושי (easy/medium/hard)

פורמט כל שאלה כ-JSON:
{{
  "question": "מה זה...",
  "correct_answer": "התשובה היא...",
  "type": "text|numeric|concept",
  "keywords": ["מילת מפתח1", "מילת מפתח2"],
  "hints": [
    "רמז 1: חשב על...",
    "רמז 2: שקול את הקשר בין...", 
    "רמז 3: התשובה כוללת..."
  ],
  "difficulty": "easy|medium|hard"
}}

חשוב: צור מגוון של רמות קושי:
- 4 שאלות קלות (easy) - שאלות בסיסיות ופשוטות
- 3 שאלות בינוניות (medium) - שאלות הדורשות הבנה מעמיקה יותר
- 3 שאלות קשות (hard) - שאלות מורכבות הדורשות ניתוח מעמיק

צור בדיוק {count} שאלות המכסות את המושגים החשובים ביותר מהמסמך. החזר רק מערך JSON של השאלות."""

        response = gemini_client.generate_content(prompt)
        
        if not response:
            raise Exception("No response from Gemini")
        
        # Handle different response formats
        response_text = response.text if hasattr(response, 'text') else str(response)
        
        if not response_text:
            raise Exception("Empty response from Gemini")
        
        # Parse JSON questions from response
        questions = parse_questions_from_gemini_response(response_text)
        
        if len(questions) >= count:
            return questions[:count]
        else:
            # If we don't have enough questions, return what we have
            print(f"⚠️ Only generated {len(questions)} questions, requested {count}")
            return questions
            
    except Exception as e:
        print(f"❌ Question generation with Gemini failed: {e}")
        raise Exception(f"Unable to generate questions from document using Gemini: {str(e)}")


def parse_questions_from_gemini_response(response_text):
    """Parse JSON questions from Gemini response"""
    import json
    import re
    
    try:
        # Clean the response text
        cleaned_text = response_text.strip()
        
        # Remove markdown code blocks if present
        cleaned_text = re.sub(r'^```json\s*', '', cleaned_text)
        cleaned_text = re.sub(r'^```\s*', '', cleaned_text)
        cleaned_text = re.sub(r'\s*```$', '', cleaned_text)
        
        cleaned_text = cleaned_text.strip()
        
        # Try to find JSON array in the response - look for opening [ and find matching ]
        start_idx = cleaned_text.find('[')
        if start_idx != -1:
            # Find the matching closing bracket
            bracket_count = 0
            end_idx = start_idx
            for i, char in enumerate(cleaned_text[start_idx:], start_idx):
                if char == '[':
                    bracket_count += 1
                elif char == ']':
                    bracket_count -= 1
                    if bracket_count == 0:
                        end_idx = i + 1
                        break
            
            if bracket_count == 0:
                json_str = cleaned_text[start_idx:end_idx]
                print(f"🔍 Extracted JSON length: {len(json_str)}")
                print(f"🔍 JSON preview: {json_str[:200]}...")
                
                # Try to fix common JSON issues
                json_str = fix_json_string(json_str)
                questions = json.loads(json_str)
                return questions
            else:
                print(f"❌ Could not find matching closing bracket. Count: {bracket_count}")
        else:
            print("❌ Could not find opening bracket")
        
        # Fallback: try to parse the entire response as JSON
        cleaned_text = fix_json_string(cleaned_text)
        questions = json.loads(cleaned_text)
        return questions
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from Gemini response: {e}")
        print(f"Response text (first 500 chars): {response_text[:500]}")
        # Fallback: try to extract questions manually
        return extract_questions_manually(response_text)


def fix_json_string(json_str):
    """Fix common JSON formatting issues, especially for Hebrew content"""
    import re
    
    # Remove markdown code blocks if present
    if json_str.startswith('```json'):
        json_str = json_str[7:]
    if json_str.startswith('```'):
        json_str = json_str[3:]
    if json_str.endswith('```'):
        json_str = json_str[:-3]
    
    # Remove trailing commas before closing brackets/braces
    json_str = re.sub(r',\s*([}\]])', r'\1', json_str)
    
    # Fix incomplete strings at the end (common with Hebrew truncation)
    # Look for unterminated strings and try to close them
    if json_str.count('"') % 2 != 0:
        # Odd number of quotes - likely incomplete string
        if json_str.rstrip().endswith(','):
            json_str = json_str.rstrip().rstrip(',')
        json_str += '"'
    
    # Try to fix incomplete JSON arrays
    if json_str.count('[') > json_str.count(']'):
        json_str += ']'
    
    # Try to fix incomplete JSON objects
    if json_str.count('{') > json_str.count('}'):
        json_str += '}'
    
    # Additional fix for Hebrew content - ensure proper encoding
    try:
        json_str = json_str.encode('utf-8').decode('utf-8')
    except:
        pass
    
    return json_str


def extract_questions_manually(response_text):
    """Extract questions manually if JSON parsing fails"""
    questions = []
    lines = response_text.split('\n')
    current_question = {}
    
    for line in lines:
        line = line.strip()
        if line.startswith('"question":'):
            if current_question:
                questions.append(current_question)
            current_question = {
                'question': line.split('"question":')[1].strip().strip('",'),
                'correct_answer': '',
                'type': 'text',
                'keywords': [],
                'hints': [],
                'difficulty': 'medium'
            }
        elif line.startswith('"correct_answer":'):
            current_question['correct_answer'] = line.split('"correct_answer":')[1].strip().strip('",')
        elif line.startswith('"hints":'):
            # Extract hints from the next few lines
            hints = []
            # This is a simplified extraction - in practice, you might need more sophisticated parsing
            current_question['hints'] = hints
    
    if current_question:
        questions.append(current_question)
    
    return questions


def ensure_question_count_with_gemini(questions, document_content, document_title, count):
    """Ensure we have enough questions by generating more if needed"""
    if len(questions) >= count:
        return questions[:count]
    
    # Generate additional questions
    try:
        global gemini_client
        if not gemini_client:
            return questions[:count]
        
        remaining = count - len(questions)
        prompt = f"""Generate {remaining} more questions from this document content.

Document Title: {document_title}
Document Content: {document_content[:2000]}...

Return only a JSON array of {remaining} questions in the same format as before."""

        response = gemini_client.generate_content(prompt)
        
        if response:
            response_text = response.text if hasattr(response, 'text') else str(response)
            if response_text:
                additional_questions = parse_questions_from_gemini_response(response_text)
                questions.extend(additional_questions)
        
        return questions[:count]
        
    except Exception as e:
        print(f"Error generating additional questions: {e}")
        return questions[:count]


def evaluate_answer_correctness(question, answer_text):
    """Evaluate if the student's answer is correct"""
    answer_text = answer_text.strip().upper()
    correct_answer = question.correct_answer.strip().upper()
    
    # For multiple choice questions
    if question.question_type == 'multiple_choice':
        # Allow both letter answers (A, B, C, D) and full text matches
        if len(answer_text) == 1 and answer_text in ['A', 'B', 'C', 'D']:
            return answer_text == correct_answer
        else:
            # Check if answer matches any option
            options = {
                'A': question.option_a,
                'B': question.option_b,
                'C': question.option_c,
                'D': question.option_d
            }
            for letter, option_text in options.items():
                if option_text and answer_text in option_text.upper():
                    return letter == correct_answer
            return False
    else:
        # For other question types, do direct comparison
        return answer_text == correct_answer


def generate_olama_hint(question, student_answer, attempt_number):
    """Generate contextual hint using OLAMA"""
    try:
        hint_prompt = f"""You are an educational tutor helping a student who gave an incorrect answer. 

QUESTION: {question.question_text}
CORRECT ANSWER: {question.correct_answer}
STUDENT'S ANSWER: {student_answer}
ATTEMPT NUMBER: {attempt_number}

Generate a helpful hint that guides the student toward the correct answer without revealing it directly. The hint should:

1. Be encouraging and supportive
2. Point out what might be wrong with their approach
3. Give a clue about the correct thinking process
4. Be appropriate for attempt #{attempt_number} (more specific hints for later attempts)
5. NOT reveal the correct answer directly

Respond with only the hint text, no extra formatting."""

        # Use the existing RAG processor to get OLAMA response
        global rag_processor
        if rag_processor:
            hint = rag_processor.query_documents(hint_prompt, limit=1)
            if hint and len(hint) > 10:  # Basic validation
                return hint
        
        # Fallback to simple response if OLAMA is not available
        return get_simple_ollama_response(hint_prompt)
        
    except Exception as e:
        print(f"Error generating OLAMA hint: {e}")
        # Fallback hints based on attempt number
        fallback_hints = {
            1: "Think carefully about the question. What key concept is being tested here?",
            2: "Consider reviewing the fundamentals related to this topic. What approach would work best?",
            3: "Break down the problem step by step. What's the first thing you need to identify?"
        }
        return fallback_hints.get(attempt_number, "Take your time and think through this systematically.")


def get_next_exam_question(exam_session, student):
    """Get the next unanswered question in the exam session"""
    # Get questions already answered by this student
    answered_question_ids = StudentAnswer.objects.filter(
        exam_session=exam_session,
        student=student
    ).values_list('question_id', flat=True)
    
    # Get the next question in order
    next_session_question = exam_session.session_questions.exclude(
        question_id__in=answered_question_ids
    ).order_by('order_index').first()
    
    if next_session_question:
        question = next_session_question.question
        question_data = {
            'id': question.id,
            'question_text': question.question_text,
            'question_type': question.question_type,
            'order_index': next_session_question.order_index
        }
        
        # Add options for multiple choice questions
        if question.question_type == 'multiple_choice':
            question_data.update({
                'option_a': question.option_a,
                'option_b': question.option_b,
                'option_c': question.option_c,
                'option_d': question.option_d
            })
        
        return question_data
    
    return None


def get_exam_progress_data(exam_session, student):
    """Get current progress data for the exam session"""
    total_questions = exam_session.session_questions.count()
    answered_questions = StudentAnswer.objects.filter(
        exam_session=exam_session,
        student=student
    ).count()
    
    correct_answers = StudentAnswer.objects.filter(
        exam_session=exam_session,
        student=student,
        is_correct=True
    ).count()
    
    return {
        'total_questions': total_questions,
        'answered_questions': answered_questions,
        'correct_answers': correct_answers,
        'progress_percentage': round((answered_questions / total_questions) * 100, 1) if total_questions > 0 else 0,
        'accuracy_percentage': round((correct_answers / answered_questions) * 100, 1) if answered_questions > 0 else 0
    }


def calculate_final_exam_score(exam_session, student):
    """Calculate final score for completed exam"""
    total_questions = exam_session.session_questions.count()
    correct_answers = StudentAnswer.objects.filter(
        exam_session=exam_session,
        student=student,
        is_correct=True
    ).count()
    
    total_attempts = ExamAnswerAttempt.objects.filter(
        exam_session=exam_session,
        student=student
    ).count()
    
    return {
        'total_questions': total_questions,
        'correct_answers': correct_answers,
        'score_percentage': round((correct_answers / total_questions) * 100, 1) if total_questions > 0 else 0,
        'total_attempts': total_attempts,
        'efficiency_score': round((correct_answers / total_attempts) * 100, 1) if total_attempts > 0 else 0
    }


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_interactive_exam_progress(request, exam_session_id):
    """
    Get current progress of an interactive exam session
    
    This function handles both ChatSession-based and ExamSession-based interactive exams
    """
    if request.user.role != 'student':
        return Response({'error': 'Only students can check exam progress'}, status=403)
    
    try:
        from .models import ChatSession, ExamSession
        
        # Try to get as ChatSession first (new interactive exam format)
        try:
            session = ChatSession.objects.get(id=exam_session_id, student=request.user)
            metadata = session.get_session_metadata()
            
            if metadata.get('is_interactive_exam'):
                # This is a chat-based interactive exam
                exam_session = InteractiveExamSession.from_dict(metadata['exam_session'])
                
                # Calculate progress
                progress_data = {
                    'answered_questions': exam_session.current_question_index,
                    'total_questions': len(exam_session.questions),
                    'progress_percentage': (exam_session.current_question_index / len(exam_session.questions)) * 100,
                    'current_question_index': exam_session.current_question_index,
                    'is_completed': exam_session.current_question_index >= len(exam_session.questions)
                }
                
                # Get current question if not completed
                if not progress_data['is_completed']:
                    current_question = exam_session.questions[exam_session.current_question_index]
                    progress_data['current_question'] = {
                        'id': exam_session.current_question_index,
                        'question_text': current_question['question'],
                        'question_type': 'short_answer',
                        'correct_answer': current_question['correct_answer']
                    }
                    
                    # Get attempt history for current question
                    question_key = str(exam_session.current_question_index)
                    question_state = exam_session.question_states.get(question_key, {})
                    attempts = question_state.get('answers', [])
                    
                    progress_data['current_question_attempts'] = [
                        {
                            'attempt_number': i + 1,
                            'answer_text': attempt['answer'],
                            'is_correct': attempt.get('is_correct', False),
                            'hint_provided': attempt.get('hint', ''),
                            'submitted_at': attempt.get('timestamp', '')
                        }
                        for i, attempt in enumerate(attempts)
                    ]
                
                return Response({
                    'status': 'success',
                    'progress': progress_data
                })
            else:
                # This is not an interactive exam session
                return Response({
                    'status': 'error',
                    'message': 'This is not an interactive exam session'
                }, status=400)
                
        except ChatSession.DoesNotExist:
            # Fall back to ExamSession (legacy format)
            try:
                exam_session = ExamSession.objects.get(id=exam_session_id)
                progress_data = get_exam_progress_data(exam_session, request.user)
                
                # Get current question if not completed
                if progress_data['answered_questions'] < progress_data['total_questions']:
                    next_question = get_next_exam_question(exam_session, request.user)
                    progress_data['current_question'] = next_question
                
                # Get attempt history for current question if applicable
                if progress_data.get('current_question'):
                    current_question_id = progress_data['current_question']['id']
                    attempts = ExamAnswerAttempt.objects.filter(
                        exam_session=exam_session,
                        student=request.user,
                        question_id=current_question_id
                    ).order_by('attempt_number')
                    
                    progress_data['current_question_attempts'] = [
                        {
                            'attempt_number': attempt.attempt_number,
                            'answer_text': attempt.answer_text,
                            'is_correct': attempt.is_correct,
                            'hint_provided': attempt.hint_provided,
                            'submitted_at': attempt.submitted_at.isoformat()
                        }
                        for attempt in attempts
                    ]
                
                return Response({
                    'status': 'success',
                    'progress': progress_data
                })
                
            except ExamSession.DoesNotExist:
                return Response({
                    'status': 'error',
                    'message': 'Exam session not found'
                }, status=404)
        
    except Exception as e:
        print(f"Error getting interactive exam progress: {e}")
        return Response({
            'status': 'error',
            'message': f'Failed to get progress: {str(e)}'
        }, status=500)


# ===================================================================
# 🎯 TASK 3.2: COLLECT AND STORE ANSWERS - NEW API ENDPOINT
# ===================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_exam_answer(request):
    """
    🎯 Task 3.2: Submit answers during an active exam session
    
    For each student reply during an active exam session:
    - Save the response in the database
    - Validate question belongs to current exam session
    - Prevent duplicate answers
    - Return next question or completion status
    """
    if request.user.role != 'student':
        return Response({'error': 'Only students can submit exam answers'}, status=403)
    
    try:
        from .serializers import ExamAnswerSubmissionSerializer, ExamAnswerResponseSerializer
        
        # Validate and save the answer
        serializer = ExamAnswerSubmissionSerializer(data=request.data, context={'request': request})
        
        if not serializer.is_valid():
            return Response({
                'status': 'error',
                'errors': serializer.errors
            }, status=400)
        
        # Save the answer
        answer = serializer.save()
        
        # Get the exam session and check if exam is complete
        exam_session = ExamSession.objects.get(id=request.data['exam_session_id'])
        
        # Count total questions and answered questions for this student in this exam session
        total_session_questions = exam_session.session_questions.count()
        answered_questions = StudentAnswer.objects.filter(
            exam_session=exam_session,
            student=request.user
        ).count()
        
        # Check if exam is completed
        if answered_questions >= total_session_questions:
            # Mark exam as completed (you might need to track this in ExamConfig or another model)
            return Response({
                'status': 'completed',
                'message': 'Exam completed successfully',
                'total_questions': total_session_questions,
                'answered_questions': answered_questions,
                'final_score': {
                    'correct_answers': StudentAnswer.objects.filter(
                        exam_session=exam_session,
                        student=request.user,
                        is_correct=True
                    ).count(),
                    'total_questions': answered_questions
                }
            })
        
        # Get next question
        answered_question_ids = StudentAnswer.objects.filter(
            exam_session=exam_session,
            student=request.user
        ).values_list('question_id', flat=True)
        
        next_question = exam_session.session_questions.exclude(
            question_id__in=answered_question_ids
        ).order_by('order_index').first()
        
        if next_question:
            # Format next question
            question = next_question.question
            next_question_data = {
                'id': question.id,
                'question_text': question.question_text,
                'question_type': question.question_type,
                'order_index': next_question.order_index
            }
            
            # Add options for multiple choice questions
            if question.question_type == 'multiple_choice':
                next_question_data.update({
                    'option_a': question.option_a,
                    'option_b': question.option_b,
                    'option_c': question.option_c,
                    'option_d': question.option_d
                })
            
            return Response({
                'status': 'saved',
                'message': 'Answer saved successfully',
                'answered_questions': answered_questions,
                'total_questions': total_session_questions,
                'progress_percentage': round((answered_questions / total_session_questions) * 100, 1),
                'next_question': next_question_data
            })
        else:
            # No more questions, exam completed
            return Response({
                'status': 'completed',
                'message': 'Exam completed successfully',
                'total_questions': total_session_questions,
                'answered_questions': answered_questions,
                'final_score': {
                    'correct_answers': StudentAnswer.objects.filter(
                        exam_session=exam_session,
                        student=request.user,
                        is_correct=True
                    ).count(),
                    'total_questions': answered_questions
                }
            })
        
    except ExamSession.DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'Exam session not found'
        }, status=404)
    except Exception as e:
        print(f"Error submitting exam answer: {e}")
        return Response({
            'status': 'error',
            'message': f'Failed to submit answer: {str(e)}'
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_exam_progress(request, exam_session_id):
    """
    Get current progress of an exam session for a student
    """
    if request.user.role != 'student':
        return Response({'error': 'Only students can check exam progress'}, status=403)
    
    try:
        exam_session = ExamSession.objects.get(id=exam_session_id)
        
        # Check if student has access to this exam session
        # This depends on your permission model - you might check if student is assigned
        
        total_questions = exam_session.session_questions.count()
        answered_questions = StudentAnswer.objects.filter(
            exam_session=exam_session,
            student=request.user
        ).count()
        
        # Get current question (next unanswered question)
        answered_question_ids = StudentAnswer.objects.filter(
            exam_session=exam_session,
            student=request.user
        ).values_list('question_id', flat=True)
        
        current_question = exam_session.session_questions.exclude(
            question_id__in=answered_question_ids
        ).order_by('order_index').first()
        
        progress_data = {
            'exam_session_id': exam_session.id,
            'total_questions': total_questions,
            'answered_questions': answered_questions,
            'progress_percentage': round((answered_questions / total_questions) * 100, 1) if total_questions > 0 else 0,
            'is_completed': answered_questions >= total_questions
        }
        
        if current_question and not progress_data['is_completed']:
            question = current_question.question
            progress_data['current_question'] = {
                'id': question.id,
                'question_text': question.question_text,
                'question_type': question.question_type,
                'order_index': current_question.order_index
            }
            
            # Add options for multiple choice questions
            if question.question_type == 'multiple_choice':
                progress_data['current_question'].update({
                    'option_a': question.option_a,
                    'option_b': question.option_b,
                    'option_c': question.option_c,
                    'option_d': question.option_d
                })
        
        return Response({
            'status': 'success',
            'progress': progress_data
        })
        
    except ExamSession.DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'Exam session not found'
        }, status=404)
    except Exception as e:
        print(f"Error getting exam progress: {e}")
        return Response({
            'status': 'error',
            'message': f'Failed to get progress: {str(e)}'
        }, status=500)


# ===================================================================
# 🎯 PHASE 4: ANALYSIS AND TEACHER DASHBOARD
# ===================================================================

class StudentPerformanceAnalyzer:
    """
    Advanced Performance Analysis System
    Provides comprehensive analysis of student performance with topic-level insights
    """
    
    def __init__(self):
        self.topic_keywords = {
            'algebra': ['equation', 'variable', 'solve', 'x', 'y', 'coefficient', 'linear', 'quadratic'],
            'geometry': ['triangle', 'circle', 'area', 'perimeter', 'volume', 'angle', 'polygon', 'rectangle'],
            'fractions': ['fraction', 'numerator', 'denominator', 'divide', 'ratio', 'percentage'],
            'arithmetic': ['add', 'subtract', 'multiply', 'divide', 'sum', 'difference', 'product'],
            'statistics': ['mean', 'median', 'mode', 'average', 'data', 'graph', 'chart'],
            'calculus': ['derivative', 'integral', 'limit', 'function', 'slope', 'rate'],
            'physics': ['force', 'energy', 'motion', 'velocity', 'acceleration', 'gravity'],
            'chemistry': ['element', 'compound', 'reaction', 'molecule', 'atom', 'periodic']
        }
    
    def analyze_answer_correctness(self, student_answer, correct_answer, question_text=""):
        """
        Advanced answer analysis using multiple comparison methods
        """
        try:
            # Normalize answers for comparison
            student_norm = str(student_answer).strip().upper()
            correct_norm = str(correct_answer).strip().upper()
            
            # Exact match
            if student_norm == correct_norm:
                return {
                    'correctness': 'correct',
                    'confidence': 1.0,
                    'method': 'exact_match',
                    'score': 1.0
                }
            
            # For multiple choice (A, B, C, D)
            if len(student_norm) == 1 and len(correct_norm) == 1:
                if student_norm in ['A', 'B', 'C', 'D'] and correct_norm in ['A', 'B', 'C', 'D']:
                    return {
                        'correctness': 'incorrect',
                        'confidence': 1.0,
                        'method': 'multiple_choice',
                        'score': 0.0
                    }
            
            # Numerical comparison with tolerance
            try:
                student_num = float(student_norm.replace(',', ''))
                correct_num = float(correct_norm.replace(',', ''))
                
                # Allow 5% tolerance for numerical answers
                tolerance = abs(correct_num * 0.05) if correct_num != 0 else 0.1
                if abs(student_num - correct_num) <= tolerance:
                    return {
                        'correctness': 'correct',
                        'confidence': 0.9,
                        'method': 'numerical_tolerance',
                        'score': 1.0
                    }
                elif abs(student_num - correct_num) <= tolerance * 2:
                    return {
                        'correctness': 'partially_correct',
                        'confidence': 0.7,
                        'method': 'numerical_close',
                        'score': 0.5
                    }
            except (ValueError, TypeError):
                pass
            
            # Text similarity for word-based answers
            student_words = set(student_norm.split())
            correct_words = set(correct_norm.split())
            
            if student_words and correct_words:
                intersection = student_words.intersection(correct_words)
                union = student_words.union(correct_words)
                similarity = len(intersection) / len(union) if union else 0
                
                if similarity >= 0.8:
                    return {
                        'correctness': 'correct',
                        'confidence': similarity,
                        'method': 'text_similarity',
                        'score': 1.0
                    }
                elif similarity >= 0.5:
                    return {
                        'correctness': 'partially_correct',
                        'confidence': similarity,
                        'method': 'text_similarity',
                        'score': 0.7
                    }
            
            # Default: incorrect
            return {
                'correctness': 'incorrect',
                'confidence': 1.0,
                'method': 'no_match',
                'score': 0.0
            }
            
        except Exception as e:
            print(f"Error in answer analysis: {e}")
            return {
                'correctness': 'error',
                'confidence': 0.0,
                'method': 'error',
                'score': 0.0
            }
    
    def identify_question_topic(self, question_text):
        """
        Identify the topic/subject area of a question based on keywords
        """
        question_lower = question_text.lower()
        topic_scores = {}
        
        for topic, keywords in self.topic_keywords.items():
            score = sum(1 for keyword in keywords if keyword in question_lower)
            if score > 0:
                topic_scores[topic] = score
        
        if topic_scores:
            # Return topic with highest score
            best_topic = max(topic_scores, key=topic_scores.get)
            confidence = topic_scores[best_topic] / len(self.topic_keywords[best_topic])
            return {
                'topic': best_topic,
                'confidence': min(confidence, 1.0),
                'all_scores': topic_scores
            }
        
        return {
            'topic': 'general',
            'confidence': 0.5,
            'all_scores': {}
        }
    
    def analyze_student_performance(self, student_id, exam_id=None):
        """
        Comprehensive analysis of a student's performance
        """
        from .models import User, StudentAnswer, TestSession, QuestionBank
        
        try:
            student = User.objects.get(id=student_id, role='student')
            
            # Get all student answers (optionally filtered by exam)
            answers_query = StudentAnswer.objects.filter(test_session__student=student)
            if exam_id:
                answers_query = answers_query.filter(test_session__exam_id=exam_id)
            
            answers = answers_query.select_related('question', 'test_session')
            
            if not answers.exists():
                return {
                    'error': 'No answers found for this student',
                    'student_name': f"{student.first_name} {student.last_name}"
                }
            
            # Analyze each answer
            analyzed_answers = []
            topic_performance = {}
            total_questions = 0
            correct_answers = 0
            
            for answer in answers:
                question = answer.question
                
                # Advanced correctness analysis
                correctness_analysis = self.analyze_answer_correctness(
                    answer.student_answer,
                    question.correct_answer,
                    question.question_text
                )
                
                # Topic identification
                topic_analysis = self.identify_question_topic(question.question_text)
                topic = topic_analysis['topic']
                
                # Track topic performance
                if topic not in topic_performance:
                    topic_performance[topic] = {
                        'total': 0,
                        'correct': 0,
                        'partially_correct': 0,
                        'incorrect': 0,
                        'total_score': 0.0,
                        'questions': []
                    }
                
                topic_performance[topic]['total'] += 1
                topic_performance[topic]['total_score'] += correctness_analysis['score']
                
                if correctness_analysis['correctness'] == 'correct':
                    topic_performance[topic]['correct'] += 1
                    correct_answers += 1
                elif correctness_analysis['correctness'] == 'partially_correct':
                    topic_performance[topic]['partially_correct'] += 1
                else:
                    topic_performance[topic]['incorrect'] += 1
                
                topic_performance[topic]['questions'].append({
                    'question_id': question.id,
                    'question_text': question.question_text[:100] + '...',
                    'student_answer': answer.student_answer,
                    'correct_answer': question.correct_answer,
                    'correctness': correctness_analysis['correctness'],
                    'score': correctness_analysis['score']
                })
                
                analyzed_answers.append({
                    'question_id': question.id,
                    'question_text': question.question_text,
                    'student_answer': answer.student_answer,
                    'correct_answer': question.correct_answer,
                    'topic': topic,
                    'correctness_analysis': correctness_analysis,
                    'is_correct': answer.is_correct,
                    'time_taken': getattr(answer, 'time_taken_seconds', None)
                })
                
                total_questions += 1
            
            # Calculate topic mastery percentages
            topic_mastery = {}
            for topic, data in topic_performance.items():
                if data['total'] > 0:
                    mastery_percentage = (data['total_score'] / data['total']) * 100
                    topic_mastery[topic] = {
                        'mastery_percentage': round(mastery_percentage, 1),
                        'questions_answered': data['total'],
                        'correct': data['correct'],
                        'partially_correct': data['partially_correct'],
                        'incorrect': data['incorrect'],
                        'performance_level': (
                            'Excellent' if mastery_percentage >= 90 else
                            'Good' if mastery_percentage >= 80 else
                            'Fair' if mastery_percentage >= 70 else
                            'Needs Improvement' if mastery_percentage >= 60 else
                            'Poor'
                        )
                    }
            
            # Overall performance metrics
            overall_score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
            
            return {
                'success': True,
                'student_info': {
                    'id': student.id,
                    'name': f"{student.first_name} {student.last_name}",
                    'email': student.email
                },
                'overall_performance': {
                    'total_questions': total_questions,
                    'correct_answers': correct_answers,
                    'score_percentage': round(overall_score, 1),
                    'grade': (
                        'A' if overall_score >= 90 else
                        'B' if overall_score >= 80 else
                        'C' if overall_score >= 70 else
                        'D' if overall_score >= 60 else 'F'
                    )
                },
                'topic_mastery': topic_mastery,
                'detailed_answers': analyzed_answers,
                'recommendations': self.generate_recommendations(topic_mastery, overall_score)
            }
            
        except User.DoesNotExist:
            return {'error': 'Student not found'}
        except Exception as e:
            print(f"Error analyzing student performance: {e}")
            return {'error': str(e)}
    
    def generate_recommendations(self, topic_mastery, overall_score):
        """
        Generate personalized learning recommendations
        """
        recommendations = []
        
        # Identify weak areas
        weak_topics = [
            topic for topic, data in topic_mastery.items()
            if data['mastery_percentage'] < 70
        ]
        
        strong_topics = [
            topic for topic, data in topic_mastery.items()
            if data['mastery_percentage'] >= 85
        ]
        
        if weak_topics:
            recommendations.append({
                'type': 'improvement',
                'priority': 'high',
                'message': f"Focus on improving: {', '.join(weak_topics)}",
                'action': 'Additional practice recommended'
            })
        
        if strong_topics:
            recommendations.append({
                'type': 'strength',
                'priority': 'medium',
                'message': f"Strong performance in: {', '.join(strong_topics)}",
                'action': 'Consider advanced topics'
            })
        
        if overall_score < 60:
            recommendations.append({
                'type': 'urgent',
                'priority': 'high',
                'message': 'Overall performance needs significant improvement',
                'action': 'Schedule additional tutoring sessions'
            })
        elif overall_score >= 90:
            recommendations.append({
                'type': 'excellence',
                'priority': 'low',
                'message': 'Excellent overall performance!',
                'action': 'Consider challenging advanced problems'
            })
        
        return recommendations

# Global performance analyzer
performance_analyzer = StudentPerformanceAnalyzer()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analyze_student_performance(request, student_id):
    """
    🎯 Phase 4, Task 4.1: Analyze Student Performance
    Comprehensive analysis with NLP-based correctness evaluation
    """
    if request.user.role != 'teacher':
        return Response({'error': 'Only teachers can access student performance analysis'}, status=403)
    
    try:
        exam_id = request.GET.get('exam_id')  # Optional filter by specific exam
        
        analysis = performance_analyzer.analyze_student_performance(student_id, exam_id)
        
        return Response(analysis)
        
    except Exception as e:
        print(f"Error in student performance analysis: {e}")
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_topic_level_analysis(request):
    """
    🎯 Phase 4, Task 4.2: Evaluate Topic-Level Knowledge
    Group performance by topic with visual analytics
    """
    if request.user.role != 'teacher':
        return Response({'error': 'Only teachers can access topic analysis'}, status=403)
    
    try:
        from .models import StudentAnswer, TestSession, QuestionBank
        
        # Get optional filters
        exam_id = request.GET.get('exam_id')
        class_filter = request.GET.get('class')  # If you have class grouping
        
        # Base query for teacher's students
        answers_query = StudentAnswer.objects.select_related('question', 'test_session__student')
        
        # Filter by exam if specified
        if exam_id:
            answers_query = answers_query.filter(test_session__exam_id=exam_id)
        
        # TODO: Add class filter if you have class grouping
        # if class_filter:
        #     answers_query = answers_query.filter(test_session__student__class_name=class_filter)
        
        answers = answers_query.all()
        
        # Analyze by topic
        topic_analysis = {}
        student_topic_performance = {}
        
        for answer in answers:
            question = answer.question
            student = answer.test_session.student
            
            # Identify topic
            topic_info = performance_analyzer.identify_question_topic(question.question_text)
            topic = topic_info['topic']
            
            # Initialize topic tracking
            if topic not in topic_analysis:
                topic_analysis[topic] = {
                    'total_questions': 0,
                    'total_correct': 0,
                    'students': set(),
                    'questions': set(),
                    'performance_distribution': {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
                }
            
            # Track student performance in this topic
            student_key = f"{student.id}_{topic}"
            if student_key not in student_topic_performance:
                student_topic_performance[student_key] = {
                    'student_name': f"{student.first_name} {student.last_name}",
                    'student_id': student.id,
                    'topic': topic,
                    'correct': 0,
                    'total': 0
                }
            
            # Update counters
            topic_analysis[topic]['total_questions'] += 1
            topic_analysis[topic]['students'].add(student.id)
            topic_analysis[topic]['questions'].add(question.id)
            student_topic_performance[student_key]['total'] += 1
            
            if answer.is_correct:
                topic_analysis[topic]['total_correct'] += 1
                student_topic_performance[student_key]['correct'] += 1
        
        # Calculate topic mastery and student distributions
        topic_results = {}
        for topic, data in topic_analysis.items():
            if data['total_questions'] > 0:
                mastery_percentage = (data['total_correct'] / data['total_questions']) * 100
                
                # Calculate student performance distribution
                student_performances = []
                for key, perf in student_topic_performance.items():
                    if perf['topic'] == topic and perf['total'] > 0:
                        student_score = (perf['correct'] / perf['total']) * 100
                        student_performances.append({
                            'student_name': perf['student_name'],
                            'student_id': perf['student_id'],
                            'score_percentage': round(student_score, 1),
                            'correct': perf['correct'],
                            'total': perf['total']
                        })
                
                # Grade distribution
                grade_dist = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
                for perf in student_performances:
                    score = perf['score_percentage']
                    if score >= 90:
                        grade_dist['A'] += 1
                    elif score >= 80:
                        grade_dist['B'] += 1
                    elif score >= 70:
                        grade_dist['C'] += 1
                    elif score >= 60:
                        grade_dist['D'] += 1
                    else:
                        grade_dist['F'] += 1
                
                topic_results[topic] = {
                    'topic_name': topic.replace('_', ' ').title(),
                    'overall_mastery_percentage': round(mastery_percentage, 1),
                    'total_questions': data['total_questions'],
                    'total_correct': data['total_correct'],
                    'students_count': len(data['students']),
                    'unique_questions': len(data['questions']),
                    'student_performances': sorted(student_performances, 
                                                 key=lambda x: x['score_percentage'], reverse=True),
                    'grade_distribution': grade_dist,
                    'performance_level': (
                        'Excellent' if mastery_percentage >= 90 else
                        'Good' if mastery_percentage >= 80 else
                        'Fair' if mastery_percentage >= 70 else
                        'Needs Improvement' if mastery_percentage >= 60 else
                        'Poor'
                    )
                }
        
        # Generate summary statistics
        summary = {
            'total_topics_analyzed': len(topic_results),
            'topics_needing_attention': len([t for t in topic_results.values() if t['overall_mastery_percentage'] < 70]),
            'top_performing_topic': max(topic_results.items(), key=lambda x: x[1]['overall_mastery_percentage']) if topic_results else None,
            'lowest_performing_topic': min(topic_results.items(), key=lambda x: x[1]['overall_mastery_percentage']) if topic_results else None
        }
        
        return Response({
            'success': True,
            'summary': summary,
            'topic_analysis': topic_results,
            'recommendations': {
                'focus_areas': [name for name, data in topic_results.items() if data['overall_mastery_percentage'] < 70],
                'strong_areas': [name for name, data in topic_results.items() if data['overall_mastery_percentage'] >= 85]
            }
        })
        
    except Exception as e:
        print(f"Error in topic-level analysis: {e}")
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def teacher_dashboard(request):
    """
    🎯 Phase 4, Task 4.3: Display Results to Teacher
    Comprehensive teacher dashboard with all analytics
    """
    if request.user.role != 'teacher':
        return Response({'error': 'Only teachers can access the dashboard'}, status=403)
    
    try:
        from .models import Exam, TestSession, StudentAnswer, User
        
        # Get teacher's exams and students
        teacher_exams = Exam.objects.filter(created_by=request.user)
        teacher_students = User.objects.filter(
            role='student',
            testsession__exam__created_by=request.user
        ).distinct()
        
        # Recent exam sessions
        recent_sessions = TestSession.objects.filter(
            exam__created_by=request.user,
            session_complete=True
        ).select_related('student', 'exam').order_by('-created_at')[:10]
        
        # Overall statistics
        total_exams = teacher_exams.count()
        total_sessions = TestSession.objects.filter(exam__created_by=request.user).count()
        completed_sessions = TestSession.objects.filter(
            exam__created_by=request.user, 
            session_complete=True
        ).count()
        
        # Performance overview
        all_answers = StudentAnswer.objects.filter(
            test_session__exam__created_by=request.user
        )
        total_answers = all_answers.count()
        correct_answers = all_answers.filter(is_correct=True).count()
        overall_success_rate = (correct_answers / total_answers * 100) if total_answers > 0 else 0
        
        # Exam performance breakdown
        exam_performance = []
        for exam in teacher_exams:
            exam_sessions = TestSession.objects.filter(exam=exam, session_complete=True)
            exam_answers = StudentAnswer.objects.filter(test_session__exam=exam)
            
            if exam_answers.exists():
                exam_correct = exam_answers.filter(is_correct=True).count()
                exam_total = exam_answers.count()
                exam_success_rate = (exam_correct / exam_total * 100) if exam_total > 0 else 0
                
                exam_performance.append({
                    'exam_id': exam.id,
                    'exam_title': exam.title,
                    'total_sessions': exam_sessions.count(),
                    'success_rate': round(exam_success_rate, 1),
                    'total_questions_answered': exam_total,
                    'created_at': exam.created_at.isoformat(),
                    'is_published': exam.is_published
                })
        
        # Student performance summary
        student_summary = []
        for student in teacher_students[:20]:  # Limit to top 20 for dashboard
            student_answers = StudentAnswer.objects.filter(
                test_session__exam__created_by=request.user,
                test_session__student=student
            )
            
            if student_answers.exists():
                student_correct = student_answers.filter(is_correct=True).count()
                student_total = student_answers.count()
                student_avg = (student_correct / student_total * 100) if student_total > 0 else 0
                
                student_summary.append({
                    'student_id': student.id,
                    'student_name': f"{student.first_name} {student.last_name}",
                    'total_questions': student_total,
                    'correct_answers': student_correct,
                    'average_score': round(student_avg, 1),
                    'last_exam': student_answers.last().test_session.created_at.isoformat() if student_answers.last() else None
                })
        
        # Sort by performance
        student_summary.sort(key=lambda x: x['average_score'], reverse=True)
        
        return Response({
            'success': True,
            'dashboard_data': {
                'overview_statistics': {
                    'total_exams': total_exams,
                    'total_sessions': total_sessions,
                    'completed_sessions': completed_sessions,
                    'overall_success_rate': round(overall_success_rate, 1),
                    'total_students': teacher_students.count(),
                    'total_questions_answered': total_answers
                },
                'exam_performance': sorted(exam_performance, key=lambda x: x['success_rate'], reverse=True),
                'student_performance': student_summary,
                'recent_sessions': [
                    {
                        'session_id': session.id,
                        'student_name': f"{session.student.first_name} {session.student.last_name}",
                        'exam_title': session.exam.title,
                        'completed_at': session.created_at.isoformat(),
                        'score': 'Calculated on request'  # We could calculate this here if needed
                    } for session in recent_sessions
                ],
                'quick_actions': [
                    {'action': 'create_exam', 'label': 'Create New Exam', 'icon': '➕'},
                    {'action': 'view_analytics', 'label': 'View Detailed Analytics', 'icon': '📊'},
                    {'action': 'export_data', 'label': 'Export Results', 'icon': '📥'},
                    {'action': 'manage_students', 'label': 'Manage Students', 'icon': '👥'}
                ]
            }
        })
        
    except Exception as e:
        print(f"Error loading teacher dashboard: {e}")
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_exam_results(request, exam_id):
    """
    🎯 Phase 4, Task 4.3: Export Results (CSV, PDF, etc.)
    Export comprehensive exam results in multiple formats
    """
    if request.user.role != 'teacher':
        return Response({'error': 'Only teachers can export results'}, status=403)
    
    try:
        from .models import Exam, TestSession, StudentAnswer
        import csv
        from django.http import HttpResponse
        from io import StringIO
        
        # Verify exam ownership
        exam = Exam.objects.get(id=exam_id, created_by=request.user)
        
        # Get export format
        export_format = request.GET.get('format', 'csv').lower()
        
        # Get all completed sessions for this exam
        sessions = TestSession.objects.filter(
            exam=exam, 
            session_complete=True
        ).select_related('student')
        
        if export_format == 'csv':
            # Create CSV response
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="exam_{exam.id}_results.csv"'
            
            writer = csv.writer(response)
            
            # Write headers
            writer.writerow([
                'Student ID', 'Student Name', 'Email', 'Session ID',
                'Total Questions', 'Correct Answers', 'Score Percentage',
                'Completed At', 'Time Taken', 'Grade'
            ])
            
            # Write data
            for session in sessions:
                answers = StudentAnswer.objects.filter(test_session=session)
                total_questions = answers.count()
                correct_answers = answers.filter(is_correct=True).count()
                score_percentage = (correct_answers / total_questions * 100) if total_questions > 0 else 0
                grade = (
                    'A' if score_percentage >= 90 else
                    'B' if score_percentage >= 80 else
                    'C' if score_percentage >= 70 else
                    'D' if score_percentage >= 60 else 'F'
                )
                
                writer.writerow([
                    session.student.id,
                    f"{session.student.first_name} {session.student.last_name}",
                    session.student.email,
                    session.id,
                    total_questions,
                    correct_answers,
                    round(score_percentage, 1),
                    session.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'N/A',  # Time taken (you could calculate this)
                    grade
                ])
            
            return response
        
        elif export_format == 'json':
            # JSON export with detailed data
            export_data = {
                'exam_info': {
                    'id': exam.id,
                    'title': exam.title,
                    'subject': exam.subject,
                    'total_questions': exam.total_questions,
                    'created_by': f"{exam.created_by.first_name} {exam.created_by.last_name}",
                    'export_date': timezone.now().isoformat()
                },
                'results': []
            }
            
            for session in sessions:
                answers = StudentAnswer.objects.filter(test_session=session).select_related('question')
                total_questions = answers.count()
                correct_answers = answers.filter(is_correct=True).count()
                score_percentage = (correct_answers / total_questions * 100) if total_questions > 0 else 0
                
                session_data = {
                    'student': {
                        'id': session.student.id,
                        'name': f"{session.student.first_name} {session.student.last_name}",
                        'email': session.student.email
                    },
                    'session': {
                        'id': session.id,
                        'completed_at': session.created_at.isoformat(),
                        'total_questions': total_questions,
                        'correct_answers': correct_answers,
                        'score_percentage': round(score_percentage, 1)
                    },
                    'answers': [
                        {
                            'question_id': answer.question.id,
                            'question_text': answer.question.question_text,
                            'student_answer': answer.student_answer,
                            'correct_answer': answer.question.correct_answer,
                            'is_correct': answer.is_correct
                        } for answer in answers
                    ]
                }
                export_data['results'].append(session_data)
            
            response = HttpResponse(
                json.dumps(export_data, indent=2),
                content_type='application/json'
            )
            response['Content-Disposition'] = f'attachment; filename="exam_{exam.id}_detailed_results.json"'
            return response
        
        else:
            return Response({'error': 'Unsupported export format. Use csv or json.'}, status=400)
            
    except Exam.DoesNotExist:
        return Response({'error': 'Exam not found'}, status=404)
    except Exception as e:
        print(f"Error exporting results: {e}")
        return Response({'error': str(e)}, status=500)

# ==================== PHASE 4: ANALYSIS AND TEACHER DASHBOARD ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analyze_student_performance(request, student_id):
    """📊 Task 4.1: Analyze Individual Student Performance Across All Exams"""
    if request.user.role != 'teacher':
        return Response({'error': 'Only teachers can analyze student performance'}, status=403)
    
    try:
        from .models import TestSession, StudentAnswer, QuestionBank, Exam
        from collections import defaultdict
        
        student = User.objects.get(id=student_id, role='student')
        
        # Get all completed exam sessions for this student
        exam_sessions = TestSession.objects.filter(
            student=student,
            test_type='exam',
            session_complete=True
        ).select_related('exam')
        
        if not exam_sessions.exists():
            return Response({
                'student_info': {
                    'id': student.id,
                    'name': f"{student.first_name} {student.last_name}",
                    'email': student.email
                },
                'analysis': {
                    'total_exams': 0,
                    'average_score': 0,
                    'performance_trend': 'No data available',
                    'topic_mastery': {},
                    'difficulty_analysis': {},
                    'recent_performance': []
                }
            })
        
        # Analyze overall performance
        total_questions = 0
        total_correct = 0
        exam_scores = []
        topic_performance = defaultdict(lambda: {'correct': 0, 'total': 0})
        difficulty_performance = defaultdict(lambda: {'correct': 0, 'total': 0})
        
        # Process each exam session
        exam_details = []
        for session in exam_sessions.order_by('-created_at'):
            # Get all answers for this session
            answers = StudentAnswer.objects.filter(test_session=session).select_related('question')
            
            session_correct = sum(1 for answer in answers if answer.is_correct)
            session_total = answers.count()
            session_score = (session_correct / session_total * 100) if session_total > 0 else 0
            
            exam_details.append({
                'exam_id': session.exam.id if session.exam else None,
                'exam_title': session.exam.title if session.exam else 'Practice Test',
                'date': session.created_at.strftime('%Y-%m-%d'),
                'score': round(session_score, 1),
                'correct_answers': session_correct,
                'total_questions': session_total
            })
            
            # Accumulate statistics
            total_questions += session_total
            total_correct += session_correct
            exam_scores.append(session_score)
            
            # Analyze by topic and difficulty
            for answer in answers:
                if answer.question:
                    # Topic analysis
                    topic = answer.question.subject or 'General'
                    topic_performance[topic]['total'] += 1
                    if answer.is_correct:
                        topic_performance[topic]['correct'] += 1
                    
                    # Difficulty analysis
                    difficulty = answer.question.difficulty_level or '3'
                    difficulty_performance[difficulty]['total'] += 1
                    if answer.is_correct:
                        difficulty_performance[difficulty]['correct'] += 1
        
        # Calculate performance metrics
        overall_score = (total_correct / total_questions * 100) if total_questions > 0 else 0
        
        # Performance trend analysis
        if len(exam_scores) >= 3:
            recent_avg = sum(exam_scores[:3]) / 3
            older_avg = sum(exam_scores[3:]) / len(exam_scores[3:]) if len(exam_scores) > 3 else recent_avg
            
            if recent_avg > older_avg + 5:
                trend = "Improving"
            elif recent_avg < older_avg - 5:
                trend = "Declining"
            else:
                trend = "Stable"
        else:
            trend = "Insufficient data"
        
        # Topic mastery analysis
        topic_mastery = {}
        for topic, stats in topic_performance.items():
            mastery_percentage = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
            
            if mastery_percentage >= 80:
                mastery_level = "Strong"
            elif mastery_percentage >= 60:
                mastery_level = "Good"
            elif mastery_percentage >= 40:
                mastery_level = "Needs Improvement"
            else:
                mastery_level = "Weak"
            
            topic_mastery[topic] = {
                'percentage': round(mastery_percentage, 1),
                'level': mastery_level,
                'correct': stats['correct'],
                'total': stats['total']
            }
        
        # Difficulty analysis
        difficulty_analysis = {}
        difficulty_labels = {'1': 'Very Easy', '2': 'Easy', '3': 'Medium', '4': 'Hard', '5': 'Very Hard'}
        
        for difficulty, stats in difficulty_performance.items():
            success_rate = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
            difficulty_analysis[difficulty_labels.get(difficulty, f'Level {difficulty}')] = {
                'success_rate': round(success_rate, 1),
                'correct': stats['correct'],
                'total': stats['total']
            }
        
        return Response({
            'success': True,
            'student_info': {
                'id': student.id,
                'name': f"{student.first_name} {student.last_name}",
                'email': student.email
            },
            'analysis': {
                'total_exams': len(exam_sessions),
                'total_questions_answered': total_questions,
                'total_correct_answers': total_correct,
                'average_score': round(overall_score, 1),
                'performance_trend': trend,
                'topic_mastery': topic_mastery,
                'difficulty_analysis': difficulty_analysis,
                'recent_exams': exam_details[:5],  # Last 5 exams
                'all_exam_scores': exam_scores
            }
        })
        
    except User.DoesNotExist:
        return Response({'error': 'Student not found'}, status=404)
    except Exception as e:
        print(f"Error analyzing student performance: {e}")
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def topic_level_analysis(request):
    """📈 Task 4.2: Evaluate Topic-Level Knowledge Across All Students"""
    if request.user.role != 'teacher':
        return Response({'error': 'Only teachers can view topic analysis'}, status=403)
    
    try:
        from .models import TestSession, StudentAnswer, QuestionBank
        from collections import defaultdict
        
        # Get filter parameters
        exam_id = request.GET.get('exam_id')
        subject = request.GET.get('subject')
        difficulty_level = request.GET.get('difficulty_level')
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        
        # Base query for completed exam sessions
        sessions_query = TestSession.objects.filter(
            test_type='exam',
            session_complete=True
        )
        
        # Apply filters
        if exam_id:
            sessions_query = sessions_query.filter(exam_id=exam_id)
        if date_from:
            sessions_query = sessions_query.filter(created_at__gte=date_from)
        if date_to:
            sessions_query = sessions_query.filter(created_at__lte=date_to)
        
        # Get all answers from filtered sessions
        answers_query = StudentAnswer.objects.filter(
            test_session__in=sessions_query
        ).select_related('question', 'test_session__student')
        
        # Apply question filters
        if subject:
            answers_query = answers_query.filter(question__subject=subject)
        if difficulty_level:
            answers_query = answers_query.filter(question__difficulty_level=difficulty_level)
        
        # Analyze by topic
        topic_stats = defaultdict(lambda: {
            'total_questions': 0,
            'correct_answers': 0,
            'students_attempted': set(),
            'difficulty_breakdown': defaultdict(lambda: {'correct': 0, 'total': 0}),
            'student_performance': []
        })
        
        for answer in answers_query:
            if answer.question:
                topic = answer.question.subject or 'General'
                difficulty = answer.question.difficulty_level or '3'
                student_id = answer.test_session.student.id
                
                # Update topic statistics
                topic_stats[topic]['total_questions'] += 1
                topic_stats[topic]['students_attempted'].add(student_id)
                topic_stats[topic]['difficulty_breakdown'][difficulty]['total'] += 1
                
                if answer.is_correct:
                    topic_stats[topic]['correct_answers'] += 1
                    topic_stats[topic]['difficulty_breakdown'][difficulty]['correct'] += 1
                
                # Track individual student performance
                topic_stats[topic]['student_performance'].append({
                    'student_id': student_id,
                    'student_name': f"{answer.test_session.student.first_name} {answer.test_session.student.last_name}",
                    'is_correct': answer.is_correct,
                    'difficulty': difficulty,
                    'question_id': answer.question.id
                })
        
        # Process results
        topic_analysis = {}
        overall_stats = {
            'total_topics': 0,
            'total_questions': 0,
            'total_students': set(),
            'average_mastery': 0
        }
        
        mastery_scores = []
        
        for topic, stats in topic_stats.items():
            # Calculate mastery percentage
            mastery_percentage = (stats['correct_answers'] / stats['total_questions'] * 100) if stats['total_questions'] > 0 else 0
            mastery_scores.append(mastery_percentage)
            
            # Determine mastery level
            if mastery_percentage >= 80:
                mastery_level = "Excellent"
                recommendations = ["Continue reinforcing strong areas", "Challenge with advanced problems"]
            elif mastery_percentage >= 60:
                mastery_level = "Good"
                recommendations = ["Provide additional practice", "Focus on weak subtopics"]
            elif mastery_percentage >= 40:
                mastery_level = "Needs Improvement"
                recommendations = ["Reteach fundamentals", "Provide more guided practice", "Consider remedial activities"]
            else:
                mastery_level = "Critical"
                recommendations = ["Intensive intervention needed", "Break down into smaller concepts", "One-on-one tutoring recommended"]
            
            # Difficulty breakdown
            difficulty_breakdown = {}
            difficulty_labels = {'1': 'Very Easy', '2': 'Easy', '3': 'Medium', '4': 'Hard', '5': 'Very Hard'}
            
            for diff, diff_stats in stats['difficulty_breakdown'].items():
                success_rate = (diff_stats['correct'] / diff_stats['total'] * 100) if diff_stats['total'] > 0 else 0
                difficulty_breakdown[difficulty_labels.get(diff, f'Level {diff}')] = {
                    'success_rate': round(success_rate, 1),
                    'correct': diff_stats['correct'],
                    'total': diff_stats['total']
                }
            
            # Student performance summary
            student_summary = defaultdict(lambda: {'correct': 0, 'total': 0})
            for perf in stats['student_performance']:
                student_key = f"{perf['student_name']} (ID: {perf['student_id']})"
                student_summary[student_key]['total'] += 1
                if perf['is_correct']:
                    student_summary[student_key]['correct'] += 1
            
            student_performance_summary = []
            for student, perf in student_summary.items():
                student_score = (perf['correct'] / perf['total'] * 100) if perf['total'] > 0 else 0
                student_performance_summary.append({
                    'student': student,
                    'score': round(student_score, 1),
                    'correct': perf['correct'],
                    'total': perf['total']
                })
            
            # Sort students by performance
            student_performance_summary.sort(key=lambda x: x['score'], reverse=True)
            
            topic_analysis[topic] = {
                'mastery_percentage': round(mastery_percentage, 1),
                'mastery_level': mastery_level,
                'total_questions': stats['total_questions'],
                'correct_answers': stats['correct_answers'],
                'students_count': len(stats['students_attempted']),
                'difficulty_breakdown': difficulty_breakdown,
                'student_performance': student_performance_summary,
                'recommendations': recommendations
            }
            
            # Update overall stats
            overall_stats['total_questions'] += stats['total_questions']
            overall_stats['total_students'].update(stats['students_attempted'])
        
        overall_stats['total_topics'] = len(topic_analysis)
        overall_stats['total_students'] = len(overall_stats['total_students'])
        overall_stats['average_mastery'] = round(sum(mastery_scores) / len(mastery_scores), 1) if mastery_scores else 0
        
        return Response({
            'success': True,
            'overall_statistics': overall_stats,
            'topic_analysis': topic_analysis,
            'filters_applied': {
                'exam_id': exam_id,
                'subject': subject,
                'difficulty_level': difficulty_level,
                'date_from': date_from,
                'date_to': date_to
            }
        })
        
    except Exception as e:
        print(f"Error in topic analysis: {e}")
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def teacher_dashboard(request):
    """🎯 Task 4.3: Comprehensive Teacher Dashboard with Visual Data"""
    if request.user.role != 'teacher':
        return Response({'error': 'Only teachers can access the dashboard'}, status=403)
    
    try:
        from .models import Exam, TestSession, StudentAnswer, QuestionBank
        from collections import defaultdict
        from django.db.models import Count, Avg
        
        # Get teacher's exams
        teacher_exams = Exam.objects.filter(created_by=request.user)
        
        # Overall statistics
        total_exams = teacher_exams.count()
        published_exams = teacher_exams.filter(is_published=True).count()
        
        # Get completed sessions for teacher's exams
        completed_sessions = TestSession.objects.filter(
            exam__in=teacher_exams,
            session_complete=True
        ).select_related('student', 'exam')
        
        total_attempts = completed_sessions.count()
        unique_students = completed_sessions.values('student').distinct().count()
        
        # Recent activity (last 30 days)
        from datetime import timedelta
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_sessions = completed_sessions.filter(created_at__gte=thirty_days_ago)
        
        # Calculate average scores
        all_answers = StudentAnswer.objects.filter(
            test_session__in=completed_sessions
        )
        
        total_questions = all_answers.count()
        correct_answers = all_answers.filter(is_correct=True).count()
        overall_avg_score = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        
        # Exam performance summary
        exam_performance = []
        for exam in teacher_exams.order_by('-created_at')[:10]:  # Last 10 exams
            exam_sessions = completed_sessions.filter(exam=exam)
            exam_answers = all_answers.filter(test_session__in=exam_sessions)
            
            exam_total = exam_answers.count()
            exam_correct = exam_answers.filter(is_correct=True).count()
            exam_score = (exam_correct / exam_total * 100) if exam_total > 0 else 0
            
            exam_performance.append({
                'exam_id': exam.id,
                'title': exam.title,
                'attempts': exam_sessions.count(),
                'average_score': round(exam_score, 1),
                'created_date': exam.created_at.strftime('%Y-%m-%d'),
                'is_published': exam.is_published
            })
        
        # Student performance overview
        student_performance = []
        student_stats = defaultdict(lambda: {'sessions': 0, 'total_questions': 0, 'correct_answers': 0})
        
        for session in completed_sessions:
            student_id = session.student.id
            student_answers = all_answers.filter(test_session=session)
            
            student_stats[student_id]['sessions'] += 1
            student_stats[student_id]['total_questions'] += student_answers.count()
            student_stats[student_id]['correct_answers'] += student_answers.filter(is_correct=True).count()
            
            if 'student_info' not in student_stats[student_id]:
                student_stats[student_id]['student_info'] = {
                    'id': session.student.id,
                    'name': f"{session.student.first_name} {session.student.last_name}",
                    'email': session.student.email
                }
        
        for student_id, stats in student_stats.items():
            avg_score = (stats['correct_answers'] / stats['total_questions'] * 100) if stats['total_questions'] > 0 else 0
            student_performance.append({
                'student_info': stats['student_info'],
                'total_exams': stats['sessions'],
                'average_score': round(avg_score, 1),
                'total_questions': stats['total_questions'],
                'correct_answers': stats['correct_answers']
            })
        
        # Sort by average score
        student_performance.sort(key=lambda x: x['average_score'], reverse=True)
        
        # Topic performance across all exams
        topic_stats = defaultdict(lambda: {'correct': 0, 'total': 0})
        for answer in all_answers:
            if answer.question and answer.question.subject:
                topic = answer.question.subject
                topic_stats[topic]['total'] += 1
                if answer.is_correct:
                    topic_stats[topic]['correct'] += 1
        
        topic_performance = []
        for topic, stats in topic_stats.items():
            success_rate = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
            topic_performance.append({
                'topic': topic,
                'success_rate': round(success_rate, 1),
                'total_questions': stats['total'],
                'correct_answers': stats['correct']
            })
        
        topic_performance.sort(key=lambda x: x['success_rate'], reverse=True)
        
        # Recent activity feed
        recent_activity = []
        for session in recent_sessions.order_by('-created_at')[:20]:
            session_answers = all_answers.filter(test_session=session)
            session_score = (session_answers.filter(is_correct=True).count() / session_answers.count() * 100) if session_answers.count() > 0 else 0
            
            recent_activity.append({
                'type': 'exam_completion',
                'student_name': f"{session.student.first_name} {session.student.last_name}",
                'exam_title': session.exam.title if session.exam else 'Practice Test',
                'score': round(session_score, 1),
                'date': session.created_at.strftime('%Y-%m-%d %H:%M'),
                'questions_answered': session_answers.count()
            })
        
        # Performance trends (last 7 days)
        performance_trend = []
        for i in range(7):
            date = timezone.now() - timedelta(days=i)
            day_sessions = completed_sessions.filter(
                created_at__date=date.date()
            )
            day_answers = all_answers.filter(test_session__in=day_sessions)
            
            daily_score = 0
            if day_answers.count() > 0:
                daily_score = (day_answers.filter(is_correct=True).count() / day_answers.count() * 100)
            
            performance_trend.append({
                'date': date.strftime('%Y-%m-%d'),
                'average_score': round(daily_score, 1),
                'total_attempts': day_sessions.count()
            })
        
        performance_trend.reverse()  # Show oldest to newest
        
        return Response({
            'success': True,
            'dashboard_data': {
                'overview': {
                    'total_exams': total_exams,
                    'published_exams': published_exams,
                    'total_attempts': total_attempts,
                    'unique_students': unique_students,
                    'overall_average_score': round(overall_avg_score, 1),
                    'recent_attempts_30_days': recent_sessions.count()
                },
                'exam_performance': exam_performance,
                'student_performance': student_performance[:20],  # Top 20 students
                'topic_performance': topic_performance,
                'recent_activity': recent_activity,
                'performance_trend': performance_trend,
                'recommendations': [
                    f"Focus on improving {topic_performance[-1]['topic']} (lowest success rate)" if topic_performance else "Create more varied question types",
                    f"Congratulate top performer: {student_performance[0]['student_info']['name']}" if student_performance else "Encourage more student participation",
                    f"Consider reviewing {exam_performance[-1]['title']} (lowest exam score)" if exam_performance else "Continue creating engaging exams"
                ]
            }
        })
        
    except Exception as e:
        print(f"Error generating teacher dashboard: {e}")
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_dashboard_data(request):
    """📄 Export dashboard data in various formats (CSV, JSON, PDF)"""
    if request.user.role != 'teacher':
        return Response({'error': 'Only teachers can export dashboard data'}, status=403)
    
    try:
        format_type = request.GET.get('format', 'csv').lower()
        data_type = request.GET.get('type', 'overview').lower()  # overview, students, topics, exams
        
        # Get dashboard data first
        dashboard_response = teacher_dashboard(request)
        if not dashboard_response.data.get('success'):
            return dashboard_response
        
        dashboard_data = dashboard_response.data['dashboard_data']
        
        if format_type == 'csv':
            import csv
            from django.http import HttpResponse
            
            response = HttpResponse(content_type='text/csv')
            
            if data_type == 'students':
                response['Content-Disposition'] = 'attachment; filename="student_performance.csv"'
                writer = csv.writer(response)
                writer.writerow(['Student Name', 'Email', 'Total Exams', 'Average Score', 'Total Questions', 'Correct Answers'])
                
                for student in dashboard_data['student_performance']:
                    writer.writerow([
                        student['student_info']['name'],
                        student['student_info']['email'],
                        student['total_exams'],
                        student['average_score'],
                        student['total_questions'],
                        student['correct_answers']
                    ])
            
            elif data_type == 'topics':
                response['Content-Disposition'] = 'attachment; filename="topic_performance.csv"'
                writer = csv.writer(response)
                writer.writerow(['Topic', 'Success Rate', 'Total Questions', 'Correct Answers'])
                
                for topic in dashboard_data['topic_performance']:
                    writer.writerow([
                        topic['topic'],
                        topic['success_rate'],
                        topic['total_questions'],
                        topic['correct_answers']
                    ])
            
            elif data_type == 'exams':
                response['Content-Disposition'] = 'attachment; filename="exam_performance.csv"'
                writer = csv.writer(response)
                writer.writerow(['Exam Title', 'Attempts', 'Average Score', 'Created Date', 'Published'])
                
                for exam in dashboard_data['exam_performance']:
                    writer.writerow([
                        exam['title'],
                        exam['attempts'],
                        exam['average_score'],
                        exam['created_date'],
                        'Yes' if exam['is_published'] else 'No'
                    ])
            
            else:  # overview
                response['Content-Disposition'] = 'attachment; filename="dashboard_overview.csv"'
                writer = csv.writer(response)
                writer.writerow(['Metric', 'Value'])
                
                overview = dashboard_data['overview']
                for key, value in overview.items():
                    writer.writerow([key.replace('_', ' ').title(), value])
            
            return response
        
        elif format_type == 'json':
            from django.http import JsonResponse
            
            response = JsonResponse(dashboard_data, safe=False)
            response['Content-Disposition'] = f'attachment; filename="dashboard_{data_type}.json"'
            return response
        
        else:
            return Response({'error': 'Unsupported export format. Use csv or json.'}, status=400)
            
    except Exception as e:
        print(f"Error exporting dashboard data: {e}")
        return Response({'error': str(e)}, status=500)


# =================
# INTERACTIVE LEARNING & SOCRATIC TUTORING SYSTEM
# =================

@api_view(['GET'])
@permission_classes([])  # Allow anonymous access for student tests
def get_test_questions(request):
    """Get algorithm questions for student level tests from teacher-generated question bank"""
    try:
        from .models import QuestionBank
        from .serializers import QuestionBankSerializer
        
        # Get query parameters
        difficulty_level = request.GET.get('difficulty_level', 'easy')  # Default to easy
        num_questions = int(request.GET.get('num_questions', 10))
        subject = request.GET.get('subject', 'algorithms')
        
        # Get approved algorithm questions from all teachers
        questions = QuestionBank.objects.filter(
            is_approved=True,
            subject=subject
        ).order_by('?')  # Random order
        
        # Filter by difficulty level if specified
        if difficulty_level:
            questions = questions.filter(difficulty_level=difficulty_level)
        
        # Limit the number of questions
        questions = questions[:num_questions]
        
        serializer = QuestionBankSerializer(questions, many=True)
        
        # Format questions for the new open-ended test interface
        formatted_questions = []
        for q in serializer.data:
            formatted_question = {
                'id': q['id'],
                'question': q['question_text'],
                'type': q.get('question_type', 'open_ended'),
                'subject': q.get('subject', 'algorithms'),
                'difficulty': q['difficulty_level'],
                'expected_approach': q.get('expected_approach', ''),
                'key_concepts': q.get('key_concepts', ''),
                'hints': q.get('hints', ''),
                'sample_solution': q.get('sample_solution', ''),
                'correct_answer': q['correct_answer'],
                'explanation': q.get('explanation', '')
            }
            formatted_questions.append(formatted_question)
        
        return Response({
            'questions': formatted_questions,
            'total_available': QuestionBank.objects.filter(is_approved=True, subject=subject).count(),
            'difficulty_level': difficulty_level,
            'subject': subject,
            'num_questions': len(formatted_questions)
        })
        
    except Exception as e:
        print(f"Error getting test questions: {e}")
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_ai_hint(request):
    """Get AI-generated hint for struggling students during algorithm questions"""
    try:
        from .models import QuestionBank, TestHint, TestSession
        
        data = request.data
        user = request.user
        question_id = data.get('question_id')
        student_input = data.get('student_input', '')
        hint_level = data.get('hint_level', 1)  # Progressive hints: 1=basic, 2=medium, 3=detailed
        test_session_id = data.get('test_session_id')
        
        # Get the question
        try:
            question = QuestionBank.objects.get(id=question_id)
        except QuestionBank.DoesNotExist:
            return Response({'error': 'Question not found'}, status=404)
        
        # Get test session if provided
        test_session = None
        if test_session_id:
            try:
                test_session = TestSession.objects.get(id=test_session_id, student=user)
            except TestSession.DoesNotExist:
                pass
        
        # Generate contextual hint based on the question and student input
        hint_text = ""
        
        if hint_level == 1:
            # Basic hint - guide toward the approach
            if question.key_concepts:
                hint_text = f"Think about these key concepts: {question.key_concepts}. "
            if question.expected_approach:
                approach_words = question.expected_approach.split()[:10]  # First 10 words
                hint_text += f"Consider this approach: {' '.join(approach_words)}..."
        
        elif hint_level == 2:
            # Medium hint - more specific guidance
            if question.expected_approach:
                approach_words = question.expected_approach.split()[:20]  # First 20 words
                hint_text = f"Here's a more detailed approach: {' '.join(approach_words)}..."
            if question.hints:
                hint_text += f" Additional hint: {question.hints}"
        
        elif hint_level >= 3:
            # Detailed hint - show sample approach but not full solution
            if question.sample_solution:
                solution_lines = question.sample_solution.split('\n')[:3]  # First 3 lines
                hint_text = f"Here's the beginning of a solution approach:\n{chr(10).join(solution_lines)}..."
            else:
                hint_text = question.hints or question.expected_approach or "Consider breaking the problem into smaller steps."
        
        if not hint_text:
            hint_text = "Try to break down the problem step by step. What is the main goal of this algorithm?"
        
        # Save the hint to track student progress
        if test_session:
            TestHint.objects.create(
                student=user,
                question=question,
                test_session=test_session,
                hint_text=hint_text,
                hint_level=hint_level,
                student_input=student_input
            )
        
        return Response({
            'hint': hint_text,
            'hint_level': hint_level,
            'question_id': question_id,
            'max_hints_reached': hint_level >= 3
        })
        
    except Exception as e:
        print(f"Error generating AI hint: {e}")
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def evaluate_answer(request):
    """Evaluate student's open-ended answer using AI and provide feedback"""
    try:
        from .models import QuestionBank, StudentAnswer, TestSession
        
        data = request.data
        user = request.user
        question_id = data.get('question_id')
        student_answer = data.get('answer', '')
        test_session_id = data.get('test_session_id')
        
        # Get the question
        try:
            question = QuestionBank.objects.get(id=question_id)
        except QuestionBank.DoesNotExist:
            return Response({'error': 'Question not found'}, status=404)
        
        # Get test session if provided
        test_session = None
        if test_session_id:
            try:
                test_session = TestSession.objects.get(id=test_session_id, student=user)
            except TestSession.DoesNotExist:
                pass
        
        # Simple evaluation logic (can be enhanced with AI)
        is_correct = False
        feedback = ""
        
        # Basic keyword matching for now - can be enhanced with LLM evaluation
        correct_answer_lower = question.correct_answer.lower()
        student_answer_lower = student_answer.lower()
        
        # Check for key concepts or approaches
        if question.key_concepts:
            key_concepts = [concept.strip().lower() for concept in question.key_concepts.split(',')]
            concepts_mentioned = sum(1 for concept in key_concepts if concept in student_answer_lower)
            concept_score = concepts_mentioned / len(key_concepts) if key_concepts else 0
        else:
            concept_score = 0
        
        # Simple scoring - can be enhanced
        if concept_score >= 0.7 or any(word in student_answer_lower for word in correct_answer_lower.split()[:5]):
            is_correct = True
            feedback = "Good job! Your answer demonstrates understanding of the key concepts."
        else:
            feedback = "Your answer needs more work. Consider the key algorithmic concepts for this problem."
        
        # Save the answer
        if test_session:
            StudentAnswer.objects.create(
                test_session=test_session,
                question=question,
                student=user,
                answer_text=student_answer,
                is_correct=is_correct
            )
        
        return Response({
            'is_correct': is_correct,
            'feedback': feedback,
            'question_id': question_id,
            'expected_approach': question.expected_approach,
            'explanation': question.explanation
        })
        
    except Exception as e:
        print(f"Error evaluating answer: {e}")
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_test_results(request):
    """Submit test results for student level assessment"""
    try:
        from .models import StudentTestResult
        
        data = request.data
        user = request.user
        
        # Create or update test result
        test_result = StudentTestResult.objects.create(
            student=user,
            difficulty_level=data.get('difficulty_level'),
            total_questions=data.get('total_questions'),
            correct_answers=data.get('correct_answers'),
            time_taken_seconds=data.get('time_taken_seconds'),
            percentage_score=data.get('percentage_score'),
            assessed_level=data.get('assessed_level'),
            questions_used=data.get('questions_used', []),  # Store question IDs used
        )
        
        return Response({
            'success': True,
            'test_result_id': test_result.id,
            'message': 'Test results saved successfully'
        })
        
    except Exception as e:
        print(f"Error saving test results: {e}")
        return Response({'error': str(e)}, status=500)

from textblob import TextBlob
from .models import ChatSession, ConversationMessage, ConversationInsight, LearningPath, QuestionBank, Exam
from .serializers import (
    ChatSessionSerializer, ChatSessionCreateSerializer, ConversationMessageSerializer,
    ConversationInsightSerializer, LearningPathSerializer, InteractiveLearningSessionResponseSerializer,
    ChatInteractionResponseSerializer, LearningProgressResponseSerializer
)

class AdaptiveQuestionGenerator:
    """
    Generates questions with adaptive difficulty based on student performance
    """
    
    def __init__(self):
        self.rag_processor = ComprehensiveRAGProcessor()
        
        # Difficulty progression templates for algebra
        self.algebra_templates = {
            1: {  # Foundation - Simple substitution and basic concepts
                'patterns': [
                    "What does x represent in the equation x + 3 = 7?",
                    "If x = 2, what is x + 5?",
                    "In 3 + x = 8, what number could x be?",
                    "If y = 4, what is 2y?",
                ],
                'concepts': ['variables', 'substitution', 'basic addition']
            },
            2: {  # Basic - Simple one-step equations
                'patterns': [
                    "Solve: x + 5 = 12",
                    "Find x: x - 3 = 9", 
                    "What is x when 2x = 10?",
                    "Solve: x/3 = 4",
                ],
                'concepts': ['one-step equations', 'inverse operations']
            },
            3: {  # Intermediate - Two-step equations
                'patterns': [
                    "Solve: 2x + 5 = 13",
                    "Find x: 3x - 7 = 14",
                    "Solve: x/2 + 3 = 8",
                    "What is x when 4x - 6 = 18?",
                ],
                'concepts': ['two-step equations', 'order of operations']
            },
            4: {  # Advanced - Multi-step and complex equations
                'patterns': [
                    "Solve: 3(x + 2) = 21",
                    "Find x: 2x + 5 = x + 12",
                    "Solve: 4x - 3(x - 1) = 7",
                    "What is x when (x + 4)/3 = 5?",
                ],
                'concepts': ['distributive property', 'combining like terms', 'variables on both sides']
            },
            5: {  # Expert - Complex multi-step equations
                'patterns': [
                    "Solve: 2(3x - 4) + 5 = 3(x + 2) - 1",
                    "Find x: (2x - 1)/3 + (x + 2)/4 = 2",
                    "Solve: x² - 5x + 6 = 0",
                    "What is x when √(x + 9) = 5?",
                ],
                'concepts': ['complex multi-step', 'fractions', 'quadratics', 'square roots']
            }
        }
        
        # Fraction difficulty progression
        self.fraction_templates = {
            1: {  # Foundation - Understanding fractions
                'patterns': [
                    "If you eat 2 out of 8 pizza slices, what fraction did you eat?",
                    "What does the bottom number (denominator) in 3/4 tell us?",
                    "Which is bigger: 1/2 or 1/4?",
                    "If a chocolate bar has 6 pieces and you eat 2, what fraction is left?",
                ],
                'concepts': ['fraction notation', 'numerator/denominator', 'basic comparison']
            },
            2: {  # Basic - Simple fraction operations
                'patterns': [
                    "What is 1/4 + 1/4?",
                    "Subtract: 3/5 - 1/5",
                    "Which is larger: 2/3 or 1/2?",
                    "What is half of 1/2?",
                ],
                'concepts': ['adding same denominators', 'subtracting fractions', 'comparison']
            },
            3: {  # Intermediate - Different denominators
                'patterns': [
                    "Add: 1/3 + 1/6",
                    "What is 2/3 - 1/4?",
                    "Multiply: 1/2 × 3/4",
                    "Convert 2/3 to a decimal",
                ],
                'concepts': ['common denominators', 'multiplication', 'decimals']
            },
            4: {  # Advanced - Complex operations
                'patterns': [
                    "Divide: 3/4 ÷ 1/2",
                    "Simplify: (2/3 + 1/4) × 3/5",
                    "What is 2¾ as an improper fraction?",
                    "Solve: x/3 + 1/6 = 2/3",
                ],
                'concepts': ['division', 'mixed numbers', 'complex operations']
            },
            5: {  # Expert - Advanced fraction problems
                'patterns': [
                    "If 3/4 of a number is 18, what is the number?",
                    "Simplify: (2/3 - 1/4) ÷ (1/2 + 1/6)",
                    "A recipe calls for 2⅓ cups of flour. If you want to make ¾ of the recipe, how much flour do you need?",
                    "Solve: (x - 1)/2 + (x + 1)/3 = 2",
                ],
                'concepts': ['word problems', 'complex operations', 'real-world applications']
            }
        }
    
    def generate_question_for_level(self, topic, difficulty_level, student_context=""):
        """Generate a question appropriate for the given difficulty level"""
        try:
            # Get templates based on topic
            if 'algebra' in topic.lower():
                templates = self.algebra_templates.get(difficulty_level, self.algebra_templates[1])
            elif 'fraction' in topic.lower():
                templates = self.fraction_templates.get(difficulty_level, self.fraction_templates[1])
            else:
                # Default to algebra templates
                templates = self.algebra_templates.get(difficulty_level, self.algebra_templates[1])
            
            # Try AI-enhanced question generation
            if self.rag_processor.llm:
                ai_question = self._generate_ai_question(topic, difficulty_level, templates, student_context)
                if ai_question:
                    return ai_question
            
            # Fallback to template-based generation
            pattern = random.choice(templates['patterns'])
            return {
                'question': pattern,
                'difficulty': difficulty_level,
                'concepts': templates['concepts'],
                'expected_answer': self._extract_expected_answer(pattern),
                'hint_progression': self._generate_hint_progression(pattern, difficulty_level)
            }
            
        except Exception as e:
            print(f"❌ Question generation failed: {e}")
            return self._get_fallback_question(topic, difficulty_level)
    
    def _generate_ai_question(self, topic, difficulty_level, templates, student_context):
        """Use AI to generate focused, concise questions"""
        try:
            concepts = ", ".join(templates['concepts'])
            example_patterns = templates['patterns'][0] if templates['patterns'] else "Basic question"
            
            prompt = f"""Generate ONE short math question for {topic} at difficulty level {difficulty_level}/5.

EXAMPLE: {example_patterns}
CONCEPTS: {concepts}
STUDENT: {student_context}

REQUIREMENTS:
- Maximum 25 words
- Clear and specific
- Level {difficulty_level} difficulty
- Encourages discovery
- No direct answers given

Generate ONE question:"""
            
            ai_response = self.rag_processor.llm.invoke(prompt)
            if ai_response and len(str(ai_response).strip()) > 10:
                question_text = str(ai_response).strip()
                
                # Ensure question is concise
                if len(question_text) > 150:
                    sentences = question_text.split('.')
                    question_text = sentences[0] + '?' if not sentences[0].endswith('?') else sentences[0]
                
                return {
                    'question': question_text,
                    'difficulty': difficulty_level,
                    'concepts': templates['concepts'],
                    'expected_answer': self._extract_expected_answer(question_text),
                    'hint_progression': self._generate_hint_progression(question_text, difficulty_level),
                    'ai_generated': True
                }
        except Exception as e:
            print(f"⚠️ AI question generation failed: {e}")
        
        return None
    
    def _extract_expected_answer(self, question):
        """Extract or calculate the expected answer from a question"""
        try:
            # Simple pattern matching for common equation types
            question_lower = question.lower()
            
            # Look for simple equations like "x + 5 = 12"
            if 'x + 5 = 12' in question:
                return 'x = 7'
            elif '2x = 10' in question:
                return 'x = 5'
            elif '2x + 5 = 13' in question:
                return 'x = 4'
            elif '3x - 7 = 14' in question:
                return 'x = 7'
            elif 'x - 3 = 9' in question:
                return 'x = 12'
            elif 'x/3 = 4' in question:
                return 'x = 12'
            elif '1/4 + 1/4' in question:
                return '1/2 or 2/4'
            elif '3/5 - 1/5' in question:
                return '2/5'
            
            # Default for conceptual questions
            return "Conceptual understanding expected"
            
        except:
            return "Answer varies"
    
    def _generate_hint_progression(self, question, difficulty_level):
        """Generate a progression of hints for the question"""
        hints = []
        
        try:
            if 'algebra' in question.lower() or any(var in question for var in ['x', 'y', '=']):
                hints = [
                    "What do you notice about this equation? What is it asking you to find?",
                    "What operation could help you isolate the variable?",
                    "What happens when you perform the same operation on both sides?",
                    "Can you check your answer by substituting it back into the original equation?",
                    "Let's work through this step by step together."
                ]
            elif any(fraction in question for fraction in ['/', 'fraction', 'pizza', 'pieces']):
                hints = [
                    "What does each part of the fraction represent?",
                    "How many equal parts is the whole divided into?",
                    "How many parts are we talking about?",
                    "Can you visualize this with a concrete example?",
                    "Let's think about this using a real-world example."
                ]
            else:
                hints = [
                    "What is this question really asking?",
                    "What information do you have to work with?",
                    "What would be a good first step?",
                    "How might you approach this differently?",
                    "Let's break this down into smaller pieces."
                ]
            
            # Adjust number of hints based on difficulty
            return hints[:max(3, difficulty_level)]
            
        except:
            return ["Think about what the question is asking.", "What would be your first step?", "Let's work through this together."]
    
    def _get_fallback_question(self, topic, difficulty_level):
        """Fallback question when generation fails"""
        fallback_questions = {
            1: "What does the variable x represent in an equation?",
            2: "Can you solve: x + 3 = 8?",
            3: "How would you solve: 2x + 1 = 9?",
            4: "What's your approach for: 3(x - 2) = 12?",
            5: "How would you tackle: 2x + 3 = x + 7?"
        }
        
        return {
            'question': fallback_questions.get(difficulty_level, "What interests you about mathematics?"),
            'difficulty': difficulty_level,
            'concepts': ['basic understanding'],
            'expected_answer': 'Various answers possible',
            'hint_progression': ["What do you think?", "How would you approach this?", "Let's explore together."]
        }


class SocraticTutor:
    """
    AI-powered adaptive tutor that guides students through progressive difficulty levels
    """
    
    def __init__(self):
        # Initialize RAG processor for AI capabilities
        self.rag_processor = ComprehensiveRAGProcessor()
        
        # Initialize adaptive question generator
        self.question_generator = AdaptiveQuestionGenerator()
        
        # Educational knowledge base for RAG
        self.knowledge_base = self._create_educational_knowledge_base()
        
        # Socratic teaching prompts
        self.socratic_prompts = {
            'encouragement': [
                "That's an interesting way to think about it!",
                "You're on the right track!",
                "Great question! What do you think?",
                "I can see you're really thinking about this.",
                "That shows good understanding!",
                "What an excellent observation!",
                "You're getting closer to something important!"
            ],
            'discovery': [
                "What do you notice about...",
                "How might you approach...",
                "What happens when you...",
                "Can you think of a way to...",
                "What pattern do you see in...",
                "How does this relate to...",
                "What would happen if...",
            ]
        }
    
    def get_adaptive_question(self, student, topic, session):
        """Generate next question based on student's adaptive difficulty level"""
        try:
            # Get or create difficulty tracker for this student and topic
            from .models import AdaptiveDifficultyTracker
            
            tracker, created = AdaptiveDifficultyTracker.objects.get_or_create(
                student=student,
                topic=topic,
                chat_session=session,
                defaults={
                    'current_difficulty': 1,  # Start at easiest level
                    'target_difficulty': 3,   # Default target
                    'subject': session.subject if session else 'math'
                }
            )
            
            if created:
                print(f"✅ Created new difficulty tracker for {student.username} - {topic}")
            
            # Generate question for current difficulty level
            question_data = self.question_generator.generate_question_for_level(
                topic, 
                tracker.current_difficulty,
                f"Student has {tracker.consecutive_successes} consecutive successes, {tracker.calculate_success_rate():.1f}% success rate"
            )
            
            # Create enhanced question with difficulty context
            enhanced_question = self._enhance_question_with_context(question_data, tracker)
            
            return enhanced_question, tracker
            
        except Exception as e:
            print(f"❌ Adaptive question generation failed: {e}")
            # Fallback to basic question
            return {
                'question': f"Let's explore {topic} together! What interests you most about this topic?",
                'difficulty': 1,
                'concepts': ['exploration'],
                'expected_answer': 'Open exploration',
                'hint_progression': ["What do you think?", "Tell me more!", "Great start!"]
            }, None
    
    def _enhance_question_with_context(self, question_data, tracker):
        """Add encouraging context based on student's progress"""
        base_question = question_data['question']
        difficulty = question_data['difficulty']
        
        # Add encouraging prefix based on progress
        if tracker.consecutive_successes >= 2:
            if difficulty > tracker.current_difficulty - 1:  # Advanced to new level
                prefix = f"🎉 Excellent progress! You've mastered Level {difficulty-1}. Ready for a new challenge?\n\n"
            else:
                prefix = f"🌟 You're doing great! Let's continue building your skills.\n\n"
        elif tracker.consecutive_failures >= 2:
            prefix = f"💪 Let's approach this step by step. Remember, every expert was once a beginner!\n\n"
        elif tracker.total_attempts == 0:
            prefix = f"🚀 Welcome to your learning journey with {tracker.topic}! Let's start with the basics.\n\n"
        else:
            prefix = f"📚 Level {difficulty} Challenge:\n\n"
        
        return {
            'question': prefix + base_question,
            'difficulty': difficulty,
            'concepts': question_data['concepts'],
            'expected_answer': question_data['expected_answer'],
            'hint_progression': question_data['hint_progression'],
            'tracker_info': {
                'current_level': tracker.current_difficulty,
                'success_rate': tracker.calculate_success_rate(),
                'consecutive_successes': tracker.consecutive_successes,
                'mastery_percentage': tracker.mastery_percentage
            }
        }
    
    def process_student_response(self, student_message, question_data, tracker, session):
        """Process student response and update difficulty tracking"""
        try:
            from .models import QuestionAttempt
            
            # Analyze if response is correct
            is_correct = self._evaluate_response(student_message, question_data)
            confidence_change = self._assess_confidence_change(student_message)
            
            # Update difficulty tracker
            new_difficulty = tracker.update_performance(is_correct, confidence_change)
            
            # Record the attempt
            attempt = QuestionAttempt.objects.create(
                student=tracker.student,
                chat_session=session,
                difficulty_tracker=tracker,
                question_text=question_data['question'],
                difficulty_level=question_data['difficulty'],
                topic=tracker.topic,
                student_answer=student_message,
                result='correct' if is_correct else 'incorrect',
                understanding_demonstrated=self._analyze_understanding(student_message, question_data),
                misconceptions_identified=self._identify_misconceptions(student_message, question_data) if not is_correct else ""
            )
            
            # Generate appropriate response
            if is_correct:
                response = self._generate_success_response(tracker, new_difficulty, question_data)
            else:
                response = self._generate_guidance_response(student_message, question_data, tracker)
            
            return response, new_difficulty != question_data['difficulty']
            
        except Exception as e:
            print(f"❌ Response processing failed: {e}")
            return "Great thinking! What's your next thought?", False
    
    def _evaluate_response(self, student_message, question_data):
        """Evaluate if student response demonstrates understanding"""
        msg_lower = student_message.lower().strip()
        expected = question_data['expected_answer'].lower()
        
        # Check for exact matches
        if expected in msg_lower:
            return True
        
        # Check for key concepts based on question type
        if 'algebra' in str(question_data['concepts']):
            # Look for algebraic understanding
            if any(phrase in msg_lower for phrase in ['x = ', 'x equals', 'x is']):
                # Extract number from response
                import re
                numbers = re.findall(r'\d+', msg_lower)
                if numbers:
                    # Check if the number appears in expected answer
                    expected_numbers = re.findall(r'\d+', expected)
                    return any(num in expected_numbers for num in numbers)
            
            # Look for process understanding
            if any(phrase in msg_lower for phrase in ['subtract', 'divide', 'add', 'multiply', 'isolate']):
                return True
        
        elif 'fraction' in str(question_data['concepts']):
            # Look for fraction notation or understanding
            if any(phrase in msg_lower for phrase in ['/', 'fraction', 'pieces', 'parts']):
                return True
        
        # Check for conceptual understanding
        if any(phrase in msg_lower for phrase in ['variable', 'unknown', 'represents', 'stands for']):
            return True
        
        return False
    
    def _assess_confidence_change(self, student_message):
        """Assess change in student confidence from their response"""
        msg_lower = student_message.lower()
        
        # Positive indicators
        if any(phrase in msg_lower for phrase in ['i think', 'i believe', 'probably', 'maybe']):
            return 0.05
        elif any(phrase in msg_lower for phrase in ['i know', 'definitely', 'sure', 'certain']):
            return 0.1
        elif any(phrase in msg_lower for phrase in ['confused', 'don\'t know', 'unsure', 'help']):
            return -0.05
        
        return 0
    
    def _generate_success_response(self, tracker, new_difficulty, question_data):
        """Generate encouraging response for correct answers"""
        if new_difficulty > question_data['difficulty']:
            return f"🎉 Outstanding! You've mastered Level {question_data['difficulty']}! Your understanding is growing beautifully. Ready to advance to Level {new_difficulty}?"
        else:
            success_messages = [
                "🌟 Excellent! You really understand this concept!",
                "✨ Perfect! Your thinking is spot on!",
                "🎯 Great job! You've got the right idea!",
                "💫 Wonderful! That shows real understanding!",
                "🏆 Fantastic! You're really getting this!"
            ]
            return random.choice(success_messages) + f" Want to try another Level {question_data['difficulty']} challenge?"
    
    def _generate_guidance_response(self, student_message, question_data, tracker):
        """Generate Socratic guidance for incorrect or incomplete responses"""
        try:
            # Use AI for contextual guidance if available
            if self.rag_processor.llm:
                ai_response = self.get_ai_socratic_response(
                    student_message,
                    tracker.topic,
                    tracker.current_difficulty * 20,  # Convert to percentage
                    f"Student at difficulty level {tracker.current_difficulty}, {tracker.consecutive_failures} consecutive struggles"
                )
                if ai_response and len(ai_response) > 10:
                    return ai_response
        except:
            pass
        
        # Fallback to hint progression
        hints = question_data.get('hint_progression', [])
        hint_index = min(tracker.consecutive_failures, len(hints) - 1)
        
        encouraging_starters = [
            "That's a good start! ",
            "I can see you're thinking about this! ",
            "You're on an interesting path! ",
            "Great effort! "
        ]
        
        return random.choice(encouraging_starters) + hints[hint_index]
    
    def _analyze_understanding(self, student_message, question_data):
        """Analyze what understanding the student demonstrated"""
        understanding_indicators = []
        msg_lower = student_message.lower()
        
        if any(concept in msg_lower for concept in question_data.get('concepts', [])):
            understanding_indicators.append(f"Demonstrated understanding of {question_data['concepts']}")
        
        if any(phrase in msg_lower for phrase in ['because', 'since', 'so', 'therefore']):
            understanding_indicators.append("Shows reasoning and justification")
        
        if '?' in student_message:
            understanding_indicators.append("Asking clarifying questions")
        
        return "; ".join(understanding_indicators) if understanding_indicators else "Basic engagement"
    
    def _identify_misconceptions(self, student_message, question_data):
        """Identify potential misconceptions from incorrect responses"""
        misconceptions = []
        msg_lower = student_message.lower()
        
        # Common algebra misconceptions
        if 'algebra' in str(question_data['concepts']):
            if 'add' in msg_lower and 'both sides' not in msg_lower:
                misconceptions.append("May not understand equation balance")
            if any(phrase in msg_lower for phrase in ['x is the answer', 'x means']):
                misconceptions.append("May confuse variable with answer")
        
        # Common fraction misconceptions
        if 'fraction' in str(question_data['concepts']):
            if 'bigger' in msg_lower and 'denominator' in msg_lower:
                misconceptions.append("May think larger denominator means larger fraction")
        
        return "; ".join(misconceptions) if misconceptions else ""
    
    def _create_educational_knowledge_base(self):
        """Create a knowledge base of educational content for RAG"""
        knowledge_content = """
        SOCRATIC METHOD IN MATHEMATICS EDUCATION:
        The Socratic method involves asking questions to help students discover answers themselves rather than providing direct answers.
        Key principles: Lead with questions, encourage exploration, build on student responses, celebrate discoveries.
        
        ALGEBRAIC EQUATIONS TEACHING:
        When teaching algebra, start with concrete examples like 2x + 5 = 11.
        Guide students to understand that x represents an unknown value.
        Help them discover the process: isolate the variable by performing inverse operations.
        Step 1: Subtract 5 from both sides: 2x = 6
        Step 2: Divide by 2: x = 3
        Always encourage verification by substituting back into the original equation.
        
        COMMON STUDENT MISCONCEPTIONS:
        - Students often want to jump to the answer without understanding the process
        - Many don't understand why we perform the same operation on both sides
        - Students may confuse the variable with the coefficient
        - Verification is often skipped but is crucial for understanding
        
        EFFECTIVE QUESTIONING STRATEGIES:
        - "What do you think x represents?" - builds conceptual understanding
        - "What operation would help us isolate x?" - guides procedural thinking
        - "How can we check if our answer is correct?" - encourages verification
        - "What pattern do you notice?" - develops mathematical reasoning
        
        FRACTION CONCEPTS:
        Fractions represent parts of a whole. Use concrete examples like pizza slices.
        Numerator = number of parts taken, Denominator = total number of parts
        Visual representations help students understand fraction relationships.
        
        GEOMETRY BASICS:
        Connect geometric concepts to real-world objects students can observe.
        Start with basic shapes and properties before moving to calculations.
        Encourage students to identify shapes in their environment.
        """
        
        try:
            # Create vector store from educational knowledge
            vector_store = self.rag_processor.create_vector_store(
                knowledge_content, 
                "educational_knowledge_base"
            )
            return vector_store
        except Exception as e:
            print(f"⚠️ Could not create knowledge base: {e}")
            return None
    
    def get_ai_socratic_response(self, student_message, topic, current_understanding, conversation_history=""):
        """Use AI to generate concise Socratic response based on student input and context"""
        print(f"🔍 AI Response Debug - Topic: {topic}, Understanding: {current_understanding}%")
        print(f"🔍 Student Message: '{student_message}'")
        
        if not self.rag_processor.llm:
            print("❌ RAG processor LLM not available - using fallback")
            return self._get_basic_socratic_response(student_message, current_understanding)
        
        try:
            # Create VERY specific prompt for algebraic equations
            if "Algebraic Equations" in topic or "equation" in topic.lower():
                socratic_prompt = f"""You are tutoring algebraic equations. Student said: "{student_message}"

CONTEXT: Working with equation 2x + 5 = 11 or similar linear equations.

RULES:
1. MAX 15 words
2. Stay focused on THIS specific equation: 2x + 5 = 11
3. If student gave correct answer, celebrate and ask verification
4. If student confused, guide them back to the basic steps
5. NEVER introduce new variables (y, z, etc.)
6. NEVER ask about negative numbers unless relevant

GOOD responses:
- Student says "x=3": "Excellent! How can we check if x=3 is correct?"
- Student says "7-2=5": "Perfect! You verified the answer! Let's try another equation."
- Student confused: "Let's go back to 2x + 5 = 11. What does x represent?"

Generate ONE brief question about 2x + 5 = 11:"""
            else:
                # General prompt for other topics
                socratic_prompt = f"""You are a Socratic math tutor. Student said: "{student_message}" about {topic}.

RULES:
1. MAX 15 words
2. Ask ONE guiding question
3. Stay on topic: {topic}
4. Guide discovery, don't give answers

Generate ONE brief question:"""
            
            print(f"🔍 Sending focused prompt to AI...")
            # Get AI response
            ai_response = self.rag_processor.llm.invoke(socratic_prompt)
            print(f"✅ AI Raw Response: '{ai_response}'")
            
            # Clean and validate response
            if isinstance(ai_response, str):
                response = ai_response.strip()
            else:
                response = str(ai_response).strip()
            
            # Remove quotes if AI added them
            if response.startswith('"') and response.endswith('"'):
                response = response[1:-1]
            
            print(f"✅ Cleaned Response: '{response}'")
            
            # Ensure response is brief (under 80 characters for better focus)
            if len(response) > 80:
                # Extract the first sentence if too long
                sentences = response.split('.')
                response = sentences[0] + '?' if not sentences[0].endswith('?') else sentences[0]
                print(f"✅ Shortened Response: '{response}'")
            
            # Validate response quality
            if self._is_confusing_response(response, topic):
                print("⚠️ Response seems confusing, using fallback")
                return self._get_focused_fallback(student_message, topic)
            
            return response
            
        except Exception as e:
            print(f"❌ AI Socratic response failed: {e}")
            return self._get_focused_fallback(student_message, topic)
    
    def _is_confusing_response(self, response, topic):
        """Check if AI response is confusing or off-topic"""
        response_lower = response.lower()
        
        # Flag confusing patterns
        confusing_patterns = [
            "what would happen to 2x if x were equal to -5",
            "is the value of y",
            "what do you think happens to the value",
            "simply added to or subtracted from",
            "when we subtract a positive number"
        ]
        
        for pattern in confusing_patterns:
            if pattern in response_lower:
                return True
        
        # Check for random variable introduction
        if "Algebraic Equations" in topic:
            # Should not introduce y, z, etc. when working with x
            unwanted_vars = ['y ', 'z ', 'a ', 'b ', 'c ']
            for var in unwanted_vars:
                if var in response_lower:
                    return True
        
        return False
    
    def _get_focused_fallback(self, student_message, topic):
        """Get focused fallback response when AI fails"""
        msg_lower = student_message.lower()
        
        if "Algebraic Equations" in topic or "equation" in topic.lower():
            # Check for correct answers
            if any(phrase in msg_lower for phrase in ['x=3', 'x = 3', 'x equals 3']):
                return "🎉 Excellent! You found x = 3! How can we verify this is correct?"
            
            if any(phrase in msg_lower for phrase in ['7-2=5', '6+5=11', '2(3)+5']):
                return "✅ Perfect verification! Ready for the next equation?"
            
            if any(phrase in msg_lower for phrase in ['subtract 5', 'minus 5']):
                return "Great thinking! What do we do with 2x = 6?"
            
            if 'understand' in msg_lower or 'confused' in msg_lower:
                return "Let's start simple. In 2x + 5 = 11, what does 'x' represent?"
            
            # Default for algebraic equations
            return "Think about our equation 2x + 5 = 11. What's the first step to find x?"
        
        # Default fallback
        return "Interesting thinking! Can you tell me more about your approach?"
    
    def _contains_direct_answer(self, response, topic):
        """Check if response contains direct answers (which violates Socratic method)"""
        # Algebra direct answers to avoid
        if 'algebra' in topic.lower():
            direct_answers = ['x = 3', 'x equals 3', 'the answer is', 'solution is', 'x is 3']
            return any(answer in response.lower() for answer in direct_answers)
        return False
    
    def _get_guiding_question(self, student_message, topic):
        """Generate a guiding question when AI gives too direct an answer"""
        if 'algebra' in topic.lower():
            if any(phrase in student_message.lower() for phrase in ['x = 3', 'x equals 3', '3']):
                return "🎉 You found a value for x! That's excellent thinking! Now, how could we verify that x = 3 is actually correct?"
            else:
                return "What do you think would be a good first step to solve this equation?"
        return "What's your thinking here? What do you notice about this problem?"
    
    def _get_basic_socratic_response(self, student_message, understanding_level):
        """Fallback Socratic response when AI is unavailable"""
        msg_lower = student_message.lower()
        
        if any(phrase in msg_lower for phrase in ['x = 3', 'x equals 3', '3']):
            return "🎉 Excellent! You found that x = 3! How could we check if this answer is correct?"
        elif any(phrase in msg_lower for phrase in ['confused', 'don\'t understand', 'help']):
            return "That's okay! Let's break this down. What's the first thing you notice about this equation?"
        elif understanding_level < 30:
            return "You're thinking about this! What do you think the 'x' represents in this equation?"
        else:
            return "Good thinking! What would be your next step?"
    
    def analyze_student_response(self, message_content):
        """Analyze student message for understanding and sentiment"""
        blob = TextBlob(message_content)
        
        # Basic sentiment analysis
        sentiment = blob.sentiment.polarity
        
        # Check for confusion indicators
        confusion_keywords = ['confused', 'don\'t understand', 'help', 'stuck', 'don\'t know', 'what', 'how']
        shows_confusion = any(keyword in message_content.lower() for keyword in confusion_keywords)
        
        # Check for discovery indicators
        discovery_keywords = ['oh', 'ah', 'i see', 'now i understand', 'that makes sense', 'got it']
        shows_discovery = any(keyword in message_content.lower() for keyword in discovery_keywords)
        
        # Check if contains question
        contains_question = '?' in message_content
        
        # Determine understanding level
        if shows_discovery:
            understanding_level = 'good'
        elif shows_confusion:
            understanding_level = 'confused'
        elif sentiment > 0.1:
            understanding_level = 'partial'
        else:
            understanding_level = 'confused'
        
        return {
            'sentiment_score': sentiment,
            'understanding_level': understanding_level,
            'contains_question': contains_question,
            'shows_confusion': shows_confusion,
            'shows_discovery': shows_discovery
        }
    
    def generate_socratic_response(self, student_message, context, hint_level=1, session=None):
        """Generate AI-powered Socratic response that guides without answering directly"""
        
        # Get conversation history for context
        conversation_history = ""
        if session:
            try:
                recent_messages = ConversationMessage.objects.filter(
                    session=session
                ).order_by('-timestamp')[:3]
                history_parts = []
                for msg in reversed(recent_messages):
                    history_parts.append(f"Student: {msg.student_message}")
                    history_parts.append(f"Tutor: {msg.tutor_response}")
                conversation_history = " | ".join(history_parts)
            except:
                conversation_history = ""
        
        # Check if student is showing understanding progression
        if session and 'algebra' in session.topic.lower():
            # Try AI response first, fallback to specific progression if needed
            try:
                ai_response = self.get_ai_socratic_response(
                    student_message, 
                    session.topic, 
                    session.current_understanding_level,
                    conversation_history
                )
                
                # If AI gives good Socratic response, use it
                if ai_response and len(ai_response) > 10:
                    return ai_response
                else:
                    # Fallback to specific algebra progression
                    return self._handle_algebra_progression(student_message, session, hint_level)
            except:
                return self._handle_algebra_progression(student_message, session, hint_level)
                
        elif session and 'fraction' in session.topic.lower():
            # Try AI response first for fractions
            try:
                ai_response = self.get_ai_socratic_response(
                    student_message, 
                    session.topic, 
                    session.current_understanding_level,
                    conversation_history
                )
                
                if ai_response and len(ai_response) > 10:
                    return ai_response
                else:
                    return self._handle_fraction_progression(student_message, session, hint_level)
            except:
                return self._handle_fraction_progression(student_message, session, hint_level)
        
        # For general topics or when session is not available, use AI
        try:
            topic = session.topic if session else context.get('topic', 'mathematics')
            understanding_level = session.current_understanding_level if session else 50
            
            ai_response = self.get_ai_socratic_response(
                student_message, 
                topic, 
                understanding_level,
                conversation_history
            )
            
            if ai_response and len(ai_response) > 10:
                return ai_response
        except Exception as e:
            print(f"⚠️ AI Socratic response failed, using fallback: {e}")
        
        # Fallback to traditional responses if AI fails
        return self._get_traditional_socratic_response(hint_level)
    
    def _get_traditional_socratic_response(self, hint_level):
        """Traditional Socratic responses when AI is unavailable"""
        discovery_phrases = [
            "What do you notice about...",
            "How might you approach...", 
            "What happens when you...",
            "Can you think of a way to...",
            "What pattern do you see in...",
            "How does this relate to...",
            "What would happen if...",
        ]
        
        if hint_level == 1:
            responses = [
                f"That's a great start! {random.choice(discovery_phrases)} the next step?",
                f"Interesting thinking! {random.choice(discovery_phrases)} this further?",
                f"You're thinking well about this. {random.choice(discovery_phrases)} what might come next?"
            ]
        elif hint_level == 2:
            responses = [
                f"Let's think about this together. When you look at the problem, what's the first thing you notice?",
                f"Good effort! What do you think would happen if you tried a different approach?", 
                f"You're on an interesting path. What tools or methods might help you here?"
            ]
        elif hint_level == 3:
            responses = [
                f"Think of this like {random.choice(['building blocks', 'a puzzle', 'a recipe'])} - what's your first step?",
                f"This reminds me of other problems where we break things down. How might you simplify this?",
                f"Consider this like {random.choice(['organizing your room', 'following directions', 'solving a mystery'])} - where do you start?"
            ]
        elif hint_level == 4:
            responses = [
                f"Let's break this down together. What information do you have to work with?",
                f"Good thinking! What if we tackled this one piece at a time? What's one thing you're sure about?",
                f"You're doing well. Let's identify what we know and what we need to find out."
            ]
        else:  # hint_level == 5
            responses = [
                f"You're working hard on this! Let's explore it step by step. What's the very first thing the problem is asking?",
                f"I can see you're thinking deeply. What happens when you focus on just one part of this?",
                f"You're being thoughtful about this. What would you try if you knew you couldn't be wrong?"
            ]
        
        return random.choice(responses)
    
    def _handle_algebra_progression(self, student_message, session, hint_level):
        """Handle algebra-specific progression with enhanced AI"""
        msg_lower = student_message.lower()
        
        # Check for correct answer recognition - x = 3
        if any(phrase in msg_lower for phrase in ['x=3', 'x = 3', 'x equals 3', 'x is 3', 'x equals three']):
            # Update understanding level for correct answer
            session.current_understanding_level = min(session.current_understanding_level + 20, 100)
            session.save()
            
            # Use AI for celebration response
            try:
                ai_prompt = f"""Student correctly answered x = 3. Generate a brief (15 words max) celebration and ask how to verify. Be encouraging and Socratic."""
                ai_response = self.rag_processor.llm.invoke(ai_prompt)
                if ai_response and len(str(ai_response)) < 100:
                    return str(ai_response).strip()
            except:
                pass
            
            return "🎉 Excellent! You found x = 3! How can we verify this is correct?"
        
        # Check for verification understanding
        elif any(phrase in msg_lower for phrase in ['2(3) + 5', '6 + 5', '= 11', 'equals 11', 'substitute', 'check']):
            session.current_understanding_level = min(session.current_understanding_level + 25, 100)
            session.save()
            
            # Use AI for mastery response
            try:
                ai_prompt = f"""Student verified x=3 correctly. Generate brief (20 words max) celebration and offer next challenge. Be encouraging."""
                ai_response = self.rag_processor.llm.invoke(ai_prompt)
                if ai_response and len(str(ai_response)) < 120:
                    return str(ai_response).strip()
            except:
                pass
            
            return "🎯 Perfect! You've mastered verification! Ready for: 3x - 7 = 14?"
        
        # Check for process understanding
        elif any(phrase in msg_lower for phrase in ['subtract 5', 'minus 5', '2x = 6', 'take away 5', 'move', 'other side']):
            session.current_understanding_level = min(session.current_understanding_level + 10, 100)
            session.save()
            
            # Use AI for process guidance
            try:
                ai_prompt = f"""Student understands moving +5. Generate brief (15 words max) encouragement and ask about next step with 2x = 6."""
                ai_response = self.rag_processor.llm.invoke(ai_prompt)
                if ai_response and len(str(ai_response)) < 80:
                    return str(ai_response).strip()
            except:
                pass
            
            return "Excellent! Now you have 2x = 6. What gets x by itself?"
        
        elif any(phrase in msg_lower for phrase in ['divide by 2', '/2', 'half', 'divide']):
            session.current_understanding_level = min(session.current_understanding_level + 15, 100)
            session.save()
            return "Perfect! Dividing by 2 gives us x = 3. How can we check this?"
        
        # Try AI response for other cases
        try:
            ai_prompt = f"""Student said: "{student_message}" about algebra. Generate ONE brief Socratic question (15 words max) to guide them. No direct answers."""
            ai_response = self.rag_processor.llm.invoke(ai_prompt)
            if ai_response and len(str(ai_response)) < 100:
                return str(ai_response).strip()
        except Exception as e:
            print(f"⚠️ AI algebra response failed: {e}")
        
        return self._get_general_response(hint_level)
    
    def _handle_fraction_progression(self, student_message, session, hint_level):
        """Handle fraction-specific progression"""
        msg_lower = student_message.lower()
        
        if any(phrase in msg_lower for phrase in ['3/8', '3 out of 8', 'three eighths']):
            return "Perfect! You wrote 3/8 - that's exactly right! The 3 tells us how many pieces you took, and the 8 tells us how many pieces the whole pizza was cut into. What about the pizza that's left?"
        
        elif any(phrase in msg_lower for phrase in ['5/8', '5 out of 8', 'five eighths']):
            return "Excellent! So you ate 3/8 and 5/8 is left. Notice something interesting: 3/8 + 5/8 = 8/8 = 1 whole pizza! What do you think happens when fractions have the same denominator?"
        
        # Continue fraction progression...
        return self._get_general_response(hint_level)
    
    def _get_general_response(self, hint_level):
        """Get general Socratic response based on hint level"""
        if hint_level <= 2:
            return random.choice([
                "That's interesting! What do you think the next step might be?",
                "Good thinking! How might you approach this differently?",
                "I can see you're processing this. What's your next thought?",
                "Hmm, tell me more about your thinking here!",
                "That's a start! What could you try next?",
                "Interesting approach! Where does that lead you?"
            ])
        elif hint_level <= 4:
            return random.choice([
                "Let's think about this step by step. What's one small thing you could try?",
                "You're on the right path. What would happen if you tried breaking this down?",
                "Good effort! What's one thing you feel confident about here?",
                "You're making progress! What comes to mind first?",
                "Let's explore this together. What's your instinct telling you?",
                "That's thoughtful! How might you build on that idea?"
            ])
        else:  # hint_level >= 5
            return random.choice([
                "You're working hard on this! Let's explore it step by step. What's the very first thing the problem is asking?",
                "I can see you're thinking deeply. What happens when you focus on just one part of this?",
                "You're being thoughtful about this. What would you try if you knew you couldn't be wrong?",
                "Let's break this down into smaller pieces. What's one thing you notice?",
                "No pressure - just explore! What stands out to you in this problem?",
                "You're learning! What's one thing that makes sense to you here?"
            ])
    
    def generate_encouragement(self, understanding_level, discovery_made=False):
        """Generate encouraging response based on student's state"""
        if discovery_made:
            return random.choice([
                "Excellent! You figured that out yourself!",
                "Yes! That's exactly the kind of thinking that leads to understanding!",
                "Wonderful discovery! How does that feel?",
                "Perfect! You just had a breakthrough moment!"
            ])
        elif understanding_level == 'good':
            return random.choice([
                "You're understanding this really well!",
                "Great thinking! You're making excellent progress!",
                "I can see your understanding growing!",
                "Fantastic! You're really getting this!"
            ])
        elif understanding_level == 'partial':
            return random.choice([
                "You're on the right track! Keep thinking!",
                "Good start! What's your next thought?",
                "Interesting idea! How might you develop it further?",
                "You're making progress! What comes next?"
            ])
        else:  # confused
            return random.choice([
                "That's okay! Confusion means you're thinking deeply!",
                "No worries! Let's explore this together!",
                "It's perfectly fine to feel uncertain - that's how learning happens!",
                "Good! Asking questions shows you're engaged!"
            ])


class ConversationStarter:
    """AI-enhanced conversation starter that generates contextual questions"""
    
    def __init__(self):
        self.rag_processor = ComprehensiveRAGProcessor()
    
    def get_ai_enhanced_starter(self, topic, subject='math', student_level=0):
        """Generate concise AI-enhanced conversation starter"""
        try:
            if self.rag_processor.llm:
                prompt = f"""Create a brief, engaging introduction for learning {topic} in {subject}.

REQUIREMENTS:
- Welcome message (10-15 words)
- ONE simple starting question (10-15 words) 
- Encouraging and curious tone
- Socratic approach (guide discovery)
- Student level: {student_level}%

Format:
Welcome message
Starting question

Example:
Welcome to Algebraic Equations! Let's discover together!
What do you think 'x' means in: x + 3 = 7?"""
                
                ai_response = self.rag_processor.llm.invoke(prompt)
                if ai_response and len(str(ai_response)) > 30:
                    response = str(ai_response).strip()
                    # Ensure it's not too long
                    if len(response) > 200:
                        lines = response.split('\n')
                        response = '\n'.join(lines[:2])
                    return response
        except Exception as e:
            print(f"⚠️ AI starter generation failed: {e}")
        
        # Fallback to static starters
        return self.get_topic_starter(topic, subject)
    
    @staticmethod
    def get_topic_starter(topic, subject='math'):
        """Generate an engaging opening question for a topic"""
        if subject.lower() == 'math':
            if 'algebra' in topic.lower():
                return "Welcome to your learning journey with Algebraic Equations! I'm here to guide you through discovery, not give you answers. Let's explore together!\n\nLet's start with a simple equation: 2x + 5 = 11. Don't worry about solving it yet - just tell me, what do you think the 'x' represents? What could it be?"
            elif 'geometry' in topic.lower():
                return "Welcome to the fascinating world of Geometry! Let's discover shapes and space together!\n\nLook around you right now - what shapes do you see? How do you think mathematicians describe and work with these shapes?"
            elif 'fraction' in topic.lower():
                return "Welcome to Fractions - where parts become whole understanding! Let's explore together!\n\nImagine you have a pizza cut into 8 slices and you eat 3 of them. How would you describe what you ate? What about what's left?"
            elif 'equation' in topic.lower():
                return "Welcome to the world of Mathematical Equations! Let's discover the beauty of balance together!\n\nThink of equations like balanced scales. What do you think happens when we add or subtract the same thing from both sides?"
            else:
                return f"Welcome to your mathematical journey with {topic}! I'm here to guide your discovery!\n\nWhat's one math concept you've always been curious about? Let's explore it together!"
        else:
            return f"Welcome to exploring {topic}! Let's discover together!\n\nWhat interests you most about {topic}? What would you like to discover today?"
    
    def get_ai_follow_up_questions(self, topic, understanding_level, recent_progress=""):
        """Generate AI-powered follow-up questions based on progress"""
        try:
            if self.rag_processor.llm:
                prompt = f"""
You are a Socratic tutor generating the next challenge for a student.

CONTEXT:
- Topic: {topic}
- Student understanding level: {understanding_level}%
- Recent progress: {recent_progress}

INSTRUCTIONS:
- Generate 3-4 progressive questions/challenges appropriate for their level
- If level < 30: Focus on foundational concepts and simple examples
- If level 30-60: Introduce intermediate challenges and connections
- If level > 60: Provide advanced problems and pattern recognition
- Always use Socratic questioning (never give direct answers)
- Make questions engaging and discovery-oriented
- Include emojis to make it exciting

Generate follow-up questions as a Python list:
                """
                
                ai_response = self.rag_processor.llm.invoke(prompt)
                if ai_response and len(str(ai_response)) > 20:
                    response_text = str(ai_response).strip()
                    # Try to extract questions from response
                    if '[' in response_text and ']' in response_text:
                        return response_text
                    else:
                        # Convert to list format if not already
                        lines = [line.strip() for line in response_text.split('\n') if line.strip()]
                        return lines[:4]  # Return first 4 questions
        except Exception as e:
            print(f"⚠️ AI follow-up generation failed: {e}")
        
        # Fallback to static questions
        return self.get_follow_up_questions(topic, understanding_level)
    def get_follow_up_questions(topic, understanding_level):
        """Get appropriate follow-up questions based on topic and understanding"""
        if 'algebra' in topic.lower():
            if understanding_level < 30:
                return [
                    "In 2x + 5 = 11, what operation do you think we should do first?",
                    "If we want to get 'x' by itself, what's getting in the way?",
                    "What happens to the equation if we subtract 5 from both sides?"
                ]
            elif understanding_level < 60:
                return [
                    "Now that we have 2x = 6, how can we find what just 'x' equals?",
                    "If 2 times something equals 6, what could that something be?",
                    "Can you check your answer by putting it back into the original equation?"
                ]
            else:
                return [
                    "🚀 Excellent! Let's try a slightly different one: 3x - 4 = 8. What's your approach?",
                    "🌟 Ready for a new challenge? How would you solve x/2 + 3 = 7?",
                    "🎯 You're becoming an algebra expert! Try this: 4x + 2 = 18. What's your strategy?",
                    "✨ Let's explore: What patterns do you notice when solving these equations?",
                    "🎉 Fantastic progress! Here's another: 5x - 3 = 12. Can you solve it?",
                    "🏆 You're on fire! Try: 2x + 7 = 15. What do you do first?"
                ]
        elif 'fraction' in topic.lower():
            if understanding_level < 30:
                return [
                    "If you ate 3 out of 8 pizza slices, how would you write that as a fraction?",
                    "What does the number on top (numerator) tell us?",
                    "What does the number on bottom (denominator) tell us?"
                ]
            elif understanding_level < 60:
                return [
                    "If you have 1/2 of a pizza and your friend has 1/4, who has more?",
                    "How could you add 1/4 + 1/4? What would you get?",
                    "What happens when you add fractions with the same denominator?"
                ]
            else:
                return [
                    "How would you add 1/3 + 1/6? What do you need to do first?",
                    "Can you multiply 2/3 × 1/4? What pattern do you see?",
                    "When might you use fractions in real life?"
                ]
        
        return [
            "What aspect of this topic interests you most?",
            "How do you think this connects to things you already know?",
            "What questions do you have about this?"
        ]


class HintEngine:
    """Manages progressive hint system"""
    
    def __init__(self):
        self.max_hint_level = 5
        self.hint_descriptions = {
            1: "Gentle nudge - encourages thinking",
            2: "Leading question - points in right direction", 
            3: "Analogy - provides relatable comparison",
            4: "Step breakdown - breaks down the process",
            5: "Guided discovery - direct but gentle guidance"
        }
    
    def get_next_hint_level(self, current_level, student_confusion_count):
        """Determine next hint level based on student progress"""
        if student_confusion_count > 2:
            return min(current_level + 2, self.max_hint_level)
        elif student_confusion_count > 0:
            return min(current_level + 1, self.max_hint_level)
        else:
            return current_level
    
    def should_escalate_hint(self, conversation_messages, current_hint_level):
        """Determine if hint level should be escalated"""
        if len(conversation_messages) < 3:
            return False
        
        recent_messages = conversation_messages[-3:]
        confusion_count = sum(1 for msg in recent_messages if msg.shows_confusion)
        
        return confusion_count >= 2 and current_hint_level < self.max_hint_level


class StudentQuestionProcessor:
    """Handles when students ask direct questions - redirects to discovery"""
    
    @staticmethod
    def process_direct_question(question, context):
        """Convert direct questions into discovery opportunities"""
        redirects = [
            "That's a great question! Instead of me telling you, what do you think might happen if you tried...?",
            "I love that you're asking questions! What's your hypothesis about this?",
            "Excellent question! What have you observed so far that might give you a clue?",
            "Great thinking! What would you try first to figure this out?",
            "That shows good curiosity! How might you investigate this yourself?",
        ]
        
        return random.choice(redirects)
    
    @staticmethod
    def identify_question_type(question):
        """Identify the type of question being asked"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['what is', 'what are', 'what does']):
            return 'definition'
        elif any(word in question_lower for word in ['how do', 'how to', 'how can']):
            return 'procedure'
        elif any(word in question_lower for word in ['why', 'why does', 'why is']):
            return 'explanation'
        elif any(word in question_lower for word in ['when', 'where']):
            return 'context'
        else:
            return 'general'


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_interactive_learning_session(request):
    """
    Start Interactive Learning session using ONLY questions from uploaded teacher documents
    
    POST /api/interactive/start/
    {
        "document_id": 38  // Optional - if not provided, will auto-select document with most questions
    }
    """
    print("🎓 Starting document-based Interactive Learning session...")
    
    try:
        from .models import Document, QuestionBank, ChatSession, ChatInteraction
        
        document_id = request.data.get('document_id')
        
        # If no document specified, find the document with the most questions
        if not document_id:
            # For students - get documents from any teacher
            # For teachers - get their own documents
            if request.user.role == 'teacher':
                documents_query = Document.objects.filter(uploaded_by=request.user)
            else:
                # Students can access all teacher documents
                documents_query = Document.objects.filter(uploaded_by__role='teacher')
            
            # Find document with most questions
            best_document = None
            max_questions = 0
            
            for doc in documents_query:
                questions_count = QuestionBank.objects.filter(
                    document=doc,
                    is_generated=True
                ).count()
                if questions_count > max_questions:
                    max_questions = questions_count
                    best_document = doc
            
            if not best_document:
                return Response({
                    'error': 'No documents with generated questions found',
                    'message': 'Please ask your teacher to upload and process documents first.'
                }, status=404)
            
            document = best_document
        else:
            # Use specified document
            try:
                document = Document.objects.get(id=document_id)
            except Document.DoesNotExist:
                return Response({'error': 'Document not found'}, status=404)
        
        # Get exactly 10 questions from the document (mix of all difficulty levels)
        questions_query = QuestionBank.objects.filter(
            document=document,
            is_generated=True
        ).order_by('difficulty_level', '?')  # Random order within difficulty levels
        
        questions = list(questions_query[:10])  # Exactly 10 questions
        
        if len(questions) < 10:
            return Response({
                'error': f'Not enough questions in document. Found {len(questions)}, need 10.',
                'message': f'Document "{document.title}" only has {len(questions)} questions. Need at least 10.'
            }, status=400)
        
        # Create interactive learning session
        session = ChatSession.objects.create(
            student=request.user,
            topic=f"Interactive Learning: {document.title}",
            session_type='interactive_learning',
            total_questions=10,
            current_question_index=0
        )
        
        # Store question IDs and document info
        session.set_session_metadata({
            'document_id': document.id,
            'question_ids': [q.id for q in questions],
            'is_document_based': True,
            'hints_used': {},  # Track hints per question: {question_id: hint_count}
            'max_hints_per_question': 3
        })
        session.save()
        
        # Get first question
        first_question = questions[0]
        
        # Create initial interaction
        welcome_message = f"🎓 Welcome to Interactive Learning!\n\n📚 We'll work through 10 questions from '{document.title}' together.\n\n❓ I'll guide you step by step, and you can ask for up to 3 hints per question if needed.\n\nLet's start with Question 1:\n\n{first_question.question_text}\n\nA) {first_question.option_a}\nB) {first_question.option_b}\nC) {first_question.option_c}\nD) {first_question.option_d}"
        
        ChatInteraction.objects.create(
            student=request.user,
            question="Started Interactive Learning session",
            answer=welcome_message,
            topic="Interactive Learning",
            document=document
        )
        
        return Response({
            'session_id': session.id,
            'document_title': document.title,
            'welcome_message': welcome_message,
            'total_questions': 10,
            'current_question': 1,
            'current_question_data': {
                'id': first_question.id,
                'question': first_question.question_text,
                'options': {
                    'A': first_question.option_a,
                    'B': first_question.option_b,
                    'C': first_question.option_c,
                    'D': first_question.option_d
                },
                'difficulty_level': first_question.difficulty_level
            },
            'hints_available': 3
        }, status=201)
        
    except Exception as e:
        print(f"❌ Error starting interactive learning: {e}")
        return Response({
            'error': str(e),
            'message': 'Failed to start interactive learning session'
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def interactive_learning_chat(request, session_id):
    """
    Handle Interactive Learning chat - supports answers and hint requests
    
    POST /api/interactive/chat/{session_id}/
    {
        "message": "A" or "hint" or "help"
    }
    """
    print(f"🎓 Processing Interactive Learning chat for session {session_id}")
    
    try:
        from .models import ChatSession, QuestionBank, ChatInteraction
        import requests
        import json
        
        # Get session
        try:
            session = ChatSession.objects.get(id=session_id, student=request.user)
        except ChatSession.DoesNotExist:
            return Response({'error': 'Learning session not found'}, status=404)
        
        # Verify this is a document-based session
        metadata = session.get_session_metadata()
        if not metadata.get('is_document_based'):
            return Response({'error': 'This is not a document-based learning session'}, status=400)
        
        student_message = request.data.get('message', '').strip().lower()
        
        if not student_message:
            return Response({'error': 'Message is required'}, status=400)
        
        # Get current question
        question_ids = metadata.get('question_ids', [])
        if session.current_question_index >= len(question_ids):
            return Response({
                'ai_response': "🎉 Congratulations! You've completed all 10 questions!",
                'session_completed': True,
                'progress': {
                    'current': session.current_question_index,
                    'total': 10,
                    'percentage': 100
                }
            })
        
        current_question_id = question_ids[session.current_question_index]
        current_question = QuestionBank.objects.get(id=current_question_id)
        
        # Handle hint requests
        if student_message in ['hint', 'help', 'רמז', 'עזרה']:
            hints_used = metadata.get('hints_used', {})
            question_hints = hints_used.get(str(current_question_id), 0)
            max_hints = metadata.get('max_hints_per_question', 3)
            
            if question_hints >= max_hints:
                hint_response = f"⚠️ You've already used all {max_hints} hints for this question. Try to answer based on what you've learned!"
            else:
                # Generate contextual hint using Ollama - MUST be available
                hint_number = question_hints + 1
                try:
                    ollama_hint = generate_question_hint(current_question, hint_number)
                    
                    # Update hints counter only if hint generation succeeded
                    hints_used[str(current_question_id)] = question_hints + 1
                    metadata['hints_used'] = hints_used
                    session.set_session_metadata(metadata)
                    session.save()
                    
                    hint_response = f"💡 Hint {hint_number}/{max_hints}:\n\n{ollama_hint}\n\nNow try to answer: A, B, C, or D?"
                    
                except Exception as e:
                    # If Ollama fails, return error message instead of generic hint
                    error_msg = str(e)
                    hint_response = f"❌ לא ניתן לספק רמז כרגע: {error_msg}\n\nאנא נסה שוב או המשך לענות על השאלה."
                    
                    # Log the error but don't update hint counter
                    print(f"🚨 Hint generation failed for question {current_question_id}: {e}")
            
            # Save interaction
            ChatInteraction.objects.create(
                student=request.user,
                question=f"Requested hint for question {session.current_question_index + 1}",
                answer=hint_response,
                topic="Interactive Learning - Hint"
            )
            
            return Response({
                'ai_response': hint_response,
                'session_completed': False,
                'progress': {
                    'current': session.current_question_index + 1,
                    'total': 10,
                    'percentage': round(((session.current_question_index + 1) / 10) * 100, 1)
                },
                'hints_used': hints_used.get(str(current_question_id), 0),
                'hints_remaining': max_hints - hints_used.get(str(current_question_id), 0)
            })
        
        # Handle answer submission
        answer = student_message.upper()
        if answer not in ['A', 'B', 'C', 'D']:
            return Response({
                'ai_response': "Please provide your answer as A, B, C, or D. You can also type 'hint' if you need help!",
                'session_completed': False
            })
        
        # Check if answer is correct
        is_correct = (answer == current_question.correct_answer.upper())
        
        # Prepare feedback
        if is_correct:
            feedback = f"✅ Excellent! That's correct!\n\n"
            if current_question.explanation:
                feedback += f"📝 {current_question.explanation}\n\n"
            
            # Move to next question
            session.current_question_index += 1
            session.save()
            
            # Check if there are more questions
            if session.current_question_index < len(question_ids):
                next_question_id = question_ids[session.current_question_index]
                next_question = QuestionBank.objects.get(id=next_question_id)
                
                feedback += f"Question {session.current_question_index + 1}/10:\n\n{next_question.question_text}\n\nA) {next_question.option_a}\nB) {next_question.option_b}\nC) {next_question.option_c}\nD) {next_question.option_d}"
                
                next_question_data = {
                    'id': next_question.id,
                    'question': next_question.question_text,
                    'options': {
                        'A': next_question.option_a,
                        'B': next_question.option_b,
                        'C': next_question.option_c,
                        'D': next_question.option_d
                    },
                    'difficulty_level': next_question.difficulty_level
                }
            else:
                # Session completed
                session.is_completed = True
                session.save()
                feedback += "🎉 Congratulations! You've completed all 10 questions successfully!"
                next_question_data = None
                
        else:
            feedback = f"❌ Not quite right. The correct answer is {current_question.correct_answer}.\n\n"
            if current_question.explanation:
                feedback += f"📝 {current_question.explanation}\n\n"
            
            feedback += "Let's try the next question!\n\n"
            
            # Move to next question even if wrong
            session.current_question_index += 1
            session.save()
            
            # Check if there are more questions
            if session.current_question_index < len(question_ids):
                next_question_id = question_ids[session.current_question_index]
                next_question = QuestionBank.objects.get(id=next_question_id)
                
                feedback += f"Question {session.current_question_index + 1}/10:\n\n{next_question.question_text}\n\nA) {next_question.option_a}\nB) {next_question.option_b}\nC) {next_question.option_c}\nD) {next_question.option_d}"
                
                next_question_data = {
                    'id': next_question.id,
                    'question': next_question.question_text,
                    'options': {
                        'A': next_question.option_a,
                        'B': next_question.option_b,
                        'C': next_question.option_c,
                        'D': next_question.option_d
                    },
                    'difficulty_level': next_question.difficulty_level
                }
            else:
                # Session completed
                session.is_completed = True
                session.save()
                feedback += "🎉 You've completed all 10 questions! Well done!"
                next_question_data = None
        
        # Save interaction
        ChatInteraction.objects.create(
            student=request.user,
            question=f"Answer: {answer}",
            answer=feedback,
            topic="Interactive Learning - Answer"
        )
        
        response_data = {
            'ai_response': feedback,
            'is_correct': is_correct,
            'session_completed': session.is_completed,
            'progress': {
                'current': session.current_question_index,
                'total': 10,
                'percentage': round((session.current_question_index / 10) * 100, 1)
            }
        }
        
        if next_question_data:
            response_data['next_question'] = next_question_data
            response_data['hints_available'] = metadata.get('max_hints_per_question', 3)
        
        return Response(response_data)
        
    except Exception as e:
        print(f"❌ Error in interactive learning chat: {e}")
        return Response({
            'error': str(e),
            'message': 'Failed to process chat message'
        }, status=500)


def generate_question_hint(question, hint_number):
    """Generate contextual hints for questions using Ollama"""
    try:
        # Create different types of hints based on hint number
        if hint_number == 1:
            prompt = f"Provide a gentle hint for this question without giving away the answer:\n\nQuestion: {question.question_text}\n\nOptions:\nA) {question.option_a}\nB) {question.option_b}\nC) {question.option_c}\nD) {question.option_d}\n\nCorrect answer: {question.correct_answer}\n\nProvide a subtle hint that guides thinking but doesn't reveal the answer. Keep it brief and encouraging."
        elif hint_number == 2:
            prompt = f"Provide a more specific hint for this question:\n\nQuestion: {question.question_text}\n\nOptions:\nA) {question.option_a}\nB) {question.option_b}\nC) {question.option_c}\nD) {question.option_d}\n\nCorrect answer: {question.correct_answer}\n\nProvide a clearer hint that narrows down the options or explains key concepts. Still don't give the direct answer."
        else:  # hint_number == 3
            prompt = f"Provide a strong hint for this question:\n\nQuestion: {question.question_text}\n\nOptions:\nA) {question.option_a}\nB) {question.option_b}\nC) {question.option_c}\nD) {question.option_d}\n\nCorrect answer: {question.correct_answer}\n\nProvide a detailed hint that almost points to the answer but still requires the student to make the final connection."
        
        # Call Ollama - MUST be available for hints to work
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3.2",
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60  # Increased timeout to ensure Ollama can respond
            )
            
            if response.status_code == 200:
                data = response.json()
                hint_text = data.get('response', '').strip()
                if hint_text:
                    return hint_text
                else:
                    raise Exception("Empty response from Ollama")
            else:
                raise Exception(f"Ollama returned status code {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"❌ Ollama timeout for hint {hint_number} - taking too long")
            raise Exception("אוללמה לא זמין כרגע. אנא נסה שוב מאוחר יותר.")
        except requests.exceptions.ConnectionError:
            print(f"❌ Ollama connection error for hint {hint_number} - server not running")
            raise Exception("שירות הרמזים לא זמין. אנא פנה למנהל המערכת.")
            
    except Exception as e:
        print(f"❌ Error generating hint: {e}")
        # Re-raise the exception so the view can handle it
        raise Exception(f"לא ניתן לייצר רמז כרגע: {str(e)}")


def get_fallback_hint(hint_number):
    """This function is removed - no fallback hints allowed"""
    pass


# =================== INTERACTIVE CHAT-BASED EXAM SYSTEM ===================
# Replaces Level Test with chat-based exam using open-ended answers

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from interactive_exam_system import (
    InteractiveExamSession, 
    AnswerEvaluator, 
    QuestionGenerator, 
    HintGenerator
)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_interactive_exam(request):
    """
    Start Interactive Chat-Based Exam session using teacher's uploaded documents
    
    POST /api/exam/start/
    {
        "document_id": 38  // Optional - if not provided, will auto-select document
    }
    """
    print("🎓 Starting Interactive Chat-Based Exam...")
    print(f"👤 User: {request.user.username} (role: {request.user.role})")
    print(f"📝 Request data: {request.data}")
    
    try:
        from .models import Document, ChatSession
        
        # Get document to use for questions
        document_id = request.data.get('document_id')
        
        if document_id:
            try:
                document = Document.objects.get(id=document_id)
                # Ensure the document is from a teacher
                if document.uploaded_by.role != 'teacher':
                    return Response({
                        'error': 'Only teacher-uploaded documents can be used for interactive exams'
                    }, status=403)
            except Document.DoesNotExist:
                return Response({'error': 'Document not found'}, status=404)
        else:
            # Auto-select document with most content - ONLY from teachers
            documents = Document.objects.filter(
                uploaded_by__role='teacher',  # Only teacher-uploaded documents
                extracted_text__isnull=False
            ).exclude(extracted_text='').order_by('-created_at')
            
            if not documents.exists():
                return Response({
                    'error': 'No teacher documents with content found. Teachers must upload and process documents first.'
                }, status=400)
            
            document = documents.first()
        
        print(f"📚 Using document: {document.title} ({len(document.extracted_text)} characters)")
        
        # Generate 10 questions from document using Gemini 2.0 Flash
        print("❓ Generating 10 questions from document using Gemini 2.0 Flash...")
        print(f"📄 Document content length: {len(document.extracted_text)} characters")
        try:
            questions = generate_questions_with_gemini(
                document.extracted_text,
                document.title,
                count=10
            )
            print(f"✅ Generated {len(questions)} questions")
            if questions:
                print(f"📝 First question: {questions[0].get('question', 'N/A')[:100]}...")
            else:
                print("⚠️ Questions list is empty!")
        except Exception as e:
            print(f"❌ Error generating questions: {e}")
            import traceback
            traceback.print_exc()
            return Response({
                'error': f'Failed to generate questions: {str(e)}',
                'message': 'Please ensure Gemini API is configured correctly.'
            }, status=500)
        
        # Create exam session
        session = ChatSession.objects.create(
            student=request.user,
            topic=f"Interactive Exam: {document.title}",
            current_question_index=0,
            total_questions=10,
            is_completed=False
        )
        
        # Create interactive exam session
        exam_session = InteractiveExamSession(
            session_id=str(session.id),
            student_id=str(request.user.id),
            document_id=str(document.id)
        )
        exam_session.questions = questions
        exam_session.state = InteractiveExamSession.ASKING
        
        # Initialize first question state
        exam_session.question_states['0'] = {
            'attemptCount': 0,
            'hintsShown': 0,
            'isCorrect': False,
            'answers': [],
            'startTime': timezone.now().isoformat()
        }
        
        # Store session metadata
        metadata = {
            'is_interactive_exam': True,
            'document_id': document.id,
            'document_title': document.title,
            'exam_session': exam_session.to_dict()
        }
        session.set_session_metadata(metadata)
        session.save()
        
        # Validate questions were generated
        if not questions or len(questions) == 0:
            return Response({
                'error': 'No questions were generated from the document',
                'message': 'Please ensure the document has sufficient content for question generation'
            }, status=500)
        
        # Get first question
        first_question = questions[0]
        
        response_data = {
            'session_id': session.id,
            'message': f"🎯 Interactive Exam: {document.title}",
            'first_question': f"Welcome to your interactive exam! I'll ask you 10 questions based on the document '{document.title}'. You'll have up to 3 attempts per question and can request hints if needed.\n\n**Question 1/10:**\n\n{first_question['question']}\n\nPlease provide your answer:",
            'ai_response': f"Welcome to your interactive exam! I'll ask you 10 questions based on the document '{document.title}'. You'll have up to 3 attempts per question and can request hints if needed.\n\n**Question 1/10:**\n\n{first_question['question']}\n\nPlease provide your answer:",
            'progress': {
                'current': 1,
                'total': 10,
                'percentage': 10.0
            },
            'exam_state': {
                'question_number': 1,
                'attempts_left': 3,
                'hints_available': 3,
                'state': 'WAITING_FOR_ANSWER'
            }
        }
        
        return Response(response_data, status=201)
        
    except Exception as e:
        print(f"❌ Error starting interactive exam: {e}")
        return Response({
            'error': str(e),
            'message': 'Failed to start interactive exam'
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def interactive_exam_chat(request, session_id):
    """
    Handle Interactive Exam chat - processes answers and manages exam flow
    
    POST /api/exam/chat/{session_id}/
    {
        "message": "student answer" or "hint"
    }
    """
    print(f"🎓 Processing Interactive Exam chat for session {session_id}")
    
    try:
        from .models import ChatSession, ChatInteraction, Document
        
        # Get session
        try:
            session = ChatSession.objects.get(id=session_id, student=request.user)
        except ChatSession.DoesNotExist:
            return Response({'error': 'Exam session not found'}, status=404)
        
        # Verify this is an interactive exam session
        metadata = session.get_session_metadata()
        if not metadata.get('is_interactive_exam'):
            return Response({'error': 'This is not an interactive exam session'}, status=400)
        
        # Restore exam session
        exam_session = InteractiveExamSession.from_dict(metadata['exam_session'])
        
        student_message = request.data.get('message', '').strip()
        
        if not student_message:
            return Response({'error': 'Message is required'}, status=400)
        
        # Check if exam is completed
        if exam_session.current_question_index >= 10:
            return generate_exam_completion_report(exam_session, session)
        
        current_question = exam_session.questions[exam_session.current_question_index]
        question_key = str(exam_session.current_question_index)
        question_state = exam_session.question_states.get(question_key, {})
        
        # Handle hint requests
        if student_message.lower() in ['hint', 'help', 'רמז', 'עזרה']:
            return handle_hint_request(exam_session, session, current_question, question_state, metadata)
        
        # Handle answer submission
        return handle_answer_submission(exam_session, session, current_question, question_state, student_message, metadata)
        
    except Exception as e:
        print(f"❌ Error in interactive exam chat: {e}")
        return Response({
            'error': str(e),
            'message': 'Failed to process exam response'
        }, status=500)


def handle_hint_request(exam_session, session, current_question, question_state, metadata):
    """Handle student hint requests during exam"""
    
    hints_shown = question_state.get('hintsShown', 0)
    max_hints = 3
    
    if hints_shown >= max_hints:
        hint_response = f"⚠️ You've already used all {max_hints} hints for this question. Please provide your answer."
    else:
        try:
            # Get document for context
            document = Document.objects.get(id=metadata['document_id'])
            
            # Use pre-computed hint or generate new one
            if 'hints' in current_question and hints_shown < len(current_question['hints']):
                hint_text = current_question['hints'][hints_shown]
            else:
                # Generate contextual hint
                student_answers = question_state.get('answers', [])
                last_answer = student_answers[-1] if student_answers else ""
                
                hint_text = HintGenerator.generate_hint(
                    current_question['question'],
                    current_question['correct_answer'],
                    last_answer,
                    hints_shown + 1,
                    document.extracted_text
                )
            
            # Update hints counter
            question_state['hintsShown'] = hints_shown + 1
            exam_session.question_states[str(exam_session.current_question_index)] = question_state
            
            # Update session metadata
            metadata['exam_session'] = exam_session.to_dict()
            session.set_session_metadata(metadata)
            session.save()
            
            hint_response = f"💡 Hint {hints_shown + 1}/{max_hints}:\n\n{hint_text}\n\nNow please provide your answer:"
            
        except Exception as e:
            print(f"❌ Error generating hint: {e}")
            hint_response = f"❌ Unable to generate hint: {str(e)}\n\nPlease try to answer the question."
    
    # Save interaction
    ChatInteraction.objects.create(
        student=request.user,
        question=f"Requested hint for question {exam_session.current_question_index + 1}",
        answer=hint_response,
        topic="Interactive Exam - Hint"
    )
    
    return Response({
        'ai_response': hint_response,
        'session_completed': False,
        'progress': {
            'current': exam_session.current_question_index + 1,
            'total': 10,
            'percentage': round(((exam_session.current_question_index + 1) / 10) * 100, 1)
        },
        'exam_state': {
            'question_number': exam_session.current_question_index + 1,
            'attempts_left': 3 - question_state.get('attemptCount', 0),
            'hints_available': max_hints - question_state.get('hintsShown', 0),
            'state': 'WAITING_FOR_ANSWER'
        }
    })


def handle_answer_submission(exam_session, session, current_question, question_state, student_answer, metadata):
    """Handle student answer submission during exam"""
    
    attempt_count = question_state.get('attemptCount', 0)
    max_attempts = 3
    
    if attempt_count >= max_attempts:
        return Response({
            'ai_response': f"You've already used all {max_attempts} attempts for this question. Moving to next question.",
            'session_completed': False
        })
    
    # Record attempt
    attempt_count += 1
    question_state['attemptCount'] = attempt_count
    question_state.setdefault('answers', []).append(student_answer)
    
    # Evaluate answer
    is_correct, feedback = AnswerEvaluator.evaluate_answer(student_answer, current_question)
    
    if is_correct:
        # Correct answer - move to next question
        question_state['isCorrect'] = True
        exam_session.total_correct += 1
        exam_session.current_question_index += 1
        
        if exam_session.current_question_index >= 10:
            # Exam completed
            exam_session.state = InteractiveExamSession.COMPLETED
            response_text = f"✅ Correct! {feedback}\n\n🎉 Congratulations! You've completed all 10 questions!"
            session_completed = True
        else:
            # Next question
            next_question = exam_session.questions[exam_session.current_question_index]
            
            # Initialize next question state
            exam_session.question_states[str(exam_session.current_question_index)] = {
                'attemptCount': 0,
                'hintsShown': 0,
                'isCorrect': False,
                'answers': [],
                'startTime': timezone.now().isoformat()
            }
            
            response_text = f"✅ Correct! {feedback}\n\n**Question {exam_session.current_question_index + 1}/10:**\n\n{next_question['question']}\n\nPlease provide your answer:"
            session_completed = False
    else:
        # Incorrect answer
        if attempt_count >= max_attempts:
            # Max attempts reached - show correct answer and move to next
            exam_session.current_question_index += 1
            
            if exam_session.current_question_index >= 10:
                # Exam completed
                exam_session.state = InteractiveExamSession.COMPLETED
                response_text = f"❌ {feedback}\n\nThe correct answer was: {current_question['correct_answer']}\n\n🎉 You've completed all 10 questions!"
                session_completed = True
            else:
                # Next question
                next_question = exam_session.questions[exam_session.current_question_index]
                
                # Initialize next question state
                exam_session.question_states[str(exam_session.current_question_index)] = {
                    'attemptCount': 0,
                    'hintsShown': 0,
                    'isCorrect': False,
                    'answers': [],
                    'startTime': timezone.now().isoformat()
                }
                
                response_text = f"❌ {feedback}\n\nThe correct answer was: {current_question['correct_answer']}\n\n**Question {exam_session.current_question_index + 1}/10:**\n\n{next_question['question']}\n\nPlease provide your answer:"
                session_completed = False
        else:
            # Still have attempts left
            attempts_left = max_attempts - attempt_count
            response_text = f"❌ {feedback}\n\nYou have {attempts_left} attempt{'s' if attempts_left != 1 else ''} remaining. You can also type 'hint' for help."
            session_completed = False
    
    # Update session
    exam_session.question_states[str(exam_session.current_question_index - (1 if is_correct or attempt_count >= max_attempts else 0))] = question_state
    
    if session_completed:
        session.is_completed = True
    
    # Update session metadata
    metadata['exam_session'] = exam_session.to_dict()
    session.set_session_metadata(metadata)
    session.save()
    
    # Save interaction
    ChatInteraction.objects.create(
        student=request.user,
        question=f"Answer: {student_answer}",
        answer=response_text,
        topic="Interactive Exam - Answer"
    )
    
    response_data = {
        'ai_response': response_text,
        'is_correct': is_correct,
        'session_completed': session_completed,
        'progress': {
            'current': exam_session.current_question_index + (0 if session_completed else 1),
            'total': 10,
            'percentage': round((exam_session.current_question_index / 10) * 100, 1)
        }
    }
    
    if not session_completed:
        response_data['exam_state'] = {
            'question_number': exam_session.current_question_index + 1,
            'attempts_left': max_attempts - question_state.get('attemptCount', 0),
            'hints_available': 3 - question_state.get('hintsShown', 0),
            'state': 'WAITING_FOR_ANSWER'
        }
    else:
        # Generate completion report
        completion_report = generate_completion_summary(exam_session)
        response_data['completion_report'] = completion_report
    
    return Response(response_data)


def generate_completion_summary(exam_session):
    """Generate exam completion summary report"""
    
    total_time = timezone.now() - exam_session.start_time
    total_minutes = total_time.total_seconds() / 60
    
    summary = {
        'score': f"{exam_session.total_correct}/10",
        'percentage': round((exam_session.total_correct / 10) * 100, 1),
        'total_time': f"{int(total_minutes)}m {int(total_time.total_seconds() % 60)}s",
        'questions_with_hints': 0,
        'questions_max_attempts': 0,
        'incorrect_questions': []
    }
    
    for i, (question_key, state) in enumerate(exam_session.question_states.items()):
        if state.get('hintsShown', 0) > 0:
            summary['questions_with_hints'] += 1
        
        if state.get('attemptCount', 0) >= 3 and not state.get('isCorrect', False):
            summary['questions_max_attempts'] += 1
        
        if not state.get('isCorrect', False):
            question = exam_session.questions[int(question_key)]
            summary['incorrect_questions'].append({
                'question_number': i + 1,
                'question': question['question'],
                'correct_answer': question['correct_answer'],
                'student_answers': state.get('answers', [])
            })
    
    return summary


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_exam_progress(request, session_id):
    """Get current exam progress and state"""
    
    try:
        session = ChatSession.objects.get(id=session_id, student=request.user)
        metadata = session.get_session_metadata()
        
        if not metadata.get('is_interactive_exam'):
            return Response({'error': 'Not an interactive exam session'}, status=400)
        
        exam_session = InteractiveExamSession.from_dict(metadata['exam_session'])
        
        return Response({
            'progress': {
                'current': exam_session.current_question_index + 1,
                'total': 10,
                'percentage': round(((exam_session.current_question_index + 1) / 10) * 100, 1)
            },
            'score': {
                'correct': exam_session.total_correct,
                'total': exam_session.current_question_index + 1
            },
            'state': exam_session.state,
            'is_completed': exam_session.state == InteractiveExamSession.COMPLETED
        })
        
    except ChatSession.DoesNotExist:
        return Response({'error': 'Session not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)
        session = ChatSession.objects.get(id=session_id, student=request.user)
        student_message = request.data.get('message', '')
        
        if not student_message:
            return Response({'error': 'Message is required'}, status=400)
        
        # Initialize AI components
        tutor = SocraticTutor()
        hint_engine = HintEngine()
        question_processor = StudentQuestionProcessor()
        
        # Check if this is the first message - start with adaptive question
        if session.total_messages == 0:
            # Get first adaptive question
            question_data, tracker = tutor.get_adaptive_question(
                request.user, 
                session.topic, 
                session
            )
            
            # Create AI message with the adaptive question
            ai_msg = ConversationMessage.objects.create(
                chat_session=session,
                message_type='ai_question',
                content=question_data['question'],
                sender='ai',
                hint_level=1
            )
            
            session.total_messages += 1
            session.save()
            
            return Response({
                'ai_response': question_data['question'],
                'understanding_level': 'starting',
                'hint_level': 1,
                'discovery_detected': False,
                'session_complete': False,
                'adaptive_info': question_data.get('tracker_info', {}),
                'current_difficulty': question_data['difficulty']
            })
        
        # Process student response
        # Analyze student message
        analysis = tutor.analyze_student_response(student_message)
        
        # Create student message record
        student_msg = ConversationMessage.objects.create(
            chat_session=session,
            message_type='student_answer' if not analysis['contains_question'] else 'student_question',
            content=student_message,
            sender='student',
            sentiment_score=analysis['sentiment_score'],
            understanding_level=analysis['understanding_level'],
            contains_question=analysis['contains_question'],
            shows_confusion=analysis['shows_confusion'],
            shows_discovery=analysis['shows_discovery']
        )
        
        # Get current question data and tracker
        from .models import AdaptiveDifficultyTracker
        try:
            tracker = AdaptiveDifficultyTracker.objects.get(
                student=request.user,
                topic=session.topic,
                chat_session=session
            )
            
            # For now, create a mock question_data from the tracker's last state
            # In a real implementation, you'd store the current question
            question_data = {
                'question': "Current question in progress",
                'difficulty': tracker.current_difficulty,
                'concepts': ['current concepts'],
                'expected_answer': 'varies',
                'hint_progression': ["Think about it", "What's your approach?", "Let's work together"]
            }
            
            # Process the response and update difficulty
            ai_response, difficulty_changed = tutor.process_student_response(
                student_message, question_data, tracker, session
            )
            
            # Generate next question if student succeeded and difficulty advanced
            next_question_data = None
            if difficulty_changed or (tracker.consecutive_successes > 0 and random.random() < 0.3):
                next_question_data, _ = tutor.get_adaptive_question(
                    request.user, 
                    session.topic, 
                    session
                )
                # Append next question to response
                ai_response += f"\n\n{next_question_data['question']}"
            
        except AdaptiveDifficultyTracker.DoesNotExist:
            # Fallback to regular response if no tracker exists
            ai_response = tutor.generate_socratic_response(
                student_message, 
                {'topic': session.topic},
                1,
                session
            )
            tracker = None
            next_question_data = None
        
        # Update session metrics
        session.total_messages += 1
        if analysis['shows_discovery']:
            session.discoveries_made += 1
            session.breakthrough_moments += 1
        if analysis['shows_confusion']:
            session.confusion_indicators += 1
        
        # Update understanding level based on tracker if available
        if tracker:
            session.current_understanding_level = tracker.mastery_percentage
        else:
            # Fallback to old logic
            if analysis['understanding_level'] == 'good':
                session.current_understanding_level = min(session.current_understanding_level + 10, 100)
            elif analysis['understanding_level'] == 'confused':
                session.current_understanding_level = max(session.current_understanding_level - 5, 0)
        
        # Update engagement score
        sentiment_factor = (analysis['sentiment_score'] + 1) / 2  # Convert -1,1 to 0,1
        session.engagement_score = (session.engagement_score * 0.8) + (sentiment_factor * 0.2)
        
        session.save()
        
        # Determine hint level
        recent_messages_qs = session.messages.order_by('-timestamp')[:5]
        recent_messages = list(recent_messages_qs)
        current_hint_level = 1
        
        if recent_messages:
            last_ai_message = None
            for msg in recent_messages:
                if msg.sender == 'ai':
                    last_ai_message = msg
                    break
            
            if last_ai_message and last_ai_message.hint_level:
                current_hint_level = last_ai_message.hint_level
        
        # Escalate hint level if needed
        if hint_engine.should_escalate_hint(recent_messages, current_hint_level):
            current_hint_level = hint_engine.get_next_hint_level(
                current_hint_level, 
                session.confusion_indicators
            )
        
        # Add encouragement if discovery was made
        encouragement = None
        if analysis['shows_discovery']:
            encouragement = tutor.generate_encouragement(analysis['understanding_level'], True)
            ai_response = encouragement + " " + ai_response
        elif analysis['understanding_level'] in ['good', 'partial']:
            encouragement = tutor.generate_encouragement(analysis['understanding_level'])
        
        # Create AI response message
        ai_msg = ConversationMessage.objects.create(
            chat_session=session,
            message_type='ai_question',
            content=ai_response,
            sender='ai',
            hint_level=current_hint_level
        )
        
        # Check for session completion based on mastery
        session_complete = False
        if tracker:
            # Complete if student has mastered the topic (high success rate and understanding)
            session_complete = (
                tracker.mastery_percentage >= 80 and 
                tracker.current_difficulty >= 3 and
                tracker.consecutive_successes >= 2
            )
        else:
            # Fallback completion logic
            session_complete = session.current_understanding_level >= 85 or session.discoveries_made >= 3
        
        if session_complete:
            session.status = 'completed'
            session.completed_at = timezone.now()
            session.save()
            
            # Offer advanced topics or next learning path
            ai_response += f"\n\n🎉 Congratulations! You've mastered {session.topic}! You're ready to explore more advanced concepts. What would you like to learn next?"
        
        # Prepare adaptive response data
        response_data = {
            'ai_response': ai_response,
            'understanding_level': analysis['understanding_level'],
            'hint_level': current_hint_level,
            'discovery_detected': analysis['shows_discovery'],
            'session_complete': session_complete,
            'encouragement': encouragement,
            'adaptive_info': {
                'current_difficulty': tracker.current_difficulty if tracker else 1,
                'success_rate': tracker.calculate_success_rate() if tracker else 0,
                'consecutive_successes': tracker.consecutive_successes if tracker else 0,
                'mastery_percentage': tracker.mastery_percentage if tracker else session.current_understanding_level,
                'next_level_progress': f"{tracker.consecutive_successes}/{tracker.success_threshold_to_advance}" if tracker else "N/A"
            }
        }
        
        response_serializer = ChatInteractionResponseSerializer(response_data)
        return Response(response_serializer.data)
        
    except ChatSession.DoesNotExist:
        return Response({'error': 'Session not found'}, status=404)
    except Exception as e:
        print(f"Error in interactive learning chat: {e}")
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_learning_session_progress(request, session_id):
    """Get progress and insights for a learning session"""
    try:
        session = ChatSession.objects.get(id=session_id, student=request.user)
        
        # Get recent insights
        recent_insights = session.insights.order_by('-detected_at')[:5]
        insights_serializer = ConversationInsightSerializer(recent_insights, many=True)
        
        # Get learning path progress if exists
        learning_path_progress = None
        if hasattr(session.student, 'learning_paths'):
            active_path = session.student.learning_paths.filter(status='active').first()
            if active_path:
                learning_path_progress = f"{active_path.current_topic} - {active_path.actual_progress_percent:.1f}% complete"
        
        response_data = {
            'session_id': session.id,
            'understanding_level': session.current_understanding_level,
            'engagement_score': session.engagement_score,
            'discoveries_made': session.discoveries_made,
            'confusion_indicators': session.confusion_indicators,
            'breakthrough_moments': session.breakthrough_moments,
            'total_messages': session.total_messages,
            'recent_insights': insights_serializer.data,
            'learning_path_progress': learning_path_progress
        }
        
        response_serializer = LearningProgressResponseSerializer(response_data)
        return Response(response_serializer.data)
        
    except ChatSession.DoesNotExist:
        return Response({'error': 'Session not found'}, status=404)
    except Exception as e:
        print(f"Error getting learning session progress: {e}")
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def end_learning_session(request, session_id):
    """End a learning session and generate final insights"""
    try:
        session = ChatSession.objects.get(id=session_id, student=request.user)
        
        # Mark session as completed
        session.status = 'completed'
        session.completed_at = timezone.now()
        session.save()
        
        # Generate final session insight
        final_insight = ConversationInsight.objects.create(
            chat_session=session,
            insight_type='topic_mastery',
            description=f"Session completed with {session.current_understanding_level}% understanding, {session.discoveries_made} discoveries made",
            confidence_score=0.9,
            recommendation=f"Student showed {'excellent' if session.current_understanding_level >= 80 else 'good' if session.current_understanding_level >= 60 else 'developing'} understanding of {session.topic}"
        )
        
        # Get session summary
        session_serializer = ChatSessionSerializer(session)
        
        return Response({
            'message': 'Session ended successfully',
            'session_summary': session_serializer.data,
            'final_insight': ConversationInsightSerializer(final_insight).data
        })
        
    except ChatSession.DoesNotExist:
        return Response({'error': 'Session not found'}, status=404)
    except Exception as e:
        print(f"Error ending learning session: {e}")
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def handle_exam_chat_interaction(request, session_id):
    """Handle chat interactions during exam mode"""
    try:
        session = ChatSession.objects.get(id=session_id, student=request.user)
        
        if session.session_type != 'exam_chat':
            return Response({'error': 'זה לא מושב מבחן צ\'אט'}, status=400)
        
        student_message = request.data.get('message', '')
        if not student_message:
            return Response({'error': 'נדרש הודעה'}, status=400)
        
        # Use the same Socratic approach but in exam context
        tutor = SocraticTutor()
        analysis = tutor.analyze_student_response(student_message)
        
        # Create student message record
        ConversationMessage.objects.create(
            chat_session=session,
            message_type='student_answer',
            content=student_message,
            sender='student',
            sentiment_score=analysis['sentiment_score'],
            understanding_level=analysis['understanding_level'],
            contains_question=analysis['contains_question'],
            shows_confusion=analysis['shows_confusion'],
            shows_discovery=analysis['shows_discovery']
        )
        
        # Generate exam-appropriate Socratic response in Hebrew
        if session.current_question:
            context = f"עובד על: {session.current_question.question_text}"
            ai_response = tutor.generate_socratic_response(student_message, context, hint_level=2)
        else:
            ai_response = "בואו נעבוד על זה צעד אחר צעד. מה המחשבה הראשונה שלך על הבעיה הזו?"
        
        # Create AI response
        ConversationMessage.objects.create(
            chat_session=session,
            message_type='ai_guidance',
            content=ai_response,
            sender='ai',
            hint_level=2
        )
        
        session.total_messages += 1
        session.save()
        
        return Response({
            'ai_response': ai_response,
            'understanding_level': analysis['understanding_level'],
            'discovery_detected': analysis['shows_discovery']
        })
        
    except ChatSession.DoesNotExist:
        return Response({'error': 'מושב לא נמצא'}, status=404)
    except Exception as e:
        print(f"Error in exam chat interaction: {e}")
        return Response({'error': 'שגיאה בעיבוד התגובה'}, status=500)


# ============= NEW STRUCTURED LEARNING SYSTEM =============

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_learning_session(request):
    """Start a new structured learning session"""
    try:
        topic = request.data.get('topic', 'Linear Equations')
        total_questions = request.data.get('total_questions', 10)
        
        # Initialize learning manager
        learning_manager = StructuredLearningManager(rag_processor)
        
        # Start session
        session = learning_manager.start_learning_session(
            student=request.user,
            topic=topic,
            total_questions=total_questions
        )
        
        # Get first question
        first_question = learning_manager.get_current_question(session)
        
        return Response({
            'success': True,
            'session_id': session.id,
            'question_data': first_question,
            'topic': topic
        })
        
    except Exception as e:
        print(f"❌ Error starting learning session: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_learning_answer(request):
    """Submit answer for current question in learning session"""
    try:
        session_id = request.data.get('session_id')
        student_answer = request.data.get('answer', '').strip()
        
        if not session_id or not student_answer:
            return Response({
                'success': False,
                'error': 'Session ID and answer required'
            }, status=400)
        
        # Get session
        try:
            session = LearningSession.objects.get(id=session_id, student=request.user)
        except LearningSession.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Session not found'
            }, status=404)
        
        # Process answer
        learning_manager = StructuredLearningManager(rag_processor)
        result = learning_manager.process_student_answer(session, student_answer)
        
        return Response({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        print(f"❌ Error processing learning answer: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_learning_progress(request, session_id):
    """Get progress for a learning session"""
    try:
        session = LearningSession.objects.get(id=session_id, student=request.user)
        
        return Response({
            'session_id': session.id,
            'topic': session.topic,
            'current_question': session.current_question_index + 1,
            'total_questions': session.total_questions,
            'correct_answers': session.correct_answers,
            'total_attempts': session.total_attempts,
            'understanding_level': session.understanding_level,
            'is_completed': session.is_completed,
            'progress_percent': int((session.current_question_index / session.total_questions) * 100) if session.total_questions > 0 else 0
        })
        
    except LearningSession.DoesNotExist:
        return Response({
            'error': 'Session not found'
        }, status=404)


# ====================
# TASK 2.1: EXAM SESSION VIEWS
# ====================

@api_view(['GET'])
@permission_classes([])  # Allow anonymous access for development
def list_topics(request):
    """List all topics that have chat-generated questions"""
    try:
        # Get topics that have chat-generated questions
        topics_with_questions = Topic.objects.filter(
            questions__is_generated=True
        ).distinct()
        
        serializer = TopicSerializer(topics_with_questions, many=True)
        return Response({
            'topics': serializer.data,
            'total_count': topics_with_questions.count()
        })
        
    except Exception as e:
        print(f"Error in list_topics: {e}")
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([])  # Allow anonymous access for development
def create_exam_session(request):
    """Create a new exam session with teacher-defined configuration"""
    # For development, skip user role check
    # if request.user.role != 'teacher':
    #     return Response({'error': 'Only teachers can create exam sessions'}, status=403)
    
    try:
        print(f"DEBUG: Received request data: {request.data}")
        
        serializer = ExamSessionCreateSerializer(data=request.data)
        if not serializer.is_valid():
            print(f"DEBUG: Serializer validation errors: {serializer.errors}")
            return Response({'errors': serializer.errors}, status=400)
        
        data = serializer.validated_data
        title = data.get('title', 'Untitled Exam Session')
        description = data.get('description', '')
        num_questions = data['num_questions']
        is_published = data.get('is_published', False)
        topic_ids = data.get('topic_ids', [])
        random_topic_distribution = data.get('random_topic_distribution', False)
        time_limit_seconds = data.get('time_limit_seconds')
        selected_question_ids = data.get('selected_question_ids', [])
        
        # Create the exam session
        # For development: handle cases where user is not authenticated
        created_by_user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
        if not created_by_user:
            # For development, get or create a default teacher user
            from django.contrib.auth import get_user_model
            User = get_user_model()
            created_by_user, _ = User.objects.get_or_create(
                username='demo_teacher',
                defaults={'role': 'teacher', 'email': 'demo@example.com'}
            )
        
        exam_session = ExamSession.objects.create(
            created_by=created_by_user,
            title=title,
            description=description,
            num_questions=num_questions,
            random_topic_distribution=random_topic_distribution,
            time_limit_seconds=time_limit_seconds,
            is_published=is_published
        )
        
        # Start with manually selected questions
        selected_questions = []
        if selected_question_ids:
            # Validate and get selected questions (ensuring they're chat-generated for this user)
            selected_questions = list(QuestionBank.objects.filter(
                id__in=selected_question_ids,
                is_generated=True,  # Only chat-generated questions
                document__uploaded_by=created_by_user  # Only questions from documents uploaded by this user
            ))
            
            if len(selected_questions) != len(selected_question_ids):
                exam_session.delete()
                return Response({
                    'error': 'Some selected questions are not valid chat-generated questions'
                }, status=400)
        
        # Get remaining questions needed
        remaining_needed = num_questions - len(selected_questions)
        additional_questions = []
        
        if remaining_needed > 0:
            # Get pool of available questions (excluding already selected)
            question_pool = QuestionBank.objects.filter(
                is_generated=True,  # Only chat-generated questions
                document__uploaded_by=created_by_user  # Only questions from documents uploaded by this user
            ).exclude(
                id__in=selected_question_ids
            )
            
            if random_topic_distribution:
                # Get all topics that have chat-generated questions
                available_topics = Topic.objects.filter(
                    questions__is_generated=True
                ).distinct()
                
                if available_topics.exists():
                    # Distribute questions evenly across topics
                    questions_per_topic = remaining_needed // available_topics.count()
                    extra_questions = remaining_needed % available_topics.count()
                    
                    for i, topic in enumerate(available_topics):
                        topic_questions_needed = questions_per_topic + (1 if i < extra_questions else 0)
                        if topic_questions_needed > 0:
                            topic_questions = list(question_pool.filter(
                                topic=topic
                            ).order_by('?')[:topic_questions_needed])
                            additional_questions.extend(topic_questions)
                            question_pool = question_pool.exclude(
                                id__in=[q.id for q in topic_questions]
                            )
                
                # Fill any remaining slots with random questions
                if len(additional_questions) < remaining_needed:
                    extra_needed = remaining_needed - len(additional_questions)
                    extra_questions = list(question_pool.order_by('?')[:extra_needed])
                    additional_questions.extend(extra_questions)
                    
            else:
                # Use specified topics
                if topic_ids:
                    question_pool = question_pool.filter(topic_id__in=topic_ids)
                
                # Distribute evenly across specified topics
                topics = Topic.objects.filter(id__in=topic_ids) if topic_ids else []
                
                if topics:
                    questions_per_topic = remaining_needed // len(topics)
                    extra_questions = remaining_needed % len(topics)
                    
                    for i, topic in enumerate(topics):
                        topic_questions_needed = questions_per_topic + (1 if i < extra_questions else 0)
                        if topic_questions_needed > 0:
                            topic_questions = list(question_pool.filter(
                                topic=topic
                            ).order_by('?')[:topic_questions_needed])
                            additional_questions.extend(topic_questions)
                            question_pool = question_pool.exclude(
                                id__in=[q.id for q in topic_questions]
                            )
                else:
                    # No specific topics, get random questions from pool
                    additional_questions = list(question_pool.order_by('?')[:remaining_needed])
        
        # Combine selected and additional questions
        all_questions = selected_questions + additional_questions
        
        if len(all_questions) < num_questions:
            exam_session.delete()
            return Response({
                'error': f'Not enough chat-generated questions available. Found {len(all_questions)}, needed {num_questions}'
            }, status=400)
        
        # Take only the needed number of questions
        final_questions = all_questions[:num_questions]
        
        # Create ExamSessionQuestion records with order_index
        for i, question in enumerate(final_questions, 1):
            ExamSessionQuestion.objects.create(
                exam_session=exam_session,
                question=question,
                order_index=i,
                time_limit_seconds=time_limit_seconds
            )
        
        # Create topic relationships
        session_topics = set()
        for question in final_questions:
            if question.topic:
                session_topics.add(question.topic)
        
        for topic in session_topics:
            ExamSessionTopic.objects.create(
                exam_session=exam_session,
                topic=topic
            )
        
        # Return the created session with full details
        response_serializer = ExamSessionSerializer(exam_session)
        return Response(response_serializer.data, status=201)
        
    except Exception as e:
        print(f"Error creating exam session: {e}")
        import traceback
        traceback.print_exc()
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_exam_session(request, session_id):
    """Get details of a specific exam session"""
    if request.user.role != 'teacher':
        return Response({'error': 'Only teachers can view exam sessions'}, status=403)
    
    try:
        exam_session = ExamSession.objects.get(
            id=session_id,
            created_by=request.user
        )
        
        serializer = ExamSessionSerializer(exam_session)
        return Response(serializer.data)
        
    except ExamSession.DoesNotExist:
        return Response({'error': 'Exam session not found'}, status=404)
    except Exception as e:
        print(f"Error getting exam session: {e}")
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_exam_sessions(request):
    """List exam sessions - for teachers: all their created sessions, for students: available published sessions"""
    try:
        if request.user.role == 'teacher':
            # Teachers see all their created exam sessions
            exam_sessions = ExamSession.objects.filter(
                created_by=request.user
            ).order_by('-created_at')
        else:
            # Students see published exam sessions they can take
            exam_sessions = ExamSession.objects.filter(
                is_published=True
            ).order_by('-created_at')
        
        serializer = ExamSessionSerializer(exam_sessions, many=True)
        return Response({
            'exam_sessions': serializer.data,
            'total_count': len(exam_sessions) if request.user.role == 'student' else exam_sessions.count()
        })
        
    except Exception as e:
        print(f"Error listing exam sessions: {e}")
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_exam_session(request, session_id):
    """Start an exam session for a student"""
    try:
        exam_session = ExamSession.objects.get(id=session_id)
        
        # Check if student can start this exam
        if not exam_session.is_published:
            return Response({'error': 'Exam is not published'}, status=400)
        
        # Get exam questions for the student
        exam_questions = ExamSessionQuestion.objects.filter(
            exam_session=exam_session
        ).order_by('order_index')
        
        questions_data = []
        for eq in exam_questions:
            question_data = {
                'id': eq.question.id,
                'question_text': eq.question.question_text,
                'options': [
                    eq.question.option_a,
                    eq.question.option_b,
                    eq.question.option_c,
                    eq.question.option_d
                ],
                'order_index': eq.order_index
            }
            questions_data.append(question_data)
        
        return Response({
            'exam_session': {
                'id': exam_session.id,
                'title': exam_session.title,
                'description': exam_session.description,
                'duration_minutes': exam_session.duration_minutes,
                'total_questions': len(questions_data)
            },
            'questions': questions_data
        })
        
    except ExamSession.DoesNotExist:
        return Response({'error': 'Exam session not found'}, status=404)
    except Exception as e:
        print(f"Error starting exam session: {e}")
        return Response({'error': str(e)}, status=500)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_exam_session(request, session_id):
    """Delete an exam session (teacher only)"""
    if request.user.role != 'teacher':
        return Response({'error': 'Only teachers can delete exam sessions'}, status=403)
    
    try:
        exam_session = ExamSession.objects.get(id=session_id, created_by=request.user)
        exam_session.delete()
        
        return Response({'message': 'Exam session deleted successfully'})
        
    except ExamSession.DoesNotExist:
        return Response({'error': 'Exam session not found'}, status=404)
    except Exception as e:
        print(f"Error deleting exam session: {e}")
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_exam_session_details(request, session_id):
    """Get detailed exam session information including questions"""
    try:
        # Get the exam session
        exam_session = ExamSession.objects.get(id=session_id)
        
        # Check permissions - only creator can view details
        if request.user.role == 'teacher' and exam_session.created_by != request.user:
            return Response({'error': 'Access denied'}, status=403)
        
        # Get linked questions
        exam_questions = ExamSessionQuestion.objects.filter(
            exam_session=exam_session
        ).select_related('question').order_by('order_index')
        
        print(f"DEBUG: Found {exam_questions.count()} questions for exam {session_id}")
        
        # Serialize exam session
        exam_data = {
            'id': exam_session.id,
            'title': exam_session.title,
            'description': exam_session.description,
            'num_questions': exam_session.num_questions,
            'time_limit_seconds': exam_session.time_limit_seconds,
            'is_published': exam_session.is_published,
            'random_topic_distribution': exam_session.random_topic_distribution,
            'created_at': exam_session.created_at.isoformat(),
            'created_by': exam_session.created_by.username,
            'total_questions': exam_questions.count()
        }
        
        # Serialize questions
        questions_data = []
        for exam_question in exam_questions:
            question = exam_question.question
            questions_data.append({
                'id': question.id,
                'question_text': question.question_text,
                'option_a': question.option_a,
                'option_b': question.option_b,
                'option_c': question.option_c,
                'option_d': question.option_d,
                'correct_answer': question.correct_answer,
                'difficulty_level': question.difficulty_level,
                'topic': question.topic.name if question.topic else None,
                'order_index': exam_question.order_index
            })
        
        print(f"DEBUG: Returning {len(questions_data)} questions for exam details")
        
        return Response({
            'success': True,
            'exam_session': exam_data,
            'questions': questions_data
        })
        
    except ExamSession.DoesNotExist:
        print(f"ERROR: Exam session {session_id} not found")
        return Response({'error': 'Exam session not found'}, status=404)
    except Exception as e:
        print(f"ERROR: Failed to get exam details for {session_id}: {str(e)}")
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def teacher_assessment_dashboard(request):
    """Get student assessment data for teachers"""
    try:
        if request.user.role != 'teacher':
            return Response({
                'error': 'Teacher access required'
            }, status=403)
        
        learning_manager = StructuredLearningManager(rag_processor)
        dashboard_data = learning_manager.get_teacher_dashboard_data(request.user)
        
        return Response({
            'success': True,
            'assessments': dashboard_data
        })
        
    except Exception as e:
        print(f"❌ Error getting teacher dashboard: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([])
def available_learning_topics(request):
    """Get available learning topics"""
    learning_manager = StructuredLearningManager(rag_processor)
    topics = list(learning_manager.question_banks.keys())
    
    return Response({
        'topics': topics
    })


# ====================
# TASK 2.2: EXAM CONFIGURATION VIEWS
# ====================

class ExamConfigViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing exam configurations
    Provides CRUD operations for storing and retrieving exam configurations
    """
    serializer_class = ExamConfigSerializer
    permission_classes = []  # Allow anonymous access for development
    
    def get_queryset(self):
        """
        Filter queryset based on user role and query parameters
        Teachers can see their own configs, students can see configs assigned to them
        """
        user = self.request.user
        queryset = ExamConfig.objects.all()
        
        if user.is_authenticated:
            if user.role == 'teacher':
                # Teachers see configs they created
                queryset = queryset.filter(teacher=user)
            elif user.role == 'student':
                # Students see configs assigned to them
                queryset = queryset.filter(assigned_student=user)
            else:
                # For development: admin or other roles see all
                pass
        else:
            # Anonymous users see all (for development)
            pass
        
        # Filter by exam session if provided
        exam_session_id = self.request.query_params.get('exam_session_id')
        if exam_session_id:
            queryset = queryset.filter(exam_session_id=exam_session_id)
        
        return queryset.select_related('teacher', 'assigned_student', 'exam_session').prefetch_related('config_questions__question')
    
    def create(self, request, *args, **kwargs):
        """Create a new exam configuration"""
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                exam_config = serializer.save()
                
                # Return the created configuration with full details
                response_serializer = self.get_serializer(exam_config)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'errors': serializer.errors,
                    'message': 'Validation failed'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            print(f"❌ Error creating exam config: {e}")
            import traceback
            traceback.print_exc()
            return Response({
                'error': str(e),
                'message': 'Failed to create exam configuration'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a specific exam configuration"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Exception as e:
            print(f"❌ Error retrieving exam config: {e}")
            return Response({
                'error': str(e),
                'message': 'Failed to retrieve exam configuration'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def list(self, request, *args, **kwargs):
        """List exam configurations with filtering"""
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'configs': serializer.data,
                'count': len(serializer.data)
            })
        except Exception as e:
            print(f"❌ Error listing exam configs: {e}")
            return Response({
                'error': str(e),
                'message': 'Failed to list exam configurations'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 📚 DOCUMENT-BASED INTERACTIVE LEARNING SYSTEM
# ================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_document_based_learning(request):
    """
    Start an interactive learning session based on questions generated from a specific document
    
    POST /api/start_document_learning/
    {
        "document_id": 42,
        "difficulty_levels": ["3", "4", "5"],  # Optional, default all levels
        "max_questions": 10  # Optional, default all available questions
    }
    """
    try:
        from .models import Document, QuestionBank, ChatSession
        
        document_id = request.data.get('document_id')
        difficulty_levels = request.data.get('difficulty_levels', ['3', '4', '5'])
        max_questions = request.data.get('max_questions', None)
        
        if not document_id:
            return Response({'error': 'document_id is required'}, status=400)
        
        # Verify document exists and belongs to user (for teachers) or is accessible
        try:
            document = Document.objects.get(id=document_id)
            
            # Check permissions
            if request.user.role == 'teacher' and document.uploaded_by != request.user:
                return Response({'error': 'You can only access your own documents'}, status=403)
                
        except Document.DoesNotExist:
            return Response({'error': 'Document not found'}, status=404)
        
        # Get questions generated from this document
        questions_query = QuestionBank.objects.filter(
            document=document,
            is_generated=True,  # Only AI-generated questions
            difficulty_level__in=difficulty_levels
        ).order_by('difficulty_level', 'id')
        
        if max_questions:
            questions_query = questions_query[:max_questions]
            
        questions = list(questions_query)
        
        if not questions:
            return Response({
                'error': 'No questions found for this document',
                'message': f'No generated questions found for document "{document.title}" with difficulty levels {difficulty_levels}'
            }, status=404)
        
        # Create a new chat session for this document-based learning
        session = ChatSession.objects.create(
            student=request.user,
            topic=f"Document: {document.title}",
            total_questions=len(questions),
            current_question_index=0
        )
        
        # Store question IDs in session metadata using helper method
        session.set_session_metadata({
            'document_id': document_id,
            'question_ids': [q.id for q in questions],
            'difficulty_levels': difficulty_levels,
            'is_document_based': True
        })
        session.save()
        
        # Get first question
        first_question = questions[0]
        
        # Create initial message
        from .models import ChatInteraction
        ChatInteraction.objects.create(
            student=request.user,
            question="Started document-based learning session",
            answer=f"📚 Welcome to interactive learning based on '{document.title}'!\n\nLet's start with the first question:\n\n{first_question.question_text}",
            topic="Document-based Learning",
            document=document
        )
        
        return Response({
            'session_id': session.id,
            'document_title': document.title,
            'total_questions': len(questions),
            'current_question': 1,
            'first_question': {
                'id': first_question.id,
                'question': first_question.question_text,
                'options': {
                    'A': first_question.option_a,
                    'B': first_question.option_b,
                    'C': first_question.option_c,
                    'D': first_question.option_d
                },
                'difficulty_level': first_question.difficulty_level
            },
            'message': f"Started learning session with {len(questions)} questions from '{document.title}'"
        }, status=201)
        
    except Exception as e:
        print(f"❌ Error starting document-based learning: {e}")
        return Response({
            'error': str(e),
            'message': 'Failed to start document-based learning session'
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_document_learning_answer(request, session_id):
    """
    Submit an answer for document-based learning session
    
    POST /api/document_learning/{session_id}/answer/
    {
        "answer": "A",
        "question_id": 154
    }
    """
    try:
        from .models import ChatSession, QuestionBank, ChatInteraction
        
        # Get session
        try:
            session = ChatSession.objects.get(id=session_id, student=request.user)
        except ChatSession.DoesNotExist:
            return Response({'error': 'Learning session not found'}, status=404)
        
        # Verify this is a document-based session
        metadata = session.get_session_metadata()
        if not metadata.get('is_document_based'):
            return Response({'error': 'This is not a document-based learning session'}, status=400)
        
        answer = request.data.get('answer', '').strip().upper()
        question_id = request.data.get('question_id')
        
        if not answer or not question_id:
            return Response({'error': 'answer and question_id are required'}, status=400)
        
        # Get current question
        try:
            current_question = QuestionBank.objects.get(id=question_id)
        except QuestionBank.DoesNotExist:
            return Response({'error': 'Question not found'}, status=404)
        
        # Check if answer is correct
        is_correct = (answer == current_question.correct_answer.upper())
        
        # Prepare feedback
        if is_correct:
            feedback = f"✅ Correct! {current_question.explanation if current_question.explanation else 'Well done!'}"
        else:
            feedback = f"❌ Incorrect. The correct answer is {current_question.correct_answer}. {current_question.explanation if current_question.explanation else ''}"
        
        # Update session progress
        session.current_question_index += 1
        question_ids = metadata.get('question_ids', [])
        
        # Check if there are more questions
        has_next = session.current_question_index < len(question_ids)
        next_question_data = None
        
        if has_next:
            next_question_id = question_ids[session.current_question_index]
            try:
                next_question = QuestionBank.objects.get(id=next_question_id)
                next_question_data = {
                    'id': next_question.id,
                    'question': next_question.question_text,
                    'options': {
                        'A': next_question.option_a,
                        'B': next_question.option_b,
                        'C': next_question.option_c,
                        'D': next_question.option_d
                    },
                    'difficulty_level': next_question.difficulty_level
                }
                feedback += f"\n\nNext question:\n{next_question.question_text}"
            except QuestionBank.DoesNotExist:
                has_next = False
        else:
            # Session completed
            session.is_completed = True
            feedback += f"\n\n🎉 Congratulations! You've completed all questions from this document. Session finished!"
        
        session.save()
        
        # Save interaction
        ChatInteraction.objects.create(
            student=request.user,
            question=f"Answer: {answer}",
            answer=feedback,
            topic="Document-based Learning - Answer"
        )
        
        response_data = {
            'is_correct': is_correct,
            'feedback': feedback,
            'progress': {
                'current': session.current_question_index,
                'total': len(question_ids),
                'percentage': round((session.current_question_index / len(question_ids)) * 100, 1)
            },
            'session_completed': not has_next
        }
        
        if next_question_data:
            response_data['next_question'] = next_question_data
        
        return Response(response_data)
        
    except Exception as e:
        print(f"❌ Error processing document learning answer: {e}")
        return Response({
            'error': str(e),
            'message': 'Failed to process answer'
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_document_learning_progress(request, session_id):
    """
    Get progress for document-based learning session
    
    GET /api/document_learning/{session_id}/progress/
    """
    try:
        from .models import ChatSession, Document
        
        # Get session
        try:
            session = ChatSession.objects.get(id=session_id, student=request.user)
        except ChatSession.DoesNotExist:
            return Response({'error': 'Learning session not found'}, status=404)
        
        # Verify this is a document-based session
        metadata = session.get_session_metadata()
        if not metadata.get('is_document_based'):
            return Response({'error': 'This is not a document-based learning session'}, status=400)
        
        # Get document info
        document_id = metadata.get('document_id')
        document = Document.objects.get(id=document_id)
        
        question_ids = metadata.get('question_ids', [])
        
        return Response({
            'session_id': session.id,
            'document_title': document.title,
            'progress': {
                'current': session.current_question_index,
                'total': len(question_ids),
                'percentage': round((session.current_question_index / len(question_ids)) * 100, 1) if question_ids else 0
            },
            'is_completed': session.is_completed,
            'started_at': session.started_at,
            'difficulty_levels': metadata.get('difficulty_levels', [])
        })
        
    except Exception as e:
        print(f"❌ Error getting document learning progress: {e}")
        return Response({
            'error': str(e),
            'message': 'Failed to get progress'
        }, status=500)


# ===================================================================
# 🎓 INTERACTIVE EXAM SYSTEM - SIMPLIFIED START
# ===================================================================

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def start_interactive_exam_duplicate(request):
#     """
#     🎓 Start a new Interactive Exam Session (DUPLICATE - DISABLED)
#     
#     This creates a generic exam session that generates questions from teacher documents
#     and provides an interactive chat-based exam experience.
#     """
#     if request.user.role != 'student':
#         return Response({'error': 'Only students can start interactive exams'}, status=403)
    
    try:
        from .models import TestSession
        import json
        from django.utils import timezone
        
        print(f"🎓 Starting interactive exam for student: {request.user.username}")
        
        # Check if student already has an active exam session
        existing_session = TestSession.objects.filter(
            student=request.user,
            test_type='exam',
            is_completed=False
        ).first()
        
        if existing_session:
            return Response({
                'error': 'You already have an active exam session. Please complete it first.',
                'session_id': existing_session.id
            }, status=400)
        
        # Create new interactive exam session
        session = TestSession.objects.create(
            student=request.user,
            test_type='exam',
            difficulty_level='3',  # Default medium difficulty
            subject='course_content',
            total_questions=10,  # Standard exam length
            time_limit_minutes=60  # 1 hour time limit
        )
        
        print(f"✅ Created interactive exam session: {session.id}")
        
        # Generate questions from teacher documents
        print("📚 Generating questions from teacher documents...")
        result = _generate_exam_questions_from_docs(request.user, 10)
        
        if 'error' in result:
            # Delete the session if question generation failed
            session.delete()
            return Response({
                'error': result['error'],
                'details': 'Failed to generate questions from teacher materials'
            }, status=400)
        
        # Store generated questions in session notes
        notes = {
            'questions': result['questions'],
            'vector_store_id': result.get('vector_store_id', ''),
            'source_documents': result.get('source_documents', []),
            'question_index': 0,
            'attempts_for_current': 0,
            'score_correct': 0,
            'exam_start_time': timezone.now().isoformat(),
            'generation_method': result.get('generation_method', 'teacher_documents'),
            'teacher_documents_used': result.get('teacher_documents_used', 0)
        }
        
        session.notes = json.dumps(notes)
        session.save()
        
        print(f"✅ Questions generated and stored. Source: {result.get('generation_method')}")
        print(f"📚 Using {result.get('teacher_documents_used', 0)} teacher documents")
        
        # Get the first question
        questions = result['questions']
        if not questions:
            session.delete()
            return Response({
                'error': 'No questions were generated from teacher materials'
            }, status=400)
        
        first_question = questions[0]
        
        # Format first question for display
        question_text = first_question.get('question_text', '')
        
        # Add multiple choice options if available
        options = []
        if first_question.get('options'):
            options_dict = first_question['options']
            for key in ['A', 'B', 'C', 'D']:
                if key in options_dict and options_dict[key]:
                    options.append(f"{key}) {options_dict[key]}")
        
        if options:
            question_display = f"{question_text}\n\n" + "\n".join(options)
        else:
            question_display = question_text
        
        # Create welcome message
        source_info = ""
        if result.get('source_documents'):
            doc_titles = [doc['title'] for doc in result['source_documents']]
            source_info = f"\n\n📚 **Questions based on:** {', '.join(doc_titles)}"
        
        welcome_message = f"""🎓 **Welcome to your Interactive Exam!**

**Exam Details:**
• **Questions:** 10 questions
• **Time Limit:** 60 minutes
• **Source:** Teacher course materials
• **Format:** Interactive with hints and guidance{source_info}

**Instructions:**
• Answer each question carefully
• You can get hints if you need help
• Type your answer and press send
• For multiple choice, use the letter (A, B, C, D)

---

**Question 1 of 10:**

{question_display}

Please provide your answer."""
        
        return Response({
            'success': True,
            'session_id': session.id,
            'exam_info': {
                'total_questions': 10,
                'time_limit_minutes': 60,
                'current_question': 1,
                'teacher_documents_used': result.get('teacher_documents_used', 0),
                'source_documents': result.get('source_documents', [])
            },
            'welcome_message': welcome_message,
            'first_question': {
                'id': first_question.get('id', 'generated_1'),
                'question_number': 1,
                'question_text': question_text,
                'question_type': first_question.get('question_type', 'open'),
                'has_options': len(options) > 0,
                'options': options
            },
            'instruction': 'The interactive exam has started! Please respond with your answer to Question 1.'
        })
        
    except Exception as e:
        print(f"❌ Error starting interactive exam: {e}")
        import traceback
        traceback.print_exc()
        return Response({
            'error': f'Failed to start interactive exam: {str(e)}',
            'details': 'Please try again or contact support if the problem persists'
        }, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_questions_from_document(request):
    """
    API מהיר ליצירת שאלות ממסמך עבור מרצה
    """
    if request.user.role != 'teacher':
        return Response({'error': 'רק מרצים יכולים ליצור שאלות'}, status=403)
    
    try:
        document_id = request.data.get('document_id')
        num_questions = request.data.get('num_questions', 10)
        difficulty = request.data.get('difficulty', 'mixed')  # basic, intermediate, advanced, mixed
        
        if not document_id:
            return Response({'error': 'חסר document_id'}, status=400)
        
        # קבלת המסמך
        try:
            document = Document.objects.get(id=document_id, uploaded_by=request.user)
        except Document.DoesNotExist:
            return Response({'error': 'המסמך לא נמצא או שאין לך הרשאה'}, status=404)
        
        if not document.extracted_text:
            return Response({'error': 'המסמך לא עובד או לא קיים טקסט'}, status=400)
        
        print(f"🚀 יוצר שאלות מהיר מהמסמך: {document.title}")
        
        # יצירת שאלות מהירה
        from .gemini_client import gemini_client
        
        if not gemini_client:
            return Response({'error': 'מערכת AI לא זמינה'}, status=503)
        
        questions = gemini_client.generate_questions_fast(
            document.extracted_text,
            num_questions=num_questions,
            difficulty=difficulty
        )
        
        if not questions:
            return Response({'error': 'לא הצלחתי ליצור שאלות'}, status=500)
        
        # שמירת השאלות למסד נתונים
        saved_questions = []
        for q_data in questions:
            # יצירת QuestionBank חדש
            question_bank = QuestionBank.objects.create(
                question_text=q_data.get('question_text', ''),
                question_type='multiple_choice',
                options=q_data.get('options', {}),
                correct_answer=q_data.get('correct_answer', 'A'),
                explanation=f"נוצר אוטומטית מהמסמך: {document.title}",
                difficulty=difficulty,
                created_by=request.user
            )
            
            saved_questions.append({
                'id': question_bank.id,
                'question_text': question_bank.question_text,
                'options': question_bank.options,
                'correct_answer': question_bank.correct_answer,
                'difficulty': difficulty
            })
        
        # עדכון מספר השאלות שנוצרו מהמסמך
        document.questions_generated_count = document.questions_generated_count + len(saved_questions)
        document.save()
        
        return Response({
            'success': True,
            'message': f'נוצרו {len(saved_questions)} שאלות בהצלחה',
            'questions': saved_questions,
            'document_name': document.title,
            'source': 'gemini_2_0_fast',
            'total_questions_from_document': document.questions_generated_count
        })
        
    except Exception as e:
        print(f"❌ שגיאה ביצירת שאלות: {e}")
        import traceback
        traceback.print_exc()
        return Response({'error': str(e)}, status=500)
>>>>>>> daniel
