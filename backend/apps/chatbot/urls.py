from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# Add chatbot-related viewsets here when ready

urlpatterns = [
    path('', include(router.urls)),
    # Add other chatbot-related URLs here
]
