"""
Document Processing Utilities with LangChain RAG
Handles PDF extraction, text splitting, and vector storage
"""
import os
import tempfile
import json
import pdfplumber
from PIL import Image
import io
import base64
from typing import List, Dict, Any, Optional

# LangChain imports
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA
from langchain.schema import Document as LangChainDocument
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain

from django.conf import settings
from .models import Document, ChatInteraction


class DocumentProcessor:
    """Handles document processing and RAG implementation"""
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        # Initialize embeddings (fallback to basic if Ollama not available)
        try:
            self.embeddings = OllamaEmbeddings(model="llama3.2", base_url="http://localhost:11434")
        except Exception:
            # Fallback to a simpler embedding if Ollama embeddings fail
            self.embeddings = None
        
        # Initialize LLM
        try:
            self.llm = Ollama(model="llama3.2", base_url="http://localhost:11434")
        except Exception:
            self.llm = None
    
    def extract_pdf_content(self, file_path: str) -> Dict[str, Any]:
        """Extract text and metadata from PDF using pdfplumber"""
        try:
            extracted_data = {
                'text': '',
                'pages': [],
                'metadata': {},
                'tables': [],
                'images': []
            }
            
            with pdfplumber.open(file_path) as pdf:
                # Extract metadata
                extracted_data['metadata'] = {
                    'title': pdf.metadata.get('Title', ''),
                    'author': pdf.metadata.get('Author', ''),
                    'creator': pdf.metadata.get('Creator', ''),
                    'producer': pdf.metadata.get('Producer', ''),
                    'subject': pdf.metadata.get('Subject', ''),
                    'creation_date': str(pdf.metadata.get('CreationDate', '')),
                    'total_pages': len(pdf.pages)
                }
                
                # Extract text from each page
                for i, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        extracted_data['pages'].append({
                            'page_number': i + 1,
                            'text': page_text
                        })
                        extracted_data['text'] += f"\n\nPage {i + 1}:\n{page_text}"
                    
                    # Extract tables
                    tables = page.extract_tables()
                    if tables:
                        for j, table in enumerate(tables):
                            extracted_data['tables'].append({
                                'page': i + 1,
                                'table_number': j + 1,
                                'data': table
                            })
                    
                    # Extract images (basic detection)
                    if hasattr(page, 'images') and page.images:
                        extracted_data['images'].extend([
                            {'page': i + 1, 'bbox': img['bbox']} 
                            for img in page.images
                        ])
            
            return extracted_data
            
        except Exception as e:
            raise Exception(f"PDF extraction failed: {str(e)}")
    
    def process_image_content(self, file_path: str) -> Dict[str, Any]:
        """Process image files"""
        try:
            with Image.open(file_path) as img:
                # Convert to base64 for storage
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                img_data = base64.b64encode(buffer.getvalue()).decode()
                
                return {
                    'text': f"Image file: {os.path.basename(file_path)}",
                    'metadata': {
                        'format': img.format,
                        'size': img.size,
                        'mode': img.mode
                    },
                    'image_data': img_data
                }
        except Exception as e:
            raise Exception(f"Image processing failed: {str(e)}")
    
    def create_vector_store(self, documents: List[LangChainDocument], doc_id: str) -> Optional[FAISS]:
        """Create FAISS vector store from documents"""
        if not self.embeddings or not documents:
            return None
            
        try:
            # Create vector store
            vectorstore = FAISS.from_documents(documents, self.embeddings)
            
            # Save vector store
            vector_path = os.path.join(settings.MEDIA_ROOT, 'vectors', f'doc_{doc_id}')
            os.makedirs(os.path.dirname(vector_path), exist_ok=True)
            vectorstore.save_local(vector_path)
            
            return vectorstore
            
        except Exception as e:
            print(f"Vector store creation failed: {e}")
            return None
    
    def load_vector_store(self, doc_id: str) -> Optional[FAISS]:
        """Load existing vector store"""
        if not self.embeddings:
            return None
            
        try:
            vector_path = os.path.join(settings.MEDIA_ROOT, 'vectors', f'doc_{doc_id}')
            if os.path.exists(vector_path):
                return FAISS.load_local(vector_path, self.embeddings)
            return None
        except Exception as e:
            print(f"Vector store loading failed: {e}")
            return None
    
    def create_rag_chain(self, vectorstore: FAISS, conversation_memory: Optional[ConversationBufferMemory] = None) -> Optional[RetrievalQA]:
        """Create RAG chain for document Q&A"""
        if not self.llm or not vectorstore:
            return None
            
        try:
            # Create custom prompt for educational context
            prompt_template = """
            You are an educational AI assistant helping students understand document content.
            Use the following pieces of context to answer the question at the end.
            If you don't know the answer based on the context, just say you don't know.
            Provide clear, educational explanations suitable for students.

            Context:
            {context}

            Question: {question}
            
            Helpful Answer:"""
            
            PROMPT = PromptTemplate(
                template=prompt_template,
                input_variables=["context", "question"]
            )
            
            # Create retrieval QA chain
            if conversation_memory:
                chain = ConversationalRetrievalChain.from_llm(
                    llm=self.llm,
                    retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
                    memory=conversation_memory,
                    return_source_documents=True
                )
            else:
                chain = RetrievalQA.from_chain_type(
                    llm=self.llm,
                    chain_type="stuff",
                    retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
                    chain_type_kwargs={"prompt": PROMPT},
                    return_source_documents=True
                )
            
            return chain
            
        except Exception as e:
            print(f"RAG chain creation failed: {e}")
            return None
    
    def process_document(self, document: Document) -> bool:
        """Process document and create vector store"""
        try:
            document.processing_status = 'processing'
            document.save()
            
            file_path = document.file_path
            
            # Extract content based on document type
            if document.document_type == 'pdf':
                extracted_data = self.extract_pdf_content(file_path)
            elif document.document_type == 'image':
                extracted_data = self.process_image_content(file_path)
            else:
                # Text file
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                extracted_data = {
                    'text': content,
                    'metadata': {'type': 'text'}
                }
            
            # Save extracted text and metadata
            document.extracted_text = extracted_data['text']
            document.metadata = json.dumps(extracted_data.get('metadata', {}))
            
            # Create documents for vector store
            if extracted_data['text']:
                # Split text into chunks
                texts = self.text_splitter.split_text(extracted_data['text'])
                
                # Create LangChain documents
                langchain_docs = [
                    LangChainDocument(
                        page_content=text,
                        metadata={
                            'source': document.title,
                            'doc_id': document.id,
                            'chunk_id': i
                        }
                    )
                    for i, text in enumerate(texts)
                ]
                
                # Create vector store
                vectorstore = self.create_vector_store(langchain_docs, str(document.id))
                
                if vectorstore:
                    document.processing_status = 'completed'
                else:
                    document.processing_status = 'completed'  # Still mark as completed even without vectors
                    document.processing_error = "Vector store creation failed, but text extraction succeeded"
            else:
                document.processing_status = 'failed'
                document.processing_error = "No text content extracted"
            
            document.save()
            return document.processing_status == 'completed'
            
        except Exception as e:
            document.processing_status = 'failed'
            document.processing_error = str(e)
            document.save()
            return False
    
    def query_document(self, document: Document, question: str, conversation_memory: Optional[ConversationBufferMemory] = None) -> Dict[str, Any]:
        """Query document using RAG"""
        try:
            # Try to load vector store
            vectorstore = self.load_vector_store(str(document.id))
            
            if vectorstore and self.llm:
                # Use RAG with vector store
                rag_chain = self.create_rag_chain(vectorstore, conversation_memory)
                
                if rag_chain:
                    if conversation_memory:
                        # Conversational retrieval
                        result = rag_chain({"question": question})
                        answer = result.get('answer', 'Could not generate answer')
                        sources = result.get('source_documents', [])
                    else:
                        # Standard retrieval QA
                        result = rag_chain({"query": question})
                        answer = result.get('result', 'Could not generate answer')
                        sources = result.get('source_documents', [])
                    
                    return {
                        'answer': answer,
                        'method': 'rag_vector',
                        'sources': [
                            {
                                'content': doc.page_content[:200] + '...',
                                'metadata': doc.metadata
                            }
                            for doc in sources
                        ]
                    }
            
            # Fallback to simple text search if no vector store
            if document.extracted_text and self.llm:
                # Simple context-based answering
                context = document.extracted_text[:3000]  # Limit context
                
                prompt = f"""
                Based on this document content:
                
                {context}
                
                Student question: {question}
                
                Please answer the question based on the document content provided.
                If the answer is not in the document, say so clearly.
                """
                
                try:
                    import requests
                    data = {
                        "model": "llama3.2",
                        "prompt": prompt,
                        "stream": False
                    }
                    response = requests.post("http://localhost:11434/api/generate", json=data)
                    response_data = response.json()
                    answer = response_data.get("response", "Sorry, I couldn't understand the question.")
                    
                    return {
                        'answer': answer,
                        'method': 'simple_context',
                        'sources': []
                    }
                except Exception:
                    return {
                        'answer': "Document processed but AI service unavailable",
                        'method': 'fallback',
                        'sources': []
                    }
            
            return {
                'answer': "Document not properly processed or AI service unavailable",
                'method': 'error',
                'sources': []
            }
            
        except Exception as e:
            return {
                'answer': f"Error querying document: {str(e)}",
                'method': 'error',
                'sources': []
            }


# Global instance
document_processor = DocumentProcessor()
