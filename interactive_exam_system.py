"""
Interactive Chat-based Exam System
Converts Level Test into chat-based exam with open-ended answers
"""
import json
import re
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import requests
from django.utils import timezone

class InteractiveExamSession:
    """Manages state for interactive chat-based exam sessions"""
    
    # Session states
    ASKING = "ASKING"
    WAITING_FOR_ANSWER = "WAITING_FOR_ANSWER" 
    EVALUATING = "EVALUATING"
    HINT_OR_NEXT = "HINT_OR_NEXT"
    COMPLETED = "COMPLETED"
    
    def __init__(self, session_id: str, student_id: str, document_id: str):
        self.session_id = session_id
        self.student_id = student_id
        self.document_id = document_id
        self.state = self.ASKING
        self.current_question_index = 0
        self.questions = []  # Will be populated with 10 questions
        self.start_time = timezone.now()
        self.question_states = {}  # question_index -> {attemptCount, hintsShown, isCorrect, answers, startTime}
        self.total_correct = 0
        
    def to_dict(self) -> Dict:
        """Serialize session to dictionary for storage"""
        return {
            'session_id': self.session_id,
            'student_id': self.student_id,
            'document_id': self.document_id,
            'state': self.state,
            'current_question_index': self.current_question_index,
            'questions': self.questions,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'question_states': self.question_states,
            'total_correct': self.total_correct
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Deserialize session from dictionary"""
        session = cls(data['session_id'], data['student_id'], data['document_id'])
        session.state = data.get('state', cls.ASKING)
        session.current_question_index = data.get('current_question_index', 0)
        session.questions = data.get('questions', [])
        session.question_states = data.get('question_states', {})
        session.total_correct = data.get('total_correct', 0)
        if data.get('start_time'):
            session.start_time = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
        return session

class AnswerEvaluator:
    """Evaluates open-ended answers against document-grounded solutions"""
    
    @staticmethod
    def normalize_answer(answer: str) -> str:
        """Normalize student answer for comparison"""
        if not answer:
            return ""
        
        # Convert to lowercase and strip whitespace
        normalized = answer.lower().strip()
        
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Remove common punctuation but keep important chars for numbers
        normalized = re.sub(r'[,;:!?"\'\(\)\[\]{}]', '', normalized)
        
        return normalized
    
    @staticmethod
    def extract_number(text: str) -> Optional[float]:
        """Extract numeric value from text"""
        # Look for numbers (including decimals, fractions)
        number_pattern = r'-?\d+(?:\.\d+)?(?:/\d+)?'
        matches = re.findall(number_pattern, text)
        
        if matches:
            try:
                # Handle fractions
                if '/' in matches[0]:
                    parts = matches[0].split('/')
                    return float(parts[0]) / float(parts[1])
                return float(matches[0])
            except:
                return None
        return None
    
    @staticmethod
    def is_numeric_match(student_answer: str, correct_answer: str, tolerance: float = 0.01) -> bool:
        """Check if numeric answers match within tolerance"""
        student_num = AnswerEvaluator.extract_number(student_answer)
        correct_num = AnswerEvaluator.extract_number(correct_answer)
        
        if student_num is None or correct_num is None:
            return False
        
        if correct_num == 0:
            return abs(student_num - correct_num) <= tolerance
        else:
            return abs(student_num - correct_num) / abs(correct_num) <= tolerance
    
    @staticmethod
    def is_keyword_match(student_answer: str, correct_answer: str, required_keywords: List[str] = None) -> bool:
        """Check if answer contains required keywords"""
        student_norm = AnswerEvaluator.normalize_answer(student_answer)
        correct_norm = AnswerEvaluator.normalize_answer(correct_answer)
        
        # Direct match
        if student_norm == correct_norm:
            return True
        
        # Keyword matching
        if required_keywords:
            student_words = set(student_norm.split())
            required_words = set(word.lower() for word in required_keywords)
            return required_words.issubset(student_words)
        
        # Partial match - check if main keywords from correct answer are present
        correct_words = set(correct_norm.split())
        student_words = set(student_norm.split())
        
        # Remove common words
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being'}
        correct_words -= common_words
        
        if not correct_words:
            return False
        
        # Check if most important words are present
        overlap = len(correct_words.intersection(student_words))
        return overlap >= len(correct_words) * 0.7  # 70% of keywords must match
    
    @staticmethod
    def evaluate_answer(student_answer: str, question_data: Dict) -> Tuple[bool, str]:
        """
        Evaluate student answer against correct answer
        Returns (is_correct, feedback_message)
        """
        if not student_answer or not student_answer.strip():
            return False, "Please provide an answer."
        
        correct_answer = question_data.get('correct_answer', '')
        question_type = question_data.get('type', 'text')
        
        # Numeric questions
        if question_type == 'numeric' or AnswerEvaluator.extract_number(correct_answer) is not None:
            if AnswerEvaluator.is_numeric_match(student_answer, correct_answer):
                return True, "Correct!"
            else:
                return False, "Not quite right. Try again or ask for a hint."
        
        # Text-based questions
        keywords = question_data.get('keywords', [])
        if AnswerEvaluator.is_keyword_match(student_answer, correct_answer, keywords):
            return True, "Correct!"
        else:
            return False, "Not quite right. Try again or ask for a hint."

class QuestionGenerator:
    """Generates questions from uploaded documents using Gemini 2.0 Flash"""
    
    @staticmethod
    def generate_questions_from_document(document_content: str, document_title: str, count: int = 10) -> List[Dict]:
        """Generate exactly 'count' questions from document content using Gemini"""
        
        # Import gemini_client from views
        try:
            from scheduler.views import gemini_client
        except ImportError:
            raise Exception("Gemini client not available")
        
        if not gemini_client:
            raise Exception("Gemini client not initialized")
        
        prompt = f"""Based on this document content, generate exactly {count} educational questions with open-ended answers (no multiple choice).

Document Title: {document_title}
Document Content: {document_content[:4000]}...

For each question, provide:
1. A clear, specific question
2. The correct answer based on the document
3. 3 progressively more specific hints
4. Keywords that should be in a correct answer
5. Question type (numeric, text, concept, etc.)

Format each question as JSON:
{{
  "question": "What is...",
  "correct_answer": "The answer is...",
  "type": "text|numeric|concept",
  "keywords": ["keyword1", "keyword2"],
  "hints": [
    "Hint 1: Think about...",
    "Hint 2: Consider the relationship between...", 
    "Hint 3: The answer involves..."
  ],
  "difficulty": "easy|medium|hard"
}}

Generate exactly {count} questions covering the most important concepts from the document. Return only the JSON array of questions."""

        try:
            response = gemini_client.generate_content(prompt)
            
            if not response:
                raise Exception("No response from Gemini")
            
            # Handle different response formats
            response_text = response.text if hasattr(response, 'text') else str(response)
            
            if not response_text:
                raise Exception("Empty response from Gemini")
            
            # Parse JSON questions from response
            questions = QuestionGenerator.parse_questions_from_response(response_text)
            
            if len(questions) >= count:
                return questions[:count]
            else:
                # If we don't have enough questions, generate more
                return QuestionGenerator.ensure_question_count(questions, document_content, document_title, count)
                
        except Exception as e:
            print(f"❌ Question generation with Gemini failed: {e}")
            raise Exception(f"Unable to generate questions from document using Gemini: {str(e)}")
    
    @staticmethod
    def parse_questions_from_response(response_text: str) -> List[Dict]:
        """Parse JSON questions from Gemini response"""
        import re
        
        try:
            # Try to find JSON array in the response
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                questions = json.loads(json_str)
                return questions
            else:
                # Try to parse the entire response as JSON
                questions = json.loads(response_text)
                return questions
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON from Gemini response: {e}")
            # Fallback: try to extract questions manually
            return QuestionGenerator.extract_questions_manually(response_text)
    
    @staticmethod
    def extract_questions_manually(response_text: str) -> List[Dict]:
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
    
    @staticmethod
    def ensure_question_count(existing_questions: List[Dict], document_content: str, document_title: str, target_count: int) -> List[Dict]:
        """Ensure we have exactly the target number of questions using Gemini"""
        if len(existing_questions) >= target_count:
            return existing_questions[:target_count]
        
        # Generate additional questions using Gemini
        try:
            from scheduler.views import gemini_client
            
            if not gemini_client:
                # Fallback to default questions if Gemini not available
                return QuestionGenerator._generate_default_questions(existing_questions, document_title, target_count)
            
            remaining = target_count - len(existing_questions)
            prompt = f"""Generate {remaining} more questions from this document content.

Document Title: {document_title}
Document Content: {document_content[:2000]}...

Return only a JSON array of {remaining} questions in the same format as before."""

            response = gemini_client.generate_content(prompt)
            
            if response and response.text:
                additional_questions = QuestionGenerator.parse_questions_from_response(response.text)
                existing_questions.extend(additional_questions)
            
            return existing_questions[:target_count]
            
        except Exception as e:
            print(f"Error generating additional questions with Gemini: {e}")
            return QuestionGenerator._generate_default_questions(existing_questions, document_title, target_count)
    
    @staticmethod
    def _generate_default_questions(existing_questions: List[Dict], document_title: str, target_count: int) -> List[Dict]:
        """Generate default questions as fallback"""
        while len(existing_questions) < target_count:
            default_question = {
                "question": f"Question {len(existing_questions) + 1} about {document_title}",
                "correct_answer": "Please provide an answer based on the document",
                "type": "text",
                "keywords": [document_title.lower()],
                "hints": [
                    "Review the document content carefully",
                    "Focus on the main concepts discussed", 
                    "The answer is directly stated in the document"
                ],
                "difficulty": "medium"
            }
            existing_questions.append(default_question)
        
        return existing_questions[:target_count]

class HintGenerator:
    """Generates contextual hints using Gemini 2.0 Flash"""
    
    @staticmethod
    def generate_hint(question: str, correct_answer: str, student_answer: str, hint_level: int, document_context: str = "") -> str:
        """Generate a contextual hint based on student's previous attempt using Gemini"""
        
        # Import gemini_client from views
        try:
            from scheduler.views import gemini_client
        except ImportError:
            return f'Hint {hint_level}: Consider the main concepts from the document.'
        
        if not gemini_client:
            return f'Hint {hint_level}: Consider the main concepts from the document.'
        
        hint_prompts = {
            1: "gentle guidance without revealing the answer",
            2: "more specific direction that narrows down the answer", 
            3: "strong hint that almost points to the answer but still requires student thinking"
        }
        
        prompt = f"""You are a helpful tutor. A student answered a question incorrectly and needs {hint_prompts.get(hint_level, 'guidance')}.

Question: {question}
Correct Answer: {correct_answer}
Student's Answer: {student_answer}
Document Context: {document_context[:500]}...

Provide a {hint_prompts.get(hint_level)} hint that helps the student understand the concept without directly giving the answer. Be encouraging and educational.

Hint:"""

        try:
            response = gemini_client.generate_content(prompt)
            
            if response:
                response_text = response.text if hasattr(response, 'text') else str(response)
                if response_text:
                    return response_text.strip()
            
            return f'Hint {hint_level}: Consider the main concepts from the document.'
                
        except Exception as e:
            print(f"❌ Hint generation with Gemini failed: {e}")
            return f'Hint {hint_level}: Consider the main concepts from the document.'
