from django.contrib import admin
from django.urls import path, include
<<<<<<< HEAD
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
=======
from django.conf import settings
from django.conf.urls.static import static
>>>>>>> daniel

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('scheduler.urls')),
<<<<<<< HEAD
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api-auth/', include('rest_framework.urls')),
]
=======
    path('api-auth/', include('rest_framework.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
>>>>>>> daniel
