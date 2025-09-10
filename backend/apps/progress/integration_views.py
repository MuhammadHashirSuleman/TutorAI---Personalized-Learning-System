"""
External Platform Integration API Views
Provides endpoints for integrating with external learning platforms
"""

from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model, login
from django.utils import timezone
from django.conf import settings
import logging
import json

from .external_integrations import (
    ExternalPlatformFactory,
    get_moodle_integration,
    get_coursera_integration,
    get_lti_integration
)
from apps.courses.models import Course

User = get_user_model()
logger = logging.getLogger(__name__)

# Custom permissions
class IsAdmin(permissions.BasePermission):
    """Allow access only to admin users"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'

class IsTeacherOrAdmin(permissions.BasePermission):
    """Allow access to teachers and admins"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['teacher', 'admin']

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsAdmin])
def get_integration_status(request):
    """
    Get status of all external platform integrations
    """
    try:
        integration_status = {
            'moodle': {
                'enabled': getattr(settings, 'MOODLE_INTEGRATION_ENABLED', False),
                'configured': bool(getattr(settings, 'MOODLE_API_KEY', '')),
                'last_sync': None,
                'status': 'not_configured'
            },
            'coursera': {
                'enabled': getattr(settings, 'COURSERA_INTEGRATION_ENABLED', False),
                'configured': bool(getattr(settings, 'COURSERA_CLIENT_ID', '')),
                'last_sync': None,
                'status': 'not_configured'
            },
            'lti': {
                'enabled': getattr(settings, 'LTI_INTEGRATION_ENABLED', True),
                'configured': bool(getattr(settings, 'LTI_CONSUMER_KEY', '')),
                'last_sync': None,
                'status': 'ready'
            }
        }
        
        # Test connections for enabled platforms
        for platform_name, platform_info in integration_status.items():
            if platform_info['enabled'] and platform_info['configured']:
                try:
                    integration = ExternalPlatformFactory.create_integration(platform_name)
                    if integration and integration.authenticate():
                        platform_info['status'] = 'connected'
                    else:
                        platform_info['status'] = 'connection_failed'
                except Exception as e:
                    platform_info['status'] = 'error'
                    platform_info['error'] = str(e)
        
        return Response({
            'integrations': integration_status,
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Integration status error: {str(e)}")
        return Response(
            {'error': 'Failed to get integration status', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsAdmin])
def sync_platform_data(request):
    """
    Sync data from external platforms
    """
    try:
        platform_name = request.data.get('platform')
        sync_type = request.data.get('sync_type', 'all')  # courses, students, grades, all
        
        if not platform_name:
            return Response(
                {'error': 'platform parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get integration instance
        integration = ExternalPlatformFactory.create_integration(platform_name)
        
        if not integration:
            return Response(
                {'error': f'Integration not available for platform: {platform_name}'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Perform sync operations
        sync_results = {
            'platform': platform_name,
            'sync_type': sync_type,
            'started_at': timezone.now().isoformat(),
            'results': {}
        }
        
        if sync_type in ['courses', 'all']:
            sync_results['results']['courses'] = integration.sync_courses().__dict__
        
        if sync_type in ['students', 'all']:
            sync_results['results']['students'] = integration.sync_students().__dict__
        
        if sync_type in ['grades', 'all']:
            sync_results['results']['grades'] = integration.sync_grades().__dict__
        
        sync_results['completed_at'] = timezone.now().isoformat()
        
        return Response(sync_results)
        
    except Exception as e:
        logger.error(f"Platform sync error: {str(e)}")
        return Response(
            {'error': 'Failed to sync platform data', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsTeacherOrAdmin])
def export_platform_data(request):
    """
    Export data to external platform format
    """
    try:
        platform_name = request.data.get('platform')
        data_type = request.data.get('data_type')  # courses, students, grades
        filters = request.data.get('filters', {})
        
        if not platform_name or not data_type:
            return Response(
                {'error': 'platform and data_type parameters are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get integration instance
        integration = ExternalPlatformFactory.create_integration(platform_name)
        
        if not integration:
            return Response(
                {'error': f'Integration not available for platform: {platform_name}'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Export data
        exported_data = integration.export_data(data_type, filters)
        
        response_data = {
            'platform': platform_name,
            'data_type': data_type,
            'filters_applied': filters,
            'exported_at': timezone.now().isoformat(),
            'data': exported_data
        }
        
        return Response(response_data)
        
    except Exception as e:
        logger.error(f"Platform export error: {str(e)}")
        return Response(
            {'error': 'Failed to export platform data', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@method_decorator(csrf_exempt, name='dispatch')
class LTILaunchView(View):
    """
    Handle LTI launch requests
    """
    
    def post(self, request):
        """Process LTI launch request"""
        try:
            # Get LTI integration
            lti_integration = get_lti_integration()
            
            if not lti_integration:
                return JsonResponse(
                    {'error': 'LTI integration not available'},
                    status=400
                )
            
            # Extract LTI parameters from request
            lti_params = {}
            for key, value in request.POST.items():
                lti_params[key] = value
            
            # Add request URL for signature validation
            lti_params['launch_url'] = request.build_absolute_uri()
            
            # Process LTI launch
            launch_result = lti_integration.process_lti_launch(lti_params)
            
            if 'error' in launch_result:
                return JsonResponse(
                    {'error': launch_result['error']},
                    status=400
                )
            
            # Extract launch session data
            launch_session = launch_result['launch_session']
            user = launch_session['user']
            course = launch_session['course']
            
            # Log the user in (simplified - in production, use proper session management)
            login(request, user)
            
            # Store launch session data in session
            request.session['lti_launch_session'] = {
                'user_id': user.id,
                'course_id': course.id,
                'resource_link_id': launch_session['resource_link_id'],
                'return_url': launch_session.get('return_url'),
                'launch_timestamp': launch_session['launch_timestamp'].isoformat()
            }
            
            # Return success response with redirect
            return JsonResponse({
                'success': True,
                'redirect_url': launch_result['redirect_url'],
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role
                },
                'course': {
                    'id': course.id,
                    'title': course.title,
                    'description': course.description
                }
            })
            
        except Exception as e:
            logger.error(f"LTI launch error: {str(e)}")
            return JsonResponse(
                {'error': 'LTI launch failed', 'details': str(e)},
                status=500
            )

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def lti_grade_passback(request):
    """
    Handle LTI grade passback
    """
    try:
        # Get LTI launch session from request session
        launch_session = request.session.get('lti_launch_session')
        
        if not launch_session:
            return Response(
                {'error': 'No active LTI session'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get grade from request
        grade = request.data.get('grade')
        
        if grade is None:
            return Response(
                {'error': 'grade parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate grade range
        if not 0 <= grade <= 100:
            return Response(
                {'error': 'grade must be between 0 and 100'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get LTI integration
        lti_integration = get_lti_integration()
        
        if not lti_integration:
            return Response(
                {'error': 'LTI integration not available'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Send grade back to LTI consumer
        success = lti_integration.send_grade_back(launch_session, grade)
        
        return Response({
            'success': success,
            'grade_sent': grade,
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"LTI grade passback error: {str(e)}")
        return Response(
            {'error': 'Grade passback failed', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsTeacherOrAdmin])
def get_external_courses(request):
    """
    Get courses from external platforms
    """
    try:
        platform = request.query_params.get('platform', 'all')
        
        external_courses = []
        
        if platform in ['moodle', 'all']:
            moodle_courses = Course.objects.filter(external_platform='moodle')
            external_courses.extend([
                {
                    'id': course.id,
                    'title': course.title,
                    'description': course.description,
                    'platform': 'moodle',
                    'external_id': course.external_id,
                    'is_active': course.is_active,
                    'instructor': course.instructor.email if course.instructor else None
                }
                for course in moodle_courses
            ])
        
        if platform in ['coursera', 'all']:
            coursera_courses = Course.objects.filter(external_platform='coursera')
            external_courses.extend([
                {
                    'id': course.id,
                    'title': course.title,
                    'description': course.description,
                    'platform': 'coursera',
                    'external_id': course.external_id,
                    'is_active': course.is_active,
                    'instructor': course.instructor.email if course.instructor else None
                }
                for course in coursera_courses
            ])
        
        if platform in ['lti', 'all']:
            lti_courses = Course.objects.filter(external_platform='lti')
            external_courses.extend([
                {
                    'id': course.id,
                    'title': course.title,
                    'description': course.description,
                    'platform': 'lti',
                    'external_id': course.external_id,
                    'is_active': course.is_active,
                    'instructor': course.instructor.email if course.instructor else None
                }
                for course in lti_courses
            ])
        
        return Response({
            'courses': external_courses,
            'total_count': len(external_courses),
            'platform_filter': platform,
            'retrieved_at': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"External courses retrieval error: {str(e)}")
        return Response(
            {'error': 'Failed to get external courses', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsAdmin])
def get_sync_history(request):
    """
    Get synchronization history for external platforms
    """
    try:
        platform = request.query_params.get('platform')
        limit = int(request.query_params.get('limit', 50))
        
        # In a real implementation, this would query a SyncHistory model
        # For now, return mock data structure
        sync_history = {
            'platform_filter': platform,
            'history': [
                {
                    'id': 1,
                    'platform': 'moodle',
                    'sync_type': 'courses',
                    'started_at': '2024-01-07T10:00:00Z',
                    'completed_at': '2024-01-07T10:05:00Z',
                    'status': 'completed',
                    'items_processed': 15,
                    'items_created': 3,
                    'items_updated': 12,
                    'items_failed': 0,
                    'errors': [],
                    'warnings': []
                },
                {
                    'id': 2,
                    'platform': 'lti',
                    'sync_type': 'students',
                    'started_at': '2024-01-07T09:30:00Z',
                    'completed_at': '2024-01-07T09:32:00Z',
                    'status': 'completed',
                    'items_processed': 25,
                    'items_created': 5,
                    'items_updated': 20,
                    'items_failed': 0,
                    'errors': [],
                    'warnings': ['LTI students are created automatically during launch']
                }
            ],
            'total_syncs': 2,
            'retrieved_at': timezone.now().isoformat()
        }
        
        return Response(sync_history)
        
    except Exception as e:
        logger.error(f"Sync history retrieval error: {str(e)}")
        return Response(
            {'error': 'Failed to get sync history', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsAdmin])
def test_platform_connection(request):
    """
    Test connection to external platform
    """
    try:
        platform_name = request.data.get('platform')
        
        if not platform_name:
            return Response(
                {'error': 'platform parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get integration instance
        integration = ExternalPlatformFactory.create_integration(platform_name)
        
        if not integration:
            return Response(
                {'error': f'Integration not available for platform: {platform_name}'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Test authentication
        auth_success = integration.authenticate()
        
        test_result = {
            'platform': platform_name,
            'connection_successful': auth_success,
            'tested_at': timezone.now().isoformat()
        }
        
        if auth_success:
            test_result['message'] = f'Successfully connected to {platform_name}'
        else:
            test_result['message'] = f'Failed to connect to {platform_name}'
            test_result['suggestions'] = [
                'Check API credentials in settings',
                'Verify platform URL is accessible',
                'Ensure API permissions are configured correctly'
            ]
        
        return Response(test_result)
        
    except Exception as e:
        logger.error(f"Platform connection test error: {str(e)}")
        return Response(
            {'error': 'Connection test failed', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_lti_course_content(request, course_id):
    """
    Get course content for LTI-launched course
    """
    try:
        # Verify LTI session
        launch_session = request.session.get('lti_launch_session')
        
        if not launch_session:
            return Response(
                {'error': 'No active LTI session'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Verify course access
        if launch_session['course_id'] != course_id:
            return Response(
                {'error': 'Access denied to this course'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get course
        course = get_object_or_404(Course, id=course_id, external_platform='lti')
        
        # Get course content (quizzes, lessons, etc.)
        from apps.courses.models import Quiz
        quizzes = Quiz.objects.filter(course=course, is_active=True)
        
        course_content = {
            'course': {
                'id': course.id,
                'title': course.title,
                'description': course.description,
                'instructor': {
                    'name': f"{course.instructor.first_name} {course.instructor.last_name}",
                    'email': course.instructor.email
                } if course.instructor else None
            },
            'quizzes': [
                {
                    'id': quiz.id,
                    'title': quiz.title,
                    'description': quiz.description,
                    'difficulty_level': quiz.difficulty_level,
                    'time_limit': quiz.time_limit,
                    'total_questions': len(quiz.questions_data) if quiz.questions_data else 0,
                    'passing_score': quiz.passing_score
                }
                for quiz in quizzes
            ],
            'lti_session': {
                'resource_link_id': launch_session['resource_link_id'],
                'launch_timestamp': launch_session['launch_timestamp'],
                'has_return_url': bool(launch_session.get('return_url'))
            },
            'retrieved_at': timezone.now().isoformat()
        }
        
        return Response(course_content)
        
    except Exception as e:
        logger.error(f"LTI course content error: {str(e)}")
        return Response(
            {'error': 'Failed to get course content', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
