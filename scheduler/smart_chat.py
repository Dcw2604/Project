"""
Multi-Model AI Chat System
Automatically chooses the best AI model based on question type
"""
from langchain_community.llms import Ollama
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from langchain.prompts import ChatPromptTemplate
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import re

class SmartModelSelector:
    """Selects the best AI model based on question content"""
    
    def __init__(self):
        # Initialize different models
        self.ollama_llm = Ollama(model="llama2", base_url="http://localhost:11434")
        # self.openai_llm = ChatOpenAI(model="gpt-3.5-turbo")  # Uncomment if you have OpenAI API key
        
    def classify_question(self, question):
        """Determine question type and best model to use"""
        question_lower = question.lower()
        
        # Math/Science questions
        if any(word in question_lower for word in ['calculate', 'solve', 'equation', 'formula', 'math']):
            return 'math'
        
        # Creative writing
        elif any(word in question_lower for word in ['write', 'story', 'poem', 'creative', 'essay']):
            return 'creative'
        
        # Code/Programming
        elif any(word in question_lower for word in ['code', 'program', 'function', 'python', 'javascript']):
            return 'code'
        
        # General questions
        else:
            return 'general'
    
    def get_specialized_prompt(self, question_type, question):
        """Get specialized prompt based on question type"""
        prompts = {
            'math': f"""You are a math tutor. Solve this step by step and explain clearly:
                     {question}""",
            
            'creative': f"""You are a creative writing assistant. Help with this request:
                        {question}""",
            
            'code': f"""You are a programming tutor. Provide clean, commented code and explanation:
                     {question}""",
            
            'general': f"""You are a helpful educational assistant. Answer this question clearly:
                       {question}"""
        }
        return prompts.get(question_type, prompts['general'])
    
    def get_answer(self, question):
        """Get AI answer using the best model for the question type"""
        question_type = self.classify_question(question)
        specialized_prompt = self.get_specialized_prompt(question_type, question)
        
        try:
            # Use Ollama for all types (you can add model switching logic here)
            answer = self.ollama_llm(specialized_prompt)
            return {
                'answer': answer,
                'model_used': 'llama2',
                'question_type': question_type
            }
        except Exception as e:
            return {
                'answer': 'Error connecting to AI service.',
                'model_used': 'none',
                'question_type': question_type,
                'error': str(e)
            }

# Global model selector instance
model_selector = SmartModelSelector()

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def smart_chat(request):
    """Smart chat that uses different AI models based on question type"""
    question = request.data.get('question', '').strip()
    user = request.user
    
    if not question:
        return Response({"error": "Missing question"}, status=400)
    
    # Get AI response
    result = model_selector.get_answer(question)
    
    # Save to database (you'll need to add these fields to ChatInteraction model)
    from .models import ChatInteraction
    ChatInteraction.objects.create(
        student=user,
        question=question,
        answer=result['answer']
    )
    
    return Response({
        "answer": result['answer'],
        "metadata": {
            "model_used": result['model_used'],
            "question_type": result['question_type'],
            "processing_method": "smart_selection"
        }
    })
