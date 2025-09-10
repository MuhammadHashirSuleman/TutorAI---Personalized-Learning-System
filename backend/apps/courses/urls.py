from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# Add course-related viewsets here when ready

urlpatterns = [
    path('', include(router.urls)),
    # Add other course-related URLs here
]
