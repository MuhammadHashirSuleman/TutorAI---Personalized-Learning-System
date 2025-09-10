"""
Enhanced Teacher Dashboard APIs
Comprehensive teacher dashboard with student analytics, class performance metrics,
and advanced teaching insights
"""

from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q, Avg, Count, Sum, Max, Min, F
from django.utils import timezone
from datetime import datetime, timedelta
import logging

from apps.courses.models import Course, CourseEnrollment, Subject, Quiz
from apps.progress.models import (
    StudentProgress, QuizResult, ClassRoom, ClassEnrollment,
    LearningGoal, PerformanceAnalytics
)
from apps.assessments.ai_services import StudentAnalyzer
from .serializers import UserSerializer

User = get_user_model()
logger = logging.getLogger(__name__)

# Custom permissions
class IsTeacher(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(request.user, 'role', None) == 'teacher'

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsTeacher])
def teacher_dashboard_overview(request):
    """
    Get comprehensive teacher dashboard overview with key metrics
    """
    teacher = request.user
    
    # Get time ranges
    now = timezone.now()
    last_30_days = now - timedelta(days=30)
    last_7_days = now - timedelta(days=7)
    
    try:
        # Basic stats
        courses = Course.objects.filter(instructor=teacher)
        total_courses = courses.count()
        
        # Student stats
        total_enrollments = CourseEnrollment.objects.filter(
            course__instructor=teacher, is_active=True
        )
        total_students = total_enrollments.values('student').distinct().count()
        new_students_30d = total_enrollments.filter(
            enrolled_at__gte=last_30_days
        ).values('student').distinct().count()
        
        # Quiz stats
        quizzes = Quiz.objects.filter(course__instructor=teacher)
        total_quizzes = quizzes.count()
        ai_generated_quizzes = quizzes.filter(ai_generated=True).count()
        
        # Performance stats
        quiz_results = QuizResult.objects.filter(
            quiz__course__instructor=teacher,
            status='completed'
        )
        
        total_quiz_attempts = quiz_results.count()
        recent_attempts = quiz_results.filter(created_at__gte=last_7_days).count()
        
        average_score = quiz_results.aggregate(Avg('score'))['score__avg'] or 0
        pass_rate = 0
        if total_quiz_attempts > 0:
            passed_attempts = quiz_results.filter(
                score__gte=F('quiz__passing_score')
            ).count()
            pass_rate = (passed_attempts / total_quiz_attempts) * 100
        
        # Active students (students with activity in last 7 days)
        active_students = StudentProgress.objects.filter(
            course__instructor=teacher,
            last_accessed__gte=last_7_days
        ).values('student').distinct().count()
        
        # Top performing students
        top_students_data = quiz_results.values(
            'student__email', 'student__first_name', 'student__last_name'
        ).annotate(
            avg_score=Avg('score'),
            total_quizzes=Count('id')
        ).filter(total_quizzes__gte=3).order_by('-avg_score')[:5]
        
        top_students = [
            {
                'email': student['student__email'],
                'name': f"{student['student__first_name'] or ''} {student['student__last_name'] or ''}".strip(),
                'average_score': round(student['avg_score'], 1),
                'total_quizzes': student['total_quizzes']
            }
            for student in top_students_data
        ]
        
        # Students needing attention (low performers)
        struggling_students_data = quiz_results.values(
            'student__email', 'student__first_name', 'student__last_name', 'student_id'
        ).annotate(
            avg_score=Avg('score'),
            total_quizzes=Count('id')
        ).filter(
            total_quizzes__gte=2,
            avg_score__lt=60
        ).order_by('avg_score')[:5]
        
        struggling_students = [
            {
                'student_id': student['student_id'],
                'email': student['student__email'],
                'name': f"{student['student__first_name'] or ''} {student['student__last_name'] or ''}".strip(),
                'average_score': round(student['avg_score'], 1),
                'total_quizzes': student['total_quizzes'],
                'needs_attention': True
            }
            for student in struggling_students_data
        ]
        
        # Recent activity timeline
        recent_activities = []
        
        # Recent quiz submissions
        recent_quiz_submissions = quiz_results.filter(
            created_at__gte=last_7_days
        ).select_related('student', 'quiz').order_by('-created_at')[:10]
        
        for submission in recent_quiz_submissions:
            recent_activities.append({
                'type': 'quiz_submission',
                'student': submission.student.email,
                'quiz_title': submission.quiz.title,
                'score': submission.score,
                'timestamp': submission.created_at,
                'status': 'passed' if submission.score >= submission.quiz.passing_score else 'failed'
            })
        
        # Recent enrollments
        recent_enrollments = total_enrollments.filter(
            enrolled_at__gte=last_7_days
        ).select_related('student', 'course').order_by('-enrolled_at')[:5]
        
        for enrollment in recent_enrollments:
            recent_activities.append({
                'type': 'new_enrollment',
                'student': enrollment.student.email,
                'course_title': enrollment.course.title,
                'timestamp': enrollment.enrolled_at,
                'status': 'enrolled'
            })
        
        # Sort activities by timestamp
        recent_activities.sort(key=lambda x: x['timestamp'], reverse=True)
        recent_activities = recent_activities[:15]  # Limit to 15 most recent
        
        # Course performance breakdown
        course_performance = []
        for course in courses:
            course_quiz_results = quiz_results.filter(quiz__course=course)
            
            if course_quiz_results.exists():
                course_avg = course_quiz_results.aggregate(Avg('score'))['score__avg']
                course_students = course_quiz_results.values('student').distinct().count()
                course_quizzes = Quiz.objects.filter(course=course).count()
                
                course_performance.append({
                    'course_id': course.id,
                    'course_title': course.title,
                    'average_score': round(course_avg, 1),
                    'enrolled_students': CourseEnrollment.objects.filter(
                        course=course, is_active=True
                    ).count(),
                    'active_students': course_students,
                    'total_quizzes': course_quizzes,
                    'difficulty_level': course.difficulty_level
                })
        
        # Weekly performance trend (last 8 weeks)
        weekly_performance = []
        for i in range(8):
            week_start = now - timedelta(weeks=i+1)
            week_end = now - timedelta(weeks=i)
            
            week_results = quiz_results.filter(
                created_at__gte=week_start,
                created_at__lt=week_end
            )
            
            if week_results.exists():
                week_avg = week_results.aggregate(Avg('score'))['score__avg']
                week_count = week_results.count()
            else:
                week_avg = 0
                week_count = 0
            
            weekly_performance.append({
                'week': f"Week {8-i}",
                'average_score': round(week_avg, 1),
                'total_attempts': week_count,
                'date_range': f"{week_start.strftime('%m/%d')} - {week_end.strftime('%m/%d')}"
            })
        
        weekly_performance.reverse()  # Show chronological order
        
        dashboard_data = {
            'overview': {
                'total_courses': total_courses,
                'total_students': total_students,
                'new_students_30d': new_students_30d,
                'active_students': active_students,
                'total_quizzes': total_quizzes,
                'ai_generated_quizzes': ai_generated_quizzes,
                'total_quiz_attempts': total_quiz_attempts,
                'recent_attempts_7d': recent_attempts,
                'average_score': round(average_score, 1),
                'pass_rate': round(pass_rate, 1)
            },
            'performance_insights': {
                'top_students': top_students,
                'struggling_students': struggling_students,
                'course_performance': course_performance,
                'weekly_trend': weekly_performance
            },
            'recent_activity': recent_activities,
            'recommendations': _generate_teacher_recommendations(
                teacher, struggling_students, course_performance
            )
        }
        
        return Response(dashboard_data)
        
    except Exception as e:
        logger.error(f"Teacher dashboard error: {str(e)}")
        return Response(
            {'error': 'Failed to load dashboard data', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def _generate_teacher_recommendations(teacher, struggling_students, course_performance):
    """Generate personalized recommendations for teachers"""
    recommendations = []
    
    # Struggling students recommendations
    if len(struggling_students) > 0:
        recommendations.append({
            'type': 'student_attention',
            'priority': 'high',
            'title': f'{len(struggling_students)} students need attention',
            'description': f'Consider creating personalized AI quizzes for struggling students',
            'action_url': '/dashboard/struggling-students/',
            'icon': '⚠️'
        })
    
    # Low performing courses
    low_performing_courses = [
        course for course in course_performance 
        if course['average_score'] < 70
    ]
    
    if low_performing_courses:
        recommendations.append({
            'type': 'course_improvement',
            'priority': 'medium',
            'title': f'{len(low_performing_courses)} courses need improvement',
            'description': 'Review course materials and consider additional resources',
            'action_url': '/dashboard/course-performance/',
            'icon': '📚'
        })
    
    # AI quiz suggestions
    recommendations.append({
        'type': 'ai_quiz',
        'priority': 'low',
        'title': 'Generate AI-powered quizzes',
        'description': 'Use AI to create personalized quizzes based on student weaknesses',
        'action_url': '/assessments/ai/generate/',
        'icon': '🤖'
    })
    
    return recommendations

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsTeacher])
def detailed_student_analytics(request):
    """
    Get detailed analytics for all students in teacher's courses
    """
    teacher = request.user
    
    # Query parameters
    course_id = request.query_params.get('course_id')
    sort_by = request.query_params.get('sort_by', 'performance')  # performance, activity, name
    filter_by = request.query_params.get('filter_by', 'all')  # all, struggling, excellent, inactive
    
    try:
        # Get enrollments
        enrollments_query = CourseEnrollment.objects.filter(
            course__instructor=teacher,
            is_active=True
        ).select_related('student', 'course')
        
        if course_id:
            enrollments_query = enrollments_query.filter(course_id=course_id)
        
        enrollments = enrollments_query.all()
        
        student_analytics = []
        
        for enrollment in enrollments:
            student = enrollment.student
            course = enrollment.course
            
            try:
                # Use StudentAnalyzer for comprehensive analysis
                analyzer = StudentAnalyzer(student.id)
                performance_summary = analyzer.get_performance_summary(course.id)
                weaknesses = analyzer.identify_weaknesses(course.id, limit=5)
                strengths = analyzer.get_strengths(course.id, limit=3)
                
                # Additional stats
                quiz_results = QuizResult.objects.filter(
                    student=student,
                    quiz__course=course,
                    status='completed'
                )
                
                last_activity = StudentProgress.objects.filter(
                    student=student,
                    course=course
                ).order_by('-last_accessed').first()
                
                # Calculate engagement score
                days_since_enrollment = (timezone.now() - enrollment.enrolled_at).days
                expected_activity = max(days_since_enrollment * 0.2, 1)  # Expected 0.2 activities per day
                actual_activity = StudentProgress.objects.filter(
                    student=student, course=course
                ).count()
                engagement_score = min((actual_activity / expected_activity) * 100, 100)
                
                # Determine student status
                avg_score = performance_summary['overall_average_score']
                if avg_score >= 85:
                    status_category = 'excellent'
                elif avg_score >= 70:
                    status_category = 'good'
                elif avg_score >= 60:
                    status_category = 'average'
                else:
                    status_category = 'struggling'
                
                # Check if inactive
                if last_activity and (timezone.now() - last_activity.last_accessed).days > 7:
                    activity_status = 'inactive'
                elif last_activity and (timezone.now() - last_activity.last_accessed).days > 3:
                    activity_status = 'low'
                else:
                    activity_status = 'active'
                
                student_data = {
                    'student_id': student.id,
                    'email': student.email,
                    'name': f"{student.first_name or ''} {student.last_name or ''}".strip() or 'N/A',
                    'course_id': course.id,
                    'course_title': course.title,
                    'enrollment_date': enrollment.enrolled_at,
                    'performance_summary': performance_summary,
                    'weaknesses': weaknesses,
                    'strengths': strengths,
                    'status_category': status_category,
                    'activity_status': activity_status,
                    'engagement_score': round(engagement_score, 1),
                    'last_activity': last_activity.last_accessed if last_activity else enrollment.enrolled_at,
                    'quiz_stats': {
                        'total_attempts': quiz_results.count(),
                        'best_score': quiz_results.aggregate(Max('score'))['score__max'] or 0,
                        'latest_score': quiz_results.order_by('-created_at').first().score if quiz_results.exists() else 0,
                        'improvement_trend': performance_summary['performance_trend']
                    },
                    'recommendations': _generate_student_recommendations(
                        performance_summary, weaknesses, activity_status
                    )
                }
                
                student_analytics.append(student_data)
                
            except Exception as e:
                logger.warning(f"Failed to analyze student {student.id}: {str(e)}")
                continue
        
        # Apply filtering
        if filter_by != 'all':
            if filter_by == 'struggling':
                student_analytics = [s for s in student_analytics if s['status_category'] in ['struggling', 'average']]
            elif filter_by == 'excellent':
                student_analytics = [s for s in student_analytics if s['status_category'] == 'excellent']
            elif filter_by == 'inactive':
                student_analytics = [s for s in student_analytics if s['activity_status'] == 'inactive']
        
        # Apply sorting
        if sort_by == 'performance':
            student_analytics.sort(key=lambda x: x['performance_summary']['overall_average_score'], reverse=True)
        elif sort_by == 'activity':
            student_analytics.sort(key=lambda x: x['last_activity'], reverse=True)
        elif sort_by == 'name':
            student_analytics.sort(key=lambda x: x['name'])
        elif sort_by == 'engagement':
            student_analytics.sort(key=lambda x: x['engagement_score'], reverse=True)
        
        return Response({
            'total_students': len(student_analytics),
            'filters_applied': {
                'course_id': course_id,
                'sort_by': sort_by,
                'filter_by': filter_by
            },
            'students': student_analytics,
            'summary_stats': {
                'excellent': len([s for s in student_analytics if s['status_category'] == 'excellent']),
                'good': len([s for s in student_analytics if s['status_category'] == 'good']),
                'average': len([s for s in student_analytics if s['status_category'] == 'average']),
                'struggling': len([s for s in student_analytics if s['status_category'] == 'struggling']),
                'inactive': len([s for s in student_analytics if s['activity_status'] == 'inactive']),
            }
        })
        
    except Exception as e:
        logger.error(f"Student analytics error: {str(e)}")
        return Response(
            {'error': 'Failed to load student analytics', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def _generate_student_recommendations(performance_summary, weaknesses, activity_status):
    """Generate recommendations for individual students"""
    recommendations = []
    
    avg_score = performance_summary['overall_average_score']
    
    if avg_score < 60:
        recommendations.append({
            'type': 'urgent_intervention',
            'message': 'Create personalized AI quiz focusing on weak concepts',
            'action': 'generate_ai_quiz'
        })
    
    if len(weaknesses) > 3:
        recommendations.append({
            'type': 'concept_review',
            'message': f'Student struggling with {len(weaknesses)} concepts',
            'action': 'review_materials'
        })
    
    if activity_status == 'inactive':
        recommendations.append({
            'type': 'engagement',
            'message': 'Student has been inactive - consider reaching out',
            'action': 'contact_student'
        })
    
    return recommendations

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsTeacher])
def class_performance_comparison(request):
    """
    Compare performance across different classes/courses
    """
    teacher = request.user
    
    try:
        courses = Course.objects.filter(instructor=teacher)
        
        comparison_data = []
        
        for course in courses:
            # Get quiz results for this course
            quiz_results = QuizResult.objects.filter(
                quiz__course=course,
                status='completed'
            )
            
            if not quiz_results.exists():
                continue
            
            # Calculate metrics
            total_students = CourseEnrollment.objects.filter(
                course=course, is_active=True
            ).count()
            
            active_students = quiz_results.values('student').distinct().count()
            avg_score = quiz_results.aggregate(Avg('score'))['score__avg']
            median_score = quiz_results.order_by('score')[quiz_results.count()//2].score if quiz_results.count() > 0 else 0
            
            # Score distribution
            score_distribution = {
                'A (90-100)': quiz_results.filter(score__gte=90).count(),
                'B (80-89)': quiz_results.filter(score__gte=80, score__lt=90).count(),
                'C (70-79)': quiz_results.filter(score__gte=70, score__lt=80).count(),
                'D (60-69)': quiz_results.filter(score__gte=60, score__lt=70).count(),
                'F (0-59)': quiz_results.filter(score__lt=60).count(),
            }
            
            # Engagement metrics
            recent_activity = StudentProgress.objects.filter(
                course=course,
                last_accessed__gte=timezone.now() - timedelta(days=7)
            ).values('student').distinct().count()
            
            engagement_rate = (recent_activity / total_students * 100) if total_students > 0 else 0
            
            # Difficulty vs Performance analysis
            easy_quizzes = Quiz.objects.filter(course=course, difficulty_level='easy')
            medium_quizzes = Quiz.objects.filter(course=course, difficulty_level='medium')
            hard_quizzes = Quiz.objects.filter(course=course, difficulty_level='hard')
            
            difficulty_performance = {
                'easy': QuizResult.objects.filter(
                    quiz__in=easy_quizzes, status='completed'
                ).aggregate(Avg('score'))['score__avg'] or 0,
                'medium': QuizResult.objects.filter(
                    quiz__in=medium_quizzes, status='completed'
                ).aggregate(Avg('score'))['score__avg'] or 0,
                'hard': QuizResult.objects.filter(
                    quiz__in=hard_quizzes, status='completed'
                ).aggregate(Avg('score'))['score__avg'] or 0,
            }
            
            course_data = {
                'course_id': course.id,
                'course_title': course.title,
                'subject': course.subject.name,
                'difficulty_level': course.difficulty_level,
                'total_students': total_students,
                'active_students': active_students,
                'participation_rate': round((active_students / total_students * 100), 1) if total_students > 0 else 0,
                'engagement_rate': round(engagement_rate, 1),
                'performance_metrics': {
                    'average_score': round(avg_score, 1),
                    'median_score': round(median_score, 1),
                    'score_distribution': score_distribution,
                    'difficulty_performance': {
                        key: round(value, 1) for key, value in difficulty_performance.items()
                    }
                },
                'quiz_stats': {
                    'total_quizzes': Quiz.objects.filter(course=course).count(),
                    'ai_generated': Quiz.objects.filter(course=course, ai_generated=True).count(),
                    'total_attempts': quiz_results.count()
                }
            }
            
            comparison_data.append(course_data)
        
        # Overall statistics
        all_results = QuizResult.objects.filter(
            quiz__course__instructor=teacher,
            status='completed'
        )
        
        overall_stats = {
            'total_courses': len(comparison_data),
            'overall_average': round(all_results.aggregate(Avg('score'))['score__avg'] or 0, 1),
            'best_performing_course': max(comparison_data, key=lambda x: x['performance_metrics']['average_score'])['course_title'] if comparison_data else None,
            'most_engaged_course': max(comparison_data, key=lambda x: x['engagement_rate'])['course_title'] if comparison_data else None
        }
        
        return Response({
            'overall_stats': overall_stats,
            'course_comparisons': comparison_data,
            'insights': _generate_comparison_insights(comparison_data)
        })
        
    except Exception as e:
        logger.error(f"Class comparison error: {str(e)}")
        return Response(
            {'error': 'Failed to load comparison data', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def _generate_comparison_insights(comparison_data):
    """Generate insights from course comparison data"""
    insights = []
    
    if not comparison_data:
        return insights
    
    # Find courses that need attention
    low_performing = [course for course in comparison_data if course['performance_metrics']['average_score'] < 70]
    high_performing = [course for course in comparison_data if course['performance_metrics']['average_score'] >= 85]
    low_engagement = [course for course in comparison_data if course['engagement_rate'] < 60]
    
    if low_performing:
        insights.append({
            'type': 'performance_concern',
            'message': f'{len(low_performing)} course(s) have below-average performance',
            'details': [course['course_title'] for course in low_performing]
        })
    
    if high_performing:
        insights.append({
            'type': 'performance_success',
            'message': f'{len(high_performing)} course(s) showing excellent performance',
            'details': [course['course_title'] for course in high_performing]
        })
    
    if low_engagement:
        insights.append({
            'type': 'engagement_concern',
            'message': f'{len(low_engagement)} course(s) have low student engagement',
            'details': [course['course_title'] for course in low_engagement]
        })
    
    return insights

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsTeacher])
def bulk_quiz_operations(request):
    """
    Perform bulk operations on multiple quizzes
    Operations: activate, deactivate, delete, duplicate
    """
    teacher = request.user
    
    quiz_ids = request.data.get('quiz_ids', [])
    operation = request.data.get('operation')
    
    if not quiz_ids or not operation:
        return Response(
            {'error': 'quiz_ids and operation are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Verify teacher owns all quizzes
        quizzes = Quiz.objects.filter(
            id__in=quiz_ids,
            course__instructor=teacher
        )
        
        if len(quizzes) != len(quiz_ids):
            return Response(
                {'error': 'Some quizzes not found or access denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        results = []
        
        if operation == 'activate':
            updated = quizzes.update(is_active=True)
            results.append(f'Activated {updated} quizzes')
            
        elif operation == 'deactivate':
            updated = quizzes.update(is_active=False)
            results.append(f'Deactivated {updated} quizzes')
            
        elif operation == 'delete':
            # Check if any quiz has been taken
            quiz_with_attempts = quizzes.filter(results__isnull=False).distinct()
            if quiz_with_attempts.exists():
                return Response(
                    {'error': 'Cannot delete quizzes that have been attempted by students'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            deleted_count = quizzes.count()
            quizzes.delete()
            results.append(f'Deleted {deleted_count} quizzes')
            
        elif operation == 'duplicate':
            for quiz in quizzes:
                new_quiz = Quiz.objects.create(
                    title=f"{quiz.title} (Copy)",
                    description=quiz.description,
                    course=quiz.course,
                    questions_data=quiz.questions_data,
                    passing_score=quiz.passing_score,
                    time_limit=quiz.time_limit,
                    attempts_allowed=quiz.attempts_allowed,
                    show_results_immediately=quiz.show_results_immediately,
                    shuffle_questions=quiz.shuffle_questions,
                    shuffle_options=quiz.shuffle_options,
                    difficulty_level=quiz.difficulty_level,
                    is_active=False  # Duplicated quizzes start inactive
                )
                results.append(f'Duplicated quiz: {quiz.title}')
        
        else:
            return Response(
                {'error': f'Unknown operation: {operation}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({
            'success': True,
            'operation': operation,
            'results': results,
            'affected_quizzes': len(quiz_ids)
        })
        
    except Exception as e:
        logger.error(f"Bulk operation error: {str(e)}")
        return Response(
            {'error': 'Bulk operation failed', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
