from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q, Avg, Count, Sum, F, Max
from django.utils import timezone
from datetime import datetime, timedelta
import logging

from .models import (
    StudentProgress, QuizResult, 
    LearningGoal, PerformanceAnalytics, Notification
)
from apps.users.models import Goal, MilestoneReward
from .serializers import (
    StudentProgressSerializer, QuizResultSerializer, 
    LearningGoalSerializer, PerformanceAnalyticsSerializer,
    StudentProgressSummarySerializer, NotificationSerializer
)
from apps.courses.models import Course, Lesson, Quiz, Subject
from rest_framework.permissions import BasePermission

# Custom permissions for AI-only system
class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(request.user, 'role', None) == 'student'

class IsStudentOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            getattr(request.user, 'role', None) == 'student' or 
            request.user.is_staff or 
            getattr(request.user, 'role', None) == 'admin'
        )

logger = logging.getLogger(__name__)
User = get_user_model()


class StudentProgressListView(generics.ListCreateAPIView):
    """List and create student progress records (AI-only system)"""
    serializer_class = StudentProgressSerializer
    permission_classes = [IsStudentOrAdmin]
    
    def get_queryset(self):
        user = self.request.user
        queryset = StudentProgress.objects.select_related(
            'student', 'course', 'lesson'
        ).prefetch_related('course__subject')
        
        # In AI-only system, students see only their own progress
        # Admins can see all progress
        if user.role == 'student':
            queryset = queryset.filter(student=user)
        elif not (user.is_staff or user.role == 'admin'):
            # If not admin or student, return empty queryset
            return StudentProgress.objects.none()
        
        # Additional filters
        course_id = self.request.query_params.get('course_id')
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        
        activity_type = self.request.query_params.get('activity_type')
        if activity_type:
            queryset = queryset.filter(activity_type=activity_type)
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-last_accessed')
    
    def perform_create(self, serializer):
        """Auto-assign student in AI system"""
        if self.request.user.role == 'student':
            serializer.save(student=self.request.user)
        else:
            serializer.save()


class StudentProgressDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete student progress (AI-only system)"""
    serializer_class = StudentProgressSerializer
    permission_classes = [IsStudentOrAdmin]
    
    def get_queryset(self):
        user = self.request.user
        queryset = StudentProgress.objects.select_related(
            'student', 'course', 'lesson'
        )
        
        if user.role == 'student':
            return queryset.filter(student=user)
        elif user.is_staff or user.role == 'admin':
            return queryset
        
        return StudentProgress.objects.none()


class QuizResultListView(generics.ListCreateAPIView):
    """List and create quiz results (AI-only system)"""
    serializer_class = QuizResultSerializer
    permission_classes = [IsStudentOrAdmin]
    
    def get_queryset(self):
        user = self.request.user
        queryset = QuizResult.objects.select_related(
            'student', 'quiz'
        )
        
        if user.role == 'student':
            queryset = queryset.filter(student=user)
        elif not (user.is_staff or user.role == 'admin'):
            return QuizResult.objects.none()
        
        # Filters
        quiz_id = self.request.query_params.get('quiz_id')
        if quiz_id:
            queryset = queryset.filter(quiz_id=quiz_id)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        if self.request.user.role == 'student':
            serializer.save(student=self.request.user)
        else:
            serializer.save()


class LearningGoalListView(generics.ListCreateAPIView):
    """List and create AI-guided learning goals"""
    serializer_class = LearningGoalSerializer
    permission_classes = [IsStudentOrAdmin]
    
    def get_queryset(self):
        user = self.request.user
        queryset = LearningGoal.objects.select_related('student')
        
        if user.role == 'student':
            return queryset.filter(student=user)
        elif user.is_staff or user.role == 'admin':
            return queryset
        
        return LearningGoal.objects.none()
    
    def perform_create(self, serializer):
        if self.request.user.role == 'student':
            serializer.save(student=self.request.user)
        else:
            serializer.save()


class LearningGoalDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete AI learning goals"""
    serializer_class = LearningGoalSerializer
    permission_classes = [IsStudentOrAdmin]
    
    def get_queryset(self):
        user = self.request.user
        queryset = LearningGoal.objects.select_related('student')
        
        if user.role == 'student':
            return queryset.filter(student=user)
        elif user.is_staff or user.role == 'admin':
            return queryset
        
        return LearningGoal.objects.none()


@api_view(['GET'])
@permission_classes([IsStudentOrAdmin])
def ai_recommended_courses(request):
    """Get AI-recommended courses for the current student"""
    try:
        user = request.user
        if user.role != 'student' and not user.is_staff and user.role != 'admin':
            return Response(
                {'error': 'Only students can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get query parameters
        subject_id = request.query_params.get('subject_id')
        difficulty = request.query_params.get('difficulty')
        limit = int(request.query_params.get('limit', 5))
        
        # Base queryset
        courses = Course.objects.all()
        
        # Apply filters
        if subject_id:
            courses = courses.filter(subject_id=subject_id)
            
        if difficulty:
            courses = courses.filter(difficulty_level=difficulty)
            
        # Get student's learning history
        if user.role == 'student':
            completed_courses = StudentProgress.objects.filter(
                student=user,
                status='completed',
                activity_type='course'
            ).values_list('course_id', flat=True)
            
            # Exclude completed courses
            courses = courses.exclude(id__in=completed_courses)
            
            # Order by AI recommendations (simplified example)
            # In a real system, this would use more sophisticated ML techniques
            courses = courses.annotate(
                relevance_score=Sum('student_ratings')
            ).order_by('-relevance_score')[:limit]
        else:
            # For admins, just return top courses
            courses = courses.order_by('-student_ratings')[:limit]
        
        # Simplified response - in a real system would use proper serializers
        response_data = [{
            'id': course.id,
            'title': course.title,
            'description': course.description,
            'ai_tutor_name': course.ai_tutor_name,
            'subject': course.subject.name if course.subject else None,
            'difficulty_level': course.difficulty_level,
            'estimated_duration': course.estimated_duration,
            'rating': course.student_ratings,
            'match_score': 'High'  # Would be calculated by AI
        } for course in courses]
        
        return Response({
            'recommended_courses': response_data,
            'count': len(response_data)
        })
    
    except Exception as e:
        logger.error(f"Error in AI recommended courses: {str(e)}")
        return Response(
            {'error': 'Failed to get AI recommendations', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        classroom = ClassRoom.objects.get(
            id=classroom_id,
            teacher=request.user
        )
    except ClassRoom.DoesNotExist:
        return Response(
            {'error': 'Classroom not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)
    
    # Student Stats
    enrollments = ClassEnrollment.objects.filter(
        classroom=classroom,
        status='active'
    ).select_related('student')
    
    total_students = enrollments.count()
    active_students = enrollments.filter(
        last_activity__gte=timezone.now() - timedelta(days=7)
    ).count()
    
    # Average attendance (placeholder - would track actual attendance)
    average_attendance = enrollments.aggregate(
        Avg('attendance_rate')
    )['attendance_rate__avg'] or 0
    
    # Performance Overview
    student_ids = enrollments.values_list('student_id', flat=True)
    quiz_results = QuizResult.objects.filter(
        student_id__in=student_ids,
        status='completed'
    )
    
    class_average_score = quiz_results.aggregate(
        Avg('score')
    )['score__avg'] or 0
    
    # Top performers (top 3)
    top_performers_data = quiz_results.values(
        'student__email', 'student__first_name', 'student__last_name'
    ).annotate(
        avg_score=Avg('score'),
        total_quizzes=Count('id')
    ).order_by('-avg_score')[:3]
    
    top_performers = []
    for performer in top_performers_data:
        name = f"{performer.get('student__first_name', '')} {performer.get('student__last_name', '')}".strip()
        top_performers.append({
            'name': name or performer['student__email'],
            'email': performer['student__email'],
            'average_score': round(performer['avg_score'], 2),
            'total_quizzes': performer['total_quizzes']
        })
    
    # Struggling students (bottom performers with score < 70)
    struggling_data = quiz_results.values(
        'student__email', 'student__first_name', 'student__last_name'
    ).annotate(
        avg_score=Avg('score'),
        total_quizzes=Count('id')
    ).filter(avg_score__lt=70).order_by('avg_score')[:5]
    
    struggling_students = []
    for student in struggling_data:
        name = f"{student.get('student__first_name', '')} {student.get('student__last_name', '')}".strip()
        struggling_students.append({
            'name': name or student['student__email'],
            'email': student['student__email'],
            'average_score': round(student['avg_score'], 2),
            'total_quizzes': student['total_quizzes']
        })
    
    # Course Progress
    assigned_courses = classroom.courses.count()
    
    # Calculate average course completion
    course_completions = StudentProgress.objects.filter(
        student_id__in=student_ids,
        activity_type='course_complete',
        status='completed'
    ).count()
    
    total_course_enrollments = enrollments.count() * assigned_courses
    average_course_completion = (
        (course_completions / total_course_enrollments * 100)
        if total_course_enrollments > 0 else 0
    )
    
    # Engagement Metrics
    total_study_time = StudentProgress.objects.filter(
        student_id__in=student_ids
    ).aggregate(Sum('time_spent'))['time_spent__sum'] or 0
    
    # Login frequency (last 30 days)
    login_counts = StudentProgress.objects.filter(
        student_id__in=student_ids,
        last_accessed__gte=thirty_days_ago
    ).values('student').annotate(
        login_days=Count('last_accessed__date', distinct=True)
    ).aggregate(Avg('login_days'))['login_days__avg'] or 0
    
    # Participation rate
    participation_scores = enrollments.aggregate(
        Avg('participation_score')
    )['participation_score__avg'] or 0
    
    # Recent Activity
    recent_submissions = QuizResult.objects.filter(
        student_id__in=student_ids,
        created_at__gte=timezone.now() - timedelta(days=7)
    ).count()
    
    pending_reviews = QuizResult.objects.filter(
        student_id__in=student_ids,
        status='submitted'
    ).count()
    
    # Performance Trends (placeholder)
    performance_trends = {
        'weekly_average': round(class_average_score, 2),
        'trend_direction': 'stable',  # Would calculate actual trend
        'participation_trend': 'improving'
    }
    
    # Intervention Needed
    intervention_needed = []
    for student in struggling_students[:3]:  # Top 3 struggling students
        intervention_needed.append(f"{student['name']} needs additional support")
    
    # Success Factors
    success_factors = [
        "Regular quiz participation",
        "Consistent daily study habits", 
        "Active engagement with course materials"
    ]
    
    analytics_data = {
        'classroom_id': classroom.id,
        'classroom_name': classroom.name,
        'teacher_name': classroom.teacher.get_full_name() or classroom.teacher.email,
        'total_students': total_students,
        'active_students': active_students,
        'average_attendance': round(average_attendance, 2),
        'class_average_score': round(class_average_score, 2),
        'top_performers': top_performers,
        'struggling_students': struggling_students,
        'assigned_courses': assigned_courses,
        'average_course_completion': round(average_course_completion, 2),
        'total_study_time': total_study_time,
        'average_login_frequency': round(login_counts, 2),
        'participation_rate': round(participation_scores, 2),
        'recent_submissions': recent_submissions,
        'pending_reviews': pending_reviews,
        'performance_trends': performance_trends,
        'intervention_needed': intervention_needed,
        'success_factors': success_factors
    }
    
    serializer = ClassroomAnalyticsSerializer(data=analytics_data)
    serializer.is_valid(raise_exception=True)
    
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def update_progress(request):
    """Update student progress for activities"""
    student = request.user
    data = request.data
    
    required_fields = ['course_id', 'activity_type']
    for field in required_fields:
        if field not in data:
            return Response(
                {'error': f'{field} is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    try:
        course = Course.objects.get(id=data['course_id'])
    except Course.DoesNotExist:
        return Response(
            {'error': 'Course not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Get or create progress record
    progress, created = StudentProgress.objects.get_or_create(
        student=student,
        course=course,
        activity_type=data['activity_type'],
        lesson_id=data.get('lesson_id'),
        defaults={
            'status': 'not_started',
            'started_at': timezone.now()
        }
    )
    
    # Update progress
    if data.get('status'):
        progress.status = data['status']
    
    if data.get('completion_percentage') is not None:
        progress.completion_percentage = data['completion_percentage']
    
    if data.get('score') is not None:
        progress.score = data['score']
        if progress.best_score is None or data['score'] > progress.best_score:
            progress.best_score = data['score']
    
    if data.get('time_spent') is not None:
        progress.time_spent += data['time_spent']
    
    if progress.status == 'completed' and not progress.completed_at:
        progress.completed_at = timezone.now()
        progress.completion_percentage = 100.0
    
    progress.save()
    
    return Response(
        StudentProgressSerializer(progress).data,
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([IsStudent])
def student_analytics(request):
    """Get comprehensive student analytics including goals and achievements"""
    try:
        student = request.user
        
        # Overall Statistics
        total_study_time = StudentProgress.objects.filter(
            student=student
        ).aggregate(Sum('time_spent'))['time_spent__sum'] or 0
        
        # Course Progress
        course_progress = StudentProgress.objects.filter(
            student=student,
            activity_type='course_complete'
        )
        
        completed_courses = course_progress.filter(status='completed').count()
        total_courses = course_progress.count()
        
        # Quiz Performance
        quiz_results = QuizResult.objects.filter(
            student=student,
            status='completed'
        )
        
        average_score = quiz_results.aggregate(Avg('score'))['score__avg'] or 0
        
        # Streak calculation (simplified)
        recent_activity = StudentProgress.objects.filter(
            student=student,
            last_accessed__gte=timezone.now() - timedelta(days=30)
        ).values('last_accessed__date').distinct().count()
        
        streak_days = min(recent_activity, 30)  # Simplified streak calculation
        
        overall_stats = {
            'total_study_time': total_study_time,
            'average_score': round(average_score, 1),
            'courses_completed': completed_courses,
            'streak_days': streak_days,
            'level': 'Intermediate Learner' if average_score >= 75 else 'Beginner Learner'
        }
        
        # Mock Analytics Data (to match frontend expectations)
        analytics_data = {
            'weekly_activity': [2, 4, 6, 8, 5, 9, 7],  # Hours per day
            'subject_performance': {
                'Mathematics': min(average_score + 5, 100),
                'Computer Science': average_score,
                'Physics': max(average_score - 10, 0),
                'English': min(average_score + 8, 100)
            },
            'learning_trend': [65, 68, 72, 75, 78, min(average_score, 100), min(average_score + 2, 100)]
        }
        
        # Get Goals from users app
        user_goals = Goal.objects.filter(user=student, status='active')
        goals_data = []
        for goal in user_goals:
            goals_data.append({
                'id': goal.id,
                'title': goal.title,
                'progress': goal.progress_percentage,
                'target_date': goal.target_date.strftime('%Y-%m-%d') if goal.target_date else None,
                'status': goal.status
            })
        
        # Get Achievements from users app
        user_achievements = MilestoneReward.objects.filter(
            user=student, 
            is_claimed=True
        ).order_by('-created_at')[:5]
        
        achievements_data = []
        for achievement in user_achievements:
            achievements_data.append({
                'id': achievement.id,
                'title': achievement.title,
                'description': achievement.description,
                'earned_date': achievement.created_at.strftime('%Y-%m-%d'),
                'badge': achievement.icon
            })
        
        # Course Progress Data
        enrolled_courses = StudentProgress.objects.filter(
            student=student
        ).values('course').distinct()
        
        courses_data = []
        for course_progress in enrolled_courses:
            course_id = course_progress['course']
            try:
                course = Course.objects.get(id=course_id)
                progress_records = StudentProgress.objects.filter(
                    student=student,
                    course=course
                )
                
                total_progress = progress_records.aggregate(
                    avg_progress=Avg('completion_percentage')
                )['avg_progress'] or 0
                
                total_time = progress_records.aggregate(
                    total_time=Sum('time_spent')
                )['total_time'] or 0
                
                completed_lessons = progress_records.filter(
                    activity_type='lesson_complete',
                    status='completed'
                ).count()
                
                total_lessons = course.lessons.count() if hasattr(course, 'lessons') else 10
                
                courses_data.append({
                    'id': course.id,
                    'title': course.title,
                    'provider': 'AI Study Platform',
                    'progress': round(total_progress, 1),
                    'time_spent': total_time // 60,  # Convert to hours
                    'completed_lessons': completed_lessons,
                    'total_lessons': total_lessons,
                    'certificate_progress': round(total_progress, 1),
                    'last_activity': progress_records.aggregate(
                        last_activity=Max('last_accessed')
                    )['last_activity']
                })
            except Course.DoesNotExist:
                continue
        
        response_data = {
            'overall': overall_stats,
            'analytics': analytics_data,
            'goals': goals_data,
            'achievements': achievements_data
        }
        
        return Response(response_data)
        
    except Exception as e:
        logger.error(f"Error in student analytics: {str(e)}")
        return Response(
            {'error': 'Failed to get analytics data', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsStudent])
def student_course_progress(request):
    """Get student course progress data using real enrollments"""
    try:
        student = request.user
        
        # Since courses are external online courses, we'll work with student progress data
        # and create course-like data from progress tracking
        
        # Get unique courses from progress tracking (external courses)
        course_progress = StudentProgress.objects.filter(
            student=student
        ).values('course').distinct()
        
        courses_data = []
        for course_data in course_progress:
            course_id = course_data['course']
            
            # Get progress records for this course
            progress_records = StudentProgress.objects.filter(
                student=student,
                course_id=course_id
            )
            
            if not progress_records.exists():
                continue
                
            # Get course info from first progress record
            first_record = progress_records.first()
            course_title = first_record.metadata.get('course_title', f'Course {course_id}') if first_record.metadata else f'Course {course_id}'
            
            # Calculate progress metrics
            total_progress = progress_records.aggregate(
                avg_progress=Avg('completion_percentage')
            )['avg_progress'] or 0
            
            total_time = progress_records.aggregate(
                total_time=Sum('time_spent')
            )['total_time'] or 0
            
            # Count different types of activities
            completed_lessons = progress_records.filter(
                activity_type='lesson_complete',
                status='completed'
            ).count()
            
            total_lessons = progress_records.filter(
                activity_type__in=['lesson_start', 'lesson_complete']
            ).values('lesson_id').distinct().count() or 1
            
            # Get last activity
            last_activity = progress_records.aggregate(
                last_activity=Max('last_accessed')
            )['last_activity']
            
            # Check if course is completed
            is_completed = progress_records.filter(
                activity_type='course_complete',
                status='completed'
            ).exists()
            
            courses_data.append({
                'id': course_id,
                'title': course_title,
                'provider': first_record.metadata.get('provider', 'Online Learning Platform') if first_record.metadata else 'Online Learning Platform',
                'instructor': first_record.metadata.get('instructor', 'Course Instructor') if first_record.metadata else 'Course Instructor',
                'progress': round(total_progress, 1),
                'time_spent': total_time // 60,  # Convert to hours
                'completed_lessons': completed_lessons,
                'total_lessons': total_lessons,
                'certificate_progress': round(total_progress, 1),
                'last_activity': last_activity.strftime('%Y-%m-%d') if last_activity else None,
                'is_completed': is_completed,
                'subject': first_record.metadata.get('subject', 'General') if first_record.metadata else 'General',
            })
        
        return Response(courses_data)
        
    except Exception as e:
        logger.error(f"Error in student course progress: {str(e)}")
        return Response(
            {'error': 'Failed to get course progress', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
