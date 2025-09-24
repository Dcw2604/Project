"""
Document Processing Utilities with LangChain RAG and Enhanced Algorithm/CS Validation
Handles PDF extraction, text splitting, vector storage, and AI-powered algorithm/CS question validation
"""
import os
import tempfile
import json
import re
import requests
import random
import pdfplumber
from PIL import Image
import io
import base64
from typing import List, Dict, Any, Optional


import json
import re
import os
import io
import base64
import random
import requests
from PIL import Image
from typing import List, Dict, Any, Optional


def extract_json_payload(text: str):
    """
    Tolerant JSON extractor that handles LLM responses with fences, prose, etc.
    """
    # strip fences
    text = re.sub(r'^\s*```(?:json)?\s*', '', text.strip(), flags=re.IGNORECASE)
    text = re.sub(r'\s*```\s*$', '', text, flags=re.IGNORECASE)
    # try direct parse
    try:
        return json.loads(text)
    except Exception:
        pass
    # find first JSON object/array in the text
    m = re.search(r'(\{.*\}|\[.*\])', text, flags=re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass
    return None


def best_snippet_for_question(doc_text: str, question: str, window=300):
    """
    Find the most relevant snippet from document for a given question
    """
    parts = re.split(r'(?<=[\.\?\!])\s+|\n+', doc_text)
    qtoks = set(re.findall(r'[A-Za-z0-9%]+', question.lower()))
    best, score = None, 0
    for sent in parts:
        stoks = set(re.findall(r'[A-Za-z0-9%]+', sent.lower()))
        overlap = len(qtoks & stoks) + 0.5*len(set(re.findall(r'\d+(?:\.\d+)?', question)) & set(re.findall(r'\d+(?:\.\d+)?', sent)))
        if overlap > score:
            score, best = overlap, sent
    return best[:window] + "..." if best and len(best) > window else best


def try_extract_answer_from_doc(extracted_text: str, question: str, known_correct=None) -> dict:
    """
    Enhanced lightweight retriever to extract answers/explanations from document text
    """
    try:
        # Look for explicit answer patterns in the document
        for pat in [r'(?i)\banswer\s*[:\-]\s*([^\n\.]+)',
                    r'(?i)\bsolution\s*[:\-]\s*([^\n\.]+)',
                    r'(?i)\bcorrect answer\s*[:\-]\s*([^\n\.]+)',
                    r'(?i)\bans\.\s*([^\n\.]+)']:
            m = re.search(pat, extracted_text)
            if m:
                ans = m.group(1).strip()
                return {
                    'answer_text': ans, 
                    'explanation': best_snippet_for_question(extracted_text, question),
                    'source_sentences': [ans]
                }
        
        # If we have a known correct answer, find its context
        if known_correct:
            esc = re.escape(str(known_correct))
            m2 = re.search(rf'.{{0,80}}{esc}.{{0,120}}', extracted_text)
            if m2:
                return {
                    'answer_text': str(known_correct), 
                    'explanation': m2.group(0).strip(),
                    'source_sentences': [m2.group(0).strip()]
                }
        
        # Fallback to best snippet matching
        snippet = best_snippet_for_question(extracted_text, question)
        return {
            'answer_text': known_correct or "",
            'explanation': snippet or "",
            'source_sentences': [snippet] if snippet else []
        }
        
    except Exception as e:
        return {
            'answer_text': known_correct or "",
            'explanation': "",
            'source_sentences': []
        }


class OllamaUnavailableError(RuntimeError):
    pass


class InsufficientQuestionsError(RuntimeError):
    pass


def llm_is_up(base="http://127.0.0.1:11434", timeout=0.8) -> bool:
    try:
        import requests
        r = requests.get(f"{base}/api/tags", timeout=timeout)
        return r.ok
    except Exception:
        return False

# LangChain imports (compatible with 0.3+)
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA
try:
    from langchain_core.documents import Document as LangChainDocument
except ImportError:
    from langchain.schema import Document as LangChainDocument
try:
    from langchain_core.prompts import PromptTemplate
except ImportError:
    from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain

from django.conf import settings
from .models import Document, ChatInteraction
from .algorithm_document_processor import AlgorithmDocumentProcessor


class DocumentProcessor:
    """Handles document processing and RAG implementation with enhanced algorithm/CS validation"""
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        # Initialize embeddings (fallback to basic if Ollama not available)
        try:
            self.embeddings = OllamaEmbeddings(model="llama3.2", base_url="http://localhost:11434")
        except Exception:
            # Fallback to a simpler embedding if Ollama embeddings fail
            self.embeddings = None
        
        # Initialize LLM
        try:
            self.llm = Ollama(model="llama3.2", base_url="http://localhost:11434")
        except Exception:
            self.llm = None
        
        # Initialize the unified algorithm processor
        self.algorithm_processor = AlgorithmDocumentProcessor()
    
    def process_document_unified(self, file_path: str, document_id: int, document_type: str = 'pdf') -> Dict[str, Any]:
        """
        Unified document processing using AlgorithmDocumentProcessor orchestration
        This is the main entry point for all document processing
        """
        return self.algorithm_processor.orchestrate_document_processing(file_path, document_id, document_type)
    
    def extract_pdf_content(self, file_path: str) -> Dict[str, Any]:
        """Extract text and metadata from PDF using pdfplumber"""
        try:
            extracted_data = {
                'text': '',
                'pages': [],
                'metadata': {},
                'tables': [],
                'images': []
            }
            
            with pdfplumber.open(file_path) as pdf:
                # Extract metadata
                extracted_data['metadata'] = {
                    'title': pdf.metadata.get('Title', ''),
                    'author': pdf.metadata.get('Author', ''),
                    'creator': pdf.metadata.get('Creator', ''),
                    'producer': pdf.metadata.get('Producer', ''),
                    'subject': pdf.metadata.get('Subject', ''),
                    'creation_date': str(pdf.metadata.get('CreationDate', '')),
                    'total_pages': len(pdf.pages)
                }
                
                # Extract text from each page
                for i, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        extracted_data['pages'].append({
                            'page_number': i + 1,
                            'text': page_text
                        })
                        extracted_data['text'] += f"\n\nPage {i + 1}:\n{page_text}"
                    
                    # Extract tables
                    tables = page.extract_tables()
                    if tables:
                        for j, table in enumerate(tables):
                            extracted_data['tables'].append({
                                'page': i + 1,
                                'table_number': j + 1,
                                'data': table
                            })
                    
                    # Extract images (basic detection) – no KeyError on 'bbox'
                    if getattr(page, 'images', None):
                        for img in page.images:
                            # pdfplumber commonly exposes x0, x1, top, bottom (or y0, y1)
                            x0 = img.get('x0')
                            x1 = img.get('x1') or (x0 + img.get('width', 0) if x0 is not None else None)
                            top = img.get('top') or img.get('y0')
                            bottom = img.get('bottom') or img.get('y1') or (top + img.get('height', 0) if top is not None else None)
                            bbox = img.get('bbox') or (x0, top, x1, bottom)
                            extracted_data['images'].append({'page': i + 1, 'bbox': bbox})
            
            return extracted_data
            
        except Exception as e:
            raise Exception(f"PDF extraction failed: {str(e)}")
    
    def process_image_content(self, file_path: str) -> Dict[str, Any]:
        """Process image files"""
        try:
            with Image.open(file_path) as img:
                # Convert to base64 for storage
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                img_data = base64.b64encode(buffer.getvalue()).decode()
                
                return {
                    'text': f"Image file: {os.path.basename(file_path)}",
                    'metadata': {
                        'format': img.format,
                        'size': img.size,
                        'mode': img.mode
                    },
                    'image_data': img_data
                }
        except Exception as e:
            raise Exception(f"Image processing failed: {str(e)}")
    
    def create_vector_store(self, documents: List[LangChainDocument], doc_id: str) -> Optional[FAISS]:
        """Create FAISS vector store from documents"""
        if not self.embeddings or not documents:
            return None
            
        try:
            # Create vector store
            vectorstore = FAISS.from_documents(documents, self.embeddings)
            
            # Save vector store
            vector_path = os.path.join(settings.MEDIA_ROOT, 'vectors', f'doc_{doc_id}')
            os.makedirs(os.path.dirname(vector_path), exist_ok=True)
            vectorstore.save_local(vector_path)
            
            return vectorstore
            
        except Exception as e:
            print(f"Vector store creation failed: {e}")
            return None
    
    def load_vector_store(self, doc_id: str) -> Optional[FAISS]:
        """Load existing vector store"""
        if not self.embeddings:
            return None
            
        try:
            vector_path = os.path.join(settings.MEDIA_ROOT, 'vectors', f'doc_{doc_id}')
            if os.path.exists(vector_path):
                # Explicitly allow deserialization for FAISS persisted stores (LangChain 0.3+)
                return FAISS.load_local(vector_path, self.embeddings, allow_dangerous_deserialization=True)
            return None
        except Exception as e:
            print(f"Vector store loading failed: {e}")
            return None
    
    def create_rag_chain(self, vectorstore: FAISS, conversation_memory: Optional[ConversationBufferMemory] = None) -> Optional[RetrievalQA]:
        """Create RAG chain for document Q&A"""
        if not self.llm or not vectorstore:
            return None
            
        try:
            # Create custom prompt for educational context
            prompt_template = """
            You are an educational AI assistant helping students understand document content.
            Use the following pieces of context to answer the question at the end.
            If you don't know the answer based on the context, just say you don't know.
            Provide clear, educational explanations suitable for students.

            Context:
            {context}

            Question: {question}
            
            Helpful Answer:"""
            
            PROMPT = PromptTemplate(
                template=prompt_template,
                input_variables=["context", "question"]
            )
            
            # Create retrieval QA chain
            if conversation_memory:
                chain = ConversationalRetrievalChain.from_llm(
                    llm=self.llm,
                    retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
                    memory=conversation_memory,
                    return_source_documents=True
                )
            else:
                chain = RetrievalQA.from_chain_type(
                    llm=self.llm,
                    chain_type="stuff",
                    retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
                    chain_type_kwargs={"prompt": PROMPT},
                    return_source_documents=True
                )
            
            return chain
            
        except Exception as e:
            print(f"RAG chain creation failed: {e}")
            return None
    
    def query_document(self, document: Document, question: str, conversation_memory: Optional[ConversationBufferMemory] = None) -> Dict[str, Any]:
        """Query document using RAG"""
        try:
            # Try to load vector store
            vectorstore = self.load_vector_store(str(document.id))
            
            if vectorstore and self.llm:
                # Use RAG with vector store
                rag_chain = self.create_rag_chain(vectorstore, conversation_memory)
                
                if rag_chain:
                    if conversation_memory:
                        # Conversational retrieval
                        result = rag_chain({"question": question})
                        answer = result.get('answer', 'Could not generate answer')
                        sources = result.get('source_documents', [])
                    else:
                        # Standard retrieval QA
                        result = rag_chain({"query": question})
                        answer = result.get('result', 'Could not generate answer')
                        sources = result.get('source_documents', [])
                    
                    return {
                        'answer': answer,
                        'method': 'rag_vector',
                        'sources': [
                            {
                                'content': doc.page_content[:200] + '...',
                                'metadata': doc.metadata
                            }
                            for doc in sources
                        ]
                    }
            
            # Fallback to simple text search if no vector store
            if document.extracted_text and self.llm:
                # Simple context-based answering
                context = document.extracted_text[:3000]  # Limit context
                
                prompt = f"""
                Based on this document content:
                
                {context}
                
                Student question: {question}
                
                Please answer the question based on the document content provided.
                If the answer is not in the document, say so clearly.
                """
                
                try:
                    data = {
                        "model": "llama3.2",
                        "prompt": prompt,
                        "stream": False
                    }
                    response = requests.post("http://localhost:11434/api/generate", json=data)
                    response_data = response.json()
                    answer = response_data.get("response", "Sorry, I couldn't understand the question.")
                    
                    return {
                        'answer': answer,
                        'method': 'simple_context',
                        'sources': []
                    }
                except Exception:
                    return {
                        'answer': "Document processed but AI service unavailable",
                        'method': 'fallback',
                        'sources': []
                    }
            
            return {
                'answer': "Document not properly processed or AI service unavailable",
                'method': 'error',
                'sources': []
            }
            
        except Exception as e:
            return {
                'answer': f"Error querying document: {str(e)}",
                'method': 'error',
                'sources': []
            }
    
    # Enhanced Algorithm Question Generation with AI Validation
    def generate_questions_from_document(self, document_id: int, difficulty_levels: List[str] = ['3', '4', '5'], 
                                       questions_per_level: int = 10, require_llm: bool = True,
                                       min_per_level: int = 10, max_per_level: int = None, 
                                       progress_callback=None) -> Dict[str, Any]:
        """
        Enhanced AI question generation with dynamic counts and uniqueness validation
        
        Features:
        - Dynamic question counts based on document length (≈1 question per 600 words)
        - Minimum 10 questions per level, maximum 100 per level (configurable)
        - Strict uniqueness filtering to prevent near-duplicates
        - Cross-level uniqueness checking
        - Algorithm/CS concept pattern detection for additional uniqueness
        
        Args:
            document_id: ID of the document to process
            difficulty_levels: List of difficulty levels ['3', '4', '5']
            questions_per_level: Base questions per level (used as fallback if dynamic calc fails)
            require_llm: Whether to require LLM availability
            min_per_level: Minimum questions per level (default: 10)
            max_per_level: Maximum questions per level (default: None, capped at 100)
            
        Returns:
            Dict with success status, question counts, and metadata
        """
        try:
            from .models import Document, QuestionBank
            
            print(f"🎯 Enhanced Dynamic Algorithm Question Generation Starting...")
            print(f"📊 Base target: {questions_per_level} questions per level (will be dynamically adjusted)")
            
            # Get document with proper error handling
            try:
                document = Document.objects.get(id=document_id)
                print(f"📄 Document: {document.title}")
            except Document.DoesNotExist:
                return {'success': False, 'error': f'Document with ID {document_id} not found'}
            
            # Check document content
            if not document.extracted_text or len(document.extracted_text.strip()) < 100:
                return {'success': False, 'error': 'Insufficient document content for question generation'}
            
            # Check if LLM is required and available
            if require_llm:
                if not self.llm or not llm_is_up("http://127.0.0.1:11434"):
                    # Stop here; caller decides how to respond
                    raise OllamaUnavailableError("Ollama is not reachable at http://127.0.0.1:11434")
            
            # Dynamic question count calculation based on document length
            # Heuristic: more text → more questions (cap to protect DB)
            import re
            words = len(re.findall(r'\w+', document.extracted_text))
            target_per_level = max(min_per_level, min(words // 600, 50))   # ~1 Q per 600 words, min 10, cap 50/level
            if max_per_level is not None:
                target_per_level = min(target_per_level, max_per_level)
            
            print(f"📊 Dynamic calculation: {words} words → {target_per_level} questions per level")
            print(f"📊 Total target: {target_per_level * len(difficulty_levels)} questions across all levels")
            
            # Question normalization function for uniqueness detection
            def _norm_q(t: str) -> str:
                t = t.lower()
                t = re.sub(r'\s+', ' ', t)
                t = re.sub(r'[^a-z0-9\.\-\+\=×÷% ]+', '', t)
                return t.strip()
            
            def _num_sig(t: str) -> str:
                nums = re.findall(r'\d+(?:\.\d+)?', t)
                return ','.join(sorted(nums))
            
            # Initialize enhanced algorithm validator
            validator = EnhancedAlgorithmValidator(self)
            
            # Generate guaranteed algorithm questions for each difficulty level
            all_questions = []
            level_breakdown = {}
            global_seen_text = set()  # Track globally unique question text
            global_seen_nums = set()  # Track globally unique number patterns
            
            for difficulty in difficulty_levels:
                difficulty_name = {'3': 'Basic', '4': 'Intermediate', '5': 'Advanced'}[difficulty]
                print(f"🔥 Generating Level {difficulty} ({difficulty_name}) questions...")
                
                # Emit progress callback for level start
                if progress_callback:
                    progress_callback(level=difficulty, status='processing', count=0)
                
                # Generate guaranteed algorithm questions with dynamic count
                level_questions = validator.generate_guaranteed_algorithm_questions(
                    document=document,
                    difficulty_level=int(difficulty),
                    count=target_per_level,
                    require_llm=require_llm
                )
                
                # Enhanced uniqueness filtering (no near-duplicates) 
                seen_text, seen_nums = set(), set()
                unique = []
                for q in level_questions:
                    qt = q.get('question', '')
                    k1, k2 = _norm_q(qt), _num_sig(qt)
                    
                    # Check both local (level) and global uniqueness
                    if k1 in seen_text or k1 in global_seen_text or (k2 and (k2 in seen_nums or k2 in global_seen_nums)):
                        print(f"  🔄 Skipping duplicate question: {qt[:50]}...")
                        continue
                    
                    seen_text.add(k1)
                    global_seen_text.add(k1)
                    if k2:
                        seen_nums.add(k2)
                        global_seen_nums.add(k2)
                    unique.append(q)
                
                level_questions = unique
                print(f"  📋 After uniqueness filtering: {len(level_questions)} unique questions")
                
                # Save questions to database with enhanced visibility flags
                saved_question_ids = []
                for q_data in level_questions:
                    try:
                        # Use lightweight retriever to enhance answers/explanations from document
                        probe = try_extract_answer_from_doc(
                            document.extracted_text,
                            q_data.get('question', ''),
                            known_correct=(q_data.get('correct_answer') or q_data.get('correct_value') or q_data.get('numeric_answer'))
                        )
                        final_correct = q_data.get('correct_answer') or probe['answer_text'] or ""
                        final_expl = q_data.get('explanation') or probe['explanation'] or ""
                        
                        question = QuestionBank.objects.create(
                            document=document,
                            question_text=q_data.get('question', 'Generated algorithm question'),
                            question_type=q_data.get('type', 'multiple_choice'),
                            difficulty_level=str(difficulty),
                            subject='algorithms',
                            option_a=q_data.get('option_a', ''),
                            option_b=q_data.get('option_b', ''),
                            option_c=q_data.get('option_c', ''),
                            option_d=q_data.get('option_d', ''),
                            correct_answer=final_correct,
                            explanation=final_expl,
                            is_approved=True,
                            created_by_ai=True,
                            is_generated=True,   # <-- IMPORTANT for filter
                        )
                        saved_question_ids.append(question.id)
                    except Exception as save_error:
                        print(f"⚠️ Failed to save question: {save_error}")
                
                level_breakdown[f'level_{difficulty}'] = len(saved_question_ids)
                all_questions.extend(saved_question_ids)
                
                # Flexible minimum enforcement per level
                min_threshold = max(1, min_per_level // 2)  # Allow at least half the minimum
                if len(saved_question_ids) == 0:
                    print(f"⚠️ Level {difficulty}: No questions generated - this may indicate a problem")
                elif len(saved_question_ids) < min_threshold:
                    print(f"⚠️ Level {difficulty}: Only {len(saved_question_ids)} questions (below threshold {min_threshold})")
                    # Don't fail immediately, but note the issue
                elif len(saved_question_ids) < min_per_level:
                    print(f"⚠️ Level {difficulty}: {len(saved_question_ids)} < ideal {min_per_level} (partial success)")
                else:
                    print(f"✅ Level {difficulty}: {len(saved_question_ids)} questions saved (minimum {min_per_level} met)")
                # Emit progress callback for level completion
                if progress_callback:
                    progress_callback(level=difficulty, status='completed', count=len(saved_question_ids))
            
            # Final total assessment (more flexible)
            total_saved = len(all_questions)
            required_total = min_per_level * len(difficulty_levels)
            minimum_total = max(len(difficulty_levels), required_total // 3)  # At least 1 per level or 1/3 of target
            
            if total_saved == 0:
                raise InsufficientQuestionsError("No questions generated at all - system failure")
            elif total_saved < minimum_total:
                raise InsufficientQuestionsError(
                    f"Total questions {total_saved} < minimum threshold {minimum_total} (too few for viable test)"
                )
            elif total_saved < required_total:
                print(f"⚠️ Generated {total_saved}/{required_total} questions (partial success - usable but below target)")
            else:
                print(f"✅ Generated {total_saved}/{required_total} questions (full success)")
            
            # Update document
            document.questions_generated_count = len(all_questions)
            document.save()
            
            total_generated = len(all_questions)
            print(f"🎉 Total generated: {total_generated} validated unique algorithm questions")
            print(f"📊 Document stats: {words} words → {target_per_level} questions per level")
            print(f"🔍 Uniqueness: {len(global_seen_text)} unique question patterns detected")
            
            return {
                'success': True,
                'questions_generated': total_generated,
                'question_ids': all_questions,
                'breakdown': level_breakdown,
                'validation_method': 'AI_enhanced_algorithm_validation_with_uniqueness',
                'document_stats': {
                    'word_count': words,
                    'target_per_level': target_per_level,
                    'unique_patterns': len(global_seen_text),
                    'total_levels': len(difficulty_levels)
                },
                'generation_method': 'dynamic_count_with_uniqueness_filtering'
            }
            
        except Exception as e:
            print(f"❌ Enhanced algorithm question generation failed: {str(e)}")
            return {'success': False, 'error': str(e)}


# Enhanced Algorithm Validation System
class EnhancedAlgorithmValidator:
    """AI-powered algorithm question validation system with RAG learning and adaptive optimization"""
    
    def __init__(self, processor):
        self.processor = processor
        self.validation_feedback_store = []  # RAG learning storage
        self.performance_metrics = {
            'total_validations': 0,
            'algorithm_detected': 0,
            'confidence_scores': [],
            'generation_success_rate': 0.0
        }
        self.adaptive_threshold = 0.6  # Dynamic confidence threshold
    
    def is_algorithm_question(self, question_text: str) -> tuple:
        """
        Enhanced AI-powered algorithm question validation with confidence scoring and adaptive learning
        Returns: (is_algorithm: bool, confidence_score: float)
        """
        # Update performance tracking
        self.performance_metrics['total_validations'] += 1
        
        if not self.processor.llm:
            return self._fallback_algorithm_validation(question_text)
        
        try:
            validation_prompt = f"""
Analyze this question and determine if it is a genuine computer science/algorithm question requiring algorithmic reasoning.

QUESTION: "{question_text}"

ALGORITHM/CS CRITERIA:
- Contains algorithms, data structures, or computational concepts
- Involves complexity analysis (Big O notation, time/space complexity)
- Requires algorithmic thinking or problem-solving strategies
- Uses CS terminology (sorting, searching, recursion, dynamic programming, etc.)
- Involves machine learning, deep learning, or AI concepts
- Contains programming concepts or code analysis

NON-CS EXAMPLES:
- Pure mathematics without algorithmic context
- Historical facts, geography, literature
- Simple definitions without computational reasoning

Provide your analysis in this EXACT format:
ANALYSIS: [Detailed reasoning about algorithmic content and complexity]
IS_ALGORITHM: [YES or NO]
CONFIDENCE: [Score from 0.0 to 1.0 where 1.0 = definitely algorithmic/CS]

Your response:"""

            response = self.processor.llm.invoke(validation_prompt)
            
            # Enhanced parsing with multiple validation checks
            is_algorithm = any(phrase in response.upper() for phrase in ["IS_ALGORITHM: YES", "IS_ALGORITHM:YES", "IS ALGORITHM: YES"])
            
            # Extract confidence score with better parsing
            confidence = 0.7  # Default
            try:
                # Try multiple patterns for confidence extraction
                patterns = [
                    r'CONFIDENCE:\s*([0-9]*\.?[0-9]+)',
                    r'CONFIDENCE\s*=\s*([0-9]*\.?[0-9]+)',
                    r'SCORE:\s*([0-9]*\.?[0-9]+)'
                ]
                
                for pattern in patterns:
                    conf_match = re.search(pattern, response.upper())
                    if conf_match:
                        confidence = float(conf_match.group(1))
                        break
                        
            except:
                confidence = 0.7
            
            # Adaptive threshold adjustment based on performance
            if len(self.performance_metrics['confidence_scores']) > 10:
                avg_confidence = sum(self.performance_metrics['confidence_scores'][-10:]) / 10
                if avg_confidence < 0.5:
                    self.adaptive_threshold = max(0.4, self.adaptive_threshold - 0.05)
                elif avg_confidence > 0.8:
                    self.adaptive_threshold = min(0.7, self.adaptive_threshold + 0.05)
            
            # Store enhanced feedback for RAG learning
            self.validation_feedback_store.append({
                'question': question_text,
                'is_algorithm': is_algorithm,
                'confidence': confidence,
                'ai_analysis': response,
                'timestamp': str(os.path.getmtime(__file__)),
                'adaptive_threshold_used': self.adaptive_threshold,
                'validation_number': self.performance_metrics['total_validations']
            })
            
            # Update performance metrics
            self.performance_metrics['confidence_scores'].append(confidence)
            if is_algorithm:
                self.performance_metrics['algorithm_detected'] += 1
            
            return is_algorithm, confidence
            
        except Exception as e:
            print(f"AI validation failed: {e}")
            return self._fallback_algorithm_validation(question_text)
    
    def _fallback_algorithm_validation(self, question_text: str) -> tuple:
        """Enhanced fallback keyword-based algorithm validation with improved accuracy"""
        # Algorithm and CS indicators with weighted scoring
        algorithm_indicators = {
            # High-weight algorithmic terms
            'algorithm': 2.0, 'complexity': 2.0, 'big o': 2.0, 'o(n)': 2.0, 'o(log n)': 2.0,
            'time complexity': 2.0, 'space complexity': 2.0, 'asymptotic': 2.0,
            
            # Data structures
            'data structure': 2.0, 'array': 1.5, 'linked list': 2.0, 'stack': 1.5, 'queue': 1.5,
            'tree': 1.5, 'binary tree': 2.0, 'graph': 1.5, 'hash table': 2.0, 'heap': 1.5,
            
            # Sorting and searching algorithms
            'sorting': 2.0, 'merge sort': 2.0, 'quick sort': 2.0, 'bubble sort': 1.5,
            'binary search': 2.0, 'linear search': 1.5, 'searching': 1.5,
            
            # Programming paradigms
            'recursion': 2.0, 'iteration': 1.5, 'dynamic programming': 2.0, 'greedy': 2.0,
            'divide and conquer': 2.0, 'backtracking': 2.0, 'memoization': 2.0,
            
            # Machine Learning and AI
            'machine learning': 2.0, 'deep learning': 2.0, 'neural network': 2.0,
            'gradient descent': 2.0, 'backpropagation': 2.0, 'convolutional': 2.0,
            'lstm': 2.0, 'transformer': 2.0, 'attention': 1.5, 'embedding': 1.5,
            'training': 1.0, 'validation': 1.0, 'overfitting': 1.5, 'regularization': 1.5,
            'activation function': 2.0, 'relu': 1.5, 'sigmoid': 1.5, 'tanh': 1.5,
            'dropout': 1.5, 'batch normalization': 1.5, 'loss function': 1.5,
            
            # Computer science concepts
            'computational': 1.5, 'optimization': 1.5, 'heuristic': 1.5, 'nondeterministic': 2.0,
            'polynomial': 1.5, 'exponential': 1.5, 'logarithmic': 1.5,
            
            # Programming and software engineering
            'function': 1.0, 'variable': 1.0, 'loop': 1.5, 'conditional': 1.5,
            'class': 1.0, 'object': 1.0, 'inheritance': 1.5, 'polymorphism': 1.5,
            
            # Specific algorithms
            'dijkstra': 2.0, 'floyd': 2.0, 'kruskal': 2.0, 'prim': 2.0,
            'breadth first': 2.0, 'depth first': 2.0, 'topological': 2.0
        }
        
        # Convert to lowercase for matching
        question_lower = question_text.lower()
        
        # Calculate weighted algorithm score
        algorithm_score = 0.0
        for indicator, weight in algorithm_indicators.items():
            if indicator in question_lower:
                algorithm_score += weight
        
        # Check for algorithmic patterns
        algorithm_patterns = [
            r'O\([^)]+\)',              # Big O notation: O(n), O(log n)
            r'time complexity',         # Time complexity analysis
            r'space complexity',        # Space complexity analysis
            r'worst case',              # Complexity analysis terms
            r'best case',
            r'average case',
            r'def \w+\(',              # Function definitions
            r'class \w+',              # Class definitions
            r'for .+ in',              # Loop patterns
            r'while .+:',              # While loops
            r'if .+:',                 # Conditional statements
        ]
        
        for pattern in algorithm_patterns:
            if re.search(pattern, question_text, re.IGNORECASE):
                algorithm_score += 1.5
        
        # Determine if algorithmic (adjusted threshold)
        is_algorithm = algorithm_score >= 2.0  # Lower threshold than math due to diverse CS concepts
        
        # Enhanced confidence calculation
        confidence = min(0.95, max(0.25, algorithm_score * 0.12))
        
        # Bonus confidence for strong algorithmic indicators
        if any(strong_indicator in question_lower for strong_indicator in 
               ['algorithm', 'complexity', 'big o', 'data structure', 'machine learning', 'deep learning']):
            confidence = min(0.95, confidence + 0.15)
        
        return is_algorithm, confidence
    
    def generate_guaranteed_algorithm_questions(self, document, difficulty_level: int, count: int = 10, require_llm: bool = True) -> list:
        """Generate guaranteed algorithmic questions with validation"""
        questions = []
        attempts = 0
        max_attempts = count * 4  # Allow more attempts for robustness
        failed_attempts = 0
        max_consecutive_failures = 5  # Allow some failures before giving up
        
        while len(questions) < count and attempts < max_attempts:
            attempts += 1
            
            try:
                # Generate question using enhanced algorithm-focused prompting
                question_data = self._generate_algorithm_focused_question(document, difficulty_level)
                
                if question_data:
                    # Enhanced validation with adaptive threshold
                    is_algorithm, confidence = self.is_algorithm_question(question_data['question'])
                    
                    if is_algorithm and confidence > self.adaptive_threshold:
                        question_data['confidence_score'] = confidence
                        question_data['validation_method'] = 'AI_enhanced_adaptive'
                        questions.append(question_data)
                        failed_attempts = 0  # Reset failure counter on success
                        print(f"  ✅ Validated algorithm question (confidence: {confidence:.2f}, threshold: {self.adaptive_threshold:.2f})")
                    else:
                        # Question generated but didn't meet validation criteria
                        print(f"  🔄 Question didn't meet criteria (is_algorithm: {is_algorithm}, confidence: {confidence:.2f})")
                        failed_attempts += 1
                else:
                    # Question generation returned None
                    print(f"  ⚠️ Question generation returned None (attempt {attempts})")
                    failed_attempts += 1
                    
            except Exception as e:
                # Handle individual generation failures gracefully
                print(f"  ⚠️ Generation attempt {attempts} failed: {str(e)}")
                failed_attempts += 1
                
                # If we have too many consecutive failures, try fallback methods
                if failed_attempts >= max_consecutive_failures and not require_llm:
                    print(f"  🔄 Switching to fallback generation after {failed_attempts} failures")
                    try:
                        fallback_question = self._generate_advanced_algorithm_question(document, difficulty_level)
                        if fallback_question:
                            fallback_question['confidence_score'] = 0.90
                            fallback_question['validation_method'] = 'advanced_guaranteed_fallback'
                            questions.append(fallback_question)
                            failed_attempts = 0  # Reset failure counter
                            print(f"  📝 Generated fallback algorithm question")
                    except Exception as fallback_error:
                        print(f"  ❌ Fallback generation also failed: {fallback_error}")
        
        # Check if we have enough questions
        if len(questions) < count:
            if require_llm:
                # Only raise exception if LLM is required and we don't have enough
                if len(questions) == 0:
                    raise OllamaUnavailableError(f"Failed to generate any questions after {attempts} attempts")
                else:
                    # We have some questions but not enough - this is still partial success
                    print(f"  ⚠️ Generated {len(questions)}/{count} questions (partial success)")
            else:
                # Try to fill remaining with guaranteed fallback questions
                print(f"  🔄 Filling remaining {count - len(questions)} questions with guaranteed fallbacks")
                while len(questions) < count:
                    try:
                        advanced_question = self._generate_advanced_algorithm_question(document, difficulty_level)
                        if advanced_question:
                            advanced_question['confidence_score'] = 0.95
                            advanced_question['validation_method'] = 'premium_guaranteed'
                            questions.append(advanced_question)
                            print(f"  🔢 Added premium algorithm question ({len(questions)}/{count})")
                        else:
                            break  # Can't generate any more
                    except Exception as e:
                        print(f"  ❌ Premium generation failed: {e}")
                        break
        
        # Update generation success rate
        self.performance_metrics['generation_success_rate'] = len(questions) / count if count > 0 else 0
        
        return questions[:count]  # Ensure exact count
    
    def get_performance_metrics(self) -> dict:
        """Get comprehensive performance metrics for the validation system"""
        total = self.performance_metrics['total_validations']
        if total == 0:
            return {
                'message': 'No validations performed yet',
                'total_validations': 0,
                'algorithm_detected_count': 0,
                'algorithm_detection_rate': 0.0,
                'average_confidence': 0.0,
                'current_adaptive_threshold': self.adaptive_threshold,
                'system_status': 'not_initialized'
            }
        
        algorithm_detection_rate = (self.performance_metrics['algorithm_detected'] / total) * 100
        
        # Safe division for average confidence
        confidence_scores = self.performance_metrics['confidence_scores']
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        
        # Calculate confidence distribution
        high_confidence = sum(1 for score in confidence_scores if score >= 0.8)
        medium_confidence = sum(1 for score in confidence_scores if 0.5 <= score < 0.8)
        low_confidence = sum(1 for score in confidence_scores if score < 0.5)
        
        return {
            'total_validations': total,
            'algorithm_detected_count': self.performance_metrics['algorithm_detected'],
            'algorithm_detection_rate': round(algorithm_detection_rate, 2),
            'average_confidence': round(avg_confidence, 3),
            'current_adaptive_threshold': self.adaptive_threshold,
            'confidence_distribution': {
                'high_confidence_validations': high_confidence,
                'medium_confidence_validations': medium_confidence,
                'low_confidence_validations': low_confidence
            },
            'recent_feedback_count': len(self.validation_feedback_store),
            'system_status': 'optimal' if avg_confidence > 0.7 else 'needs_tuning'
        }
    
    def optimize_validation_system(self) -> dict:
        """Analyze performance and optimize validation parameters"""
        metrics = self.get_performance_metrics()
        
        if metrics.get('total_validations', 0) < 5:
            return {'message': 'Insufficient data for optimization. Need at least 5 validations.'}
        
        optimizations_made = []
        
        # Adjust adaptive threshold based on performance
        avg_confidence = metrics['average_confidence']
        if avg_confidence < 0.6:
            self.adaptive_threshold = max(0.4, self.adaptive_threshold - 0.1)
            optimizations_made.append(f"Lowered threshold to {self.adaptive_threshold}")
        elif avg_confidence > 0.85:
            self.adaptive_threshold = min(0.75, self.adaptive_threshold + 0.05)
            optimizations_made.append(f"Raised threshold to {self.adaptive_threshold}")
        
        # Analyze recent validation patterns
        recent_validations = self.validation_feedback_store[-10:] if len(self.validation_feedback_store) >= 10 else self.validation_feedback_store
        
        if recent_validations:
            recent_algorithm_rate = sum(1 for v in recent_validations if v['is_algorithm']) / len(recent_validations)
            if recent_algorithm_rate > 0.9:
                optimizations_made.append("High algorithm detection rate - system performing well")
            elif recent_algorithm_rate < 0.3:
                optimizations_made.append("Low algorithm detection rate - may need recalibration")
        
        return {
            'optimization_status': 'completed',
            'optimizations_made': optimizations_made,
            'new_adaptive_threshold': self.adaptive_threshold,
            'performance_after_optimization': self.get_performance_metrics()
        }
    
    def _generate_algorithm_focused_question(self, document, difficulty_level: int) -> dict:
        """Generate algorithm-focused question using AI with enhanced prompting"""
        if not self.processor.llm:
            return None
        
        try:
            content_snippet = document.extracted_text[:800]
            
            difficulty_prompts = {
                3: "BASIC algorithm question about fundamental concepts, simple data structures, or basic complexity analysis",
                4: "INTERMEDIATE algorithm question requiring understanding of algorithms, data structures, and their analysis",
                5: "ADVANCED algorithm or deep learning question requiring sophisticated reasoning about complex systems"
            }
            
            algorithm_prompt = f"""
You are a computer science professor creating educational questions. Based on this content, create an ALGORITHM/CS question:

CONTENT: {content_snippet}

REQUIREMENTS - MUST BE CS/ALGORITHM RELATED:
- Question MUST involve algorithms, data structures, complexity analysis, or computational thinking
- Include specific algorithmic problems, CS concepts, or complexity scenarios  
- Focus on: algorithms, data structures, machine learning, deep learning, complexity analysis, programming concepts
- Create a {difficulty_prompts.get(difficulty_level, 'computer science')}

Return your response as JSON ONLY, no other text:
{{
    "question": "Algorithm or computer science question",
    "option_a": "Technical option A",
    "option_b": "Technical option B",
    "option_c": "Technical option C", 
    "option_d": "Technical option D",
    "correct_answer": "A or B or C or D",
    "explanation": "Technical explanation with algorithmic reasoning"
}}

Generate the algorithm question now:"""

            response = self.processor.llm.invoke(algorithm_prompt)
            
            # Use robust JSON parsing
            payload = extract_json_payload(response)
            if not payload:
                print(f"  ⚠️ LLM returned unparsable content: {response[:100]}...")
                return None  # Return None instead of raising exception
            
            # Validate required fields
            required_fields = ['question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer']
            missing_fields = [field for field in required_fields if field not in payload]
            if missing_fields:
                print(f"  ⚠️ LLM response missing fields: {missing_fields}")
                return None  # Return None instead of raising exception
            
            # Add defaults and return
            payload['type'] = payload.get('type', 'multiple_choice')
            payload['explanation'] = payload.get('explanation', 'AI-generated algorithmic explanation')
            
            return payload
            
        except Exception as e:
            print(f"Algorithm-focused generation failed: {e}")
            return None
    
    def _generate_advanced_algorithm_question(self, document, difficulty_level: int) -> dict:
        """Generate advanced high-quality algorithmic questions with diverse content"""
        try:
            # Algorithm question templates by difficulty
            if difficulty_level == 3:  # Basic
                templates = [
                    {
                        'type': 'complexity',
                        'generator': lambda: self._create_complexity_question(),
                        'description': 'Basic complexity analysis'
                    },
                    {
                        'type': 'data_structure',
                        'generator': lambda: self._create_data_structure_question(),
                        'description': 'Basic data structure concepts'
                    }
                ]
            elif difficulty_level == 4:  # Intermediate
                templates = [
                    {
                        'type': 'sorting',
                        'generator': lambda: self._create_sorting_question(),
                        'description': 'Sorting algorithm analysis'
                    },
                    {
                        'type': 'search',
                        'generator': lambda: self._create_search_question(),
                        'description': 'Search algorithm concepts'
                    }
                ]
            else:  # Advanced (Level 5)
                templates = [
                    {
                        'type': 'ml_concept',
                        'generator': lambda: self._create_ml_question(),
                        'description': 'Machine learning concepts'
                    },
                    {
                        'type': 'advanced_ds',
                        'generator': lambda: self._create_advanced_ds_question(),
                        'description': 'Advanced data structures'
                    }
                ]
            
            # Select random template and generate question
            import random
            template = random.choice(templates)
            return template['generator']()
            
        except Exception as e:
            print(f"Advanced algorithm generation failed: {e}")
            return self._generate_fallback_algorithm_question(document, difficulty_level)
    
    def _create_complexity_question(self) -> dict:
        """Create basic complexity analysis questions"""
        questions = [
            {
                'question': "What is the time complexity of binary search?",
                'option_a': "O(n)",
                'option_b': "O(log n)",
                'option_c': "O(n²)",
                'option_d': "O(1)",
                'correct_answer': "B",
                'explanation': "Binary search divides the search space in half each iteration, resulting in O(log n) complexity"
            },
            {
                'question': "What is the worst-case time complexity of bubble sort?",
                'option_a': "O(n)",
                'option_b': "O(n log n)",
                'option_c': "O(n²)",
                'option_d': "O(1)",
                'correct_answer': "C",
                'explanation': "Bubble sort compares each element with every other element, resulting in O(n²) complexity"
            },
            {
                'question': "Which data structure provides O(1) average time complexity for insertion and deletion?",
                'option_a': "Array",
                'option_b': "Linked List",
                'option_c': "Hash Table",
                'option_d': "Binary Tree",
                'correct_answer': "C",
                'explanation': "Hash tables provide O(1) average time complexity for insertion, deletion, and lookup operations"
            }
        ]
        import random
        return random.choice(questions)
    
    def _create_data_structure_question(self) -> dict:
        """Create basic data structure questions"""
        questions = [
            {
                'question': "Which data structure follows LIFO (Last In, First Out) principle?",
                'option_a': "Queue",
                'option_b': "Stack",
                'option_c': "Array",
                'option_d': "Linked List",
                'correct_answer': "B",
                'explanation': "Stack follows LIFO principle where the last element added is the first one to be removed"
            },
            {
                'question': "What is the main advantage of a linked list over an array?",
                'option_a': "Faster random access",
                'option_b': "Less memory usage",
                'option_c': "Dynamic size allocation",
                'option_d': "Better cache locality",
                'correct_answer': "C",
                'explanation': "Linked lists can dynamically allocate memory during runtime, unlike arrays with fixed size"
            },
            {
                'question': "In a binary tree, what is the maximum number of children each node can have?",
                'option_a': "1",
                'option_b': "2",
                'option_c': "3",
                'option_d': "Unlimited",
                'correct_answer': "B",
                'explanation': "By definition, each node in a binary tree can have at most 2 children (left and right)"
            }
        ]
        import random
        return random.choice(questions)
    
    def _create_sorting_question(self) -> dict:
        """Create sorting algorithm questions"""
        questions = [
            {
                'question': "Which sorting algorithm is most efficient for small datasets?",
                'option_a': "Merge Sort",
                'option_b': "Quick Sort",
                'option_c': "Insertion Sort",
                'option_d': "Heap Sort",
                'correct_answer': "C",
                'explanation': "Insertion sort has low overhead and performs well on small datasets despite O(n²) complexity"
            },
            {
                'question': "Which sorting algorithm guarantees O(n log n) time complexity in all cases?",
                'option_a': "Quick Sort",
                'option_b': "Bubble Sort",
                'option_c': "Merge Sort",
                'option_d': "Selection Sort",
                'correct_answer': "C",
                'explanation': "Merge sort consistently performs at O(n log n) regardless of input distribution"
            },
            {
                'question': "What is the space complexity of merge sort?",
                'option_a': "O(1)",
                'option_b': "O(log n)",
                'option_c': "O(n)",
                'option_d': "O(n²)",
                'correct_answer': "C",
                'explanation': "Merge sort requires O(n) additional space for the temporary arrays used during merging"
            }
        ]
        import random
        return random.choice(questions)
    
    def _create_search_question(self) -> dict:
        """Create search algorithm questions"""
        questions = [
            {
                'question': "Binary search requires the input array to be:",
                'option_a': "Unsorted",
                'option_b': "Sorted",
                'option_c': "Of prime length",
                'option_d': "Containing unique elements only",
                'correct_answer': "B",
                'explanation': "Binary search works by repeatedly dividing a sorted array in half to find the target element"
            },
            {
                'question': "What is the time complexity of linear search in the worst case?",
                'option_a': "O(1)",
                'option_b': "O(log n)",
                'option_c': "O(n)",
                'option_d': "O(n²)",
                'correct_answer': "C",
                'explanation': "Linear search may need to check every element in the worst case, resulting in O(n) complexity"
            },
            {
                'question': "Which search algorithm is most suitable for unsorted data?",
                'option_a': "Binary Search",
                'option_b': "Interpolation Search",
                'option_c': "Linear Search",
                'option_d': "Jump Search",
                'correct_answer': "C",
                'explanation': "Linear search works on both sorted and unsorted data, making it suitable for unsorted arrays"
            }
        ]
        import random
        return random.choice(questions)
    
    def _create_ml_question(self) -> dict:
        """Create machine learning questions"""
        questions = [
            {
                'question': "Which activation function is commonly used in hidden layers of deep neural networks?",
                'option_a': "Sigmoid",
                'option_b': "ReLU",
                'option_c': "Tanh",
                'option_d': "Linear",
                'correct_answer': "B",
                'explanation': "ReLU is preferred in hidden layers due to reduced vanishing gradient problem and computational efficiency"
            },
            {
                'question': "What is the main purpose of backpropagation in neural networks?",
                'option_a': "Forward pass computation",
                'option_b': "Weight initialization",
                'option_c': "Gradient computation and weight updates",
                'option_d': "Data preprocessing",
                'correct_answer': "C",
                'explanation': "Backpropagation computes gradients and updates weights to minimize the loss function"
            },
            {
                'question': "Which technique helps prevent overfitting in deep learning models?",
                'option_a': "Increasing model complexity",
                'option_b': "Dropout",
                'option_c': "Using more training data only",
                'option_d': "Removing validation set",
                'correct_answer': "B",
                'explanation': "Dropout randomly deactivates neurons during training, preventing over-reliance on specific features"
            }
        ]
        import random
        return random.choice(questions)
    
    def _create_advanced_ds_question(self) -> dict:
        """Create advanced data structure questions"""
        questions = [
            {
                'question': "What is the primary advantage of a B-tree over a binary search tree?",
                'option_a': "Simpler implementation",
                'option_b': "Better performance for disk-based storage",
                'option_c': "Lower memory usage",
                'option_d': "Faster insertion only",
                'correct_answer': "B",
                'explanation': "B-trees are optimized for disk storage with high branching factor, reducing disk I/O operations"
            },
            {
                'question': "Which data structure is best suited for implementing a priority queue?",
                'option_a': "Array",
                'option_b': "Linked List",
                'option_c': "Heap",
                'option_d': "Stack",
                'correct_answer': "C",
                'explanation': "Heaps provide O(log n) insertion and O(log n) extraction of the highest priority element"
            },
            {
                'question': "What is the time complexity of finding the shortest path in a graph using Dijkstra's algorithm?",
                'option_a': "O(V)",
                'option_b': "O(V + E)",
                'option_c': "O(V log V + E)",
                'option_d': "O(V²)",
                'correct_answer': "C",
                'explanation': "Dijkstra's algorithm using a min-heap has complexity O(V log V + E) where V is vertices and E is edges"
            }
        ]
        import random
        return random.choice(questions)
    
    def _generate_fallback_algorithm_question(self, document, difficulty_level: int) -> dict:
        """Generate fallback algorithm question when AI generation fails"""
        try:
            if difficulty_level <= 3:
                return self._create_complexity_question()
            elif difficulty_level == 4:
                return self._create_sorting_question()
            else:
                return self._create_ml_question()
        except Exception as e:
            # Ultimate fallback
            return {
                'question': "What does 'algorithm' mean in computer science?",
                'option_a': "A programming language",
                'option_b': "A step-by-step procedure for solving a problem",
                'option_c': "A type of computer hardware",
                'option_d': "A software application",
                'correct_answer': "B",
                'explanation': "An algorithm is a well-defined sequence of steps for solving a computational problem",
                'type': 'multiple_choice'
            }
    
    def _create_search_question(self) -> dict:
        """Create search algorithm questions"""
        questions = [
            {
                'question': "Which search algorithm works only on sorted arrays?",
                'option_a': "Linear Search",
                'option_b': "Binary Search",
                'option_c': "Depth-First Search",
                'option_d': "Breadth-First Search",
                'correct_answer': "B",
                'explanation': "Binary search requires the array to be sorted to work correctly by dividing the search space"
            },
            {
                'question': "What is the time complexity of linear search in the worst case?",
                'option_a': "O(1)",
                'option_b': "O(log n)",
                'option_c': "O(n)",
                'option_d': "O(n²)",
                'correct_answer': "C",
                'explanation': "Linear search may need to check every element in the worst case, giving O(n) complexity"
            },
            {
                'question': "Which traversal visits all nodes at depth d before visiting nodes at depth d+1?",
                'option_a': "Depth-First Search",
                'option_b': "Breadth-First Search",
                'option_c': "Binary Search",
                'option_d': "Linear Search",
                'correct_answer': "B",
                'explanation': "Breadth-First Search explores all nodes at the current depth before moving to the next level"
            }
        ]
        return random.choice(questions)
    
    def _create_ml_question(self) -> dict:
        """Create machine learning questions"""
        questions = [
            {
                'question': "What is the purpose of a loss function in machine learning?",
                'option_a': "To increase model complexity",
                'option_b': "To measure prediction error",
                'option_c': "To store training data",
                'option_d': "To visualize results",
                'correct_answer': "B",
                'explanation': "A loss function quantifies how far the model's predictions are from the actual values"
            },
            {
                'question': "What does 'overfitting' mean in machine learning?",
                'option_a': "Model performs well on training but poorly on new data",
                'option_b': "Model has too few parameters",
                'option_c': "Training takes too long",
                'option_d': "Model is too simple",
                'correct_answer': "A",
                'explanation': "Overfitting occurs when a model memorizes training data but fails to generalize to new examples"
            },
            {
                'question': "Which activation function is most commonly used in deep learning?",
                'option_a': "Sigmoid",
                'option_b': "Tanh",
                'option_c': "ReLU",
                'option_d': "Linear",
                'correct_answer': "C",
                'explanation': "ReLU (Rectified Linear Unit) is widely used due to its simplicity and effectiveness in deep networks"
            }
        ]
        return random.choice(questions)
    
    def _create_advanced_ds_question(self) -> dict:
        """Create advanced data structure questions"""
        questions = [
            {
                'question': "What is the main advantage of a B-tree over a binary search tree?",
                'option_a': "Simpler implementation",
                'option_b': "Better performance for disk-based storage",
                'option_c': "Uses less memory",
                'option_d': "Faster insertion",
                'correct_answer': "B",
                'explanation': "B-trees are optimized for systems with slow disk access by minimizing disk reads"
            },
            {
                'question': "Which data structure is best for implementing a priority queue?",
                'option_a': "Array",
                'option_b': "Linked List",
                'option_c': "Heap",
                'option_d': "Stack",
                'correct_answer': "C",
                'explanation': "Heaps provide efficient O(log n) insertion and O(log n) removal of the highest priority element"
            },
            {
                'question': "What is the time complexity of finding the shortest path using Dijkstra's algorithm?",
                'option_a': "O(V + E)",
                'option_b': "O(V log V + E)",
                'option_c': "O(V²)",
                'option_d': "O(E log V)",
                'correct_answer': "B",
                'explanation': "Dijkstra's algorithm with a priority queue has complexity O(V log V + E) where V is vertices and E is edges"
            }
        ]
        return random.choice(questions)


# Global document processor instance
document_processor = DocumentProcessor()
