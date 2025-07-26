#!/usr/bin/env python
"""
Export chat interactions for model training
Run with: python export_training_data.py
"""
import os
import django
import json
import csv

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from scheduler.models import ChatInteraction

def export_to_json():
    """Export all chat interactions to JSON format"""
    interactions = ChatInteraction.objects.all()
    data = []
    
    for chat in interactions:
        data.append({
            'student': chat.student.username,
            'question': chat.question,
            'answer': chat.answer,
            'timestamp': chat.timestamp.isoformat()
        })
    
    with open('training_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Exported {len(data)} interactions to training_data.json")

def export_to_csv():
    """Export all chat interactions to CSV format"""
    interactions = ChatInteraction.objects.all()
    
    with open('training_data.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['student', 'question', 'answer', 'timestamp'])
        
        for chat in interactions:
            writer.writerow([
                chat.student.username,
                chat.question,
                chat.answer,
                chat.timestamp.isoformat()
            ])
    
    print(f"Exported {interactions.count()} interactions to training_data.csv")

if __name__ == '__main__':
    print("Exporting training data...")
    export_to_json()
    export_to_csv()
    print("Export complete!")
