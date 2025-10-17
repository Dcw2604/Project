"""
URLs — Cleaned
---------------
- Routes only the cleaned views (document upload, exam creation, interactive exam).
- Removed duplicate/legacy endpoints.
"""

from django.urls import path
from .exam_integration_views import DocumentUploadView, ExamCreationView
from .interactive_exam_views import StartExamView, SubmitAnswerView, FinishExamView, GetExamQuestionsView, StudentAnalyticsView, AllStudentsAnalyticsView, GetExamsView, GetExamResultsView
from .views import HealthCheckView
from .auth_views import LoginView, RegisterView, LogoutView, MeView
urlpatterns = [
     path("health/", HealthCheckView.as_view(), name="health-check"),
    path("documents/upload/", DocumentUploadView.as_view(), name="document-upload"),
    path("exams/create/", ExamCreationView.as_view(), name="exam-create"),
    path("exams/", GetExamsView.as_view(), name="exams-list"),

    path("exams/<int:exam_id>/start/", StartExamView.as_view(), name="exam-start"),
    path("exams/<int:exam_id>/submit/", SubmitAnswerView.as_view(), name="exam-submit"),
    path("exams/<int:exam_id>/finish/", FinishExamView.as_view(), name="exam-finish"),
    path("exams/<int:exam_id>/questions/", GetExamQuestionsView.as_view(), name="exam-questions"),
    path('analytics/student/<int:student_id>/exam/<int:exam_session_id>/', 
     StudentAnalyticsView.as_view(), name='student_analytics'),
    path('analytics/exam/<int:exam_session_id>/students/', 
     AllStudentsAnalyticsView.as_view(), name='all_students_analytics'),
    path("exams/<int:exam_id>/results/", GetExamResultsView.as_view(), name="exam-results"),
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("auth/me/", MeView.as_view(), name="auth-me"),
]
