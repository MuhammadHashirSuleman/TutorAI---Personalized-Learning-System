"""
Enhanced Class Management Views
Improved classroom management with bulk operations and advanced filtering
Provides comprehensive classroom administration features
"""

from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q, Avg, Count, Sum, Max, Min, F
from django.utils import timezone
from django.db import transaction
from datetime import datetime, timedelta
import logging
import csv
import io

from apps.courses.models import Course, CourseEnrollment, Quiz
from .models import (
    StudentProgress, QuizResult, ClassRoom, ClassEnrollment,
    LearningGoal, PerformanceAnalytics
)
from .serializers import ClassRoomSerializer, ClassEnrollmentSerializer
from apps.assessments.ai_services import StudentAnalyzer

User = get_user_model()
logger = logging.getLogger(__name__)

# Custom permissions
class IsTeacher(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(request.user, 'role', None) == 'teacher'

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsTeacher])
def enhanced_class_list(request):
    """
    Get enhanced class list with filtering, sorting, and search capabilities
    """
    teacher = request.user
    
    # Query parameters
    search = request.query_params.get('search', '')
    subject_filter = request.query_params.get('subject', '')
    status_filter = request.query_params.get('status', '')
    sort_by = request.query_params.get('sort_by', 'created_at')
    sort_order = request.query_params.get('sort_order', 'desc')
    performance_filter = request.query_params.get('performance', '')  # high, medium, low
    page_size = int(request.query_params.get('page_size', 20))
    page = int(request.query_params.get('page', 1))
    
    try:
        # Base queryset
        classes = ClassRoom.objects.filter(teacher=teacher)
        
        # Search functionality
        if search:
            classes = classes.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(class_code__icontains=search)
            )
        
        # Subject filter
        if subject_filter:
            classes = classes.filter(subject__name__icontains=subject_filter)
        
        # Status filter
        if status_filter:
            if status_filter == 'active':
                classes = classes.filter(is_active=True)
            elif status_filter == 'inactive':
                classes = classes.filter(is_active=False)
        
        # Enhanced class data with performance metrics
        enhanced_classes = []
        
        for classroom in classes:
            # Get enrollments
            enrollments = ClassEnrollment.objects.filter(
                classroom=classroom,
                status='active'
            ).select_related('student')
            
            # Calculate performance metrics
            student_ids = enrollments.values_list('student_id', flat=True)
            quiz_results = QuizResult.objects.filter(
                student_id__in=student_ids,
                quiz__course__in=classroom.courses.all(),
                status='completed'
            )
            
            total_students = enrollments.count()
            avg_performance = quiz_results.aggregate(Avg('score'))['score__avg'] or 0
            
            # Classify performance
            if avg_performance >= 80:
                performance_level = 'high'
            elif avg_performance >= 60:
                performance_level = 'medium'
            else:
                performance_level = 'low'
            
            # Recent activity (last 7 days)
            recent_activity = StudentProgress.objects.filter(
                student_id__in=student_ids,
                last_accessed__gte=timezone.now() - timedelta(days=7)
            ).values('student').distinct().count()
            
            activity_rate = (recent_activity / total_students * 100) if total_students > 0 else 0
            
            class_data = {
                'id': classroom.id,
                'name': classroom.name,
                'description': classroom.description,
                'class_code': classroom.class_code,
                'class_type': classroom.class_type,
                'subject': classroom.subject.name if classroom.subject else 'No Subject',
                'is_active': classroom.is_active,
                'created_at': classroom.created_at,
                'updated_at': classroom.updated_at,
                'metrics': {
                    'total_students': total_students,
                    'max_students': classroom.max_students,
                    'capacity_percentage': (total_students / classroom.max_students * 100) if classroom.max_students > 0 else 0,
                    'avg_performance': round(avg_performance, 1),
                    'performance_level': performance_level,
                    'activity_rate': round(activity_rate, 1),
                    'total_courses': classroom.courses.count(),
                    'total_assignments': classroom.total_assignments,
                    'engagement_score': classroom.engagement_score
                },
                'status_indicators': {
                    'needs_attention': avg_performance < 60 or activity_rate < 50,
                    'high_performing': avg_performance >= 85 and activity_rate >= 80,
                    'at_capacity': total_students >= classroom.max_students * 0.9
                }
            }
            
            enhanced_classes.append(class_data)
        
        # Apply performance filter
        if performance_filter:
            enhanced_classes = [
                cls for cls in enhanced_classes 
                if cls['metrics']['performance_level'] == performance_filter
            ]
        
        # Sorting
        reverse_order = sort_order == 'desc'
        if sort_by == 'name':
            enhanced_classes.sort(key=lambda x: x['name'].lower(), reverse=reverse_order)
        elif sort_by == 'students':
            enhanced_classes.sort(key=lambda x: x['metrics']['total_students'], reverse=reverse_order)
        elif sort_by == 'performance':
            enhanced_classes.sort(key=lambda x: x['metrics']['avg_performance'], reverse=reverse_order)
        elif sort_by == 'activity':
            enhanced_classes.sort(key=lambda x: x['metrics']['activity_rate'], reverse=reverse_order)
        else:  # default: created_at
            enhanced_classes.sort(key=lambda x: x['created_at'], reverse=reverse_order)
        
        # Pagination
        total_classes = len(enhanced_classes)
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        paginated_classes = enhanced_classes[start_index:end_index]
        
        # Summary statistics
        if enhanced_classes:
            summary_stats = {
                'total_classes': total_classes,
                'active_classes': sum(1 for cls in enhanced_classes if cls['is_active']),
                'total_students': sum(cls['metrics']['total_students'] for cls in enhanced_classes),
                'avg_class_size': round(
                    sum(cls['metrics']['total_students'] for cls in enhanced_classes) / len(enhanced_classes), 1
                ),
                'overall_performance': round(
                    sum(cls['metrics']['avg_performance'] for cls in enhanced_classes) / len(enhanced_classes), 1
                ),
                'high_performing_classes': sum(
                    1 for cls in enhanced_classes if cls['metrics']['performance_level'] == 'high'
                ),
                'classes_needing_attention': sum(
                    1 for cls in enhanced_classes if cls['status_indicators']['needs_attention']
                )
            }
        else:
            summary_stats = {
                'total_classes': 0,
                'active_classes': 0,
                'total_students': 0,
                'avg_class_size': 0,
                'overall_performance': 0,
                'high_performing_classes': 0,
                'classes_needing_attention': 0
            }
        
        return Response({
            'classes': paginated_classes,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_pages': (total_classes + page_size - 1) // page_size,
                'total_items': total_classes,
                'has_next': end_index < total_classes,
                'has_previous': page > 1
            },
            'filters_applied': {
                'search': search,
                'subject': subject_filter,
                'status': status_filter,
                'performance': performance_filter,
                'sort_by': sort_by,
                'sort_order': sort_order
            },
            'summary_stats': summary_stats
        })
        
    except Exception as e:
        logger.error(f"Enhanced class list error: {str(e)}")
        return Response(
            {'error': 'Failed to load class list', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsTeacher])
def bulk_class_operations(request):
    """
    Perform bulk operations on multiple classes
    Operations: activate, deactivate, delete, duplicate, archive
    """
    teacher = request.user
    
    class_ids = request.data.get('class_ids', [])
    operation = request.data.get('operation')
    operation_data = request.data.get('operation_data', {})
    
    if not class_ids or not operation:
        return Response(
            {'error': 'class_ids and operation are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Verify teacher owns all classes
        classes = ClassRoom.objects.filter(
            id__in=class_ids,
            teacher=teacher
        )
        
        if len(classes) != len(class_ids):
            return Response(
                {'error': 'Some classes not found or access denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        results = []
        
        with transaction.atomic():
            if operation == 'activate':
                updated = classes.update(is_active=True)
                results.append(f'Activated {updated} classes')
                
            elif operation == 'deactivate':
                updated = classes.update(is_active=False)
                results.append(f'Deactivated {updated} classes')
                
            elif operation == 'delete':
                # Check if any class has active students
                for classroom in classes:
                    active_students = ClassEnrollment.objects.filter(
                        classroom=classroom,
                        status='active'
                    ).count()
                    
                    if active_students > 0:
                        return Response(
                            {'error': f'Cannot delete class "{classroom.name}" with active students'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                
                deleted_count = classes.count()
                classes.delete()
                results.append(f'Deleted {deleted_count} classes')
                
            elif operation == 'duplicate':
                for classroom in classes:
                    new_classroom = ClassRoom.objects.create(
                        name=f"{classroom.name} (Copy)",
                        description=classroom.description,
                        class_type=classroom.class_type,
                        teacher=teacher,
                        subject=classroom.subject,
                        max_students=classroom.max_students,
                        meeting_schedule=classroom.meeting_schedule,
                        timezone=classroom.timezone,
                        is_active=False  # Start inactive
                    )
                    
                    # Copy courses association
                    new_classroom.courses.set(classroom.courses.all())
                    
                    results.append(f'Duplicated class: {classroom.name}')
                    
            elif operation == 'archive':
                # Custom archive operation - deactivate and move end_date
                archive_date = timezone.now().date()
                updated = classes.update(
                    is_active=False,
                    end_date=archive_date
                )
                results.append(f'Archived {updated} classes')
                
            elif operation == 'bulk_update':
                # Bulk update operation with custom data
                update_fields = operation_data.get('update_fields', {})
                
                if 'max_students' in update_fields:
                    classes.update(max_students=update_fields['max_students'])
                    results.append(f'Updated max_students for {len(classes)} classes')
                
                if 'subject_id' in update_fields:
                    classes.update(subject_id=update_fields['subject_id'])
                    results.append(f'Updated subject for {len(classes)} classes')
                
                if 'class_type' in update_fields:
                    classes.update(class_type=update_fields['class_type'])
                    results.append(f'Updated class_type for {len(classes)} classes')
            
            else:
                return Response(
                    {'error': f'Unknown operation: {operation}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response({
            'success': True,
            'operation': operation,
            'results': results,
            'affected_classes': len(class_ids)
        })
        
    except Exception as e:
        logger.error(f"Bulk class operation error: {str(e)}")
        return Response(
            {'error': 'Bulk operation failed', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsTeacher])
def bulk_student_operations(request):
    """
    Perform bulk operations on students across multiple classes
    Operations: enroll, unenroll, move_class, send_message, export_data
    """
    teacher = request.user
    
    student_ids = request.data.get('student_ids', [])
    class_ids = request.data.get('class_ids', [])
    operation = request.data.get('operation')
    operation_data = request.data.get('operation_data', {})
    
    if not student_ids or not operation:
        return Response(
            {'error': 'student_ids and operation are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Verify teacher has access to all specified classes
        if class_ids:
            teacher_classes = ClassRoom.objects.filter(
                id__in=class_ids,
                teacher=teacher
            )
            
            if len(teacher_classes) != len(class_ids):
                return Response(
                    {'error': 'Access denied to some classes'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Verify students exist
        students = User.objects.filter(
            id__in=student_ids,
            role='student'
        )
        
        if len(students) != len(student_ids):
            return Response(
                {'error': 'Some students not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        results = []
        
        with transaction.atomic():
            if operation == 'enroll':
                target_class_id = operation_data.get('target_class_id')
                if not target_class_id:
                    return Response(
                        {'error': 'target_class_id required for enroll operation'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                target_class = ClassRoom.objects.get(
                    id=target_class_id,
                    teacher=teacher
                )
                
                enrolled_count = 0
                for student in students:
                    enrollment, created = ClassEnrollment.objects.get_or_create(
                        classroom=target_class,
                        student=student,
                        defaults={'status': 'active'}
                    )
                    
                    if created:
                        enrolled_count += 1
                    elif enrollment.status != 'active':
                        enrollment.status = 'active'
                        enrollment.save()
                        enrolled_count += 1
                
                results.append(f'Enrolled {enrolled_count} students in {target_class.name}')
                
            elif operation == 'unenroll':
                if not class_ids:
                    return Response(
                        {'error': 'class_ids required for unenroll operation'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                unenrolled_count = ClassEnrollment.objects.filter(
                    classroom_id__in=class_ids,
                    student_id__in=student_ids,
                    status='active'
                ).update(status='completed')
                
                results.append(f'Unenrolled {unenrolled_count} student-class pairs')
                
            elif operation == 'move_class':
                source_class_id = operation_data.get('source_class_id')
                target_class_id = operation_data.get('target_class_id')
                
                if not source_class_id or not target_class_id:
                    return Response(
                        {'error': 'source_class_id and target_class_id required'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Verify both classes belong to teacher
                source_class = ClassRoom.objects.get(id=source_class_id, teacher=teacher)
                target_class = ClassRoom.objects.get(id=target_class_id, teacher=teacher)
                
                moved_count = 0
                for student in students:
                    # Deactivate from source
                    ClassEnrollment.objects.filter(
                        classroom=source_class,
                        student=student,
                        status='active'
                    ).update(status='completed')
                    
                    # Enroll in target
                    enrollment, created = ClassEnrollment.objects.get_or_create(
                        classroom=target_class,
                        student=student,
                        defaults={'status': 'active'}
                    )
                    
                    if created or enrollment.status != 'active':
                        if not created:
                            enrollment.status = 'active'
                            enrollment.save()
                        moved_count += 1
                
                results.append(f'Moved {moved_count} students from {source_class.name} to {target_class.name}')
                
            elif operation == 'export_data':
                # Export student data for specified classes
                export_data = _export_student_data(students, class_ids, teacher)
                
                return Response({
                    'success': True,
                    'operation': operation,
                    'export_data': export_data,
                    'total_students': len(students)
                })
                
            elif operation == 'send_message':
                # This would integrate with a messaging system
                message_content = operation_data.get('message', '')
                if not message_content:
                    return Response(
                        {'error': 'message content required'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # For now, just log the message (in real implementation, send via email/notification)
                logger.info(f"Message to {len(students)} students: {message_content}")
                results.append(f'Message queued for {len(students)} students')
                
            else:
                return Response(
                    {'error': f'Unknown operation: {operation}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response({
            'success': True,
            'operation': operation,
            'results': results,
            'affected_students': len(student_ids)
        })
        
    except Exception as e:
        logger.error(f"Bulk student operation error: {str(e)}")
        return Response(
            {'error': 'Bulk student operation failed', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def _export_student_data(students, class_ids, teacher):
    """Export comprehensive student data for analysis"""
    export_data = []
    
    for student in students:
        # Get enrollments in teacher's classes
        enrollments = ClassEnrollment.objects.filter(
            student=student,
            classroom__teacher=teacher
        )
        
        if class_ids:
            enrollments = enrollments.filter(classroom_id__in=class_ids)
        
        # Get performance data
        quiz_results = QuizResult.objects.filter(
            student=student,
            quiz__course__instructor=teacher,
            status='completed'
        )
        
        if class_ids:
            # Filter by courses associated with classes
            course_ids = ClassRoom.objects.filter(
                id__in=class_ids
            ).values_list('courses__id', flat=True)
            quiz_results = quiz_results.filter(quiz__course_id__in=course_ids)
        
        # Calculate metrics
        avg_score = quiz_results.aggregate(Avg('score'))['score__avg'] or 0
        total_quizzes = quiz_results.count()
        
        # Get latest activity
        latest_progress = StudentProgress.objects.filter(
            student=student
        ).order_by('-last_accessed').first()
        
        student_data = {
            'student_id': student.id,
            'email': student.email,
            'first_name': student.first_name or '',
            'last_name': student.last_name or '',
            'date_joined': student.date_joined.isoformat(),
            'classes_enrolled': enrollments.count(),
            'total_quizzes_taken': total_quizzes,
            'average_score': round(avg_score, 1),
            'last_activity': latest_progress.last_accessed.isoformat() if latest_progress else None,
            'enrollment_details': [
                {
                    'class_name': enrollment.classroom.name,
                    'enrolled_at': enrollment.enrolled_at.isoformat(),
                    'status': enrollment.status,
                    'overall_grade': enrollment.overall_grade
                }
                for enrollment in enrollments
            ]
        }
        
        export_data.append(student_data)
    
    return export_data

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsTeacher])
def class_analytics_summary(request):
    """
    Get comprehensive analytics summary across all teacher's classes
    """
    teacher = request.user
    
    try:
        # Get all teacher's classes
        classes = ClassRoom.objects.filter(teacher=teacher)
        
        # Time range filter
        time_range = request.query_params.get('time_range', '30')  # days
        end_date = timezone.now()
        start_date = end_date - timedelta(days=int(time_range))
        
        analytics_summary = {
            'overview': {},
            'performance_distribution': {},
            'engagement_metrics': {},
            'class_comparisons': [],
            'recommendations': []
        }
        
        # Overall metrics
        total_students = ClassEnrollment.objects.filter(
            classroom__teacher=teacher,
            status='active'
        ).values('student').distinct().count()
        
        total_courses = classes.values('courses').distinct().count()
        
        # Performance metrics
        all_quiz_results = QuizResult.objects.filter(
            quiz__course__instructor=teacher,
            status='completed',
            created_at__gte=start_date
        )
        
        avg_performance = all_quiz_results.aggregate(Avg('score'))['score__avg'] or 0
        total_quiz_attempts = all_quiz_results.count()
        
        # Engagement metrics
        active_students = StudentProgress.objects.filter(
            course__instructor=teacher,
            last_accessed__gte=start_date
        ).values('student').distinct().count()
        
        engagement_rate = (active_students / total_students * 100) if total_students > 0 else 0
        
        analytics_summary['overview'] = {
            'total_classes': classes.count(),
            'active_classes': classes.filter(is_active=True).count(),
            'total_students': total_students,
            'total_courses': total_courses,
            'avg_performance': round(avg_performance, 1),
            'total_quiz_attempts': total_quiz_attempts,
            'active_students': active_students,
            'engagement_rate': round(engagement_rate, 1)
        }
        
        # Performance distribution
        performance_ranges = {
            'excellent': all_quiz_results.filter(score__gte=90).count(),
            'good': all_quiz_results.filter(score__gte=80, score__lt=90).count(),
            'average': all_quiz_results.filter(score__gte=70, score__lt=80).count(),
            'below_average': all_quiz_results.filter(score__gte=60, score__lt=70).count(),
            'poor': all_quiz_results.filter(score__lt=60).count()
        }
        
        analytics_summary['performance_distribution'] = {
            'ranges': performance_ranges,
            'percentages': {
                level: round((count / total_quiz_attempts * 100), 1) if total_quiz_attempts > 0 else 0
                for level, count in performance_ranges.items()
            }
        }
        
        # Class-by-class comparison
        for classroom in classes:
            class_students = ClassEnrollment.objects.filter(
                classroom=classroom,
                status='active'
            ).values_list('student_id', flat=True)
            
            class_results = all_quiz_results.filter(student_id__in=class_students)
            class_avg = class_results.aggregate(Avg('score'))['score__avg'] or 0
            
            analytics_summary['class_comparisons'].append({
                'class_id': classroom.id,
                'class_name': classroom.name,
                'student_count': len(class_students),
                'avg_performance': round(class_avg, 1),
                'total_attempts': class_results.count(),
                'status': classroom.is_active
            })
        
        # Generate recommendations
        recommendations = []
        
        if avg_performance < 70:
            recommendations.append({
                'type': 'performance',
                'priority': 'high',
                'title': 'Overall Performance Needs Attention',
                'message': f'Average performance of {avg_performance:.1f}% indicates need for intervention'
            })
        
        if engagement_rate < 60:
            recommendations.append({
                'type': 'engagement',
                'priority': 'medium',
                'title': 'Student Engagement is Low',
                'message': f'Only {engagement_rate:.1f}% of students active recently'
            })
        
        low_performing_classes = [
            cls for cls in analytics_summary['class_comparisons']
            if cls['avg_performance'] < 65 and cls['total_attempts'] > 0
        ]
        
        if low_performing_classes:
            recommendations.append({
                'type': 'class_attention',
                'priority': 'high',
                'title': f'{len(low_performing_classes)} Classes Need Attention',
                'message': 'Consider additional support or AI-generated practice quizzes'
            })
        
        analytics_summary['recommendations'] = recommendations
        
        return Response(analytics_summary)
        
    except Exception as e:
        logger.error(f"Class analytics summary error: {str(e)}")
        return Response(
            {'error': 'Failed to generate analytics summary', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsTeacher])
def create_class_with_template(request):
    """
    Create a new class using predefined templates
    """
    teacher = request.user
    
    template_type = request.data.get('template_type')
    class_data = request.data.get('class_data', {})
    
    if not template_type:
        return Response(
            {'error': 'template_type is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Template configurations
        templates = {
            'beginner_class': {
                'class_type': 'regular',
                'max_students': 25,
                'meeting_schedule': {
                    'frequency': 'weekly',
                    'duration': 60,
                    'days': ['monday', 'wednesday', 'friday']
                },
                'default_settings': {
                    'auto_enroll': False,
                    'grade_tracking': True,
                    'ai_recommendations': True
                }
            },
            'advanced_class': {
                'class_type': 'advanced',
                'max_students': 15,
                'meeting_schedule': {
                    'frequency': 'bi-weekly',
                    'duration': 90,
                    'days': ['tuesday', 'thursday']
                },
                'default_settings': {
                    'auto_enroll': False,
                    'grade_tracking': True,
                    'ai_recommendations': True,
                    'peer_review': True
                }
            },
            'remedial_class': {
                'class_type': 'remedial',
                'max_students': 12,
                'meeting_schedule': {
                    'frequency': 'daily',
                    'duration': 45,
                    'days': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
                },
                'default_settings': {
                    'auto_enroll': False,
                    'grade_tracking': True,
                    'ai_recommendations': True,
                    'extra_support': True
                }
            },
            'honors_class': {
                'class_type': 'honors',
                'max_students': 20,
                'meeting_schedule': {
                    'frequency': 'weekly',
                    'duration': 75,
                    'days': ['monday', 'wednesday']
                },
                'default_settings': {
                    'auto_enroll': False,
                    'grade_tracking': True,
                    'ai_recommendations': True,
                    'advanced_analytics': True
                }
            }
        }
        
        if template_type not in templates:
            return Response(
                {'error': f'Unknown template type: {template_type}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        template = templates[template_type]
        
        # Create class with template data
        classroom_data = {
            'name': class_data.get('name', f'New {template_type.replace("_", " ").title()}'),
            'description': class_data.get('description', f'Class created from {template_type} template'),
            'class_type': template['class_type'],
            'teacher': teacher,
            'max_students': class_data.get('max_students', template['max_students']),
            'meeting_schedule': class_data.get('meeting_schedule', template['meeting_schedule']),
            'is_active': class_data.get('is_active', True)
        }
        
        # Handle subject
        subject_id = class_data.get('subject_id')
        if subject_id:
            from apps.courses.models import Subject
            classroom_data['subject'] = Subject.objects.get(id=subject_id)
        
        # Create the classroom
        with transaction.atomic():
            classroom = ClassRoom.objects.create(**classroom_data)
            
            # Generate unique class code
            classroom.generate_class_code()
            
            # Add courses if specified
            course_ids = class_data.get('course_ids', [])
            if course_ids:
                courses = Course.objects.filter(
                    id__in=course_ids,
                    instructor=teacher
                )
                classroom.courses.set(courses)
        
        # Serialize response
        serializer = ClassRoomSerializer(classroom)
        
        return Response({
            'success': True,
            'classroom': serializer.data,
            'template_applied': template_type,
            'template_settings': template['default_settings']
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Template class creation error: {str(e)}")
        return Response(
            {'error': 'Failed to create class from template', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
