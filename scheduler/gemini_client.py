"""
Gemini Client — Cleaned
-----------------------
- Provides wrapper around Gemini API.
- Generates multiple-choice questions with difficulty levels.
"""

import os
import logging
import google.generativeai as genai

logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(levelname)s %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Configure Gemini
API_KEY = os.getenv("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    logger.warning("GEMINI_API_KEY not found. Gemini features will be disabled.")
    API_KEY = None



def generate_questions_from_text(text: str, num_questions: int = 5):
    """
    Generate multiple-choice questions from input text using Gemini Flash 2.0.
    Each question includes: text, 4 options, correct answer, explanation, difficulty.
    """
    if not API_KEY:
        logger.warning("Gemini API key not configured. Returning empty questions.")
        return []
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        prompt = f"""
        Create {num_questions} multiple-choice questions (with exactly 4 options each) 
        based only on the following text:

        {text}

        Return the output strictly as a JSON array of objects, where each object has:
        - question_text (string)
        - option_a (string)
        - option_b (string)
        - option_c (string)
        - option_d (string)
        - correct_answer (string: one of "A","B","C","D")
        - explanation (string)
        - difficulty_level (integer: 3=easy, 4=medium, 5=hard)
        """

        response = model.generate_content(prompt)

        # Parse response
        questions = response.text.strip()
        import json
        parsed = json.loads(questions)

        logger.info("Gemini generated %s questions", len(parsed))
        return parsed

    except Exception as e:
        logger.error("Gemini question generation failed: %s", e)
        return []
