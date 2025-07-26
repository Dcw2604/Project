from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LessonViewSet, UserRegistrationView, chat_interaction,
    upload_document, list_documents, get_chat_history,
    clear_conversation_memory
)

# Create a router and register our viewset with it
router = DefaultRouter()
router.register(r'lessons', LessonViewSet)

# Main API endpoints
urlpatterns = [
    # Authentication
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    
    # Chat endpoints (comprehensive RAG implementation)
    path('chat_interaction/', chat_interaction, name="chat_interaction"),
    path('chat_history/', get_chat_history, name="get_chat_history"),
    path('clear_memory/', clear_conversation_memory, name="clear_memory"),
    
    # Document endpoints
    path('upload_document/', upload_document, name="upload_document"),
    path('documents/', list_documents, name="list_documents"),
    
    # Router endpoints (lessons)
    path('', include(router.urls)),
]
