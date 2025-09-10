from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, NoteViewSet, StudentProfileViewSet,
    get_user_stats, upload_profile_picture, remove_profile_picture,
    user_goals, user_achievements, update_goal_progress
)
from .admin_views import get_notifications, mark_notification_read, delete_user_account

router = DefaultRouter()
router.register(r'', UserViewSet)  # Empty string since main urls.py already includes 'users/'
router.register(r'notes', NoteViewSet, basename='notes')
router.register(r'student-profiles', StudentProfileViewSet, basename='student-profiles')

urlpatterns = [
    path('', include(router.urls)),
    
    # Profile management endpoints
    path('profile/stats/', get_user_stats, name='user-stats'),
    path('profile/upload-picture/', upload_profile_picture, name='upload-profile-picture'),
    path('profile/remove-picture/', remove_profile_picture, name='remove-profile-picture'),
    
    # User search - endpoint available through UserViewSet
    
    # Goals and Achievements
    path('goals/', user_goals, name='user-goals'),
    path('achievements/', user_achievements, name='user-achievements'),
    path('goals/<int:goal_id>/progress/', update_goal_progress, name='update-goal-progress'),
    
    # New Features
    path('features/', include('apps.users.feature_urls')),
    
    # Notifications
    path('notifications/', get_notifications, name='user-notifications'),
    path('notifications/<int:notification_id>/read/', mark_notification_read, name='user-mark-notification-read'),
    
    # Account Management
    path('delete-account/', delete_user_account, name='user-delete-account'),
]
