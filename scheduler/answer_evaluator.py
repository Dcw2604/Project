"""
Answer Evaluator
----------------
- Evaluates student answers using AI (Gemini) for open-ended questions
- Falls back to similarity matching if AI is unavailable
- Supports both multiple choice and open-ended questions
- Returns: (is_correct, score)
"""

import difflib
import os
import json
import re
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

try:
    import google.generativeai as genai
    
    # Configure Gemini
    API_KEY = os.getenv("GEMINI_API_KEY")
    if API_KEY:
        genai.configure(api_key=API_KEY)
        GEMINI_AVAILABLE = True
    else:
        logger.warning("GEMINI_API_KEY not found. AI evaluation will be disabled.")
        GEMINI_AVAILABLE = False
        
except ImportError:
    logger.warning("google.generativeai not available. AI evaluation will be disabled.")
    GEMINI_AVAILABLE = False


class AnswerEvaluator:
    def __init__(self, grading_instructions: str = ""):
        self.gemini_available = GEMINI_AVAILABLE
        self.grading_instructions = grading_instructions
    def evaluate_answer(self, question_text: str, correct_answer: str, student_answer: str, 
                       question_type: str = "multiple_choice", sample_answer: str = "", 
                       max_points: int = 10) -> Tuple[bool, float]:
        """
        Evaluate student's answer.
        
        Args:
            question_text (str): The original question.
            correct_answer (str): The expected correct answer (for multiple choice).
            student_answer (str): The student's submitted answer.
            question_type (str): Type of question ("multiple_choice" or "open_ended").
            sample_answer (str): Sample answer for open-ended questions.
            max_points (int): Maximum points for this question (default: 10).
            
        Returns:
            tuple: (is_correct: bool, score: float)
        """
        
        if not student_answer:
            return False, 0.0
        
         # Calculate points per question (100 divided by total questions)
        points_per_question = max_points

        # Handle multiple choice questions
        if question_type == "multiple_choice":
            return self._evaluate_multiple_choice(correct_answer, student_answer, max_points)
        
        # Handle open-ended questions with AI
        elif question_type == "open_ended":
            return self._evaluate_open_ended(question_text, student_answer, sample_answer, max_points)
        
        # Fallback to old method
        else:
            return self._evaluate_similarity(correct_answer, student_answer, max_points)
    
    def _evaluate_multiple_choice(self, correct_answer: str, student_answer: str, max_points: int) -> Tuple[bool, float]:
        """Evaluate multiple choice answers"""
        
        correct = str(correct_answer).strip().lower()
        student = str(student_answer).strip().lower()
        
        if student == correct:
            return True, float(max_points)
        else:
            return False, 0.0
    
    def _evaluate_open_ended(self, question_text: str, student_answer: str, sample_answer: str, max_points: int) -> Tuple[bool, float]:
        """Evaluate open-ended answers using AI"""
        
        if not self.gemini_available:
            logger.warning("Gemini not available, using similarity fallback")
            return self._evaluate_similarity(sample_answer, student_answer, max_points)
        
        try:
            # Create prompt for Gemini
            prompt = self._create_evaluation_prompt(question_text, student_answer, sample_answer, max_points, self.grading_instructions)
            # Get evaluation from Gemini
            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(prompt)
            result_text = response.text or str(response)
            
            # Parse Gemini's response
            points_earned = self._parse_gemini_response(result_text, max_points)
            
            # Determine if passing (>= 60%)
            is_passing = points_earned >= (max_points * 0.6)
            
            logger.info(f"AI Evaluation: {points_earned}/{max_points} points (Passing: {is_passing})")
            
            return is_passing, points_earned
            
        except Exception as e:
            logger.error(f"Gemini evaluation failed: {e}")
            # Fallback to similarity evaluation
            return self._evaluate_similarity(sample_answer, student_answer, max_points)
    
    def _create_evaluation_prompt(self, question_text: str, student_answer: str, sample_answer: str, max_points: int, grading_instructions: str = "") -> str:
        """Create a prompt for Gemini to evaluate the answer"""
        
        prompt = f"""
You are an expert teacher evaluating a student's answer. Please be fair and objective.

QUESTION: {question_text}

SAMPLE/EXPECTED ANSWER: {sample_answer}

STUDENT'S ANSWER: {student_answer}

MAXIMUM POINTS: {max_points}

LANGUAGE: Provide all feedback and reasoning in HEBREW language.

Please evaluate the student's answer and provide:
1. A score from 0 to {max_points} points
2. Brief feedback explaining the score

EVALUATION CRITERIA:
{f'''
SPECIFIC GRADING INSTRUCTIONS FROM TEACHER:
{grading_instructions}

Use the above instructions as your PRIMARY evaluation criteria.
''' if grading_instructions else '''
GENERAL CRITERIA (no specific instructions provided):
- Give credit for correct concepts even if wording is different
- Consider partial credit for partially correct answers
- Be generous but fair in scoring
- Focus on understanding, not exact wording
- Award points for relevant knowledge demonstrated
'''}

Respond in this EXACT JSON format:
{{
    "score": <number from 0 to {max_points}>,
    "feedback": "<brief explanation of the score>",
    "reasoning": "<why this score was given>"
}}

Only return the JSON, no other text.
"""
        return prompt
    
    def _parse_gemini_response(self, response_text: str, max_points: int) -> float:
        """Parse Gemini's response to extract the score"""
        
        try:
            # Try to find JSON in the response
            json_match = re.search(r'\{[^}]*"score"[^}]*\}', response_text)
            if json_match:
                json_str = json_match.group()
                result = json.loads(json_str)
                score = float(result.get("score", 0))
                
                # Ensure score is within bounds
                score = max(0, min(score, max_points))
                return score
            
            # Fallback: look for number pattern
            number_match = re.search(r'"score":\s*(\d+(?:\.\d+)?)', response_text)
            if number_match:
                score = float(number_match.group(1))
                return max(0, min(score, max_points))
            
            # Last resort: look for any number
            number_match = re.search(r'\b(\d+(?:\.\d+)?)\b', response_text)
            if number_match:
                score = float(number_match.group(1))
                return max(0, min(score, max_points))
            
            logger.warning(f"Could not parse score from Gemini response: {response_text}")
            return 0.0
            
        except Exception as e:
            logger.error(f"Error parsing Gemini response: {e}")
            return 0.0
    
    def _evaluate_similarity(self, correct_answer: str, student_answer: str, max_points: int) -> Tuple[bool, float]:
        """Fallback evaluation using similarity matching"""
        
        if not student_answer or not correct_answer:
            return False, 0.0
        
        # Normalize inputs
        correct = str(correct_answer).strip().lower()
        student = str(student_answer).strip().lower()
        
        # Exact match
        if student == correct:
            return True, float(max_points)
        
        # Similarity check
        similarity = difflib.SequenceMatcher(None, correct, student).ratio()
        
        if similarity > 0.85:  # very close → full credit
            return True, float(max_points)
        elif similarity > 0.6:  # somewhat close → partial credit
            return False, float(max_points * 0.5)
        else:  # wrong
            return False, 0.0