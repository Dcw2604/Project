#!/usr/bin/env python3
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from scheduler.models import Document
from scheduler.views import generate_questions_with_gemini

print("🧪 Testing Question Generation with Gemini")
print("=" * 50)

# Get a document with content
doc = Document.objects.filter(
    uploaded_by__role='teacher',
    extracted_text__isnull=False
).exclude(extracted_text='').first()

if not doc:
    print("❌ No documents with content found")
    sys.exit(1)

print(f"📚 Using document: {doc.title}")
print(f"📄 Content length: {len(doc.extracted_text)} characters")
print(f"👤 Uploaded by: {doc.uploaded_by.username}")

# Test question generation
print("\n❓ Generating questions...")
try:
    questions = generate_questions_with_gemini(
        doc.extracted_text,
        doc.title,
        count=3  # Generate just 3 for testing
    )
    
    print(f"✅ Generated {len(questions)} questions")
    
    for i, q in enumerate(questions, 1):
        print(f"\nQuestion {i}:")
        print(f"  Q: {q.get('question', 'N/A')}")
        print(f"  A: {q.get('correct_answer', 'N/A')}")
        print(f"  Type: {q.get('type', 'N/A')}")
        print(f"  Hints: {len(q.get('hints', []))}")
        
except Exception as e:
    print(f"❌ Error generating questions: {e}")
    import traceback
    traceback.print_exc()