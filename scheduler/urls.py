from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LessonViewSet, UserRegistrationView, chat_interaction,
    upload_document, list_documents, get_chat_history,
    clear_conversation_memory, user_login, user_logout, test_image_upload,
    delete_document, list_questions, create_question, update_question,
    delete_question, start_test, submit_answer, complete_test, get_test_history,
    create_test_questions, practice_chat,
    create_exam, list_exams, get_exam, assign_students_to_exam, publish_exam, start_exam, start_exam_chat, get_exam_results,
    export_exam_results,
    # Phase 4: Analysis and Teacher Dashboard
    analyze_student_performance, topic_level_analysis, teacher_dashboard, export_dashboard_data,
    # Interactive Learning & Socratic Tutoring
    start_interactive_learning_session, interactive_learning_chat, get_learning_session_progress, 
    end_learning_session, handle_exam_chat_interaction,
    # NEW: Structured Learning System
    start_learning_session, submit_learning_answer, get_learning_progress, 
    teacher_assessment_dashboard, available_learning_topics
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
    path('questions/create_test/', create_test_questions, name="create_test_questions"),  # Test endpoint
    path('questions/<int:question_id>/', update_question, name="update_question"),
    path('questions/<int:question_id>/delete/', delete_question, name="delete_question"),
    
    # Test endpoints
    path('tests/start/', start_test, name="start_test"),
    path('tests/submit_answer/', submit_answer, name="submit_answer"),
    path('tests/practice_chat/', practice_chat, name="practice_chat"),
    path('tests/complete/', complete_test, name="complete_test"),
    path('tests/history/', get_test_history, name="get_test_history"),
    path('test_image/', test_image_upload, name="test_image_upload"),

    # Exam endpoints
    path('exams/', list_exams, name='list_exams'),
    path('exams/create/', create_exam, name='create_exam'),
    path('exams/<int:exam_id>/', get_exam, name='get_exam'),
    path('exams/<int:exam_id>/assign_students/', assign_students_to_exam, name='assign_students_to_exam'),
    path('exams/<int:exam_id>/publish/', publish_exam, name='publish_exam'),
    path('exams/<int:exam_id>/start/', start_exam, name='start_exam'),
    path('exams/<int:exam_id>/start_chat/', start_exam_chat, name='start_exam_chat'),  # Chat-based exam mode
    path('exams/results/<int:test_session_id>/', get_exam_results, name='get_exam_results'),  # View exam results
    path('exams/<int:exam_id>/export/', export_exam_results, name='export_exam_results'),  # Export results
    
    # 🎯 Phase 4: Analysis and Teacher Dashboard
    path('analytics/student/<int:student_id>/', analyze_student_performance, name='analyze_student_performance'),
    path('analytics/topics/', topic_level_analysis, name='topic_level_analysis'),
    path('teacher/dashboard/', teacher_dashboard, name='teacher_dashboard'),
    path('teacher/dashboard/export/', export_dashboard_data, name='export_dashboard_data'),
    
    # 🧠 Interactive Learning & Socratic Tutoring System
    path('interactive/start/', start_interactive_learning_session, name='start_interactive_learning'),
    path('interactive/chat/<int:session_id>/', interactive_learning_chat, name='interactive_learning_chat'),
    path('interactive/progress/<int:session_id>/', get_learning_session_progress, name='learning_session_progress'),
    path('interactive/end/<int:session_id>/', end_learning_session, name='end_learning_session'),
    path('interactive/exam_chat/<int:session_id>/', handle_exam_chat_interaction, name='exam_chat_interaction'),
    
    # 📚 NEW: Structured Learning System (Replaces Student Practice)
    path('learning/start/', start_learning_session, name='start_learning_session'),
    path('learning/answer/', submit_learning_answer, name='submit_learning_answer'),
    path('learning/progress/<int:session_id>/', get_learning_progress, name='get_learning_progress'),
    path('learning/topics/', available_learning_topics, name='available_learning_topics'),
    
    # 👨‍🏫 Teacher Assessment Dashboard
    path('teacher/assessments/', teacher_assessment_dashboard, name='teacher_assessment_dashboard'),
    
    # Router endpoints (lessons)
    path('', include(router.urls)),
]
