import ollama
import json
import re
from typing import List, Dict, Any

class AlgorithmDocumentProcessor:
    def __init__(self):
        self.model_name = "llama3.2"
    
    def extract_json_from_response(self, content: str) -> Dict[str, Any]:
        """
        Robust JSON extraction that handles code fences and other formatting
        """
        try:
            # First, try direct JSON parsing
            return json.loads(content)
        except json.JSONDecodeError:
            pass
        
        # Remove code fences and backticks
        content = re.sub(r'```json\s*', '', content, flags=re.IGNORECASE)
        content = re.sub(r'```\s*', '', content)
        content = content.strip('`')
        
        # Try to find the most complete JSON-like content between braces
        # This regex handles nested braces better
        json_pattern = r'\{(?:[^{}]|(?:\{[^{}]*\}))*\}'
        json_matches = re.findall(json_pattern, content, re.DOTALL)
        
        for json_match in json_matches:
            try:
                parsed = json.loads(json_match)
                # Prefer matches that have a 'questions' key
                if 'questions' in parsed:
                    return parsed
            except json.JSONDecodeError:
                continue
        
        # If we found JSON objects but none with 'questions', return the first valid one
        for json_match in json_matches:
            try:
                return json.loads(json_match)
            except json.JSONDecodeError:
                continue
        
        # Try to find array-like content
        array_match = re.search(r'\[.*\]', content, re.DOTALL)
        if array_match:
            try:
                array_data = json.loads(array_match.group())
                return {"questions": array_data}
            except json.JSONDecodeError:
                pass
        
        # Try to extract individual question objects from prose
        # Look for question patterns in the text
        questions = self.extract_questions_from_prose(content)
        if questions:
            return {"questions": questions}
        
        # Last resort: return empty structure
        print("DEBUG: All JSON extraction methods failed, returning empty structure")
        return {"questions": []}
    
    def extract_questions_from_prose(self, content: str) -> List[Dict]:
        """
        Extract question data from prose text when JSON parsing fails completely
        """
        questions = []
        
        # Look for question patterns
        # Pattern 1: "Question: ..." followed by options "A) ..." etc.
        question_blocks = re.split(r'(?:Question\s*\d*[:\.]|Q\d+[:\.])', content, flags=re.IGNORECASE)
        
        for block in question_blocks[1:]:  # Skip first empty split
            if len(block.strip()) < 10:
                continue
                
            # Extract question text (first line or until options)
            lines = block.strip().split('\n')
            question_text = ""
            options = {'A': '', 'B': '', 'C': '', 'D': ''}
            correct_answer = 'A'
            explanation = ""
            
            current_section = 'question'
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check for option patterns
                option_match = re.match(r'^([ABCD])\)\s*(.+)', line, re.IGNORECASE)
                if option_match:
                    letter = option_match.group(1).upper()
                    text = option_match.group(2)
                    options[letter] = text
                    current_section = 'options'
                    continue
                
                # Check for answer patterns
                answer_match = re.match(r'(?:Answer|Correct)[:\s]*([ABCD])', line, re.IGNORECASE)
                if answer_match:
                    correct_answer = answer_match.group(1).upper()
                    current_section = 'answer'
                    continue
                
                # Check for explanation patterns
                if re.match(r'(?:Explanation|Because|Solution)[:\s]', line, re.IGNORECASE):
                    explanation = re.sub(r'(?:Explanation|Because|Solution)[:\s]*', '', line, flags=re.IGNORECASE)
                    current_section = 'explanation'
                    continue
                
                # Add to current section
                if current_section == 'question' and not question_text:
                    question_text = line
                elif current_section == 'explanation':
                    explanation += " " + line
            
            # Only add if we have minimum required data
            if question_text and any(options.values()):
                questions.append({
                    'question_text': question_text,
                    'option_a': options.get('A', 'Option A'),
                    'option_b': options.get('B', 'Option B'),
                    'option_c': options.get('C', 'Option C'),
                    'option_d': options.get('D', 'Option D'),
                    'correct_answer': correct_answer,
                    'explanation': explanation or f"Explanation for: {question_text[:50]}..."
                })
        
        print(f"DEBUG: Extracted {len(questions)} questions from prose")
        return questions[:5]  # Limit to 5 questions as requested
        
    def process_math_document(self, text: str, document_id: str) -> Dict[str, Any]:
        """
        Process a math document and extract questions by difficulty levels
        """
        try:
            # Clean and prepare text
            cleaned_text = self.clean_text(text)
            
            # Extract questions for each difficulty level
            level_3_questions = self.extract_questions_by_level(cleaned_text, "3", "basic")
            level_4_questions = self.extract_questions_by_level(cleaned_text, "4", "intermediate") 
            level_5_questions = self.extract_questions_by_level(cleaned_text, "5", "advanced")
            
            # Prepare RAG knowledge base
            knowledge_chunks = self.prepare_rag_chunks(cleaned_text)
            
            return {
                'level_3_questions': level_3_questions,
                'level_4_questions': level_4_questions,
                'level_5_questions': level_5_questions,
                'knowledge_chunks': knowledge_chunks,
                'total_questions': len(level_3_questions) + len(level_4_questions) + len(level_5_questions)
            }
            
        except Exception as e:
            print(f"Error processing document: {e}")
            return {
                'level_3_questions': [],
                'level_4_questions': [],
                'level_5_questions': [],
                'knowledge_chunks': [],
                'total_questions': 0,
                'error': str(e)
            }
    
    def extract_questions_by_level(self, text: str, level: str, difficulty: str) -> List[Dict]:
        """
        Extract math questions for a specific difficulty level using Llama
        """
        try:
            prompt = f"""
            You are a math teacher creating questions from educational content.
            
            From the following math content, generate 5 multiple choice questions at {difficulty} level (Level {level}):
            
            Level {level} Requirements:
            - Level 3: Basic arithmetic, simple algebra, basic geometry
            - Level 4: Intermediate algebra, trigonometry, advanced geometry
            - Level 5: Advanced calculus, complex equations, derivatives, integrals
            
            Content: {text[:3000]}
            
            For each question, provide:
            1. Question text
            2. Four multiple choice options (A, B, C, D)
            3. Correct answer (letter)
            4. Detailed explanation
            
            Format your response as JSON:
            {{
                "questions": [
                    {{
                        "question_text": "What is 2 + 2?",
                        "option_a": "3",
                        "option_b": "4", 
                        "option_c": "5",
                        "option_d": "6",
                        "correct_answer": "B",
                        "explanation": "2 + 2 equals 4 because we are adding two units to two units"
                    }}
                ]
            }}
            """
            
            response = ollama.chat(model=self.model_name, messages=[
                {'role': 'user', 'content': prompt}
            ])
            
            # Extract JSON from response with enhanced tolerance
            content = response['message']['content']
            print(f"DEBUG: Raw LLM response for level {level}: {content[:200]}...")
            
            # First, try to extract the first {...} block using regex
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content, re.DOTALL)
            
            if json_match:
                json_text = json_match.group()
                print(f"DEBUG: Extracted JSON block: {json_text[:100]}...")
                
                try:
                    parsed_response = json.loads(json_text)
                    questions = parsed_response.get('questions', [])
                    print(f"DEBUG: Successfully parsed {len(questions)} questions for level {level}")
                    return questions
                except json.JSONDecodeError as e:
                    print(f"DEBUG: JSON parsing failed for level {level}: {e}")
                    # Fallback to robust parsing method
                    parsed_response = self.extract_json_from_response(content)
                    return parsed_response.get('questions', [])
            else:
                print(f"DEBUG: No JSON block found in response for level {level}")
                # Try the robust parsing method as fallback
                parsed_response = self.extract_json_from_response(content)
                return parsed_response.get('questions', [])
                
        except Exception as e:
            print(f"Error extracting level {level} questions: {e}")
            return self.generate_fallback_questions(level)
    
    def extract_questions_fallback(self, content: str, level: str) -> List[Dict]:
        """
        Fallback method to extract questions when JSON parsing fails
        """
        questions = []
        # Basic regex patterns to extract question components
        question_pattern = r'(?:Question|Q\d+)[:.]?\s*(.+?)(?=Option|A\)|\n\n)'
        
        # This is a simplified fallback - in production, you'd want more robust parsing
        matches = re.findall(question_pattern, content, re.IGNORECASE | re.DOTALL)
        
        for i, match in enumerate(matches[:3]):  # Limit to 3 questions
            questions.append({
                'question_text': match.strip(),
                'option_a': f'Option A for question {i+1}',
                'option_b': f'Option B for question {i+1}',
                'option_c': f'Option C for question {i+1}',
                'option_d': f'Option D for question {i+1}',
                'correct_answer': 'A',
                'explanation': f'Explanation for level {level} question {i+1}'
            })
        
        return questions
    
    def generate_fallback_questions(self, level: str) -> List[Dict]:
        """
        Generate basic fallback questions when AI extraction fails
        """
        fallback_questions = {
            '3': [
                {
                    'question_text': 'What is 15% of 200?',
                    'option_a': '30',
                    'option_b': '25',
                    'option_c': '35',
                    'option_d': '40',
                    'correct_answer': 'A',
                    'explanation': '15% of 200 = 0.15 × 200 = 30'
                },
                {
                    'question_text': 'Solve: 7 × 8 = ?',
                    'option_a': '56',
                    'option_b': '54',
                    'option_c': '58',
                    'option_d': '52',
                    'correct_answer': 'A',
                    'explanation': '7 × 8 = 56'
                }
            ],
            '4': [
                {
                    'question_text': 'Solve for x: 2x + 5 = 15',
                    'option_a': '5',
                    'option_b': '10',
                    'option_c': '7',
                    'option_d': '3',
                    'correct_answer': 'A',
                    'explanation': '2x + 5 = 15, so 2x = 10, therefore x = 5'
                },
                {
                    'question_text': 'What is sin(30°)?',
                    'option_a': '1/2',
                    'option_b': '√3/2',
                    'option_c': '1',
                    'option_d': '√2/2',
                    'correct_answer': 'A',
                    'explanation': 'sin(30°) = 1/2'
                }
            ],
            '5': [
                {
                    'question_text': 'What is the derivative of x² + 3x + 2?',
                    'option_a': '2x + 3',
                    'option_b': 'x + 3',
                    'option_c': '2x + 2',
                    'option_d': 'x² + 3',
                    'correct_answer': 'A',
                    'explanation': 'The derivative of x² + 3x + 2 is 2x + 3'
                },
                {
                    'question_text': 'Evaluate ∫(2x + 1)dx',
                    'option_a': 'x² + x + C',
                    'option_b': '2x² + x + C',
                    'option_c': 'x² + 2x + C',
                    'option_d': '2x + C',
                    'correct_answer': 'A',
                    'explanation': '∫(2x + 1)dx = x² + x + C'
                }
            ]
        }
        
        return fallback_questions.get(level, [])
    
    def prepare_rag_chunks(self, text: str) -> List[str]:
        """
        Prepare text chunks for RAG knowledge base
        """
        # Split text into meaningful chunks for RAG
        chunk_size = 500
        chunks = []
        
        words = text.split()
        for i in range(0, len(words), chunk_size):
            chunk = ' '.join(words[i:i + chunk_size])
            if len(chunk.strip()) > 50:  # Only include meaningful chunks
                chunks.append(chunk)
        
        return chunks
    
    def clean_text(self, text: str) -> str:
        """
        Clean and prepare text for processing
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters that might interfere
        text = re.sub(r'[^\w\s\.\,\!\?\+\-\=\(\)\[\]\{\}\^\*\/\\]', '', text)
        return text.strip()
    
    def orchestrate_document_processing(self, file_path: str, document_id: int, document_type: str = 'pdf') -> Dict[str, Any]:
        """
        Unified orchestration for complete document processing pipeline:
        1. Extract full text → save to extracted_text/processed_content
        2. Build RAG chunks → save to rag_chunks  
        3. Generate questions → write to QuestionBank and bump questions_generated_count
        """
        from .models import Document, QuestionBank
        import json
        
        try:
            # Get the document
            document = Document.objects.get(id=document_id)
            
            # Step 1: Extract full text based on document type
            extracted_text = ""
            metadata = {}
            
            if document_type == 'pdf':
                text_result = self.extract_pdf_content(file_path)
                extracted_text = text_result.get('text', '')
                metadata = text_result.get('metadata', {})
            elif document_type == 'image':
                text_result = self.extract_image_content(file_path)
                extracted_text = text_result.get('text', '')
                metadata = text_result.get('metadata', {})
            else:  # text files
                with open(file_path, 'r', encoding='utf-8') as f:
                    extracted_text = f.read()
                metadata = {"file_type": document_type}
            
            # Save extracted text to document
            document.extracted_text = extracted_text or ""
            document.processed_content = extracted_text or ""
            document.metadata = json.dumps(metadata)
            
            # Step 2: Build RAG chunks and save
            if extracted_text and len(extracted_text.strip()) > 100:
                knowledge_chunks = self.prepare_rag_chunks(extracted_text)
                document.rag_chunks = json.dumps(knowledge_chunks)
                
                # Step 3: Generate questions using the math processor
                math_result = self.process_math_document(extracted_text, str(document_id))
                
                # Save questions to QuestionBank
                total_questions_created = 0
                for level in ['3', '4', '5']:
                    level_questions = math_result.get(f'level_{level}_questions', [])
                    for q_data in level_questions:
                        if self.validate_question_data(q_data):
                            question = QuestionBank.objects.create(
                                document=document,
                                question_text=q_data.get('question_text', ''),
                                question_type='multiple_choice',
                                difficulty_level=level,
                                subject='math',
                                option_a=q_data.get('option_a', ''),
                                option_b=q_data.get('option_b', ''),
                                option_c=q_data.get('option_c', ''),
                                option_d=q_data.get('option_d', ''),
                                correct_answer=q_data.get('correct_answer', 'A'),
                                explanation=q_data.get('explanation', ''),
                                is_approved=True,
                                created_by_ai=True,
                                is_generated=True
                            )
                            total_questions_created += 1
                
                # Update document question count
                document.questions_generated_count = total_questions_created
                document.processing_status = 'completed'
            else:
                # Text too short for question generation
                document.rag_chunks = json.dumps([])
                document.questions_generated_count = 0
                document.processing_status = 'completed'
            
            document.save()
            
            return {
                'success': True,
                'questions_generated': document.questions_generated_count,
                'text_length': len(extracted_text),
                'chunks_created': len(json.loads(document.rag_chunks or '[]')),
                'processing_status': document.processing_status
            }
            
        except Exception as e:
            print(f"Error in orchestrate_document_processing: {e}")
            try:
                document = Document.objects.get(id=document_id)
                document.processing_status = 'failed'
                document.save()
            except:
                pass
            
            return {
                'success': False,
                'error': str(e),
                'questions_generated': 0
            }
    
    def extract_pdf_content(self, file_path: str) -> Dict[str, Any]:
        """Extract text from PDF files using enhanced DocumentProcessor with OCR fallback"""
        try:
            # Import DocumentProcessor for enhanced PDF processing
            from .document_processing import DocumentProcessor
            
            print("DEBUG: Using enhanced PDF processing with OCR fallback...")
            
            # Create DocumentProcessor instance and use enhanced extraction
            doc_processor = DocumentProcessor()
            result = doc_processor.extract_pdf_content(file_path)
            
            # Ensure compatibility with existing code expecting 'text' and 'metadata'
            if 'text' not in result:
                result['text'] = ''
            if 'metadata' not in result:
                result['metadata'] = {}
            
            print(f"DEBUG: Enhanced PDF extraction completed. Text length: {len(result['text'])}")
            
            return result
            
        except Exception as e:
            print(f"ERROR: Enhanced PDF extraction failed: {str(e)}")
            # Fallback to simple extraction
            try:
                import pdfplumber
                
                print("DEBUG: Falling back to simple PDF extraction...")
                
                extracted_data = {
                    'text': '',
                    'metadata': {}
                }
                
                with pdfplumber.open(file_path) as pdf:
                    # Extract metadata
                    extracted_data['metadata'] = {
                        'total_pages': len(pdf.pages),
                        'title': pdf.metadata.get('Title', ''),
                        'author': pdf.metadata.get('Author', '')
                    }
                    
                    # Extract text from all pages
                    full_text = ""
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            full_text += f"\n{page_text}"
                    
                    extracted_data['text'] = full_text.strip()
                
                print(f"DEBUG: Simple PDF extraction completed. Text length: {len(extracted_data['text'])}")
                return extracted_data
                
            except Exception as fallback_error:
                print(f"ERROR: Both enhanced and simple PDF extraction failed: {fallback_error}")
                return {
                    'text': f"PDF extraction failed: {str(fallback_error)}",
                    'metadata': {}
                }
    
    def extract_image_content(self, file_path: str) -> Dict[str, Any]:
        """Extract text from image files (placeholder for OCR)"""
        try:
            # This is a placeholder - in production you'd use OCR
            import os
            return {
                'text': f"Image file: {os.path.basename(file_path)} (OCR processing would go here)",
                'metadata': {
                    'file_name': os.path.basename(file_path),
                    'file_type': 'image'
                }
            }
        except Exception as e:
            return {
                'text': f"Image processing failed: {str(e)}",
                'metadata': {}
            }
    
    def validate_question_data(self, q_data: Dict[str, Any]) -> bool:
        """Validate that question data has required fields"""
        required_fields = ['question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer']
        return all(field in q_data and q_data[field] for field in required_fields)
