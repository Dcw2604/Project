#!/usr/bin/env python3
"""
Enhanced Question Generation Script
Generates 30 validated math questions with even distribution across difficulty levels.
Uses the enhanced DocumentProcessor with AI validation and RAG-based learning.
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from scheduler.models import Document, QuestionBank
from scheduler.document_processing import DocumentProcessor
from django.core.exceptions import ObjectDoesNotExist


def generate_30_questions():
    """Generate 30 validated math questions with perfect distribution"""
    
    print("🔄 Starting Enhanced Question Generation...")
    print("=" * 60)
    
    try:
        # Get a document to use for generation
        document = Document.objects.first()
        if not document:
            print("❌ Error: No documents found in database.")
            return
        
        print(f"📄 Using document: {document.filename}")
        print(f"📊 Document difficulty level: {document.difficulty_level}")
        
        # Initialize enhanced processor
        processor = DocumentProcessor()
        
        # Target distribution: 10 questions per level
        target_distribution = {3: 10, 4: 10, 5: 10}
        current_counts = {3: 0, 4: 0, 5: 0}
        
        print("\n🎯 Target Distribution:")
        for level, count in target_distribution.items():
            print(f"   Level {level}: {count} questions")
        
        print("\n🚀 Generating questions...")
        total_generated = 0
        attempts = 0
        max_attempts = 100  # Prevent infinite loops
        
        while sum(current_counts.values()) < 30 and attempts < max_attempts:
            attempts += 1
            
            # Determine which level to generate for
            needed_levels = [level for level, target in target_distribution.items() 
                           if current_counts[level] < target]
            
            if not needed_levels:
                break
                
            # Focus on level that needs the most questions
            target_level = min(needed_levels, key=lambda x: current_counts[x])
            
            try:
                # Generate questions using enhanced system
                questions = processor.generate_questions_from_document(
                    document=document,
                    num_questions=5,  # Generate in batches
                    difficulty_level=target_level
                )
                
                if questions:
                    for question_data in questions:
                        if current_counts[target_level] >= target_distribution[target_level]:
                            break
                            
                        # Save to database
                        question_bank = QuestionBank(
                            document=document,
                            question=question_data['question'],
                            answer=question_data['answer'],
                            difficulty_level=target_level,
                            question_type='math',
                            metadata={
                                'enhanced_validation': True,
                                'ai_confidence_score': question_data.get('confidence_score', 'N/A'),
                                'validation_method': 'AI + RAG',
                                'generation_attempt': attempts
                            }
                        )
                        question_bank.save()
                        
                        current_counts[target_level] += 1
                        total_generated += 1
                        
                        print(f"✅ Generated question {total_generated}/30 (Level {target_level})")
                        print(f"   Question: {question_data['question'][:80]}...")
                        
                        if question_data.get('confidence_score'):
                            print(f"   AI Confidence: {question_data['confidence_score']}")
                
                # Show progress
                print(f"\n📊 Progress Update (Attempt {attempts}):")
                for level in [3, 4, 5]:
                    progress = f"{current_counts[level]}/{target_distribution[level]}"
                    print(f"   Level {level}: {progress}")
                print()
                
            except Exception as e:
                print(f"⚠️  Generation attempt {attempts} failed: {e}")
                continue
        
        # Final summary
        print("\n" + "=" * 60)
        print("🏁 GENERATION COMPLETE!")
        print("=" * 60)
        
        print(f"📈 Total questions generated: {total_generated}")
        print(f"🔄 Total attempts made: {attempts}")
        
        print("\n📊 Final Distribution:")
        total_in_db = 0
        for level in [3, 4, 5]:
            count = QuestionBank.objects.filter(
                document=document, 
                difficulty_level=level,
                metadata__enhanced_validation=True
            ).count()
            total_in_db += count
            print(f"   Level {level}: {count} questions")
        
        print(f"\n💾 Total enhanced questions in database: {total_in_db}")
        
        # Validate all questions are genuinely mathematical
        print("\n🔍 Validating question quality...")
        enhanced_questions = QuestionBank.objects.filter(
            metadata__enhanced_validation=True
        )
        
        math_count = 0
        for q in enhanced_questions:
            if processor._is_math_question(q.question):
                math_count += 1
        
        print(f"✅ Mathematical questions: {math_count}/{enhanced_questions.count()}")
        print(f"🎯 Math validation rate: {(math_count/enhanced_questions.count())*100:.1f}%")
        
        if total_generated >= 30:
            print("\n🎉 SUCCESS: 30 validated math questions generated!")
        else:
            print(f"\n⚠️  PARTIAL: Only {total_generated} questions generated.")
            
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        return False
    
    return True


if __name__ == "__main__":
    success = generate_30_questions()
    if success:
        print("\n✨ Enhanced question generation completed successfully!")
    else:
        print("\n💥 Question generation failed!")
        sys.exit(1)
