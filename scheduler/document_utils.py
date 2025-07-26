"""
Document Processing Utilities
Handles PDF text extraction, document management, and LangChain integration
"""
import os
import tempfile
import json
import pdfplumber
from PIL import Image
import io
import hashlib
from typing import Dict, List, Optional, Tuple
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

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
        Extract text from images using OCR (basic implementation)
        """
        result = {
            'text': '',
            'metadata': {},
            'processing_errors': []
        }
        
        try:
            # For now, just get image metadata
            with Image.open(file_path) as img:
                result['metadata'] = {
                    'format': img.format,
                    'mode': img.mode,
                    'size': img.size,
                    'width': img.width,
                    'height': img.height
                }
                # Note: OCR would require additional libraries like pytesseract
                result['text'] = "[Image content - OCR not implemented yet]"
                
        except Exception as e:
            result['processing_errors'].append(f"Image processing failed: {str(e)}")
        
        return result
    
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
