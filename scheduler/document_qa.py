"""
Document-based Q&A using LangChain RAG (Retrieval-Augmented Generation)
Students can upload PDFs and ask questions about the content
"""
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings
from langchain.chains import RetrievalQA
from langchain_community.llms import Ollama
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import os
import tempfile

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def document_qa(request):
    """
    Upload a document and ask questions about it
    """
    question = request.data.get('question', '').strip()
    uploaded_file = request.FILES.get('document')
    
    if not question or not uploaded_file:
        return Response({"error": "Need both question and document"}, status=400)
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            for chunk in uploaded_file.chunks():
                tmp_file.write(chunk)
            tmp_path = tmp_file.name
        
        # Load and process document
        loader = PyPDFLoader(tmp_path)
        documents = loader.load()
        
        # Split document into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        texts = text_splitter.split_documents(documents)
        
        # Create embeddings and vector store
        embeddings = OllamaEmbeddings(model="llama2")
        vectorstore = FAISS.from_documents(texts, embeddings)
        
        # Create retrieval QA chain
        llm = Ollama(model="llama2", base_url="http://localhost:11434")
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vectorstore.as_retriever(search_kwargs={"k": 3})
        )
        
        # Get answer
        answer = qa_chain.run(question)
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        return Response({
            "answer": answer,
            "document_processed": True,
            "chunks_created": len(texts)
        })
        
    except Exception as e:
        return Response({"error": f"Document processing failed: {str(e)}"}, status=500)
