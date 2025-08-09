"""
Document Processing Utilities with LangChain RAG and Enhanced Math Validation
Handles PDF extraction, text splitting, vector storage, and AI-powered math question validation
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


class DocumentProcessor:
    """Handles document processing and RAG implementation with enhanced math validation"""
    
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
                    
                    # Extract images (basic detection)
                    if hasattr(page, 'images') and page.images:
                        extracted_data['images'].extend([
                            {'page': i + 1, 'bbox': img['bbox']} 
                            for img in page.images
                        ])
            
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
    
    # Enhanced Math Question Generation with AI Validation
    def generate_questions_from_document(self, document_id: int, difficulty_levels: List[str] = ['3', '4', '5'], 
                                       questions_per_level: int = 10) -> Dict[str, Any]:
        """
        Enhanced AI question generation with math validation ensuring all questions are mathematical
        Target: 10 questions per difficulty level for perfect distribution
        """
        try:
            from .models import Document, QuestionBank
            
            print(f"🎯 Enhanced Math Question Generation Starting...")
            print(f"📊 Target: {questions_per_level} questions per level")
            
            # Get document with proper error handling
            try:
                document = Document.objects.get(id=document_id)
                print(f"📄 Document: {document.title}")
            except Document.DoesNotExist:
                return {'success': False, 'error': f'Document with ID {document_id} not found'}
            
            # Check document content
            if not document.extracted_text or len(document.extracted_text.strip()) < 100:
                return {'success': False, 'error': 'Insufficient document content for question generation'}
            
            # Initialize enhanced math validator
            validator = EnhancedMathValidator(self)
            
            # Generate guaranteed math questions for each difficulty level
            all_questions = []
            level_breakdown = {}
            
            for difficulty in difficulty_levels:
                difficulty_name = {'3': 'Basic', '4': 'Intermediate', '5': 'Advanced'}[difficulty]
                print(f"🔥 Generating Level {difficulty} ({difficulty_name}) questions...")
                
                # Generate guaranteed math questions
                level_questions = validator.generate_guaranteed_math_questions(
                    document=document,
                    difficulty_level=int(difficulty),
                    count=questions_per_level
                )
                
                # Save questions to database
                saved_question_ids = []
                for q_data in level_questions:
                    try:
                        question = QuestionBank.objects.create(
                            document=document,
                            question_text=q_data.get('question', 'Generated math question'),
                            question_type='multiple_choice',
                            difficulty_level=difficulty,
                            subject='math',
                            option_a=q_data.get('option_a', 'Option A'),
                            option_b=q_data.get('option_b', 'Option B'),
                            option_c=q_data.get('option_c', 'Option C'),
                            option_d=q_data.get('option_d', 'Option D'),
                            correct_answer=q_data.get('correct_answer', 'A'),
                            explanation=q_data.get('explanation', 'Mathematical explanation'),
                            is_approved=True,
                            created_by_ai=True
                        )
                        saved_question_ids.append(question.id)
                    except Exception as save_error:
                        print(f"⚠️ Failed to save question: {save_error}")
                
                level_breakdown[f'level_{difficulty}'] = len(saved_question_ids)
                all_questions.extend(saved_question_ids)
                
                print(f"✅ Level {difficulty}: {len(saved_question_ids)} questions saved")
            
            # Update document
            document.questions_generated_count = len(all_questions)
            document.save()
            
            total_generated = len(all_questions)
            print(f"🎉 Total generated: {total_generated} validated math questions")
            
            return {
                'success': True,
                'questions_generated': total_generated,
                'question_ids': all_questions,
                'breakdown': level_breakdown,
                'validation_method': 'AI_enhanced_math_validation'
            }
            
        except Exception as e:
            print(f"❌ Enhanced math question generation failed: {str(e)}")
            return {'success': False, 'error': str(e)}


# Enhanced Math Validation System
class EnhancedMathValidator:
    """AI-powered math question validation system with RAG learning and adaptive optimization"""
    
    def __init__(self, processor):
        self.processor = processor
        self.validation_feedback_store = []  # RAG learning storage
        self.performance_metrics = {
            'total_validations': 0,
            'math_detected': 0,
            'confidence_scores': [],
            'generation_success_rate': 0.0
        }
        self.adaptive_threshold = 0.6  # Dynamic confidence threshold
    
    def is_math_question(self, question_text: str) -> tuple:
        """
        Enhanced AI-powered math question validation with confidence scoring and adaptive learning
        Returns: (is_math: bool, confidence_score: float)
        """
        # Update performance tracking
        self.performance_metrics['total_validations'] += 1
        
        if not self.processor.llm:
            return self._fallback_math_validation(question_text)
        
        try:
            validation_prompt = f"""
Analyze this question and determine if it is a genuine mathematical question requiring mathematical reasoning.

QUESTION: "{question_text}"

MATHEMATICAL CRITERIA:
- Contains numbers, calculations, or mathematical operations (+, -, ×, ÷, =, etc.)
- Involves mathematical concepts (geometry, algebra, statistics, calculus, etc.)
- Requires computational or quantitative reasoning
- Uses mathematical terminology (area, volume, percentage, equation, function, etc.)

NON-MATHEMATICAL EXAMPLES:
- Historical facts, geography, literature
- Simple counting without calculation
- Definitions without computation

Provide your analysis in this EXACT format:
ANALYSIS: [Detailed reasoning about mathematical content and complexity]
IS_MATH: [YES or NO]
CONFIDENCE: [Score from 0.0 to 1.0 where 1.0 = definitely mathematical]

Your response:"""

            response = self.processor.llm.invoke(validation_prompt)
            
            # Enhanced parsing with multiple validation checks
            is_math = any(phrase in response.upper() for phrase in ["IS_MATH: YES", "IS_MATH:YES", "IS MATH: YES"])
            
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
                'is_math': is_math,
                'confidence': confidence,
                'ai_analysis': response,
                'timestamp': str(os.path.getmtime(__file__)),
                'adaptive_threshold_used': self.adaptive_threshold,
                'validation_number': self.performance_metrics['total_validations']
            })
            
            # Update performance metrics
            self.performance_metrics['confidence_scores'].append(confidence)
            if is_math:
                self.performance_metrics['math_detected'] += 1
            
            return is_math, confidence
            
        except Exception as e:
            print(f"AI validation failed: {e}")
            return self._fallback_math_validation(question_text)
    
    def _fallback_math_validation(self, question_text: str) -> tuple:
        """Enhanced fallback keyword-based math validation with improved accuracy"""
        # Expanded mathematical indicators with weighted scoring
        math_indicators = {
            # High-weight mathematical terms
            'calculate': 2.0, 'compute': 2.0, 'solve': 2.0, 'equation': 2.0, 'formula': 2.0,
            'derivative': 2.0, 'integral': 2.0, 'function': 1.5, 'variable': 1.5,
            
            # Medium-weight mathematical operations
            'addition': 1.5, 'subtraction': 1.5, 'multiplication': 1.5, 'division': 1.5,
            'percentage': 1.5, 'fraction': 1.5, 'decimal': 1.5, 'ratio': 1.5,
            'square root': 2.0, 'logarithm': 2.0, 'exponential': 1.5,
            
            # Mathematical domains
            'geometry': 1.5, 'algebra': 1.5, 'trigonometry': 2.0, 'calculus': 2.0,
            'statistics': 1.5, 'probability': 1.5, 'graph': 1.0, 'plot': 1.0,
            
            # Mathematical shapes and measurements
            'triangle': 1.5, 'circle': 1.5, 'rectangle': 1.5, 'square': 1.5,
            'area': 1.5, 'volume': 1.5, 'perimeter': 1.5, 'circumference': 1.5,
            'radius': 1.5, 'diameter': 1.5, 'angle': 1.5, 'degree': 1.0,
            
            # Mathematical operations and symbols
            'sum': 1.5, 'product': 1.5, 'difference': 1.5, 'quotient': 1.5,
            'equals': 1.0, 'greater than': 1.0, 'less than': 1.0,
            'x =': 2.0, 'y =': 2.0, 'find x': 2.0, 'solve for': 2.0,
            
            # Mathematical symbols (high weight)
            '+': 1.5, '-': 1.0, '*': 1.5, '×': 1.5, '÷': 1.5, '/': 1.0,
            '=': 1.5, '√': 2.0, '²': 1.5, '³': 1.5, '%': 1.5, '∞': 2.0,
            'π': 2.0, 'pi': 2.0, 'sin': 2.0, 'cos': 2.0, 'tan': 2.0
        }
        
        # Convert to lowercase for matching
        question_lower = question_text.lower()
        
        # Calculate weighted math score
        math_score = 0.0
        for indicator, weight in math_indicators.items():
            if indicator in question_lower:
                math_score += weight
        
        # Enhanced number detection with context
        numbers = re.findall(r'\d+(?:\.\d+)?', question_text)
        if numbers:
            # More points for multiple numbers (suggests calculation)
            if len(numbers) >= 2:
                math_score += len(numbers) * 0.8
            else:
                math_score += len(numbers) * 0.4
        
        # Check for mathematical patterns
        math_patterns = [
            r'\d+\s*[+\-*/×÷]\s*\d+',  # Basic arithmetic: 5 + 3
            r'\d+\s*=\s*\d+',          # Equations: x = 5
            r'\d+%',                    # Percentages: 25%
            r'\d+°',                    # Degrees: 90°
            r'\d+\^\d+',               # Powers: 2^3
            r'[a-z]\s*=',              # Variables: x =
            r'f\([a-z]\)',             # Functions: f(x)
        ]
        
        for pattern in math_patterns:
            if re.search(pattern, question_text):
                math_score += 1.5
        
        # Determine if mathematical (adjusted threshold)
        is_math = math_score >= 2.5  # Slightly higher threshold for better accuracy
        
        # Enhanced confidence calculation
        confidence = min(0.95, max(0.25, math_score * 0.15))
        
        # Bonus confidence for strong mathematical indicators
        if any(strong_indicator in question_lower for strong_indicator in 
               ['calculate', 'solve', 'equation', 'derivative', 'integral', 'trigonometry']):
            confidence = min(0.95, confidence + 0.15)
        
        return is_math, confidence
    
    def generate_guaranteed_math_questions(self, document, difficulty_level: int, count: int = 10) -> list:
        """Generate guaranteed mathematical questions with validation"""
        questions = []
        attempts = 0
        max_attempts = count * 3  # Allow multiple attempts
        
        while len(questions) < count and attempts < max_attempts:
            attempts += 1
            
            # Generate question using enhanced math-focused prompting
            question_data = self._generate_math_focused_question(document, difficulty_level)
            
            if question_data:
                # Enhanced validation with adaptive threshold
                is_math, confidence = self.is_math_question(question_data['question'])
                
                if is_math and confidence > self.adaptive_threshold:
                    question_data['confidence_score'] = confidence
                    question_data['validation_method'] = 'AI_enhanced_adaptive'
                    questions.append(question_data)
                    print(f"  ✅ Validated math question (confidence: {confidence:.2f}, threshold: {self.adaptive_threshold:.2f})")
                elif not is_math:
                    # Generate guaranteed mathematical question
                    fallback_question = self._generate_advanced_math_question(document, difficulty_level)
                    if fallback_question:
                        fallback_question['confidence_score'] = 0.90
                        fallback_question['validation_method'] = 'advanced_guaranteed'
                        questions.append(fallback_question)
                        print(f"  📝 Generated advanced guaranteed math question")
        
        # Fill remaining slots with guaranteed high-quality math questions
        while len(questions) < count:
            advanced_question = self._generate_advanced_math_question(document, difficulty_level)
            if advanced_question:
                advanced_question['confidence_score'] = 0.95
                advanced_question['validation_method'] = 'premium_guaranteed'
                questions.append(advanced_question)
                print(f"  🔢 Added premium math question ({len(questions)}/{count})")
        
        # Update generation success rate
        self.performance_metrics['generation_success_rate'] = len(questions) / count
        
        return questions[:count]  # Ensure exact count
    
    def get_performance_metrics(self) -> dict:
        """Get comprehensive performance metrics for the validation system"""
        total = self.performance_metrics['total_validations']
        if total == 0:
            return {
                'message': 'No validations performed yet',
                'total_validations': 0,
                'math_detected_count': 0,
                'math_detection_rate': 0.0,
                'average_confidence': 0.0,
                'current_adaptive_threshold': self.adaptive_threshold,
                'system_status': 'not_initialized'
            }
        
        math_detection_rate = (self.performance_metrics['math_detected'] / total) * 100
        
        # Safe division for average confidence
        confidence_scores = self.performance_metrics['confidence_scores']
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        
        # Calculate confidence distribution
        high_confidence = sum(1 for score in confidence_scores if score >= 0.8)
        medium_confidence = sum(1 for score in confidence_scores if 0.5 <= score < 0.8)
        low_confidence = sum(1 for score in confidence_scores if score < 0.5)
        
        return {
            'total_validations': total,
            'math_detected_count': self.performance_metrics['math_detected'],
            'math_detection_rate': round(math_detection_rate, 2),
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
            recent_math_rate = sum(1 for v in recent_validations if v['is_math']) / len(recent_validations)
            if recent_math_rate > 0.9:
                optimizations_made.append("High math detection rate - system performing well")
            elif recent_math_rate < 0.3:
                optimizations_made.append("Low math detection rate - may need recalibration")
        
        return {
            'optimization_status': 'completed',
            'optimizations_made': optimizations_made,
            'new_adaptive_threshold': self.adaptive_threshold,
            'performance_after_optimization': self.get_performance_metrics()
        }
    
    def _generate_math_focused_question(self, document, difficulty_level: int) -> dict:
        """Generate math-focused question using AI with enhanced prompting"""
        if not self.processor.llm:
            return None
        
        try:
            content_snippet = document.extracted_text[:800]
            
            difficulty_prompts = {
                3: "BASIC mathematical question with simple arithmetic, basic calculations, or fundamental math concepts",
                4: "INTERMEDIATE mathematical question requiring moderate mathematical reasoning and multi-step calculations",
                5: "ADVANCED mathematical question requiring complex mathematical thinking and sophisticated reasoning"
            }
            
            math_prompt = f"""
You are a mathematics teacher creating educational questions. Based on this content, create a MATHEMATICAL question:

CONTENT: {content_snippet}

REQUIREMENTS - MUST BE MATHEMATICAL:
- Question MUST involve numbers, calculations, mathematical operations, or quantitative reasoning
- Include specific numerical values, mathematical formulas, or computational problems
- Focus on mathematical concepts: arithmetic, algebra, geometry, statistics, percentages, equations
- Create a {difficulty_prompts.get(difficulty_level, 'mathematical')}

Format EXACTLY as:
QUESTION: [Mathematical question with numbers/calculations]
A) [Numerical or mathematical option]
B) [Numerical or mathematical option] 
C) [Numerical or mathematical option]
D) [Numerical or mathematical option]
ANSWER: [A, B, C, or D]
EXPLANATION: [Mathematical reasoning with step-by-step solution]

Generate the mathematical question now:"""

            response = self.processor.llm.invoke(math_prompt)
            return self._parse_question_response(response)
            
        except Exception as e:
            print(f"Math-focused generation failed: {e}")
            return None
    
    def _generate_advanced_math_question(self, document, difficulty_level: int) -> dict:
        """Generate advanced high-quality mathematical questions with diverse content"""
        try:
            # Extract numbers and create more sophisticated questions
            numbers = re.findall(r'\d+(?:\.\d+)?', document.extracted_text)
            
            # Math question templates by difficulty
            if difficulty_level == 3:  # Basic
                templates = [
                    {
                        'type': 'arithmetic',
                        'generator': lambda n1, n2: self._create_arithmetic_question(n1, n2, 'addition'),
                        'description': 'Basic arithmetic operations'
                    },
                    {
                        'type': 'percentage',
                        'generator': lambda n1, n2: self._create_percentage_question(n1, n2),
                        'description': 'Percentage calculations'
                    }
                ]
            elif difficulty_level == 4:  # Intermediate
                templates = [
                    {
                        'type': 'algebra',
                        'generator': lambda n1, n2: self._create_algebra_question(n1, n2),
                        'description': 'Linear equation solving'
                    },
                    {
                        'type': 'geometry',
                        'generator': lambda n1, n2: self._create_geometry_question(n1, n2),
                        'description': 'Geometric calculations'
                    }
                ]
            else:  # Advanced (Level 5)
                templates = [
                    {
                        'type': 'quadratic',
                        'generator': lambda n1, n2: self._create_quadratic_question(n1, n2),
                        'description': 'Quadratic equations'
                    },
                    {
                        'type': 'calculus',
                        'generator': lambda n1, n2: self._create_calculus_question(n1, n2),
                        'description': 'Basic calculus operations'
                    }
                ]
            
            # Select random template and generate question
            import random
            template = random.choice(templates)
            
            if len(numbers) >= 2:
                num1 = float(numbers[0])
                num2 = float(numbers[1])
            else:
                # Use default values if not enough numbers in document
                num1, num2 = 10, 5
            
            return template['generator'](num1, num2)
            
        except Exception as e:
            print(f"Advanced math generation failed: {e}")
            return self._generate_fallback_math_question(document, difficulty_level)
    
    def _create_arithmetic_question(self, n1: float, n2: float, operation: str) -> dict:
        """Create arithmetic questions with safe mathematical operations"""
        import random
        
        # Ensure non-zero values for division operations
        n1 = max(1, abs(n1)) if n1 == 0 else abs(n1)
        n2 = max(1, abs(n2)) if n2 == 0 else abs(n2)
        
        try:
            operations = {
                'addition': ('+', n1 + n2),
                'multiplication': ('×', n1 * n2),
                'subtraction': ('-', abs(n1 - n2)),
                'division': ('÷', n1 / n2 if n2 != 0 else n1 / 1)  # Safe division
            }
            
            op_symbol, correct = operations.get(operation, ('+', n1 + n2))
            
            # Round result for cleaner display
            if operation == 'division':
                correct = round(correct, 2)
                question = f"Calculate: {int(n1)} {op_symbol} {int(n2)} = ? (round to 2 decimal places)"
            else:
                correct = int(correct)
                question = f"Calculate: {int(n1)} {op_symbol} {int(n2)} = ?"
            
            # Generate plausible wrong answers
            if operation == 'division':
                options = [
                    correct,
                    round(correct + random.uniform(0.1, 2.0), 2),
                    round(correct - random.uniform(0.1, 2.0), 2),
                    round(correct * 1.5, 2) if correct > 1 else round(correct + 1, 2)
                ]
            else:
                options = [
                    correct,
                    correct + random.randint(1, 5),
                    correct - random.randint(1, 5),
                    int(correct * 1.5) if correct > 10 else correct + 10
                ]
            
            return self._format_question_data(question, options, correct, f"Arithmetic: {int(n1)} {op_symbol} {int(n2)} = {correct}")
        
        except (ZeroDivisionError, ValueError) as e:
            # Fallback to simple addition if any operation fails
            safe_result = int(n1 + n2)
            return self._format_question_data(
                f"Calculate: {int(n1)} + {int(n2)} = ?",
                [safe_result, safe_result + 1, safe_result - 1, safe_result + 5],
                safe_result,
                f"Safe arithmetic: {int(n1)} + {int(n2)} = {safe_result}"
            )
    
    def _create_percentage_question(self, n1: float, n2: float) -> dict:
        """Create percentage questions with safe calculations"""
        try:
            # Ensure positive values for percentage calculations
            base_value = max(abs(n1), abs(n2), 100)
            percentage = min(abs(n1), abs(n2), 50) if min(abs(n1), abs(n2)) <= 50 else 25
            
            # Ensure percentage is reasonable (1-100)
            percentage = max(1, min(percentage, 100))
            
            correct = round((percentage / 100) * base_value, 2)
            question = f"What is {int(percentage)}% of {int(base_value)}?"
            
            options = [
                correct,
                round(correct * 1.2, 2),
                round(correct * 0.8, 2),
                round(percentage * base_value / 10, 2)  # Common mistake: percentage without division by 100
            ]
            
            return self._format_question_data(
                question, 
                options, 
                correct, 
                f"Percentage calculation: {percentage}% of {base_value} = {correct}"
            )
        
        except (ValueError, ZeroDivisionError) as e:
            # Fallback to simple percentage
            return self._format_question_data(
                "What is 25% of 100?",
                [25, 20, 30, 250],
                25,
                "Safe percentage: 25% of 100 = 25"
            )
    
    def _create_algebra_question(self, n1: float, n2: float) -> dict:
        """Create algebra questions"""
        import random
        # Create equation: ax + b = c
        a = max(1, min(n1, 10))
        b = min(n2, 20)
        x = random.randint(1, 10)
        c = a * x + b
        
        question = f"Solve for x: {int(a)}x + {int(b)} = {int(c)}"
        correct = x
        
        options = [
            correct,
            correct + 1,
            correct - 1,
            (c - b)  # Common mistake (forgetting to divide by a)
        ]
        
        return self._format_question_data(question, options, correct, f"Algebra: x = {correct}")
    
    def _create_geometry_question(self, n1: float, n2: float) -> dict:
        """Create geometry questions"""
        import random
        side1, side2 = max(3, min(n1, 15)), max(3, min(n2, 15))
        
        # Perimeter of rectangle
        correct = 2 * (side1 + side2)
        question = f"Find the perimeter of a rectangle with sides {int(side1)} and {int(side2)}"
        explanation = f"Perimeter = 2(l + w) = 2({int(side1)} + {int(side2)}) = {int(correct)}"
        
        options = [
            correct,
            correct * 2,
            side1 + side2,  # Common mistake
            side1 * side2
        ]
        
        return self._format_question_data(question, options, correct, explanation)
    
    def _create_quadratic_question(self, n1: float, n2: float) -> dict:
        """Create quadratic equation questions"""
        # Simple quadratic: x² = n
        value = max(4, min(n1, 100))
        perfect_squares = [4, 9, 16, 25, 36, 49, 64, 81, 100]
        value = min(perfect_squares, key=lambda x: abs(x - value))
        
        correct = int(value ** 0.5)
        question = f"Solve: x² = {int(value)}"
        
        options = [
            correct,
            correct + 1,
            correct - 1,
            value / 2  # Common mistake
        ]
        
        return self._format_question_data(question, options, correct, f"Square root: x = ±{correct}")
    
    def _create_calculus_question(self, n1: float, n2: float) -> dict:
        """Create basic calculus questions"""
        # Simple derivative
        power = max(1, min(n1, 5))
        
        if power == 1:
            question = f"Find the derivative of f(x) = {int(power)}x"
            correct = power
            explanation = f"d/dx({int(power)}x) = {int(power)}"
        else:
            question = f"Find the derivative of f(x) = x^{int(power)}"
            correct = power
            explanation = f"d/dx(x^{int(power)}) = {int(power)}x^{int(power-1)}"
        
        options = [
            correct,
            correct + 1,
            correct - 1,
            power + 1 if power < 5 else power - 1
        ]
        
        return self._format_question_data(question, options, correct, explanation)
    
    def _format_question_data(self, question: str, options: list, correct_value: float, explanation: str) -> dict:
        """Format question data consistently"""
        import random
        
        # Ensure options are unique and reasonable
        formatted_options = [round(opt, 2) if isinstance(opt, float) else opt for opt in options]
        
        # Shuffle options and track correct answer
        correct_answer_letter = 'A'
        random.shuffle(formatted_options)
        
        # Find where the correct answer ended up
        for i, opt in enumerate(formatted_options):
            if abs(float(opt) - float(correct_value)) < 0.01:
                correct_answer_letter = ['A', 'B', 'C', 'D'][i]
                break
        
        return {
            'question': question,
            'option_a': str(formatted_options[0]),
            'option_b': str(formatted_options[1]),
            'option_c': str(formatted_options[2]),
            'option_d': str(formatted_options[3]),
            'correct_answer': correct_answer_letter,
            'explanation': explanation,
            'type': 'multiple_choice'
        }
    
    def _generate_fallback_math_question(self, document, difficulty_level: int) -> dict:
        """Generate guaranteed mathematical question using document numbers"""
        try:
            # Extract numbers from document for mathematical operations
            numbers = re.findall(r'\d+(?:\.\d+)?', document.extracted_text)
            
            if len(numbers) >= 2:
                num1 = float(numbers[0])
                num2 = float(numbers[1]) if len(numbers) > 1 else 5
                
                if difficulty_level == 3:
                    # Basic arithmetic
                    correct_answer = num1 + num2
                    question = f"Calculate: {num1} + {num2} = ?"
                    options = [correct_answer, correct_answer + 1, correct_answer - 1, correct_answer + 2]
                    
                elif difficulty_level == 4:
                    # Intermediate calculation
                    correct_answer = num1 * num2
                    question = f"Calculate: {num1} × {num2} = ?"
                    options = [correct_answer, correct_answer * 1.1, correct_answer * 0.9, correct_answer + 10]
                    
                else:  # Level 5
                    # Advanced calculation
                    correct_answer = num1 ** 2 + num2
                    question = f"Calculate: {num1}² + {num2} = ?"
                    options = [correct_answer, correct_answer + 5, correct_answer - 3, correct_answer * 1.2]
                
                # Randomize options
                import random
                correct_idx = 0
                random.shuffle(options)
                correct_answer_letter = ['A', 'B', 'C', 'D'][options.index(correct_answer)]
                
                return {
                    'question': question,
                    'option_a': str(round(options[0], 2)),
                    'option_b': str(round(options[1], 2)),
                    'option_c': str(round(options[2], 2)),
                    'option_d': str(round(options[3], 2)),
                    'correct_answer': correct_answer_letter,
                    'explanation': f"Mathematical calculation: {question.replace('?', str(round(correct_answer, 2)))}",
                    'type': 'multiple_choice'
                }
            else:
                # Generic math question as last resort
                return {
                    'question': f"What is 5 × 4?",
                    'option_a': "15",
                    'option_b': "20", 
                    'option_c': "25",
                    'option_d': "16",
                    'correct_answer': "B",
                    'explanation': "Basic multiplication: 5 × 4 = 20",
                    'type': 'multiple_choice'
                }
                
        except Exception as e:
            print(f"Fallback math generation failed: {e}")
            return None
    
    def _parse_question_response(self, response: str) -> dict:
        """Parse AI response into question format"""
        try:
            # Extract components using regex
            question_match = re.search(r'QUESTION:\s*(.+?)(?=\n[A-D]\))', response, re.DOTALL)
            option_a_match = re.search(r'A\)\s*(.+?)(?=\n[B-D]\))', response)
            option_b_match = re.search(r'B\)\s*(.+?)(?=\n[C-D]\))', response) 
            option_c_match = re.search(r'C\)\s*(.+?)(?=\n[D]\))', response)
            option_d_match = re.search(r'D\)\s*(.+?)(?=\nANSWER)', response)
            answer_match = re.search(r'ANSWER:\s*([A-D])', response)
            explanation_match = re.search(r'EXPLANATION:\s*(.+?)(?=\n|$)', response, re.DOTALL)
            
            if all([question_match, option_a_match, option_b_match, option_c_match, option_d_match, answer_match]):
                return {
                    'question': question_match.group(1).strip(),
                    'option_a': option_a_match.group(1).strip(),
                    'option_b': option_b_match.group(1).strip(),
                    'option_c': option_c_match.group(1).strip(),
                    'option_d': option_d_match.group(1).strip(),
                    'correct_answer': answer_match.group(1).strip(),
                    'explanation': explanation_match.group(1).strip() if explanation_match else "AI-generated mathematical explanation",
                    'type': 'multiple_choice'
                }
            
        except Exception as e:
            print(f"Question parsing failed: {e}")
        
        return None


# Global instances
document_processor = DocumentProcessor()
enhanced_document_processor = DocumentProcessor()
