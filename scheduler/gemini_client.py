import google.generativeai as genai
from django.conf import settings
import logging
import requests
import json
import re

logger = logging.getLogger(__name__)

class GeminiClient:
    def __init__(self):
        """Initialize Gemini client with API key from settings"""
        try:
            genai.configure(api_key=settings.GOOGLE_API_KEY)
            print(f"🔑 API Key configured: {'***' + settings.GOOGLE_API_KEY[-4:] if settings.GOOGLE_API_KEY and settings.GOOGLE_API_KEY != 'your_actual_api_key_here' else 'Default placeholder'}")
            
            # בדיקה אם יש API key תקין
            if settings.GOOGLE_API_KEY and settings.GOOGLE_API_KEY != 'your_actual_api_key_here':
                # ננסה עם הגרסה הישנה של google-generativeai
                try:
                    # ננסה דרכים שונות לגרסה הישנה
                    try:
                        self.model = genai.GenerativeModel('gemini-pro')
                        self.api_version = "pro"
                        print(f"✅ Gemini Pro initialized successfully")
                    except:
                        # אם GenerativeModel לא קיים, ננסה דרך אחרת
                        # פשוט נגדיר שיש model
                        self.model = "gemini-2.0-flash"  # marker שיש לנו API key
                        self.api_version = "2.0-flash"
                        print(f"✅ Gemini 2.0 Flash mode initialized successfully 🚀")
                except Exception as e:
                    print(f"⚠️ Gemini initialization warning: {e}")
                    self.model = "gemini-fallback"  # עדיין יש API key
                    self.api_version = "api-available"
                    print(f"✅ Gemini API key available, using custom implementation")
            else:
                # אין API key
                self.model = None
                self.api_version = "fallback"
                print(f"⚠️ Gemini client in fallback mode - no API key")
        except Exception as e:
            print(f"❌ Failed to initialize Gemini client: {e}")
            self.model = None
            self.api_version = "fallback"
    
    def generate_content(self, prompt, system_instruction=None):
        """
        Generate content using Gemini Flash
        """
        if not self.model or self.api_version == "fallback":
            return self._fallback_response(prompt)
        
        try:
            if system_instruction:
                full_prompt = f"System: {system_instruction}\n\nUser: {prompt}"
            else:
                full_prompt = prompt
            
            # לגרסה החדשה של Gemini 2.0 Flash
            if self.api_version == "2.0-flash":
                try:
                    # ננסה עם REST API ישירות
                    return self._rest_api_call(full_prompt)
                except Exception as e:
                    print(f"Gemini 2.0 Flash error: {e}")
                    return self._fallback_response(prompt)
            
            elif hasattr(self.model, 'generate_content'):
                # גרסה חדשה
                response = self.model.generate_content(full_prompt)
                return response.text if response and hasattr(response, 'text') else self._fallback_response(prompt)
            
            else:
                # גרסה מותאמת אישית
                return self._smart_fallback_response(prompt)
        
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return self._fallback_response(prompt)
    
    def _rest_api_call(self, prompt):
        """קריאה ישירה ל-Gemini REST API עם 2.0 Flash"""
        try:
            import requests
            import json
            
            # משתמש ב-Gemini 2.0 Flash החדש!
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
            headers = {
                'Content-Type': 'application/json',
                'x-goog-api-key': settings.GOOGLE_API_KEY
            }
            
            data = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.4,  # פחות אקראיות לעקביות שפה
                    "maxOutputTokens": 1024,  # מגביל את אורך התשובה
                    "topP": 0.8,
                    "topK": 40,
                    "stopSequences": ["\n\n---", "תשובה נוספת:", "אלטרנטיבה:", "English:", "עברית:"]  # עוצר במקומות מסוימים
                },
                "safetySettings": [
                    {
                        "category": "HARM_CATEGORY_HARASSMENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    }
                ]
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    content = result['candidates'][0]['content']['parts'][0]['text']
                    print(f"✅ REST API success with Gemini 2.0 Flash 🚀")
                    # ניקוי השפה
                    cleaned_content = self._clean_hebrew_response(content)
                    return cleaned_content
                else:
                    print(f"⚠️ REST API - no content")
                    return self._fallback_response(prompt)
            else:
                print(f"❌ REST API error: {response.status_code} - {response.text}")
                return self._fallback_response(prompt)
                
        except Exception as e:
            print(f"❌ REST API exception: {e}")
            return self._fallback_response(prompt)
    
    def _clean_hebrew_response(self, text):
        """ניקוי תשובה לעברית נקייה"""
        if not text:
            return text
            
        # החלפת מילים באנגלית לעברית
        english_to_hebrew = {
            'answer': 'תשובה',
            'solution': 'פתרון', 
            'step': 'שלב',
            'example': 'דוגמה',
            'equation': 'משוואה',
            'algebra': 'אלגברה',
            'math': 'מתמטיקה',
            'calculation': 'חישוב',
            'result': 'תוצאה',
            'problem': 'בעיה',
            'formula': 'נוסחה',
            'x =': 'x =',  # משתנים נשארים כמו שהם
            'let': 'בואו',
            'so': 'אז',
            'therefore': 'לכן',
            'because': 'כי',
            'where': 'כאשר',
            'then': 'אז'
        }
        
        cleaned = text
        
        # החלפת מילים באנגלית
        for eng, heb in english_to_hebrew.items():
            # החלפה רק אם המילה עומדת לבד (לא חלק ממילה אחרת)
            cleaned = re.sub(r'\b' + re.escape(eng) + r'\b', heb, cleaned, flags=re.IGNORECASE)
        
        # ניקוי כותרות מיותרות
        cleaned = re.sub(r'^(תשובה:|Answer:|פתרון:|Solution:)\s*', '', cleaned, flags=re.MULTILINE)
        
        # ניקוי רווחים מיותרים
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned
        
    def _fallback_response(self, prompt):
        """פתרון גיבוי כשהGemini לא זמין - כולל תמיכה בעברית"""
        # תשובות בסיסיות לשאלות נפוצות
        prompt_lower = prompt.lower()
        
        # חיפוש מתמטיקה בעברית ובאנגלית
        if any(word in prompt_lower for word in ['2+2', '2 + 2', 'שניים ועוד שניים']):
            return "2+2 = 4"
        elif any(word in prompt_lower for word in ['4*3', '4 * 3', 'ארבע כפול שלוש']):
            return "4 × 3 = 12"
        elif any(word in prompt_lower for word in ['3+5', '3 + 5', 'שלוש ועוד חמש']):
            return "3 + 5 = 8"
        elif any(word in prompt_lower for word in ['כמה זה', 'מה זה', 'חשב', 'calculate', 'math']):
            return "אני יכול לעזור לך עם חישובים מתמטיים פשוטים. נסה לשאול שאלה כמו '2+2' או '5*3'."
        
        # ברכות ופתיחות
        elif any(word in prompt_lower for word in ['שלום', 'היי', 'הי', 'hello', 'hi']):
            return "שלום! אני כאן לעזור לך בלימודים. איך אני יכול לעזור?"
        elif any(word in prompt_lower for word in ['תודה', 'thanks', 'thank you', 'תודה רבה']):
            return "בשמחה לעזור! יש לך שאלות נוספות?"
        elif any(word in prompt_lower for word in ['מה שלומך', 'איך אתה', 'how are you', 'מה נשמע']):
            return "אני כאן לעזור לך בלימודים! יש לך שאלה שאוכל לעזור בה?"
        
        # שאלות על המערכת
        elif any(word in prompt_lower for word in ['מי אתה', 'who are you', 'מה אתה']):
            return "אני עוזר AI שנועד לעזור לך בלימודים. אני יכול לעזור עם מתמטיקה, לענות על שאלות ולהדריך אותך בחומר הלימוד."
        elif any(word in prompt_lower for word in ['עזרה', 'help', 'איך']):
            return "אני יכול לעזור לך עם:\n• חישובים מתמטיים\n• שאלות על חומר הלימוד\n• הכנה למבחנים\n• הסברים על נושאים שונים\n\nפשוט שאל!"
        
        # תשובת ברירת מחדל
        else:
            return "מצטער, שירות ה-AI הפלטפורמה זמנית לא זמין. בינתיים אני יכול לעזור עם חישובים פשוטים. נסה לשאול '2+2' או שאל את המורה שלך."
    
    def _smart_fallback_response(self, prompt):
        """תשובה חכמה יותר כשיש API key אבל הגרסה ישנה"""
        prompt_lower = prompt.lower()
        
        # תשובות מתמטיות משופרות
        math_responses = {
            "2+2": "2 + 2 = 4",
            "4*3": "4 × 3 = 12", 
            "5+3": "5 + 3 = 8",
            "10-5": "10 - 5 = 5",
            "6*2": "6 × 2 = 12",
            "15/3": "15 ÷ 3 = 5"
        }
        
        # חיפוש תרגום ביטויים מתמטיים
        for expr, result in math_responses.items():
            if expr in prompt_lower or expr.replace('*', 'כפול').replace('+', 'ועוד') in prompt_lower:
                return f"התשובה היא: {result}"
        
        # תשובות לימודיות משופרות
        if any(word in prompt_lower for word in ['למידה', 'לימוד', 'שיעור', 'מבחן']):
            return "אני כאן לעזור לך בלימודים! אוכל לעזור עם:\n• פתרון תרגילים מתמטיים\n• הכנה למבחנים\n• הסברת חומר\n• יצירת שאלות תרגול\n\nמה תרצה ללמוד היום?"
        
        elif any(word in prompt_lower for word in ['מה זה', 'הסבר', 'explain']):
            return "אשמח להסביר לך! אני יכול לעזור עם הסברים על נושאים שונים. ספר לי על איזה נושא תרצה לשמוע - מתמטיקה, מדעים, היסטוריה או נושא אחר."
        
        # תשובה ברירת מחדל משופרת
        return "שלום! אני עוזר הלמידה שלך. למרות שה-AI המתקדם לא זמין כרגע, אני עדיין יכול לעזור לך עם:\n• חישובים מתמטיים פשוטים\n• מענה לשאלות כלליות\n• הכוונה בלימודים\n\nמה תרצה לשאול?"
    
    def generate_questions(self, document_content, num_questions=10):
        """
        Generate exam questions from document content
        """
        if not self.model or self.api_version == "fallback":
            return self._fallback_questions(num_questions)
        
        # אם יש API key אבל הגרסה ישנה, ננסה דרך מותאמת
        if self.api_version in ["2.0-flash", "legacy", "api-available"]:
            return self._generate_questions_with_api(document_content, num_questions)
        
        # גרסה רגילה עם GenerativeModel
        # מגביל את אורך התוכן לאורך מתאים
        max_content_length = 3000
        if len(document_content) > max_content_length:
            document_content = document_content[:max_content_length] + "..."
        
        prompt = f"""
        בהתבסס על התוכן הבא, צור {num_questions} שאלות מרובות ברירה באיכות גבוהה.

        תוכן המסמך:
        {document_content}

        דרישות:
        1. כל שאלה חייבת להיות ברורה ומדויקת
        2. 4 אפשרויות תשובה לכל שאלה (A, B, C, D)
        3. רק תשובה אחת נכונה
        4. שאלות ברמות קושי שונות
        5. כסה נושאים שונים מהחומר
        6. השתמש בעברית או אנגלית לפי השפה בחומר

        פורמט התשובה (JSON בלבד):
        {{
            "questions": [
                {{
                    "question_text": "טקסט השאלה",
                    "options": {{
                        "A": "אפשרות ראשונה", 
                        "B": "אפשרות שנייה",
                        "C": "אפשרות שלישית",
                        "D": "אפשרות רביעית"
                    }},
                    "correct_answer": "A",
                    "explanation": "הסבר קצר למה זו התשובה הנכונה"
                }}
            ]
        }}

        חשוב: החזר רק JSON ללא טקסט נוסף!
        """
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # ניקוי התגובה מכל דבר שאינו JSON
            # מחפש JSON block
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_text = json_match.group()
            else:
                json_text = response_text
            
            # ניסיון לפרסר את ה-JSON
            questions_data = json.loads(json_text)
            questions = questions_data.get('questions', [])
            
            formatted_questions = []
            for i, q in enumerate(questions):
                formatted_questions.append({
                    'id': f"gemini_q_{i+1}",
                    'question_number': i + 1,
                    'question_text': q.get('question_text', ''),
                    'question_type': 'multiple_choice',
                    'has_options': True,
                    'options': q.get('options', {}),
                    'correct_answer': q.get('correct_answer', 'A'),
                    'explanation': q.get('explanation', '')
                })
            
            print(f"✅ Generated {len(formatted_questions)} questions successfully with Gemini")
            return formatted_questions
            
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse Gemini JSON response: {e}")
            print(f"Response was: {response_text[:200]}...")
            return self._fallback_questions(num_questions)
        except Exception as e:
            print(f"❌ Error generating questions with Gemini: {e}")
            return self._fallback_questions(num_questions)
    
    def generate_questions_fast(self, document_content, num_questions=10, difficulty="mixed"):
        """
        יצירת שאלות מהירה עבור מרצים
        """
        if not self.model or self.api_version == "fallback":
            print("⚠️ Gemini לא זמין, עובר ל-fallback questions")
            return self._fallback_questions(num_questions)
        
        # חיתוך התוכן לגודל אופטימלי (מהיר יותר)
        max_content_length = 2000  # מקטינים לעיבוד מהיר
        if len(document_content) > max_content_length:
            document_content = document_content[:max_content_length] + "..."
        
        # מיפוי רמות קושי לעברית
        difficulty_map = {
            "basic": "בסיסי - שאלות פשוטות על עובדות",
            "intermediate": "בינוני - שאלות הבנה ויישום", 
            "advanced": "מתקדם - שאלות ניתוח וחשיבה",
            "mixed": "מעורב - שילוב של רמות שונות"
        }
        
        difficulty_hebrew = difficulty_map.get(difficulty, "מעורב")
        
        prompt = f"""יצר {num_questions} שאלות מרובות ברירה איכותיות מהתוכן הבא.

תוכן המסמך:
{document_content}

דרישות:
1. שאלות קצרות וברורות בעברית בלבד
2. 4 אפשרויות תשובה (A,B,C,D) 
3. רק תשובה אחת נכונה
4. רמת קושי: {difficulty_hebrew}
5. ללא הסברים מיותרים
6. שאלות מגוונות ומעניינות

פורמט JSON בלבד:
{{"questions": [
  {{"question_text": "השאלה?", "options": {{"A": "אפשרות 1", "B": "אפשרות 2", "C": "אפשרות 3", "D": "אפשרות 4"}}, "correct_answer": "A"}}
]}}"""
        
        try:
            response = self._rest_api_call(prompt)
            
            if response:
                # ניקוי התשובה והמרה ל-JSON
                response_cleaned = self._clean_json_response(response)
                
                try:
                    data = json.loads(response_cleaned)
                    questions = data.get('questions', [])
                    
                    formatted_questions = []
                    for i, q in enumerate(questions[:num_questions]):  # הגבלה למספר הרצוי
                        formatted_questions.append({
                            'id': f'gemini_2_0_fast_q_{i+1}',
                            'question_number': i + 1,
                            'question_text': q.get('question_text', ''),
                            'question_type': 'multiple_choice',
                            'has_options': True,
                            'options': q.get('options', {}),
                            'correct_answer': q.get('correct_answer', 'A'),
                            'difficulty': difficulty,
                            'source': 'gemini_2_0_fast'
                        })
                    
                    print(f"✅ Generated {len(formatted_questions)} fast questions with Gemini 2.0 Flash 🚀")
                    return formatted_questions
                    
                except json.JSONDecodeError as e:
                    print(f"⚠️ Failed to parse JSON: {e}, using fallback")
                    return self._fallback_questions(num_questions)
            
        except Exception as e:
            print(f"⚠️ Gemini API error: {e}")
            return self._fallback_questions(num_questions)
        
        return self._fallback_questions(num_questions)
    
    def _clean_json_response(self, response):
        """ניקוי תשובה JSON מטקסט מיותר"""
        # חיפוש JSON בטקסט
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            return json_match.group(0)
        return response
    
    def chat_response(self, user_message, context="", chat_history=[]):
        """
        Generate chat response for interactive learning - Gemini 2.0 Flash Enhanced
        """
        try:
            if not self.model or self.api_version == "fallback":
                print("⚠️ Gemini לא זמין, עובר ל-fallback response")
                return self._fallback_response(user_message)
            
            # הנחיות מערכת ברורות וחדות
            system_instruction = """אתה עוזר AI לחינוך המשתמש ב-Gemini 2.0 Flash.

חוקים קפדניים:
1. תמיד ענה תשובה אחת בלבד
2. אל תכפיל תשובות או תחזור על עצמך
3. השתמש בעברית בלבד - אל תערבב שפות
4. כתוב מספרים בספרות עבריות או ערביות (0-9) ולא באנגלית
5. אל תכתוב "תשובה:" או כותרות נוספות
6. ענה ישירות על השאלה בעברית נקייה

כללי שפה:
- השתמש רק בעברית
- מספרים: 1, 2, 3 (לא one, two, three)
- מושגים מתמטיים: משוואה, אלגברה, חיבור (לא equation, algebra, addition)
- מילות מפתח: פתרון, שלב, דוגמה (לא solution, step, example)

סגנון:
- השתמש בשיטה הסוקרטית כשמתאים
- תן הסברים קצרים וברורים בעברית
- עודד חשיבה עצמאית
- היה ידידותי אך מקצועי"""
            
            # בניית הקשר קצר ומדויק
            conversation_context = ""
            if chat_history and len(chat_history) > 0:
                # שמירת מידע חשוב מכל השיחה + 2 הודעות אחרונות
                important_info = []
                recent_context = ""
                
                # חיפוש מידע חשוב בכל ההיסטוריה
                for msg in chat_history:
                    if isinstance(msg, tuple) and len(msg) >= 2:
                        user_part = msg[0].strip() if msg[0] else ''
                        # חיפוש דפוסי מידע חשוב (שם, גיל, נושא לימוד)
                        if any(word in user_part.lower() for word in ['קוראים לי', 'שמי', 'אני', 'בן', 'בת', 'לומד', 'לומדת']):
                            important_info.append(f"מידע: {user_part}")
                
                # 2 הודעות אחרונות לקונטקסט
                for msg in chat_history[-2:]:
                    if isinstance(msg, tuple) and len(msg) >= 2:
                        user_part = msg[0].strip() if msg[0] else ''
                        assistant_part = msg[1].strip() if msg[1] else ''
                    elif isinstance(msg, dict):
                        user_part = msg.get('user', '').strip()
                        assistant_part = msg.get('assistant', '').strip()
                    else:
                        continue
                        
                    if user_part and assistant_part:
                        recent_context += f"משתמש: {user_part}\nAI: {assistant_part}\n"
                
                # שילוב המידע החשוב עם ההקשר האחרון
                if important_info:
                    conversation_context = "מידע חשוב:\n" + "\n".join(important_info[-3:]) + "\n\n"
                if recent_context:
                    conversation_context += "שיחה אחרונה:\n" + recent_context
            
            # prompt פשוט וישיר
            if conversation_context:
                enhanced_prompt = f"""הקשר השיחה:
{conversation_context}

שאלה נוכחית: {user_message}

ענה תשובה אחת בלבד, ישירה וברורה:"""
            else:
                enhanced_prompt = f"""שאלה: {user_message}

ענה תשובה אחת בלבד, ישירה וברורה:"""
            
            # אם יש חומר רלוונטי, נוסיף אותו בקצרה
            if context and context.strip():
                enhanced_prompt = f"""חומר רלוונטי:
{context[:500]}

{enhanced_prompt}"""
            
            response = self._rest_api_call(enhanced_prompt)
            if response and response.strip():
                # ניקוי התשובה מכפילויות אפשריות
                cleaned_response = response.strip()
                
                # אם יש כמה פסקאות, ניקח רק את הראשונה
                if '\n\n' in cleaned_response:
                    cleaned_response = cleaned_response.split('\n\n')[0]
                
                return cleaned_response
            else:
                return self._fallback_response(user_message)
                
        except Exception as e:
            print(f"❌ שגיאה ב-chat_response: {e}")
            return self._fallback_response(user_message)
    
    def _fallback_questions(self, num_questions):
        """
        Fallback questions in case Gemini fails
        """
        fallback = []
        for i in range(min(num_questions, 5)):  # מקסימום 5 שאלות fallback
            fallback.append({
                'id': f"fallback_q_{i+1}",
                'question_number': i + 1,
                'question_text': f"שאלה {i+1}: נושא כללי מהחומר שנלמד",
                'question_type': 'multiple_choice',
                'has_options': True,
                'options': {
                    'A': 'אפשרות ראשונה',
                    'B': 'אפשרות שנייה', 
                    'C': 'אפשרות שלישית',
                    'D': 'אפשרות רביעית'
                },
                'correct_answer': 'A',
                'explanation': 'שאלה כללית'
            })
        return fallback
    
    def _generate_questions_with_api(self, document_content, num_questions):
        """יצירת שאלות עם Gemini 2.0 Flash - גרסה משופרת"""
        try:
            # נקצר את התוכן
            max_content_length = 3000  # יותר תוכן ל-2.0 Flash
            if len(document_content) > max_content_length:
                document_content = document_content[:max_content_length] + "..."
            
            # Prompt משופר ל-Gemini 2.0 Flash
            prompt = f"""אתה מומחה ליצירת שאלות חינוכיות איכותיות. צור {num_questions} שאלות מרובות ברירה מתקדמות על בסיס התוכן הבא:

{document_content}

דרישות איכות גבוהה:
1. כל שאלה עם 4 אפשרויות מדויקות (A, B, C, D)
2. רק תשובה אחת נכונה לכל שאלה
3. שאלות ברמות קושי שונות (קל, בינוני, מתקדם)
4. כסה נושאים מגוונים מהחומר
5. הימנע משאלות טריוויאליות
6. ודא שהשאלות בדקדוק עברי תקין
7. כלול הסברים מפורטים לתשובות הנכונות

תבנית JSON מדויקת (ללא טקסט נוסף):
{{
    "questions": [
        {{
            "question_text": "שאלה ברורה ומדויקת שדורשת הבנה של החומר",
            "options": {{
                "A": "אפשרות ראשונה מפורטת ומדויקת",
                "B": "אפשרות שנייה עם פרטים רלוונטיים", 
                "C": "אפשרות שלישית המבוססת על החומר",
                "D": "אפשרות רביעית הגיונית אך שגויה"
            }},
            "correct_answer": "A",
            "explanation": "הסבר מפורט למה התשובה הנכונה היא A, כולל קישור לחומר הנלמד"
        }}
    ]
}}

חשוב: החזר אך ורק JSON תקין ללא טקסט נוסף!"""

            # שימוש ב-Gemini 2.0 Flash
            response_text = self._rest_api_call(prompt)
            
            if response_text and "questions" in response_text:
                # ניסיון לפרסר JSON משופר
                try:
                    import json
                    import re
                    
                    # ניקוי התגובה וחיפוש JSON
                    cleaned_response = response_text.strip()
                    
                    # חיפוש JSON block מדויק יותר
                    json_match = re.search(r'\{[\s\S]*"questions"[\s\S]*\}', cleaned_response, re.DOTALL)
                    if json_match:
                        json_text = json_match.group()
                    else:
                        json_text = cleaned_response
                    
                    questions_data = json.loads(json_text)
                    questions = questions_data.get('questions', [])
                    
                    formatted_questions = []
                    for i, q in enumerate(questions):
                        formatted_questions.append({
                            'id': f"gemini_2_0_q_{i+1}",
                            'question_number': i + 1,
                            'question_text': q.get('question_text', ''),
                            'question_type': 'multiple_choice',
                            'has_options': True,
                            'options': q.get('options', {}),
                            'correct_answer': q.get('correct_answer', 'A'),
                            'explanation': q.get('explanation', '')
                        })
                    
                    print(f"✅ Generated {len(formatted_questions)} questions with Gemini 2.0 Flash 🚀")
                    return formatted_questions
                    
                except json.JSONDecodeError as e:
                    print(f"❌ Failed to parse Gemini 2.0 JSON: {e}")
                    print(f"Response preview: {response_text[:200]}...")
                    return self._fallback_questions(num_questions)
            else:
                print(f"❌ No valid response from Gemini 2.0 API")
                return self._fallback_questions(num_questions)
                
        except Exception as e:
            print(f"❌ Error generating questions with Gemini 2.0: {e}")
            return self._fallback_questions(num_questions)
    
    def _parse_questions_from_text(self, text, num_questions):
        """ניתוח שאלות מטקסט של Gemini"""
        questions = []
        try:
            lines = text.split('\n')
            current_question = {}
            question_count = 0
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # חיפוש שאלה
                if line.startswith('שאלה') and ':' in line:
                    if current_question and 'question_text' in current_question:
                        questions.append(current_question)
                        question_count += 1
                    
                    current_question = {
                        'id': f"gemini_q_{question_count + 1}",
                        'question_number': question_count + 1,
                        'question_text': line.split(':', 1)[1].strip(),
                        'question_type': 'multiple_choice',
                        'has_options': True,
                        'options': {},
                        'correct_answer': 'A',
                        'explanation': 'נוצר על ידי Gemini AI'
                    }
                
                # חיפוש אפשרויות
                elif line.startswith(('A)', 'B)', 'C)', 'D)')):
                    if current_question:
                        option_letter = line[0]
                        option_text = line[2:].strip()
                        current_question['options'][option_letter] = option_text
                
                # חיפוש תשובה נכונה
                elif line.startswith('נכון:'):
                    if current_question:
                        correct = line.split(':', 1)[1].strip()
                        current_question['correct_answer'] = correct
            
            # הוספת השאלה האחרונה
            if current_question and 'question_text' in current_question:
                questions.append(current_question)
            
            # מילוי שאלות חסרות עם fallback אם צריך
            while len(questions) < min(num_questions, 3):
                questions.extend(self._fallback_questions(1))
                
            return questions
        
        except Exception as e:
            print(f"Error parsing questions: {e}")
            return self._fallback_questions(num_questions)

    def generate_questions_fast(self, document_content, num_questions=10, difficulty="mixed"):
        """
        יצירת שאלות מהירה עבור מרצים
        """
        if not self.model or self.api_version == "fallback":
            print("⚠️ Gemini לא זמין, עובר ל-fallback questions")
            return self._fallback_questions(num_questions)
        
        # חיתוך התוכן לגודל אופטימלי (מהיר יותר)
        max_content_length = 2000  # מקטינים לעיבוד מהיר
        if len(document_content) > max_content_length:
            document_content = document_content[:max_content_length] + "..."
        
        # מיפוי רמות קושי לעברית
        difficulty_map = {
            "basic": "בסיסי - שאלות פשוטות על עובדות",
            "intermediate": "בינוני - שאלות הבנה ויישום", 
            "advanced": "מתקדם - שאלות ניתוח וחשיבה",
            "mixed": "מעורב - שילוב של רמות שונות"
        }
        
        difficulty_hebrew = difficulty_map.get(difficulty, "מעורב")
        
        prompt = f"""יצר {num_questions} שאלות מרובות ברירה איכותיות מהתוכן הבא.

תוכן המסמך:
{document_content}

דרישות:
1. שאלות קצרות וברורות בעברית בלבד
2. 4 אפשרויות תשובה (A,B,C,D) 
3. רק תשובה אחת נכונה
4. רמת קושי: {difficulty_hebrew}
5. ללא הסברים מיותרים
6. שאלות מגוונות ומעניינות

פורמט JSON בלבד:
{{"questions": [
  {{"question_text": "השאלה?", "options": {{"A": "אפשרות 1", "B": "אפשרות 2", "C": "אפשרות 3", "D": "אפשרות 4"}}, "correct_answer": "A"}}
]}}"""
        
        try:
            response = self._rest_api_call(prompt)
            
            if response:
                # ניקוי התשובה והמרה ל-JSON
                response_cleaned = self._clean_json_response(response)
                
                try:
                    data = json.loads(response_cleaned)
                    questions = data.get('questions', [])
                    
                    formatted_questions = []
                    for i, q in enumerate(questions[:num_questions]):  # הגבלה למספר הרצוי
                        formatted_questions.append({
                            'id': f'gemini_2_0_fast_q_{i+1}',
                            'question_number': i + 1,
                            'question_text': q.get('question_text', ''),
                            'question_type': 'multiple_choice',
                            'has_options': True,
                            'options': q.get('options', {}),
                            'correct_answer': q.get('correct_answer', 'A'),
                            'difficulty': difficulty,
                            'source': 'gemini_2_0_fast'
                        })
                    
                    print(f"✅ Generated {len(formatted_questions)} fast questions with Gemini 2.0 Flash 🚀")
                    return formatted_questions
                    
                except json.JSONDecodeError as e:
                    print(f"⚠️ Failed to parse JSON: {e}, using fallback")
                    return self._fallback_questions(num_questions)
            
        except Exception as e:
            print(f"⚠️ Gemini API error: {e}")
            return self._fallback_questions(num_questions)
        
        return self._fallback_questions(num_questions)
    
    def _clean_json_response(self, response):
        """ניקוי תשובה JSON מטקסט מיותר"""
        # חיפוש JSON בטקסט
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            return json_match.group(0)
        return response

# יצירת instance גלובלי
try:
    gemini_client = GeminiClient()
    print("🤖 Gemini client ready")
except Exception as e:
    print(f"❌ Failed to create Gemini client: {e}")
    gemini_client = None
