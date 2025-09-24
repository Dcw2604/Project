#!/usr/bin/env python
"""
Quick script to populate sample data for testing exam session functionality
Run with: python populate_sample_data.py
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from scheduler.models import User, Document, Topic, QuestionBank

def create_sample_data():
    print("🔄 Creating sample data...")
    
    # Create demo teacher user
    teacher, created = User.objects.get_or_create(
        username='demo_teacher',
        defaults={
            'email': 'teacher@demo.com',
            'role': 'teacher',
            'first_name': 'Demo',
            'last_name': 'Teacher'
        }
    )
    if created:
        teacher.set_password('demo123')
        teacher.save()
    print(f"✅ Teacher user: {teacher.username}")

    # Create sample document
    doc, created = Document.objects.get_or_create(
        title='Math Practice Document',
        defaults={
            'uploaded_by': teacher,
            'document_type': 'pdf',
            'file_path': '/demo/math_practice.pdf',
            'processing_status': 'completed',
            'questions_generated_count': 15
        }
    )
    print(f"✅ Document: {doc.title}")

    # Create topics
    topics_data = [
        {'name': 'Algebra', 'description': 'Basic algebraic concepts and equations'},
        {'name': 'Geometry', 'description': 'Shapes, areas, and geometric calculations'},
        {'name': 'Calculus', 'description': 'Differential and integral calculus'},
        {'name': 'Statistics', 'description': 'Data analysis and probability'},
        {'name': 'Trigonometry', 'description': 'Trigonometric functions and identities'}
    ]
    
    topics = []
    for topic_data in topics_data:
        topic, created = Topic.objects.get_or_create(
            name=topic_data['name'],
            defaults=topic_data
        )
        topics.append(topic)
        print(f"✅ Topic: {topic.name}")

    # Create sample questions
    questions_data = [
        {
            'question_text': 'Solve for x: 2x + 5 = 15',
            'topic': topics[0],  # Algebra
            'difficulty_level': '3',
            'correct_answer': 'x = 5',
            'option_a': 'x = 5',
            'option_b': 'x = 10',
            'option_c': 'x = 7',
            'option_d': 'x = 3'
        },
        {
            'question_text': 'What is the area of a circle with radius 4?',
            'topic': topics[1],  # Geometry
            'difficulty_level': '3',
            'correct_answer': '16π',
            'option_a': '8π',
            'option_b': '16π',
            'option_c': '4π',
            'option_d': '32π'
        },
        {
            'question_text': 'Find the derivative of x²',
            'topic': topics[2],  # Calculus
            'difficulty_level': '4',
            'correct_answer': '2x',
            'option_a': 'x',
            'option_b': '2x',
            'option_c': 'x²',
            'option_d': '2x²'
        },
        {
            'question_text': 'What is the probability of rolling a 6 on a fair die?',
            'topic': topics[3],  # Statistics
            'difficulty_level': '3',
            'correct_answer': '1/6',
            'option_a': '1/6',
            'option_b': '1/3',
            'option_c': '1/2',
            'option_d': '1/4'
        },
        {
            'question_text': 'What is sin(90°)?',
            'topic': topics[4],  # Trigonometry
            'difficulty_level': '3',
            'correct_answer': '1',
            'option_a': '0',
            'option_b': '1',
            'option_c': '-1',
            'option_d': '1/2'
        }
    ]
    
    for i, q_data in enumerate(questions_data):
        question, created = QuestionBank.objects.get_or_create(
            question_text=q_data['question_text'],
            defaults={
                'document': doc,
                'topic': q_data['topic'],
                'difficulty_level': q_data['difficulty_level'],
                'correct_answer': q_data['correct_answer'],
                'option_a': q_data['option_a'],
                'option_b': q_data['option_b'],
                'option_c': q_data['option_c'],
                'option_d': q_data['option_d'],
                'is_generated': True,  # Mark as chat-generated
                'question_type': 'multiple_choice'
            }
        )
        print(f"✅ Question {i+1}: {question.question_text[:50]}...")

    # Create additional questions for better testing
    for topic in topics:
        for diff in ['3', '4', '5']:
            for i in range(3):  # 3 questions per difficulty per topic
                question, created = QuestionBank.objects.get_or_create(
                    question_text=f"Sample {topic.name} question (Level {diff}) #{i+1}",
                    defaults={
                        'document': doc,
                        'topic': topic,
                        'difficulty_level': diff,
                        'correct_answer': 'Sample answer',
                        'option_a': 'Option A',
                        'option_b': 'Option B',
                        'option_c': 'Option D',
                        'option_d': 'Option D',
                        'is_generated': True,
                        'question_type': 'multiple_choice'
                    }
                )

    print(f"\n🎉 Sample data created successfully!")
    print(f"📊 Created {Topic.objects.count()} topics")
    print(f"📊 Created {QuestionBank.objects.filter(is_generated=True).count()} chat-generated questions")
    print(f"📊 Created {User.objects.filter(role='teacher').count()} teacher(s)")

if __name__ == '__main__':
    create_sample_data()
