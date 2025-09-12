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
    teacher_assessment_dashboard, available_learning_topics,
    # TASK 2.1: Exam Session Views
    list_topics, create_exam_session, get_exam_session, list_exam_sessions,
    # TASK 2.2: Exam Config Views
    ExamConfigViewSet,
    # Document status tracking
    document_status,
    # TASK 3.2: Exam Answer Collection
    submit_exam_answer, get_exam_progress,
    # Interactive Exam Learning with OLAMA
    submit_interactive_exam_answer, get_interactive_exam_progress,
    # Document-Based Interactive Learning
    start_document_based_learning, submit_document_learning_answer, get_document_learning_progress,
    # NEW: Interactive Exam System (Chat-based)
    start_interactive_exam, interactive_exam_chat, get_exam_progress,
    # Fast Question Generation
    generate_questions_from_document
)

# Import clean interactive exam views
from .interactive_exam_views import start_exam as clean_start_exam, submit_answer as clean_submit_answer, get_exam_state, finish_exam

# Create a router and register our viewset with it
router = DefaultRouter()
router.register(r'lessons', LessonViewSet)
router.register(r'exam-configs', ExamConfigViewSet, basename='exam-config')

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
    path('documents/<int:document_id>/status/', document_status, name="document_status"),  # Status endpoint
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
    
    # Interactive Exam (General - uses teacher documents)
    path('exam/start/', start_interactive_exam, name='start_interactive_exam'),  # Generic interactive exam
    path('exam/chat/<int:session_id>/', handle_exam_chat_interaction, name='interactive_exam_chat'),
    path('exam/progress/<int:session_id>/', get_interactive_exam_progress, name='interactive_exam_progress'),
    
    # 🎯 Phase 4: Analysis and Teacher Dashboard
    path('analytics/student/<int:student_id>/', analyze_student_performance, name='analyze_student_performance'),
    path('analytics/topics/', topic_level_analysis, name='topic_level_analysis'),
    path('teacher/dashboard/', teacher_dashboard, name='teacher_dashboard'),
    path('teacher/dashboard/export/', export_dashboard_data, name='export_dashboard_data'),
    
    # 🧠 Interactive Learning & Socratic Tutoring System
    path('interactive/start/', start_interactive_learning_session, name='start_interactive_learning'),
    path('interactive/chat/<int:session_id>/', interactive_learning_chat, name='interactive_learning_chat'),
    path('interactive/progress/<int:session_id>/', get_learning_progress, name='learning_session_progress'),  # Fixed: use structured learning progress
    path('interactive/end/<int:session_id>/', end_learning_session, name='end_learning_session'),
    path('interactive/exam_chat/<int:session_id>/', handle_exam_chat_interaction, name='exam_chat_interaction'),
    
    # 📚 NEW: Structured Learning System (Replaces Student Practice)
    path('learning/start/', start_learning_session, name='start_learning_session'),
    path('learning/answer/', submit_learning_answer, name='submit_learning_answer'),
    path('learning/progress/<int:session_id>/', get_learning_progress, name='get_learning_progress'),
    path('learning/topics/', available_learning_topics, name='available_learning_topics'),
    
    # 👨‍🏫 Teacher Assessment Dashboard
    path('teacher/assessments/', teacher_assessment_dashboard, name='teacher_assessment_dashboard'),
    
    # 📝 TASK 2.1: Exam Session Management
    path('topics/', list_topics, name='list_topics'),
    path('exam-sessions/', create_exam_session, name='create_exam_session_alias'),  # Frontend expects this path
    path('exam-sessions/list/', list_exam_sessions, name='list_exam_sessions_alias'),  # Additional alias
    path('exam-sessions/<int:session_id>/', get_exam_session, name='get_exam_session_alias'),  # Additional alias
    path('exams/sessions/', create_exam_session, name='create_exam_session'),  # Original path
    path('exams/sessions/list/', list_exam_sessions, name='list_exam_sessions'),
    path('exams/sessions/<int:session_id>/', get_exam_session, name='get_exam_session'),
    
    # 🎯 TASK 3.2: Exam Answer Collection & Progression
    path('student-answers/', submit_exam_answer, name='submit_exam_answer'),
    path('exam-progress/<int:exam_session_id>/', get_exam_progress, name='get_exam_progress'),
    
    # 🧠 Interactive Exam Learning with OLAMA Integration
    path('interactive-exam-answers/', submit_interactive_exam_answer, name='submit_interactive_exam_answer'),
    path('interactive-exam-progress/<int:exam_session_id>/', get_interactive_exam_progress, name='get_interactive_exam_progress'),
    
    # 📚 Document-Based Interactive Learning System
    path('start_document_learning/', start_document_based_learning, name='start_document_based_learning'),
    path('document_learning/<int:session_id>/answer/', submit_document_learning_answer, name='submit_document_learning_answer'),
    path('document_learning/<int:session_id>/progress/', get_document_learning_progress, name='get_document_learning_progress'),
    
    # 🎓 CLEAN INTERACTIVE EXAM SYSTEM - Questions from Teacher Documents Only
    path('clean-exam/start/', clean_start_exam, name='clean_start_exam'),
    path('clean-exam/answer/', clean_submit_answer, name='clean_submit_answer'),
    path('clean-exam/state/', get_exam_state, name='get_exam_state'),
    path('clean-exam/finish/', finish_exam, name='finish_exam'),
    
    # 🚀 Fast Question Generation for Teachers
    path('generate_questions_from_document/', generate_questions_from_document, name='generate_questions_from_document'),
    
    # Router endpoints (lessons)
    path('', include(router.urls)),
]
