"""
Test Gemini connection
----------------------
- Loads .env
- Prints the GEMINI_API_KEY and GEMINI_MODEL (debug only)
- Tries to call Gemini Flash
"""

import os
from dotenv import load_dotenv

# Load .env מהתיקייה הראשית
load_dotenv()

# Debug: נוודא שהמפתח נטען
print("DEBUG GEMINI_API_KEY:", os.getenv("GEMINI_API_KEY"))
print("DEBUG GEMINI_MODEL:", os.getenv("GEMINI_MODEL"))

# אם חסר API key - נעצור
if not os.getenv("GEMINI_API_KEY"):
    raise ValueError("GEMINI_API_KEY missing in environment variables!")

import google.generativeai as genai

# קונפיגורציה
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model_name = os.getenv("GEMINI_MODEL", "models/gemini-2.5-flash")
model = genai.GenerativeModel(model_name)

# בדיקה בפועל
response = model.generate_content("Hello Gemini! Just say hi.")
print("MODEL RESPONSE:", response.text if hasattr(response, "text") else response)
# Add this test at the end of the file
print("\n=== Testing Question Generation ===")
test_content = "Data Structures and Algorithms are fundamental concepts in computer science. A stack is a LIFO data structure."
response = model.generate_content(f"Generate 2 multiple-choice questions about: {test_content}")
print("Question generation test:", response.text)