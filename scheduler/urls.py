from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LessonViewSet, UserRegistrationView, chat_interaction,
    upload_document, list_documents, get_chat_history,
    clear_conversation_memory, user_login, user_logout, test_image_upload,
    delete_document, list_questions, create_question, update_question,
    delete_question, start_test, submit_answer, complete_test, get_test_history
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
    path('documents/<int:document_id>/', delete_document, name="delete_document"),
    path('rag_documents/', list_documents, name="rag_documents"),  # Alias for frontend compatibility
    
    # Question management endpoints
    path('questions/', list_questions, name="list_questions"),
    path('questions/create/', create_question, name="create_question"),
    path('questions/<int:question_id>/', update_question, name="update_question"),
    path('questions/<int:question_id>/delete/', delete_question, name="delete_question"),
    
    # Test endpoints
    path('tests/start/', start_test, name="start_test"),
    path('tests/submit_answer/', submit_answer, name="submit_answer"),
    path('tests/complete/', complete_test, name="complete_test"),
    path('tests/history/', get_test_history, name="get_test_history"),
    path('test_image/', test_image_upload, name="test_image_upload"),
    
    # Router endpoints (lessons)
    path('', include(router.urls)),
]
