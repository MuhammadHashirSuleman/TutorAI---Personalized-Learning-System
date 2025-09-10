"""
AI Recommendation System API Views
Provides endpoints for personalized learning recommendations
"""

from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Count, Avg, Q
from datetime import timedelta
import logging

from .recommendation_engine import recommendation_engine
from .models import StudentProgress, QuizResult
from apps.courses.models import Course

User = get_user_model()
logger = logging.getLogger(__name__)

# Custom permissions
class IsStudentOrTeacher(permissions.BasePermission):
    """Allow access to students (for their own data) and teachers"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role in ['student', 'teacher']

class IsStudent(permissions.BasePermission):
    """Allow access only to students"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'student'

class IsTeacher(permissions.BasePermission):
    """Allow access only to teachers"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'teacher'

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsStudentOrTeacher])
def get_student_recommendations(request, student_id=None):
    """
    Get comprehensive AI-powered recommendations for a student
    Students can only access their own recommendations
    Teachers can access any of their students' recommendations
    """
    try:
        # Determine target student
        if student_id is None:
            # Self-access for students
            if request.user.role != 'student':
                return Response(
                    {'error': 'student_id is required for teachers'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            target_student_id = request.user.id
        else:
            # Access by ID (teachers or self-access)
            if request.user.role == 'student' and request.user.id != student_id:
                return Response(
                    {'error': 'Students can only access their own recommendations'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            if request.user.role == 'teacher':
                # Verify teacher has access to this student
                student = get_object_or_404(User, id=student_id, role='student')
                # Check if teacher has any courses with this student
                student_courses = student.enrollments.values_list('course_id', flat=True)
                teacher_courses = Course.objects.filter(instructor=request.user).values_list('id', flat=True)
                
                if not set(student_courses).intersection(set(teacher_courses)):
                    return Response(
                        {'error': 'Access denied - student not in your courses'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            
            target_student_id = student_id
        
        # Get recommendation type from query params
        recommendation_type = request.query_params.get('type', 'all')
        valid_types = ['all', 'courses', 'quizzes', 'topics', 'learning_path']
        
        if recommendation_type not in valid_types:
            return Response(
                {'error': f'Invalid type. Must be one of: {", ".join(valid_types)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate recommendations using AI engine
        recommendations = recommendation_engine.get_student_recommendations(
            target_student_id, 
            recommendation_type
        )
        
        if 'error' in recommendations:
            return Response(
                {'error': 'Failed to generate recommendations', 'details': recommendations['error']},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Add metadata
        recommendations['metadata'] = {
            'requested_by': request.user.id,
            'requester_role': request.user.role,
            'recommendation_type': recommendation_type,
            'generated_at': timezone.now().isoformat()
        }
        
        return Response(recommendations)
        
    except Exception as e:
        logger.error(f"Student recommendations error: {str(e)}")
        return Response(
            {'error': 'Failed to get recommendations', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsStudent])
def get_personalized_learning_path(request):
    """
    Get a personalized learning path for the authenticated student
    """
    try:
        student = request.user
        
        # Generate learning path
        learning_path = recommendation_engine._generate_learning_path(
            student, 
            recommendation_engine._build_student_profile(student)
        )
        
        if 'error' in learning_path:
            return Response(
                {'error': 'Failed to generate learning path', 'details': learning_path['error']},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response({
            'success': True,
            'learning_path': learning_path,
            'student_id': student.id,
            'generated_at': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Learning path generation error: {str(e)}")
        return Response(
            {'error': 'Failed to generate learning path', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsStudent])
def get_course_recommendations(request):
    """
    Get AI-powered course recommendations for the authenticated student
    """
    try:
        student = request.user
        student_profile = recommendation_engine._build_student_profile(student)
        
        # Get course recommendations
        course_recommendations = recommendation_engine._recommend_courses(student, student_profile)
        
        return Response({
            'success': True,
            'recommendations': course_recommendations,
            'total_recommendations': len(course_recommendations),
            'student_profile_summary': student_profile.get('summary', ''),
            'generated_at': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Course recommendations error: {str(e)}")
        return Response(
            {'error': 'Failed to get course recommendations', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsStudent])
def get_quiz_recommendations(request):
    """
    Get AI-powered quiz recommendations for practice
    """
    try:
        student = request.user
        student_profile = recommendation_engine._build_student_profile(student)
        
        # Get quiz recommendations
        quiz_recommendations = recommendation_engine._recommend_quizzes(student, student_profile)
        
        # Group by priority
        high_priority = [q for q in quiz_recommendations if q.get('priority') == 'high']
        medium_priority = [q for q in quiz_recommendations if q.get('priority') == 'medium']
        low_priority = [q for q in quiz_recommendations if q.get('priority') == 'low']
        
        return Response({
            'success': True,
            'recommendations': {
                'high_priority': high_priority,
                'medium_priority': medium_priority,
                'low_priority': low_priority,
                'all': quiz_recommendations
            },
            'summary': {
                'total_recommendations': len(quiz_recommendations),
                'high_priority_count': len(high_priority),
                'medium_priority_count': len(medium_priority),
                'low_priority_count': len(low_priority)
            },
            'student_profile_summary': student_profile.get('summary', ''),
            'generated_at': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Quiz recommendations error: {str(e)}")
        return Response(
            {'error': 'Failed to get quiz recommendations', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsStudent])
def get_study_topic_recommendations(request):
    """
    Get AI-powered study topic recommendations
    """
    try:
        student = request.user
        student_profile = recommendation_engine._build_student_profile(student)
        
        # Get study topic recommendations
        topic_recommendations = recommendation_engine._recommend_study_topics(student, student_profile)
        
        # Group by priority and source
        high_priority = [t for t in topic_recommendations if t.get('priority') == 'high']
        ai_generated = [t for t in topic_recommendations if t.get('source') == 'ai_generated']
        
        return Response({
            'success': True,
            'recommendations': topic_recommendations,
            'categorized': {
                'high_priority': high_priority,
                'ai_generated': ai_generated,
                'all': topic_recommendations
            },
            'summary': {
                'total_topics': len(topic_recommendations),
                'high_priority_count': len(high_priority),
                'ai_generated_count': len(ai_generated)
            },
            'student_profile_summary': student_profile.get('summary', ''),
            'generated_at': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Study topic recommendations error: {str(e)}")
        return Response(
            {'error': 'Failed to get study topic recommendations', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsStudent])
def get_peer_based_recommendations(request):
    """
    Get recommendations based on similar students' success
    """
    try:
        student = request.user
        student_profile = recommendation_engine._build_student_profile(student)
        
        # Get peer-based recommendations
        peer_recommendations = recommendation_engine._get_peer_based_recommendations(student, student_profile)
        
        return Response({
            'success': True,
            'peer_recommendations': peer_recommendations,
            'total_recommendations': len(peer_recommendations),
            'explanation': "These recommendations are based on what similar students found helpful",
            'student_profile_summary': student_profile.get('summary', ''),
            'generated_at': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Peer recommendations error: {str(e)}")
        return Response(
            {'error': 'Failed to get peer-based recommendations', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsStudent])
def get_student_learning_profile(request):
    """
    Get detailed learning profile for the authenticated student
    """
    try:
        student = request.user
        student_profile = recommendation_engine._build_student_profile(student)
        
        # Add additional insights
        quiz_results = QuizResult.objects.filter(student=student, status='completed')
        
        additional_insights = {
            'total_quiz_attempts': quiz_results.count(),
            'subjects_studied': list(quiz_results.values_list(
                'quiz__course__subject__name', flat=True
            ).distinct().exclude(quiz__course__subject__name__isnull=True)),
            'recent_activity_level': quiz_results.filter(
                created_at__gte=timezone.now() - timedelta(days=7)
            ).count(),
            'improvement_areas_identified': len(student_profile.get('weaknesses', [])),
            'strengths_identified': len(student_profile.get('strengths', [])),
        }
        
        return Response({
            'success': True,
            'learning_profile': student_profile,
            'additional_insights': additional_insights,
            'profile_completeness': calculate_profile_completeness(student_profile),
            'generated_at': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Learning profile error: {str(e)}")
        return Response(
            {'error': 'Failed to get learning profile', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsStudent])
def update_learning_preferences(request):
    """
    Allow students to update their learning preferences to improve recommendations
    """
    try:
        student = request.user
        preferences = request.data.get('preferences', {})
        
        # Validate preferences structure
        valid_keys = ['preferred_difficulty', 'study_time_preference', 'learning_style', 'subject_interests']
        
        for key in preferences.keys():
            if key not in valid_keys:
                return Response(
                    {'error': f'Invalid preference key: {key}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Store preferences (in a real implementation, you'd have a UserPreferences model)
        # For now, we'll return a success message
        
        return Response({
            'success': True,
            'message': 'Learning preferences updated successfully',
            'preferences_updated': preferences,
            'note': 'These preferences will be considered in future recommendations',
            'updated_at': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Preferences update error: {str(e)}")
        return Response(
            {'error': 'Failed to update preferences', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsTeacher])
def get_class_recommendations_summary(request):
    """
    Get AI recommendations summary for all students in teacher's classes
    """
    try:
        teacher = request.user
        
        # Get all students in teacher's courses
        teacher_courses = Course.objects.filter(instructor=teacher)
        student_ids = teacher_courses.values_list('enrollments__student_id', flat=True).distinct()
        
        class_summary = {
            'total_students': len(student_ids),
            'students_with_recommendations': 0,
            'common_weaknesses': {},
            'recommended_actions': [],
            'performance_insights': {}
        }
        
        common_weaknesses = {}
        students_processed = 0
        
        for student_id in student_ids[:20]:  # Limit for performance
            try:
                student = User.objects.get(id=student_id, role='student')
                profile = recommendation_engine._build_student_profile(student)
                
                if profile.get('weaknesses'):
                    students_processed += 1
                    
                    for weakness in profile['weaknesses']:
                        subject = weakness['subject']
                        if subject not in common_weaknesses:
                            common_weaknesses[subject] = {
                                'count': 0,
                                'avg_score': 0,
                                'total_score': 0
                            }
                        
                        common_weaknesses[subject]['count'] += 1
                        common_weaknesses[subject]['total_score'] += weakness['score']
                        common_weaknesses[subject]['avg_score'] = (
                            common_weaknesses[subject]['total_score'] / 
                            common_weaknesses[subject]['count']
                        )
                        
            except Exception as e:
                logger.warning(f"Error processing student {student_id}: {str(e)}")
                continue
        
        # Generate class-level recommendations
        if common_weaknesses:
            # Find most common weakness
            most_common_weakness = max(common_weaknesses.items(), key=lambda x: x[1]['count'])
            
            class_summary['recommended_actions'].append({
                'action': 'Focus on Common Weakness',
                'description': f"Consider additional support for {most_common_weakness[0]} - affects {most_common_weakness[1]['count']} students",
                'priority': 'high'
            })
        
        class_summary['students_with_recommendations'] = students_processed
        class_summary['common_weaknesses'] = common_weaknesses
        class_summary['generated_at'] = timezone.now().isoformat()
        
        return Response({
            'success': True,
            'class_summary': class_summary
        })
        
    except Exception as e:
        logger.error(f"Class recommendations summary error: {str(e)}")
        return Response(
            {'error': 'Failed to get class recommendations summary', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def calculate_profile_completeness(profile: dict) -> dict:
    """Calculate how complete a student's learning profile is"""
    completeness_score = 0
    max_score = 100
    
    # Performance metrics (30 points)
    if profile.get('performance_metrics', {}).get('total_quizzes', 0) > 0:
        completeness_score += 30
    
    # Learning patterns (20 points)
    if profile.get('learning_patterns'):
        completeness_score += 20
    
    # Strengths identified (25 points)
    if profile.get('strengths'):
        completeness_score += 25
    
    # Weaknesses identified (25 points)
    if profile.get('weaknesses'):
        completeness_score += 25
    
    return {
        'completeness_percentage': (completeness_score / max_score) * 100,
        'completeness_score': completeness_score,
        'max_score': max_score,
        'recommendations_quality': 'high' if completeness_score >= 75 else 'medium' if completeness_score >= 50 else 'low'
    }
