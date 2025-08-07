#!/usr/bin/env python3
"""
Test script to verify OCR functionality with Tesseract fallback
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scheduler.document_utils import DocumentProcessor

def create_test_image():
    """Create a simple test image with text"""
    # Create a white image
    img = Image.new('RGB', (400, 100), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a standard font, fallback to default if not available
    try:
        # Try to use a larger font
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        try:
            # Fallback to default font
            font = ImageFont.load_default()
        except:
            font = None
    
    # Draw text
    text = "Hello OCR Test 123"
    if font:
        draw.text((10, 30), text, fill='black', font=font)
    else:
        draw.text((10, 30), text, fill='black')
    
    # Save test image
    test_image_path = "test_ocr_image.png"
    img.save(test_image_path)
    return test_image_path, text

def test_ocr():
    """Test OCR functionality"""
    print("🔍 Testing OCR functionality...")
    
    # Create test image
    test_image_path, expected_text = create_test_image()
    print(f"📝 Created test image with text: '{expected_text}'")
    
    try:
        # Initialize document processor
        processor = DocumentProcessor()
        
        # Test OCR extraction
        print("🔬 Running OCR extraction...")
        result = processor.extract_image_text(test_image_path)
        
        # Display results
        print("\n📊 OCR Results:")
        print(f"  ✅ Text extracted: '{result['text']}'")
        print(f"  📈 Overall confidence: {result['overall_confidence']:.2f}")
        print(f"  🎯 Text quality: {result['text_quality']}")
        print(f"  🔧 Processing errors: {len(result['processing_errors'])}")
        
        if result['processing_errors']:
            print("  ⚠️ Errors:")
            for error in result['processing_errors']:
                print(f"    - {error}")
        
        print(f"  📋 Metadata: {result['metadata']}")
        
        # Check if text was extracted successfully
        if result['text'].strip() and not result['text'].startswith("OCR not available"):
            print("✅ OCR is working! Text was successfully extracted.")
            
            # Check if the extracted text contains expected words
            extracted_words = result['text'].lower().split()
            expected_words = expected_text.lower().split()
            matches = sum(1 for word in expected_words if any(word in ext_word for ext_word in extracted_words))
            
            if matches > 0:
                print(f"🎯 Text recognition accuracy: {matches}/{len(expected_words)} words matched")
            else:
                print("⚠️ Extracted text doesn't match expected text, but OCR is functional")
        elif result['text'].startswith("OCR not available"):
            print("❌ OCR is not available - PaddleOCR is not installed")
            print("💡 To enable OCR functionality, install PaddleOCR:")
            print("   pip install paddlepaddle")
            print("   pip install paddleocr")
        else:
            print("❌ OCR failed - no text was extracted")
    
    except Exception as e:
        print(f"❌ OCR test failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up test image
        try:
            os.remove(test_image_path)
            print("🧹 Cleaned up test image")
        except:
            pass

if __name__ == "__main__":
    test_ocr()
