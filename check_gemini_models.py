#!/usr/bin/env python
"""
🔍 בדיקת גרסאות Gemini זמינות
"""
import requests

api_key = 'AIzaSyBmFzrrIy5wtnyLjWMfMl_vLZnQiVtAJiw'
url = 'https://generativelanguage.googleapis.com/v1beta/models'
headers = {'x-goog-api-key': api_key}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    models = response.json()
    print('🤖 Available Gemini models:')
    
    for model in models.get('models', []):
        name = model.get('name', 'N/A')
        if 'gemini' in name.lower():
            print(f'   ✅ {name}')
            
    print('\n🚀 המלצות לשיפור:')
    print('   🔥 gemini-1.5-pro-latest - הגרסה המתקדמת ביותר')
    print('   ⚡ gemini-1.5-flash-latest - מהיר ואיכותי')
    print('   🧠 gemini-1.5-pro-002 - גרסה יציבה מתקדמת')
            
else:
    print(f'❌ Error: {response.status_code}')
    print(response.text)
