"""
Document Processing Utilities
Handles PDF text extraction, document management, and LangChain integration
"""
import os
import tempfile
import json
import time
import pdfplumber
from PIL import Image, ImageEnhance, ImageFilter
import io
import hashlib
from typing import Dict, List, Optional, Tuple
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

# OCR imports with fallback handling
try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
    print("✅ OpenCV (cv2) available for advanced image processing")
except ImportError:
    CV2_AVAILABLE = False
    print("⚠️ OpenCV not available - using basic image processing")

try:
    import pytesseract
    
    # Test if Tesseract is actually executable and configured
    try:
        version = pytesseract.get_tesseract_version()
        TESSERACT_AVAILABLE = True
        print(f"✅ Tesseract OCR available - Version: {version}")
    except Exception as e:
        TESSERACT_AVAILABLE = False
        print(f"❌ Tesseract executable not found or not configured: {e}")
        print("📥 Please install Tesseract OCR:")
        print("   1. Download from: https://github.com/UB-Mannheim/tesseract/wiki")
        print("   2. Install to default location")
        print("   3. Restart Django server")
        
except ImportError:
    TESSERACT_AVAILABLE = False
    print("❌ pytesseract not installed - OCR functionality will be limited")
    print("📦 Install with: pip install pytesseract")

# LangChain imports with fallback handling
try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_community.vectorstores import FAISS
    from langchain_community.embeddings import OllamaEmbeddings
    from langchain.chains import RetrievalQA
    from langchain_community.llms import Ollama
    from langchain.memory import ConversationBufferMemory
    from langchain.schema import HumanMessage, AIMessage
    LANGCHAIN_AVAILABLE = True
except ImportError as e:
    print(f"LangChain not available: {e}")
    LANGCHAIN_AVAILABLE = False

class DocumentProcessor:
    """
    Comprehensive document processing with PDF extraction and AI integration
    """
    
    def __init__(self):
        self.upload_dir = os.path.join(settings.MEDIA_ROOT, 'documents') if hasattr(settings, 'MEDIA_ROOT') else 'media/documents'
        self.ensure_upload_dir()
        self.text_splitter = None
        self.embeddings = None
        self.llm = None
        self.init_langchain()
    
    def ensure_upload_dir(self):
        """Create upload directory if it doesn't exist"""
        os.makedirs(self.upload_dir, exist_ok=True)
    
    def init_langchain(self):
        """Initialize LangChain components with error handling"""
        if not LANGCHAIN_AVAILABLE:
            return
        
        try:
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
                separators=["\n\n", "\n", " ", ""]
            )
            
            # Initialize with Ollama embeddings
            self.embeddings = OllamaEmbeddings(
                model="llama3.2",
                base_url="http://localhost:11434"
            )
            
            self.llm = Ollama(
                model="llama3.2",
                base_url="http://localhost:11434",
                temperature=0.7
            )
        except Exception as e:
            print(f"LangChain initialization failed: {e}")
            self.text_splitter = None
            self.embeddings = None
            self.llm = None
    
    def calculate_file_hash(self, file_content: bytes) -> str:
        """Calculate SHA-256 hash of file content for deduplication"""
        return hashlib.sha256(file_content).hexdigest()
    
    def save_uploaded_file(self, uploaded_file, user_id: int) -> Tuple[str, str]:
        """
        Save uploaded file and return (file_path, file_hash)
        """
        # Read file content
        file_content = uploaded_file.read()
        file_hash = self.calculate_file_hash(file_content)
        
        # Create unique filename
        timestamp = int(time.time())
        filename = f"user_{user_id}_{timestamp}_{uploaded_file.name}"
        file_path = os.path.join(self.upload_dir, filename)
        
        # Save file
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        return file_path, file_hash
    
    def extract_pdf_text(self, file_path: str) -> Dict:
        """
        Extract text and metadata from PDF using pdfplumber
        Returns comprehensive document information
        """
        result = {
            'text': '',
            'pages': [],
            'metadata': {},
            'tables': [],
            'images_detected': 0,
            'processing_errors': []
        }
        
        try:
            with pdfplumber.open(file_path) as pdf:
                # Extract metadata
                if pdf.metadata:
                    result['metadata'] = {
                        'title': pdf.metadata.get('Title', ''),
                        'author': pdf.metadata.get('Author', ''),
                        'subject': pdf.metadata.get('Subject', ''),
                        'creator': pdf.metadata.get('Creator', ''),
                        'creation_date': str(pdf.metadata.get('CreationDate', '')),
                        'modification_date': str(pdf.metadata.get('ModDate', ''))
                    }
                
                # Process each page
                all_text = []
                for page_num, page in enumerate(pdf.pages, 1):
                    try:
                        # Extract text
                        page_text = page.extract_text()
                        if page_text:
                            all_text.append(page_text)
                            result['pages'].append({
                                'page_number': page_num,
                                'text': page_text[:500] + '...' if len(page_text) > 500 else page_text,
                                'char_count': len(page_text)
                            })
                        
                        # Extract tables
                        tables = page.extract_tables()
                        if tables:
                            for table_idx, table in enumerate(tables):
                                result['tables'].append({
                                    'page': page_num,
                                    'table_index': table_idx,
                                    'rows': len(table),
                                    'columns': len(table[0]) if table else 0,
                                    'preview': table[:3] if len(table) > 3 else table  # First 3 rows
                                })
                        
                        # Count images (approximate)
                        if hasattr(page, 'images'):
                            result['images_detected'] += len(page.images)
                            
                    except Exception as e:
                        result['processing_errors'].append(f"Page {page_num}: {str(e)}")
                
                result['text'] = '\n\n'.join(all_text)
                result['total_pages'] = len(pdf.pages)
                result['total_characters'] = len(result['text'])
                result['estimated_reading_time'] = max(1, len(result['text']) // 1000)  # Rough estimate
                
        except Exception as e:
            result['processing_errors'].append(f"PDF processing failed: {str(e)}")
        
        return result
    
    def extract_image_text(self, file_path: str) -> Dict:
        """
        Enhanced text extraction from images using OCR with pytesseract
        Includes advanced preprocessing, confidence scoring, and text validation
        """
        result = {
            'text': '',
            'metadata': {},
            'processing_errors': [],
            'confidence_scores': [],
            'text_regions': [],
            'overall_confidence': 0,
            'text_quality': 'unknown'
        }

        try:
            with Image.open(file_path) as img:
                # Extract comprehensive metadata
                result['metadata'] = {
                    'format': img.format,
                    'mode': img.mode,
                    'size': img.size,
                    'width': img.width,
                    'height': img.height,
                    'has_transparency': img.mode in ('RGBA', 'LA') or 'transparency' in img.info,
                    'file_size_mb': os.path.getsize(file_path) / (1024 * 1024) if os.path.exists(file_path) else 0
                }

                # Check if OCR is available
                if not TESSERACT_AVAILABLE:
                    result['processing_errors'].append("Tesseract OCR is not installed. Please install Tesseract to enable text extraction from images.")
                    result['text'] = "OCR not available - Tesseract not installed"
                    result['text_quality'] = 'failed'
                    return result

                # Enhanced image preprocessing
                processed_img = self._preprocess_image_for_ocr(img)
                
                # Also try a more aggressive preprocessing approach for difficult images
                processed_img_alt = self._aggressive_preprocess_image(img)

                # Multiple OCR configurations for better accuracy
                configs = [
                    r'--oem 3 --psm 6',  # Default configuration - good for uniform text blocks
                    r'--oem 3 --psm 3',  # Fully automatic page segmentation
                    r'--oem 3 --psm 4',  # Single column of text of variable sizes
                    r'--oem 3 --psm 7',  # Single text line
                    r'--oem 3 --psm 8',  # Single word
                    r'--oem 3 --psm 11', # Sparse text
                    r'--oem 3 --psm 12', # Sparse text with OSD
                    r'--oem 3 --psm 13', # Raw line. Treat the image as a single text line
                ]
                
                best_text = ""
                best_confidence = 0
                all_results = []
                
                # Try multiple OCR configurations and pick the best result
                # Test both regular and aggressive preprocessing
                preprocessed_images = [
                    ("standard", processed_img),
                    ("aggressive", processed_img_alt)
                ]
                
                for preprocess_type, test_img in preprocessed_images:
                    print(f"🔧 Testing {preprocess_type} preprocessing...")
                    
                    for config in configs:
                        try:
                            print(f"🔍 Trying OCR config: {config}")
                            # Extract text with current configuration
                            text = pytesseract.image_to_string(test_img, config=config).strip()
                            print(f"   📝 Extracted text ({len(text)} chars): '{text[:100]}...' " if len(text) > 100 else f"   📝 Extracted text: '{text}'")
                            
                            # Get detailed confidence data
                            detailed_data = pytesseract.image_to_data(test_img, config=config, output_type=pytesseract.Output.DICT)
                            
                            if detailed_data and text:
                                # Calculate average confidence for this configuration
                                confidences = [int(conf) for conf in detailed_data['conf'] if int(conf) > 0]
                                avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                                print(f"   📊 Average confidence: {avg_confidence:.1f}%, Individual confidences: {confidences[:5]}{'...' if len(confidences) > 5 else ''}")
                                
                                all_results.append({
                                    'text': text,
                                    'confidence': avg_confidence,
                                    'config': config,
                                    'preprocessing': preprocess_type,
                                    'confidences': confidences,
                                    'detailed_data': detailed_data
                                })
                                
                                # Track the best result - prefer higher confidence but also consider text length
                                text_score = avg_confidence + (len(text) * 0.1)  # Slight bonus for longer text
                                current_best_score = best_confidence + (len(best_text) * 0.1)
                                
                                if text_score > current_best_score:
                                    best_confidence = avg_confidence
                                    best_text = text
                                    print(f"   ⭐ New best result! Score: {text_score:.1f} (preprocessing: {preprocess_type})")
                            else:
                                print(f"   ❌ No text found with this config")
                                    
                        except Exception as e:
                            print(f"   ❌ OCR config '{config}' failed: {str(e)}")
                            result['processing_errors'].append(f"OCR config '{config}' with {preprocess_type} preprocessing failed: {str(e)}")
                
                # Use the best result found
                if best_text:
                    result['text'] = best_text
                    result['overall_confidence'] = best_confidence
                    
                    # Find the best result details
                    best_result = max(all_results, key=lambda x: x['confidence']) if all_results else None
                    
                    if best_result:
                        result['confidence_scores'] = best_result['confidences']
                        detailed_data = best_result['detailed_data']
                        
                        # Extract high-confidence text regions with positions
                        for i, text_piece in enumerate(detailed_data['text']):
                            if text_piece.strip() and int(detailed_data['conf'][i]) > 30:
                                result['text_regions'].append({
                                    'text': text_piece,
                                    'confidence': int(detailed_data['conf'][i]),
                                    'bbox': {
                                        'left': detailed_data['left'][i],
                                        'top': detailed_data['top'][i],
                                        'width': detailed_data['width'][i],
                                        'height': detailed_data['height'][i]
                                    }
                                })
                
                # Determine text quality based on confidence and length
                if result['overall_confidence'] >= 80 and len(result['text']) > 10:
                    result['text_quality'] = 'excellent'
                elif result['overall_confidence'] >= 60 and len(result['text']) > 5:
                    result['text_quality'] = 'good'
                elif result['overall_confidence'] >= 40 and len(result['text']) > 0:
                    result['text_quality'] = 'fair'
                else:
                    result['text_quality'] = 'poor'
                
                # Add processing summary
                result['metadata']['processing_summary'] = {
                    'configs_tried': len(configs),
                    'successful_configs': len(all_results),
                    'total_characters': len(result['text']),
                    'total_regions': len(result['text_regions']),
                    'average_region_confidence': sum(r['confidence'] for r in result['text_regions']) / len(result['text_regions']) if result['text_regions'] else 0
                }

        except Exception as e:
            result['processing_errors'].append(f"Image processing failed: {str(e)}")
            result['text_quality'] = 'failed'

        return result
    
    def _preprocess_image_for_ocr(self, img: Image.Image) -> Image.Image:
        """
        Enhanced image preprocessing for improved OCR accuracy
        Includes: resolution enhancement, noise reduction, contrast optimization, and text detection
        """
        try:
            # Step 1: Convert to RGB and ensure proper format
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Check if OpenCV is available for advanced processing
            if not CV2_AVAILABLE:
                print("OpenCV not available - using basic PIL processing")
                return self._basic_preprocess_image(img)
            
            # Convert PIL to OpenCV format for advanced processing
            img_array = np.array(img)
            img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            
            # Step 2: Resolution Enhancement - Smart upscaling for small images
            height, width = img_cv.shape[:2]
            if width < 600 or height < 400:  # Increased thresholds for better quality
                # Calculate optimal scale factor
                scale_factor = max(600 / width, 400 / height)
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                img_cv = cv2.resize(img_cv, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
            
            # Step 3: Noise Reduction - Multiple filter approach
            # Apply bilateral filter to reduce noise while preserving edges
            img_cv = cv2.bilateralFilter(img_cv, 9, 75, 75)
            
            # Convert to grayscale for text processing
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            
            # Apply morphological operations to clean up text
            kernel = np.ones((1,1), np.uint8)
            gray = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
            
            # Step 4: Contrast and Brightness Optimization
            # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            gray = clahe.apply(gray)
            
            # Additional contrast enhancement using gamma correction
            gamma = 1.2  # Slightly brighten
            gray = np.power(gray / 255.0, gamma) * 255.0
            gray = np.uint8(gray)
            
            # Step 5: Text Enhancement - Sharpen text regions
            # Apply unsharp masking for text sharpening
            blurred = cv2.GaussianBlur(gray, (0, 0), 1.0)
            sharpened = cv2.addWeighted(gray, 1.5, blurred, -0.5, 0)
            
            # Convert back to PIL Image
            processed_img = Image.fromarray(sharpened, mode='L').convert('RGB')
            
            return processed_img
            
        except Exception as e:
            print(f"Advanced preprocessing failed: {e}, falling back to basic processing")
            return self._basic_preprocess_image(img)
    
    def _basic_preprocess_image(self, img: Image.Image) -> Image.Image:
        """
        Basic image preprocessing using only PIL when OpenCV is not available
        """
        try:
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Basic resize for small images
            width, height = img.size
            if width < 300:
                scale_factor = 300 / width
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Basic contrast and sharpness enhancement
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.2)
            
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(1.1)
            
            return img
        except Exception as e:
            print(f"Basic preprocessing failed: {e}, returning original image")
            # Return original image if all processing fails
            return img

    def _aggressive_preprocess_image(self, img: Image.Image) -> Image.Image:
        """
        Aggressive image preprocessing for very difficult images
        Uses extreme enhancement and multiple techniques
        """
        try:
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Check if OpenCV is available for advanced processing
            if not CV2_AVAILABLE:
                print("OpenCV not available - using basic aggressive processing")
                return self._basic_aggressive_preprocess_image(img)
            
            # Convert PIL to OpenCV format
            img_array = np.array(img)
            img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            
            # Extreme upscaling for small images
            height, width = img_cv.shape[:2]
            if width < 800 or height < 600:
                scale_factor = max(800 / width, 600 / height)
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                img_cv = cv2.resize(img_cv, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
            
            # Convert to grayscale
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            
            # Aggressive noise reduction
            gray = cv2.medianBlur(gray, 3)
            gray = cv2.bilateralFilter(gray, 9, 75, 75)
            
            # Extreme contrast enhancement
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
            gray = clahe.apply(gray)
            
            # Apply threshold to get pure black and white
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Morphological operations to clean up
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
            binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            
            # Try to invert if background is dark
            white_pixels = cv2.countNonZero(binary)
            total_pixels = binary.shape[0] * binary.shape[1]
            if white_pixels < total_pixels * 0.5:  # More black than white, probably inverted
                binary = cv2.bitwise_not(binary)
            
            # Convert back to PIL Image
            processed_img = Image.fromarray(binary, mode='L').convert('RGB')
            
            return processed_img
            
        except Exception as e:
            print(f"Aggressive preprocessing failed: {e}, falling back to basic aggressive processing")
            return self._basic_aggressive_preprocess_image(img)
    
    def _basic_aggressive_preprocess_image(self, img: Image.Image) -> Image.Image:
        """
        Basic aggressive preprocessing using only PIL
        """
        try:
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Extreme resize for small images
            width, height = img.size
            if width < 400:
                scale_factor = 400 / width
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert to grayscale and then back to RGB for consistent processing
            img = img.convert('L').convert('RGB')
            
            # Extreme contrast enhancement
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(2.0)  # Much higher contrast
            
            # Extreme sharpness
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(2.0)
            
            # Brightness adjustment
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(1.2)
            
            return img
        except Exception as e:
            print(f"Basic aggressive preprocessing failed: {e}, returning original image")
            return img
    
    def create_vector_store(self, text: str, document_id: str) -> Optional[object]:
        """
        Create FAISS vector store from document text for semantic search
        """
        if not LANGCHAIN_AVAILABLE or not self.text_splitter or not self.embeddings:
            return None
        
        try:
            # Split text into chunks
            chunks = self.text_splitter.split_text(text)
            
            if not chunks:
                return None
            
            # Create vector store
            vectorstore = FAISS.from_texts(
                chunks, 
                self.embeddings,
                metadatas=[{"document_id": document_id, "chunk_id": i} for i in range(len(chunks))]
            )
            
            return vectorstore
            
        except Exception as e:
            print(f"Vector store creation failed: {e}")
            return None
    
    def query_document(self, vectorstore, question: str, max_chunks: int = 3) -> str:
        """
        Query document using RAG (Retrieval-Augmented Generation)
        """
        if not LANGCHAIN_AVAILABLE or not self.llm or not vectorstore:
            return "Document search not available - LangChain not configured"
        
        try:
            # Create retrieval QA chain
            qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=vectorstore.as_retriever(
                    search_kwargs={"k": max_chunks}
                ),
                return_source_documents=True
            )
            
            # Get answer
            response = qa_chain({"query": question})
            return response.get("result", "No answer found")
            
        except Exception as e:
            return f"Document query failed: {str(e)}"
    
    def summarize_document(self, text: str, max_length: int = 2000) -> str:
        """
        Generate document summary using AI
        """
        if not self.llm:
            return "Summary not available - AI not configured"
        
        # Truncate text if too long
        if len(text) > max_length:
            text = text[:max_length] + "..."
        
        prompt = f"""
        Please provide a concise summary of the following document content:
        
        {text}
        
        Summary should include:
        - Main topics covered
        - Key concepts
        - Educational level (if applicable)
        - Suggested use cases for students
        
        Summary:
        """
        
        try:
            response = self.llm(prompt)
            return response
        except Exception as e:
            return f"Summary generation failed: {str(e)}"

# Global instance
document_processor = DocumentProcessor()

# Utility functions for views
def process_uploaded_document(uploaded_file, user, title: str = None) -> Dict:
    """
    Process uploaded document and return processing results
    """
    if not title:
        title = uploaded_file.name
    
    # Determine document type
    file_extension = os.path.splitext(uploaded_file.name)[1].lower()
    if file_extension == '.pdf':
        doc_type = 'pdf'
    elif file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
        doc_type = 'image'
    else:
        doc_type = 'text'
    
    try:
        # Save file
        file_path, file_hash = document_processor.save_uploaded_file(uploaded_file, user.id)
        
        # Extract content based on type
        if doc_type == 'pdf':
            extraction_result = document_processor.extract_pdf_text(file_path)
        elif doc_type == 'image':
            extraction_result = document_processor.extract_image_text(file_path)
        else:
            # For text files, just read content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            extraction_result = {'text': content, 'metadata': {}, 'processing_errors': []}
        
        return {
            'success': True,
            'file_path': file_path,
            'file_hash': file_hash,
            'document_type': doc_type,
            'title': title,
            'extraction_result': extraction_result
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

import time  # Add this import at the top
