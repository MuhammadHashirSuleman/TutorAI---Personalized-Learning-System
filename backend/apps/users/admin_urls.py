from django.urls import path
from .admin_views import (
    get_all_users, 
    get_system_analytics, 
    manage_user,
    send_notification_to_students,
    get_notifications,
    mark_notification_read,
    delete_user_account
)

urlpatterns = [
    path('users/', get_all_users, name='admin-users'),
    path('analytics/', get_system_analytics, name='admin-analytics'), 
    path('users/<int:user_id>/<str:action>/', manage_user, name='admin-manage-user'),
    path('send-notification/', send_notification_to_students, name='admin-send-notification'),
    path('notifications/', get_notifications, name='get-notifications'),
    path('notifications/<int:notification_id>/read/', mark_notification_read, name='mark-notification-read'),
    path('delete-account/', delete_user_account, name='delete-user-account'),
]
