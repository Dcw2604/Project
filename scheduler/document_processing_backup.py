"""
Document Processing Utilities with LangChain RAG
Handles PDF extraction, text splitting, and vector storage
"""
import os
import tempfile
import json
        """Load vector store from disk"""
        if not self.embeddings:
            return None
            
        try:
            vector_path = os.path.join(settings.MEDIA_ROOT, 'vectors', f'doc_{doc_id}')
            if os.path.exists(vector_path):
                return FAISS.load_local(vector_path, self.embeddings)
            return None
        except Exception as e:
            print(f"Vector store loading failed: {e}")
            return None
    
    def _get_or_create_vector_store(self, document):
        """Get existing vector store or create new one for document"""
        try:
            # Try to load existing vector store
            vector_store = self.load_vector_store(str(document.id))
            
            if vector_store:
                return vector_store
            
            # Create new vector store if none exists
            if document.extracted_text:
                texts = [document.extracted_text]
                langchain_docs = [
                    LangChainDocument(
                        page_content=text,
                        metadata={"source": f"document_{document.id}", "chunk": i}
                    )
                    for i, text in enumerate(texts)
                ]
                
                vector_store = self.create_vector_store(langchain_docs, str(document.id))
                return vector_store
            
            return None
            
        except Exception as e:
            print(f"Error creating vector store: {e}")
            return None
import pdfplumber
from PIL import Image
import io
import base64
from typing import List, Dict, Any, Optional

# LangChain imports
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA
from langchain.schema import Document as LangChainDocument
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain

from django.conf import settings
from .models import Document, ChatInteraction


class DocumentProcessor:
    """Handles document processing and RAG implementation"""
    
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
                return FAISS.load_local(vector_path, self.embeddings)
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
    
    def process_document(self, document: Document) -> bool:
        """Process document and create vector store"""
        try:
            document.processing_status = 'processing'
            document.save()
            
            file_path = document.file_path
            
            # Extract content based on document type
            if document.document_type == 'pdf':
                extracted_data = self.extract_pdf_content(file_path)
            elif document.document_type == 'image':
                extracted_data = self.process_image_content(file_path)
            else:
                # Text file
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                extracted_data = {
                    'text': content,
                    'metadata': {'type': 'text'}
                }
            
            # Save extracted text and metadata
            document.extracted_text = extracted_data['text']
            document.metadata = json.dumps(extracted_data.get('metadata', {}))
            
            # Create documents for vector store
            if extracted_data['text']:
                # Split text into chunks
                texts = self.text_splitter.split_text(extracted_data['text'])
                
                # Create LangChain documents
                langchain_docs = [
                    LangChainDocument(
                        page_content=text,
                        metadata={
                            'source': document.title,
                            'doc_id': document.id,
                            'chunk_id': i
                        }
                    )
                    for i, text in enumerate(texts)
                ]
                
                # Create vector store
                vectorstore = self.create_vector_store(langchain_docs, str(document.id))
                
                if vectorstore:
                    document.processing_status = 'completed'
                else:
                    document.processing_status = 'completed'  # Still mark as completed even without vectors
                    document.processing_error = "Vector store creation failed, but text extraction succeeded"
            else:
                document.processing_status = 'failed'
                document.processing_error = "No text content extracted"
            
            document.save()
            return document.processing_status == 'completed'
            
        except Exception as e:
            document.processing_status = 'failed'
            document.processing_error = str(e)
            document.save()
            return False
    
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
                    import requests
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
    
    def generate_questions_from_document(self, document_id: int, difficulty_levels: List[str] = ['3', '4', '5'], 
                                       questions_per_level: int = 6) -> Dict[str, Any]:
        """
        Enhanced AI question generation with increased questions per difficulty level
        - Level 3 (Basic): 8 questions
        - Level 4 (Intermediate): 6 questions  
        - Level 5 (Advanced): 4 questions
        - Total: Up to 18 questions per document
        """
        try:
            from .models import Document, QuestionBank
            
            print(f"DEBUG: Attempting to retrieve document with ID: {document_id}")
            
            # Get document with proper error handling
            try:
                document = Document.objects.get(id=document_id)
                print(f"DEBUG: Document retrieved successfully: {document.title}")
                print(f"DEBUG: Document extracted_text length: {len(document.extracted_text) if document.extracted_text else 0}")
            except Document.DoesNotExist:
                print(f"ERROR: Document with ID {document_id} does not exist")
                return {'success': False, 'error': f'Document with ID {document_id} not found'}
            
            # Check if document has extracted text
            if not document.extracted_text:
                print(f"ERROR: Document {document_id} has no extracted text")
                return {'success': False, 'error': 'No extracted text found in document'}
            
            # Ensure we have sufficient text (minimum 100 characters)
            if len(document.extracted_text.strip()) < 100:
                print(f"ERROR: Document {document_id} has insufficient text: {len(document.extracted_text)} characters")
                return {'success': False, 'error': f'Document has insufficient text for question generation ({len(document.extracted_text)} chars)'}
            
            print(f"SUCCESS: Document {document_id} has {len(document.extracted_text)} characters of text")
            
            # Enhanced question generation with more questions per level
            question_targets = {
                '3': 8,   # Increased from ~3-5 to 8 basic questions
                '4': 6,   # Increased from ~3-5 to 6 intermediate questions  
                '5': 4    # Increased from ~2-3 to 4 advanced questions
            }
            
            # Split text into more chunks for better question variety
            text_chunks = self.text_splitter.split_text(document.extracted_text)
            if len(text_chunks) > 6:
                text_chunks = text_chunks[:6]  # Use up to 6 chunks for variety
            
            generated_questions = []
            
            print(f"🎯 Enhanced Question Generation: Target questions per level: {question_targets}")
            print(f"📄 Processing {len(text_chunks)} text chunks from document")
            
            for difficulty in difficulty_levels:
                difficulty_name = {'3': 'Basic', '4': 'Intermediate', '5': 'Advanced'}[difficulty]
                target_count = question_targets.get(difficulty, 3)
                
                print(f"🔥 Generating {target_count} Level {difficulty} ({difficulty_name}) questions...")
                
                questions_for_level = []
                
                # Generate questions from multiple chunks for variety
                chunks_to_use = min(len(text_chunks), 3)  # Use up to 3 chunks per level
                questions_per_chunk = max(1, target_count // chunks_to_use)
                remaining_questions = target_count % chunks_to_use
                
                for i, chunk in enumerate(text_chunks[:chunks_to_use]):
                    # Distribute questions evenly, with extras going to first chunks
                    chunk_question_count = questions_per_chunk + (1 if i < remaining_questions else 0)
                    
                    chunk_questions = self._generate_questions_for_chunk(
                        chunk, difficulty, difficulty_name, chunk_question_count
                    )
                    
                    questions_for_level.extend(chunk_questions)
                    
                    print(f"  📝 Generated {len(chunk_questions)} questions from chunk {i+1}")
                
                # Ensure we don't exceed target
                if len(questions_for_level) > target_count:
                    questions_for_level = questions_for_level[:target_count]
                
                # Save questions to database
                for q_data in questions_for_level:
                    # Enhanced data validation
                    question_type = q_data.get('type', 'multiple_choice')
                    if not question_type:
                        question_type = 'multiple_choice'
                    
                    # Ensure all required fields have content
                    question_text = q_data.get('question', f'Generated {difficulty_name} question')
                    option_a = q_data.get('option_a', 'Option A') or 'Option A'
                    option_b = q_data.get('option_b', 'Option B') or 'Option B'
                    option_c = q_data.get('option_c', 'Option C') or 'Option C'
                    option_d = q_data.get('option_d', 'Option D') or 'Option D'
                    correct_answer = q_data.get('correct_answer', 'A') or 'A'
                    explanation = q_data.get('explanation', 'AI-generated explanation') or 'AI-generated explanation'
                    
                    # Create QuestionBank entry with enhanced validation
                    question = QuestionBank.objects.create(
                        document=document,
                        question_text=question_text,
                        question_type=question_type,
                        difficulty_level=difficulty,
                        subject='math',  # Default subject
                        option_a=option_a,
                        option_b=option_b,
                        option_c=option_c,
                        option_d=option_d,
                        correct_answer=correct_answer,
                        explanation=explanation,
                        is_approved=True,
                        created_by_ai=True
                    )
                    generated_questions.append(question.id)
                
                print(f"  ✅ Successfully created {len(questions_for_level)} Level {difficulty} questions in database")
            
            total_generated = len(generated_questions)
            print(f"🎉 Total questions generated: {total_generated}")
            
            # Update document with question count
            document.questions_generated_count = total_generated
            document.save()
            
            return {
                'success': True,
                'questions_generated': total_generated,
                'question_ids': generated_questions,
                'breakdown': {
                    'level_3_generated': len([q for q in generated_questions if QuestionBank.objects.get(id=q).difficulty_level == '3']),
                    'level_4_generated': len([q for q in generated_questions if QuestionBank.objects.get(id=q).difficulty_level == '4']), 
                    'level_5_generated': len([q for q in generated_questions if QuestionBank.objects.get(id=q).difficulty_level == '5']),
                    'targets': question_targets
                }
            }
            
        except Exception as e:
            print(f"❌ Enhanced question generation failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _generate_questions_for_chunk(self, text_chunk: str, difficulty_level: str, 
                                    difficulty_name: str, num_questions: int = 3) -> List[Dict]:
        """
        Enhanced question generation for each text chunk with improved prompts and higher token limits
        """
        
        if not self.llm:
            # Fallback to hardcoded questions if LLM not available
            return self._generate_fallback_questions(text_chunk, difficulty_level, num_questions)
        
        # Enhanced prompts for each difficulty level
        level_specific_prompts = {
            '3': f"""
Based on the following mathematical content, generate EXACTLY {num_questions} basic-level multiple choice questions.

MATHEMATICAL CONTENT:
{text_chunk}

LEVEL 3 (BASIC) REQUIREMENTS:
- Focus on fundamental concepts and definitions
- Basic arithmetic and algebraic manipulations  
- Direct applications of formulas
- Simple problem recognition
- Clear, straightforward questions

Generate exactly {num_questions} questions. Format as JSON:
{{
    "questions": [
        {{
            "question": "Clear, specific question text",
            "option_a": "First option",
            "option_b": "Second option", 
            "option_c": "Third option",
            "option_d": "Fourth option",
            "correct_answer": "A",
            "explanation": "Step-by-step explanation why this answer is correct",
            "type": "multiple_choice"
        }}
    ]
}}

IMPORTANT: Generate exactly {num_questions} complete questions with all fields filled.
""",
            '4': f"""
Based on the following mathematical content, generate EXACTLY {num_questions} intermediate-level multiple choice questions.

MATHEMATICAL CONTENT:
{text_chunk}

LEVEL 4 (INTERMEDIATE) REQUIREMENTS:
- Multi-step problem solving
- Application of multiple mathematical concepts
- Moderate complexity calculations  
- Pattern recognition and analysis
- Integration of different mathematical areas

Generate exactly {num_questions} questions. Format as JSON:
{{
    "questions": [
        {{
            "question": "Multi-step question requiring analysis",
            "option_a": "Detailed first option",
            "option_b": "Detailed second option", 
            "option_c": "Detailed third option",
            "option_d": "Detailed fourth option",
            "correct_answer": "B",
            "explanation": "Comprehensive explanation with solution steps",
            "type": "multiple_choice"
        }}
    ]
}}

IMPORTANT: Generate exactly {num_questions} complete questions with detailed explanations.
""",
            '5': f"""
Based on the following mathematical content, generate EXACTLY {num_questions} advanced-level multiple choice questions.

MATHEMATICAL CONTENT:
{text_chunk}

LEVEL 5 (ADVANCED) REQUIREMENTS:
- Complex multi-step problem solving
- Integration of multiple advanced mathematical concepts
- Advanced analytical thinking and reasoning
- Real-world application scenarios
- Higher-order mathematical skills

Generate exactly {num_questions} questions. Format as JSON:
{{
    "questions": [
        {{
            "question": "Complex analytical question requiring deep understanding",
            "option_a": "Sophisticated first option",
            "option_b": "Sophisticated second option", 
            "option_c": "Sophisticated third option",
            "option_d": "Sophisticated fourth option",
            "correct_answer": "C",
            "explanation": "Detailed explanation with complete solution methodology",
            "type": "multiple_choice"
        }}
    ]
}}

IMPORTANT: Generate exactly {num_questions} complete questions with comprehensive explanations.
"""
        }
        
        # Use level-specific prompt
        prompt = level_specific_prompts.get(difficulty_level, level_specific_prompts['3'])
        
        try:
            print(f"  🤖 Generating {num_questions} Level {difficulty_level} questions using enhanced AI prompt...")
            
            # Enhanced LLM call with much higher token limits for multiple questions
            response = self.llm.invoke(
                prompt,
                max_tokens=3000,  # Significantly increased token limit for multiple questions
                temperature=0.3,  # Slightly lower temperature for more consistent output
                top_p=0.9        # Good diversity while maintaining quality
            )
            
            print(f"  📝 AI Response length: {len(response)} characters")
            
            # Enhanced JSON parsing with multiple fallback methods
            import re
            import json
            
            # Method 1: Try to find complete JSON block
            json_match = re.search(r'\{[^}]*"questions"[^}]*\[.*?\]\s*\}', response, re.DOTALL)
            if json_match:
                try:
                    json_data = json.loads(json_match.group())
                    questions = json_data.get('questions', [])
                    if questions and len(questions) > 0:
                        print(f"  ✅ Successfully parsed {len(questions)} questions from JSON")
                        return questions[:num_questions]  # Ensure we don't exceed target
                except json.JSONDecodeError:
                    print("  ⚠️ JSON parsing failed, trying alternative parsing...")
            
            # Method 2: Try to parse individual question objects
            question_pattern = r'\{[^}]*"question"[^}]*"explanation"[^}]*\}'
            question_matches = re.findall(question_pattern, response, re.DOTALL)
            
            parsed_questions = []
            for match in question_matches[:num_questions]:
                try:
                    q_obj = json.loads(match)
                    if q_obj.get('question') and q_obj.get('option_a'):
                        parsed_questions.append(q_obj)
                except:
                    continue
            
            if parsed_questions:
                print(f"  ✅ Parsed {len(parsed_questions)} questions using pattern matching")
                return parsed_questions
                
            # Method 3: Manual parsing for common formats
            questions = []
            lines = response.split('\n')
            current_q = {}
            
            for line in lines:
                line = line.strip()
                if '"question":' in line:
                    if current_q:
                        questions.append(current_q)
                    current_q = {'question': self._extract_value(line)}
                elif '"option_a":' in line:
                    current_q['option_a'] = self._extract_value(line)
                elif '"option_b":' in line:
                    current_q['option_b'] = self._extract_value(line)
                elif '"option_c":' in line:
                    current_q['option_c'] = self._extract_value(line)
                elif '"option_d":' in line:
                    current_q['option_d'] = self._extract_value(line)
                elif '"correct_answer":' in line:
                    current_q['correct_answer'] = self._extract_value(line)
                elif '"explanation":' in line:
                    current_q['explanation'] = self._extract_value(line)
                    current_q['type'] = 'multiple_choice'
            
            if current_q and 'question' in current_q:
                questions.append(current_q)
                
            if questions:
                print(f"  ✅ Manually parsed {len(questions)} questions")
                return questions[:num_questions]
                
            # Fallback if all parsing fails
            print(f"  ⚠️ All parsing methods failed, using fallback questions")
            return self._generate_fallback_questions(text_chunk, difficulty_level, num_questions)
                
        except Exception as e:
            print(f"  ❌ Error in enhanced question generation: {str(e)}")
            return self._generate_fallback_questions(text_chunk, difficulty_level, num_questions)
    
    def _extract_value(self, line: str) -> str:
        """Extract quoted value from JSON-like line"""
        try:
            # Find text between quotes after the colon
            start = line.find(':')
            if start == -1:
                return ""
            value_part = line[start+1:].strip()
            if value_part.startswith('"') and value_part.endswith('"'):
                return value_part[1:-1]
            elif value_part.startswith('"'):
                # Find closing quote
                end_quote = value_part.find('"', 1)
                if end_quote != -1:
                    return value_part[1:end_quote]
            return value_part.strip('"').strip(',')
        except:
            return ""
        
        try:
            response = self.llm.invoke(prompt)
            # Try to parse JSON response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_data = json.loads(json_match.group())
                return json_data.get('questions', [])
            else:
                # Fallback if JSON parsing fails
                return self._generate_fallback_questions(text_chunk, difficulty_level, num_questions)
                
        except Exception as e:
            print(f"Error generating questions: {e}")
            return self._generate_fallback_questions(text_chunk, difficulty_level, num_questions)
    
    def _generate_fallback_questions(self, text_chunk: str, difficulty_level: str, num_questions: int) -> List[Dict]:
        """Generate fallback questions when LLM is not available"""
        
        difficulty_templates = {
            '3': [
                {
                    'question': 'What is the main concept discussed in this section?',
                    'option_a': 'Basic arithmetic operations',
                    'option_b': 'Complex equations',
                    'option_c': 'Advanced calculus',
                    'option_d': 'Abstract theory',
                    'correct_answer': 'A',
                    'explanation': 'This is a fundamental concept.',
                    'type': 'multiple_choice'
                },
                {
                    'question': 'Which of the following is a key principle mentioned?',
                    'option_a': 'Order of operations',
                    'option_b': 'Advanced integration',
                    'option_c': 'Complex variables',
                    'option_d': 'Theoretical proofs',
                    'correct_answer': 'A',
                    'explanation': 'This represents a basic mathematical principle.',
                    'type': 'multiple_choice'
                },
                {
                    'question': 'What type of problem is primarily addressed?',
                    'option_a': 'Simple calculations',
                    'option_b': 'Differential equations',
                    'option_c': 'Matrix operations',
                    'option_d': 'Statistical analysis',
                    'correct_answer': 'A',
                    'explanation': 'This focuses on basic problem-solving.',
                    'type': 'multiple_choice'
                },
                {
                    'question': 'Which mathematical operation is most relevant?',
                    'option_a': 'Addition and subtraction',
                    'option_b': 'Limits and derivatives',
                    'option_c': 'Vector algebra',
                    'option_d': 'Set theory',
                    'correct_answer': 'A',
                    'explanation': 'Basic operations are the foundation.',
                    'type': 'multiple_choice'
                },
                {
                    'question': 'What is the primary learning objective?',
                    'option_a': 'Understanding basic concepts',
                    'option_b': 'Mastering advanced topics',
                    'option_c': 'Developing proofs',
                    'option_d': 'Abstract reasoning',
                    'correct_answer': 'A',
                    'explanation': 'The goal is foundational understanding.',
                    'type': 'multiple_choice'
                },
                {
                    'question': 'Which skill is being developed?',
                    'option_a': 'Basic computation',
                    'option_b': 'Analytical thinking',
                    'option_c': 'Research methods',
                    'option_d': 'Theoretical analysis',
                    'correct_answer': 'A',
                    'explanation': 'Focus is on computational skills.',
                    'type': 'multiple_choice'
                },
                {
                    'question': 'What type of examples are used?',
                    'option_a': 'Simple, concrete cases',
                    'option_b': 'Complex applications',
                    'option_c': 'Abstract scenarios',
                    'option_d': 'Theoretical models',
                    'correct_answer': 'A',
                    'explanation': 'Simple examples aid understanding.',
                    'type': 'multiple_choice'
                },
                {
                    'question': 'Which approach is emphasized?',
                    'option_a': 'Step-by-step procedures',
                    'option_b': 'Independent discovery',
                    'option_c': 'Critical analysis',
                    'option_d': 'Abstract reasoning',
                    'correct_answer': 'A',
                    'explanation': 'Procedural learning is key at this level.',
                    'type': 'multiple_choice'
                }
            ],
            '4': [
                {
                    'question': 'Which intermediate concept is most relevant to this material?',
                    'option_a': 'Linear equations',
                    'option_b': 'Quadratic functions',
                    'option_c': 'Trigonometry',
                    'option_d': 'Basic arithmetic',
                    'correct_answer': 'B',
                    'explanation': 'This involves intermediate mathematical concepts.',
                    'type': 'multiple_choice'
                },
                {
                    'question': 'What type of analysis is required?',
                    'option_a': 'Graphical interpretation',
                    'option_b': 'Simple calculation',
                    'option_c': 'Advanced calculus',
                    'option_d': 'Abstract theory',
                    'correct_answer': 'A',
                    'explanation': 'Intermediate level requires analytical skills.',
                    'type': 'multiple_choice'
                },
                {
                    'question': 'Which mathematical relationship is explored?',
                    'option_a': 'Cause and effect',
                    'option_b': 'Simple proportions',
                    'option_c': 'Complex derivatives',
                    'option_d': 'Theoretical constructs',
                    'correct_answer': 'A',
                    'explanation': 'Understanding relationships is key.',
                    'type': 'multiple_choice'
                },
                {
                    'question': 'What problem-solving strategy is used?',
                    'option_a': 'Multi-step procedures',
                    'option_b': 'Single operations',
                    'option_c': 'Advanced proofs',
                    'option_d': 'Abstract reasoning',
                    'correct_answer': 'A',
                    'explanation': 'Intermediate problems require multiple steps.',
                    'type': 'multiple_choice'
                },
                {
                    'question': 'Which skill is being developed?',
                    'option_a': 'Analytical reasoning',
                    'option_b': 'Basic computation',
                    'option_c': 'Advanced research',
                    'option_d': 'Theoretical proof',
                    'correct_answer': 'A',
                    'explanation': 'Focus is on developing reasoning skills.',
                    'type': 'multiple_choice'
                },
                {
                    'question': 'What type of application is emphasized?',
                    'option_a': 'Real-world problems',
                    'option_b': 'Abstract exercises',
                    'option_c': 'Theoretical examples',
                    'option_d': 'Basic drills',
                    'correct_answer': 'A',
                    'explanation': 'Applications make concepts meaningful.',
                    'type': 'multiple_choice'
                }
            ],
            '5': [
                {
                    'question': 'What advanced mathematical principle is demonstrated?',
                    'option_a': 'Complex analysis',
                    'option_b': 'Basic algebra',
                    'option_c': 'Simple arithmetic',
                    'option_d': 'Elementary geometry',
                    'correct_answer': 'A',
                    'explanation': 'This requires advanced mathematical understanding.',
                    'type': 'multiple_choice'
                },
                {
                    'question': 'Which sophisticated concept is explored?',
                    'option_a': 'Abstract structures',
                    'option_b': 'Concrete examples',
                    'option_c': 'Simple procedures',
                    'option_d': 'Basic operations',
                    'correct_answer': 'A',
                    'explanation': 'Advanced topics involve abstract thinking.',
                    'type': 'multiple_choice'
                },
                {
                    'question': 'What type of mathematical reasoning is required?',
                    'option_a': 'Deductive proof',
                    'option_b': 'Simple calculation',
                    'option_c': 'Pattern recognition',
                    'option_d': 'Memory recall',
                    'correct_answer': 'A',
                    'explanation': 'Advanced mathematics requires rigorous reasoning.',
                    'type': 'multiple_choice'
                },
                {
                    'question': 'Which advanced technique is applied?',
                    'option_a': 'Mathematical modeling',
                    'option_b': 'Basic formulas',
                    'option_c': 'Simple substitution',
                    'option_d': 'Direct computation',
                    'correct_answer': 'A',
                    'explanation': 'Advanced problems use sophisticated techniques.',
                    'type': 'multiple_choice'
                }
            ]
        }
        
        templates = difficulty_templates.get(difficulty_level, difficulty_templates['3'])
        # Return up to the requested number of questions, repeating if necessary
        if len(templates) >= num_questions:
            return templates[:num_questions]
        else:
            # If we need more questions than available, repeat the templates
            repeated_templates = []
            for i in range(num_questions):
                template_index = i % len(templates)
                question = templates[template_index].copy()
                # Modify the question slightly to avoid exact duplicates
                if i >= len(templates):
                    question['question'] = f"Additionally, {question['question'].lower()}"
                repeated_templates.append(question)
            return repeated_templates
    
    def get_rag_answer_for_question(self, question_text: str, document_id: int) -> str:
        """
        Use RAG to get an answer/explanation for a question based on document content
        """
        try:
            from .models import Document
            
            document = Document.objects.get(id=document_id)
            if not document.extracted_text:
                return "No document content available for explanation."
            
            # Create vector store for this document if not exists
            vector_store = self._get_or_create_vector_store(document)
            
            if not vector_store:
                return "Unable to process document for explanation."
            
            # Query the document for answer
            query_result = self.query_document(document_id, question_text)
            
            if query_result.get('method') == 'rag' and query_result.get('answer'):
                return query_result['answer']
            else:
                return "Unable to generate explanation from document content."
                
        except Exception as e:
            return f"Error generating explanation: {str(e)}"


# Global instance
document_processor = DocumentProcessor()
