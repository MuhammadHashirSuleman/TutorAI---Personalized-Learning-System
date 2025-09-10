from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import student_views, views

# Create router for student viewsets
router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    
    # Enrollment requests
    path('enrollment-requests/', student_views.my_enrollment_requests, name='my-enrollment-requests'),
    path('enrollment-requests/create/', student_views.create_enrollment_request, name='create-enrollment-request'),
    path('enrollment-requests/<int:request_id>/cancel/', student_views.cancel_enrollment_request, name='cancel-enrollment-request'),
    
    # Student's classes
    path('my-classes/', student_views.my_classes, name='my-classes'),
    path('classes/<int:class_id>/', student_views.class_detail, name='student-class-detail'),
    
    # Available subjects
    path('subjects/', student_views.available_subjects, name='available-subjects'),
    
    # Assignments and tasks
    path('assignments/', student_views.student_assignments, name='student-assignments'),
    path('assignments/<int:assignment_id>/', student_views.assignment_detail, name='assignment-detail'),
    path('assignments/submit/', student_views.submit_assignment, name='submit-assignment'),
    
    # Notifications
    path('notifications/', views.student_notifications, name='student-notifications'),
    path('notifications/stats/', views.student_notification_stats, name='student-notification-stats'),
    path('notifications/<int:notification_id>/', views.student_notification_detail, name='student-notification-detail'),
]
