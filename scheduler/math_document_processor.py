import ollama
import json
import re
from typing import List, Dict, Any

class MathDocumentProcessor:
    def __init__(self):
        self.model_name = "llama3.2"
        
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
            
            # Extract JSON from response
            content = response['message']['content']
            
            # Try to parse JSON response
            try:
                parsed_response = json.loads(content)
                return parsed_response.get('questions', [])
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract questions manually
                return self.extract_questions_fallback(content, level)
                
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
