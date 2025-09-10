"""
URL configuration for external platform integration APIs.
"""

from django.urls import path
from . import integration_views
from .integration_views import LTILaunchView

app_name = 'integration'

urlpatterns = [
    # Integration status and management
    path('status/', integration_views.get_integration_status, name='integration_status'),
    path('sync/', integration_views.sync_platform_data, name='sync_platform_data'),
    path('export/', integration_views.export_platform_data, name='export_platform_data'),
    path('test-connection/', integration_views.test_platform_connection, name='test_connection'),
    
    # LTI-specific endpoints
    path('lti/launch/', LTILaunchView.as_view(), name='lti_launch'),
    path('lti/grade-passback/', integration_views.lti_grade_passback, name='lti_grade_passback'),
    path('lti/course/<int:course_id>/content/', integration_views.get_lti_course_content, name='lti_course_content'),
    
    # External platform data retrieval
    path('courses/', integration_views.get_external_courses, name='external_courses'),
    path('sync-history/', integration_views.get_sync_history, name='sync_history'),
]
