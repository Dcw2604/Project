from django.shortcuts import render
from rest_framework import generics, permissions
from .serializers import UserRegistrationSerializer
from .models import User, Lesson, ChatInteraction 
from rest_framework import viewsets, permissions
from .serializers import LessonSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from sympy import sympify # type: ignore
from sympy.core.sympify import SympifyError
import requests

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]


# ViewSet that provides CRUD operations (Create, Read, Update, Delete)
# for Lesson objects through the API
class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()  # All lessons from the database
    serializer_class = LessonSerializer  # Use the serializer we defined
    permission_classes = [permissions.IsAuthenticated]  # Require login for access

@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def chat_interaction(request):
    if request.method == 'GET':
        return Response({"message": "ה-API הזה מקבל שאלות ב-POST בלבד."})
    question = request.data.get('question', '').strip()
    user = request.user

    if not question:
        return Response({"error": "Missing question"}, status=400)

    # ניתוח מתמטי
    try:
        expr = sympify(question)
        result = expr.evalf()
        answer = f"{question} = {result}"

    except SympifyError:
        # שליחה ל־LLM
        data = {
            "model": "llama2",
            "prompt": question,
            "stream": False
        }
        try:
            response = requests.post("http://localhost:11434/api/generate", json=data)
            response_data = response.json()
            answer = response_data.get("response", "Sorry, I didn’t understand.")
        except:
            answer = "Error connecting to AI service."

    # שמירה ב-DB
    ChatInteraction.objects.create(
        student=user,
        question=question,
        answer=answer
    )

    return Response({"answer": answer})