"""
Simple PDF Text Extraction using pdfplumber
This is a lightweight alternative to the complex LangChain RAG system
"""
import pdfplumber
import tempfile
import os
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import ChatInteraction
import requests

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def simple_pdf_chat(request):
    """
    Simple PDF text extraction + chat
    Students upload PDF, AI reads the text and answers questions
    """
    question = request.data.get('question', '').strip()
    uploaded_file = request.FILES.get('document')
    
    if not question:
        return Response({"error": "Missing question"}, status=400)
    
    pdf_text = ""
    
    # Extract text from PDF if provided
    if uploaded_file:
        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                for chunk in uploaded_file.chunks():
                    tmp_file.write(chunk)
                tmp_path = tmp_file.name
            
            # Extract text using pdfplumber
            with pdfplumber.open(tmp_path) as pdf:
                pdf_pages = []
                for page in pdf.pages[:5]:  # Limit to first 5 pages for performance
                    text = page.extract_text()
                    if text:
                        pdf_pages.append(text)
                
                pdf_text = "\n".join(pdf_pages)
            
            # Clean up temp file
            os.unlink(tmp_path)
            
        except Exception as e:
            return Response({"error": f"PDF processing failed: {str(e)}"}, status=500)
    
    # Create enhanced prompt with PDF context
    if pdf_text:
        enhanced_question = f"""
        Based on this document content:
        
        {pdf_text[:2000]}...  # Limit context to avoid token limits
        
        Student question: {question}
        
        Please answer the question based on the document content provided.
        """
    else:
        enhanced_question = question
    
    # Send to Ollama (same as your current system)
    data = {
        "model": "llama3.2",
        "prompt": enhanced_question,
        "stream": False
    }
    
    try:
        response = requests.post("http://localhost:11434/api/generate", json=data)
        response_data = response.json()
        answer = response_data.get("response", "Sorry, I didn't understand.")
    except Exception as e:
        answer = f"Error connecting to AI service: {str(e)}"
    
    # Save to your existing database
    ChatInteraction.objects.create(
        student=request.user,
        question=question,
        answer=answer,
        topic="Document Q&A" if pdf_text else "General",
        notes=f"PDF uploaded: {uploaded_file.name}" if uploaded_file else None
    )
    
    return Response({
        "answer": answer,
        "pdf_processed": bool(pdf_text),
        "pdf_length": len(pdf_text) if pdf_text else 0
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def extract_pdf_summary(request):
    """
    Extract and summarize PDF content
    Useful for getting overview of study materials
    """
    uploaded_file = request.FILES.get('document')
    
    if not uploaded_file:
        return Response({"error": "No PDF file provided"}, status=400)
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            for chunk in uploaded_file.chunks():
                tmp_file.write(chunk)
            tmp_path = tmp_file.name
        
        # Extract text and metadata using pdfplumber
        with pdfplumber.open(tmp_path) as pdf:
            # Get metadata
            metadata = pdf.metadata
            num_pages = len(pdf.pages)
            
            # Extract text from first few pages
            text_samples = []
            for i, page in enumerate(pdf.pages[:3]):  # First 3 pages
                text = page.extract_text()
                if text:
                    text_samples.append(f"Page {i+1}: {text[:500]}...")
            
            # Extract any tables from first page
            tables = []
            if pdf.pages:
                first_page_tables = pdf.pages[0].extract_tables()
                if first_page_tables:
                    tables = first_page_tables[:2]  # First 2 tables
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        # Create summary request
        summary_prompt = f"""
        Please provide a summary of this PDF document:
        
        Title: {metadata.get('Title', 'Unknown')}
        Pages: {num_pages}
        
        Content sample:
        {' '.join(text_samples)}
        
        Please summarize the main topics and purpose of this document.
        """
        
        # Get AI summary
        data = {
            "model": "llama3.2",
            "prompt": summary_prompt,
            "stream": False
        }
        
        response = requests.post("http://localhost:11434/api/generate", json=data)
        response_data = response.json()
        summary = response_data.get("response", "Could not generate summary.")
        
        return Response({
            "summary": summary,
            "metadata": {
                "title": metadata.get('Title', 'Unknown'),
                "author": metadata.get('Author', 'Unknown'),
                "pages": num_pages,
                "has_tables": len(tables) > 0
            },
            "text_preview": text_samples[0] if text_samples else "No text extracted"
        })
        
    except Exception as e:
        return Response({"error": f"PDF processing failed: {str(e)}"}, status=500)

# Example usage functions
def demonstrate_pdfplumber_features():
    """
    Examples of what pdfplumber can do
    """
    features = {
        "text_extraction": "Extract plain text from PDFs",
        "table_extraction": "Extract tables as structured data",
        "metadata_access": "Get title, author, creation date, etc.",
        "page_analysis": "Analyze individual pages",
        "coordinate_based": "Extract text from specific areas",
        "image_detection": "Detect images and their positions"
    }
    
    return features
