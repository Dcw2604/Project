from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LessonViewSet

# Create a router and register our viewset with it
router = DefaultRouter()
router.register(r'lessons', LessonViewSet)

# Include the router's URLs in this app's URLs
urlpatterns = [
    path('', include(router.urls)),
]