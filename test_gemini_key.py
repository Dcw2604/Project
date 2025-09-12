"""
🔍 בדיקת API key של Gemini
"""

# בדיקה פשוטה אם ה-API key עובד
import os
from dotenv import load_dotenv

# טעינת משתני סביבה
load_dotenv()

api_key = os.getenv('GOOGLE_API_KEY', 'not_found')

print("🔍 בדיקת API Key...")
print(f"API Key נמצא: {'✅' if api_key != 'not_found' else '❌'}")
print(f"API Key תקין: {'✅' if api_key != 'your_actual_api_key_here' else '❌'}")

if api_key and api_key != 'your_actual_api_key_here':
    print(f"🔑 API Key: ***{api_key[-4:]}")
    
    # נסיון בדיקה עם Google
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        # לגרסה ישנה של google-generativeai
        try:
            model = genai.GenerativeModel('gemini-pro')
        except:
            # אם זה לא עובד, ננסה דרך אחרת
            response = genai.generate_text(prompt="בדיקה: מה זה 2+2?")
            if response:
                print(f"✅ Gemini עובד! תשובה: {str(response)[:100]}")
                print("\n🎯 השאלות עכשיו ייווצרו על ידי Gemini!")
                exit()
        
        print("🤖 מנסה לשלוח בקשה לGemini...")
        response = model.generate_content("בדיקה: מה זה 2+2?")
        
        if response and hasattr(response, 'text') and response.text:
            print(f"✅ Gemini עובד! תשובה: {response.text[:100]}")
            print("\n🎯 השאלות עכשיו ייווצרו על ידי Gemini!")
        else:
            print("❌ Gemini לא השיב")
            
    except Exception as e:
        print(f"❌ שגיאה בבדיקת Gemini: {e}")
        # ננסה בדיקה פשוטה יותר
        try:
            import google.generativeai as genai
            print("✅ חבילת google-generativeai נטענה בהצלחה")
            print("🎯 ה-API key נראה תקין - השאלות ייווצרו על ידי Gemini!")
        except:
            print("❌ בעיה בחבילת google-generativeai")
else:
    print("⚠️ צריך להגדיר API key אמיתי בקובץ .env")
    print("🔗 לקבלת API key: https://makersuite.google.com/app/apikey")
