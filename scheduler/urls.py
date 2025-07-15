from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LessonViewSet ,UserRegistrationView

# Create a router and register our viewset with it
router = DefaultRouter()
router.register(r'lessons', LessonViewSet)

# Include the router's URLs in this app's URLs
urlpatterns = [
     path('api/register/', UserRegistrationView.as_view(), name='user-register'),
    path('', include(router.urls)),
]