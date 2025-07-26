"""
Enhanced Chat View that combines Database Memory + LangChain Session Memory
This shows how to use your existing ChatInteraction model with LangChain
"""
from django.shortcuts import render
from rest_framework import generics, permissions, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import UserRegistrationSerializer, LessonSerializer
from .models import User, Lesson, ChatInteraction
from sympy import sympify
from sympy.core.sympify import SympifyError
import requests
from datetime import datetime, timedelta

# LangChain imports (install with: pip install langchain langchain-community)
try:
    from langchain.memory import ConversationBufferMemory
    from langchain.schema import HumanMessage, AIMessage
    from langchain_community.llms import Ollama
    from langchain.chains import ConversationChain
    from langchain.prompts import PromptTemplate
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

# Store conversation memory per user (session-based)
user_memories = {}

def get_user_memory(user_id):
    """Get or create conversation memory for a specific user"""
    if user_id not in user_memories:
        user_memories[user_id] = ConversationBufferMemory(return_messages=True)
    return user_memories[user_id]

def get_recent_chat_context(user, limit=5):
    """
    Get recent chat history from database to provide context
    This uses your existing ChatInteraction model!
    """
    recent_chats = ChatInteraction.objects.filter(
        student=user
    ).order_by('-created_at')[:limit]
    
    context = []
    for chat in reversed(recent_chats):  # Reverse to get chronological order
        context.append(f"Student previously asked: {chat.question}")
        context.append(f"AI answered: {chat.answer}")
    
    return "\n".join(context) if context else "No previous conversations."

@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def enhanced_chat_with_database_memory(request):
    """
    Enhanced chat that combines:
    1. Your existing database memory (ChatInteraction model)
    2. LangChain session memory for better conversation flow
    """
    if request.method == 'GET':
        return Response({
            "message": "Enhanced AI Chat with Database + Session Memory",
            "langchain_available": LANGCHAIN_AVAILABLE
        })
    
    question = request.data.get('question', '').strip()
    user = request.user
    
    if not question:
        return Response({"error": "Missing question"}, status=400)
    
    # Try math first (unchanged from your current system)
    try:
        expr = sympify(question)
        result = expr.evalf()
        answer = f"{question} = {result}"
        is_math = True
    except SympifyError:
        is_math = False
        
        if LANGCHAIN_AVAILABLE:
            try:
                # Get user's session memory
                memory = get_user_memory(user.id)
                
                # Get recent database history for context
                db_context = get_recent_chat_context(user, limit=3)
                
                # Create enhanced prompt with database context
                enhanced_prompt = PromptTemplate(
                    input_variables=["db_history", "session_history", "input"],
                    template="""You are a helpful educational AI assistant for {student_name}.

Recent conversation history from database:
{db_history}

Current session conversation:
{session_history}

Based on this context, please provide a helpful response to:
Student: {input}
AI Assistant:"""
                )
                
                # Create LangChain LLM
                llm = Ollama(model="llama3.2", base_url="http://localhost:11434")
                
                # Create conversation chain
                conversation = ConversationChain(
                    llm=llm,
                    memory=memory,
                    prompt=enhanced_prompt
                )
                
                # Get AI response with both database and session context
                answer = conversation.predict(
                    db_history=db_context,
                    student_name=user.username,
                    input=question
                )
                
            except Exception as e:
                print(f"LangChain error: {e}")
                # Fallback to your current Ollama direct call
                data = {
                    "model": "llama3.2",
                    "prompt": f"Previous context: {get_recent_chat_context(user, 2)}\n\nStudent question: {question}",
                    "stream": False
                }
                try:
                    response = requests.post("http://localhost:11434/api/generate", json=data)
                    response_data = response.json()
                    answer = response_data.get("response", "Sorry, I didn't understand.")
                except:
                    answer = "Error connecting to AI service."
        else:
            # Fallback to your current system when LangChain not available
            data = {
                "model": "llama3.2", 
                "prompt": question,
                "stream": False
            }
            try:
                response = requests.post("http://localhost:11434/api/generate", json=data)
                response_data = response.json()
                answer = response_data.get("response", "Sorry, I didn't understand.")
            except:
                answer = "Error connecting to AI service."
    
    # Save to your existing database (unchanged!)
    chat_interaction = ChatInteraction.objects.create(
        student=user,
        question=question,
        answer=answer,
        topic="Math" if is_math else "General",
        difficulty_estimate="Auto-detected" if is_math else "Unknown"
    )
    
    return Response({
        "answer": answer,
        "chat_id": chat_interaction.id,
        "enhanced_memory": LANGCHAIN_AVAILABLE,
        "type": "math" if is_math else "general"
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chat_history(request):
    """
    Get user's chat history from database
    This uses your existing ChatInteraction model
    """
    limit = request.GET.get('limit', 10)
    
    chats = ChatInteraction.objects.filter(
        student=request.user
    ).order_by('-created_at')[:limit]
    
    history = []
    for chat in chats:
        history.append({
            "id": chat.id,
            "question": chat.question,
            "answer": chat.answer,
            "created_at": chat.created_at.isoformat(),
            "topic": chat.topic,
            "difficulty": chat.difficulty_estimate
        })
    
    return Response({
        "history": history,
        "total_conversations": ChatInteraction.objects.filter(student=request.user).count()
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def clear_session_memory(request):
    """
    Clear LangChain session memory (database memory remains intact)
    """
    user_id = request.user.id
    if user_id in user_memories:
        del user_memories[user_id]
    
    return Response({
        "message": "Session memory cleared",
        "database_memory": "Database conversations remain intact"
    })

# Your existing views remain unchanged
class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]
