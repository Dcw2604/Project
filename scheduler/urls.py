from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LessonViewSet, UserRegistrationView, chat_interaction,
    upload_document, list_documents, get_chat_history,
    clear_conversation_memory, user_login, user_logout
)

# Create a router and register our viewset with it
router = DefaultRouter()
router.register(r'lessons', LessonViewSet)

# Main API endpoints
urlpatterns = [
    # Authentication
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('login/', user_login, name='user-login'),
    path('logout/', user_logout, name='user-logout'),
    path('token/', user_login, name='token'),  # Alias for frontend compatibility
    
    # Chat endpoints (comprehensive RAG implementation)
    path('chat_interaction/', chat_interaction, name="chat_interaction"),
    path('rag_chat/', chat_interaction, name="rag_chat"),  # Alias for frontend compatibility
    path('chat_history/', get_chat_history, name="get_chat_history"),
    path('clear_memory/', clear_conversation_memory, name="clear_memory"),
    path('rag_clear_memory/', clear_conversation_memory, name="rag_clear_memory"),  # Alias for frontend compatibility
    
    # Document endpoints
    path('upload_document/', upload_document, name="upload_document"),
    path('documents/', list_documents, name="list_documents"),
    path('rag_documents/', list_documents, name="rag_documents"),  # Alias for frontend compatibility
    
    # Router endpoints (lessons)
    path('', include(router.urls)),
]
