from rest_framework import viewsets, permissions, status, generics
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.contrib.auth import get_user_model
from django.db.models import Q, Avg, Sum
from django.shortcuts import get_object_or_404
from django.db import models
from django.utils import timezone
import logging
from .models import Note, StudentProfile
from apps.progress.models import Notification
from .serializers import (
    UserSerializer, NoteSerializer, UserProfileSerializer, 
    UserUpdateSerializer, StudentProfileSerializer
)
from apps.progress.serializers import NotificationSerializer

User = get_user_model()
logger = logging.getLogger(__name__)

class UserViewSet(viewsets.ModelViewSet):
    """
    Comprehensive ViewSet for managing users with full CRUD operations
    """
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'retrieve' or self.action == 'profile':
            return UserProfileSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer
    
    def get_queryset(self):
        """
        Return queryset based on user permissions and filters
        """
        queryset = User.objects.select_related('student_profile')
        
        # Admin users can see all users
        if self.request.user.is_staff or self.request.user.role == 'admin':
            # Apply search filters for admin
            search = self.request.query_params.get('search', None)
            role_filter = self.request.query_params.get('role', None)
            
            if search:
                queryset = queryset.filter(
                    Q(first_name__icontains=search) |
                    Q(last_name__icontains=search) |
                    Q(email__icontains=search) |
                    Q(username__icontains=search)
                )
            
            if role_filter:
                queryset = queryset.filter(role=role_filter)
                
            return queryset
        
        # Only students and admins exist in AI system
        
        # Students can only see themselves
        else:
            return queryset.filter(id=self.request.user.id)
    
    @action(detail=False, methods=['get', 'put', 'patch'], url_path='profile')
    def profile(self, request):
        """
        Get or update current user's profile
        """
        user = request.user
        
        if request.method == 'GET':
            serializer = UserProfileSerializer(user)
            return Response(serializer.data)
        
        elif request.method in ['PUT', 'PATCH']:
            serializer = UserUpdateSerializer(
                user, 
                data=request.data, 
                partial=request.method == 'PATCH'
            )
            if serializer.is_valid():
                serializer.save()
                # Return complete profile data
                profile_serializer = UserProfileSerializer(user)
                return Response(profile_serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['delete'], url_path='delete-account')
    def delete_account(self, request):
        """
        Delete current user's account permanently
        """
        user = request.user
        
        # Additional validation
        if not user or not user.is_authenticated:
            return Response({
                'error': 'Authentication required',
                'detail': 'You must be logged in to delete your account'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Get password from request data
        password = request.data.get('password')
        if not password:
            return Response({
                'error': 'Password required',
                'detail': 'You must provide your password to delete your account'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify password
        if not user.check_password(password):
            return Response({
                'error': 'Invalid password',
                'detail': 'The password you provided is incorrect'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user_id = user.id
            user_email = user.email
            logger.info(f"Attempting to delete user account - ID: {user_id}, Email: {user_email}")
            
            # Clean up related data manually to avoid constraint errors
            try:
                # Import models for cleanup from various apps
                from .models import Goal, MilestoneReward, Note, SavedChatHistory, DailyQuoteAssignment, DocumentSummary
                
                # Delete related data from other apps first (with error handling)
                try:
                    # Authentication app
                    try:
                        from apps.authentication.models import AuthToken, LoginHistory
                        AuthToken.objects.filter(user=user).delete()
                        LoginHistory.objects.filter(user=user).delete()
                    except Exception as auth_error:
                        logger.warning(f"Could not delete authentication data: {str(auth_error)}")
                    
                    # Chatbot app
                    try:
                        from apps.chatbot.models import ChatSession
                        ChatSession.objects.filter(user=user).delete()
                    except Exception as chatbot_error:
                        logger.warning(f"Could not delete chatbot data: {str(chatbot_error)}")
                    
                    # Progress app
                    try:
                        from apps.progress.models import StudentProgress, QuizResult, LearningGoal, PerformanceAnalytics
                        StudentProgress.objects.filter(student=user).delete()
                        QuizResult.objects.filter(student=user).delete()
                        LearningGoal.objects.filter(student=user).delete()
                        PerformanceAnalytics.objects.filter(student=user).delete()
                    except Exception as progress_error:
                        logger.warning(f"Could not delete progress data: {str(progress_error)}")
                    
                    # Courses app - Skip course cleanup as models don't exist
                    # CourseEnrollment table doesn't exist, skipping course data cleanup
                    
                    logger.info(f"Deleted related data from other apps for user {user_id}")
                except Exception as other_apps_error:
                    logger.warning(f"Could not delete some data from other apps for user {user_id}: {str(other_apps_error)}")
                
                # Delete MilestoneReward first (references both user and goal)
                MilestoneReward.objects.filter(user=user).delete()
                logger.info(f"Deleted milestone rewards for user {user_id}")
                
                # Delete Goals (references user)
                Goal.objects.filter(user=user).delete()
                logger.info(f"Deleted goals for user {user_id}")
                
                # Delete users app related data
                Note.objects.filter(user=user).delete()
                SavedChatHistory.objects.filter(user=user).delete()
                DailyQuoteAssignment.objects.filter(user=user).delete()
                DocumentSummary.objects.filter(user=user).delete()
                logger.info(f"Deleted user notes and related data for user {user_id}")
                
            except Exception as cleanup_error:
                logger.warning(f"Could not delete some related data for user {user_id}: {str(cleanup_error)}")
                # Continue with deletion
            
            # Perform hard delete of user account
            user.delete()
            
            logger.info(f"Successfully deleted user account - ID: {user_id}, Email: {user_email}")
            
            return Response({
                'message': 'Account deleted successfully'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error deleting user account {user.id}: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Exception details: {e}")
            return Response({
                'error': 'Failed to delete account',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], url_path='dashboard-stats')
    def dashboard_stats(self, request):
        """
        Get dashboard statistics for current user
        """
        user = request.user
        stats = {
            'user_id': user.id,
            'full_name': user.get_full_name() or user.username,
            'email': user.email,
            'role': user.role,
            'is_verified': user.is_verified,
            'join_date': user.created_at,
            'profile_completion': self.calculate_profile_completion(user),
        }
        
        if user.role == 'student':
            # Add student-specific stats
            from apps.progress.models import StudentProgress, QuizResult
            # Calculate course statistics from progress tracking (external courses)
            progress = StudentProgress.objects.filter(student=user)
            total_courses = progress.values('course').distinct().count()
            completed_courses = progress.filter(
                activity_type='course_complete', 
                status='completed'
            ).values('course').distinct().count()
            courses_in_progress = total_courses - completed_courses
            
            quiz_results = QuizResult.objects.filter(student=user)
            progress = StudentProgress.objects.filter(student=user)
            
            stats.update({
                'total_courses': total_courses,
                'completed_courses': completed_courses,
                'courses_in_progress': courses_in_progress,
                'total_quizzes': quiz_results.count(),
                'average_score': quiz_results.aggregate(
                    avg_score=models.Avg('score')
                )['avg_score'] or 0,
                'study_time': progress.aggregate(
                    total_time=models.Sum('time_spent')
                )['total_time'] or 0,
            })
        # Only students and admins in AI system - no teacher stats needed
        
        return Response(stats)
    
    def calculate_profile_completion(self, user):
        """Calculate profile completion percentage"""
        completion = 0
        total_fields = 0
        
        # Base user fields to check (only if they exist on the model)
        fields_to_check = [
            'first_name', 'last_name', 'phone_number', 'date_of_birth', 'profile_picture'
        ]
        
        for field in fields_to_check:
            if hasattr(user, field):  # Only check if field exists
                total_fields += 1
                field_value = getattr(user, field)
                if field_value:  # Check if field has a value
                    completion += 1
        
        # Check role-specific profile
        if user.role == 'student' and hasattr(user, 'student_profile'):
            profile_fields = ['learning_style', 'learning_goals']  # Only check existing fields
            for field in profile_fields:
                if hasattr(user.student_profile, field):
                    total_fields += 1
                    field_value = getattr(user.student_profile, field, None)
                    if field_value:
                        completion += 1
                    
        # Only students have profiles in AI system
        
        return round((completion / total_fields) * 100, 1) if total_fields > 0 else 0
    
    def perform_create(self, serializer):
        """Create user with appropriate profile"""
        user = serializer.save()
        
        # Create student profile only
        if user.role == 'student':
            StudentProfile.objects.get_or_create(user=user)
    
    def destroy(self, request, *args, **kwargs):
        """Soft delete user (deactivate instead of hard delete)"""
        user = self.get_object()
        
        # Only allow admin or self to deactivate
        if request.user.is_staff or request.user == user:
            user.is_active = False
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        return Response(
            {'error': 'Permission denied'}, 
            status=status.HTTP_403_FORBIDDEN
        )

class StudentProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing student profiles
    """
    serializer_class = StudentProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return appropriate student profiles based on user role"""
        if self.request.user.role == 'admin' or self.request.user.is_staff:
            return StudentProfile.objects.select_related('user')
        # Only students and admins in AI system
        elif self.request.user.role == 'student':
            return StudentProfile.objects.filter(user=self.request.user)
        
        return StudentProfile.objects.none()
    
    def perform_create(self, serializer):
        """Create or update student profile"""
        if self.request.user.role == 'student':
            serializer.save(user=self.request.user)




class NoteViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user notes
    """
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    
    def get_queryset(self):
        """Return only the current user's notes"""
        queryset = Note.objects.filter(user=self.request.user)
        
        # Apply filters
        subject = self.request.query_params.get('subject', None)
        is_favorite = self.request.query_params.get('is_favorite', None)
        search = self.request.query_params.get('search', None)
        
        if subject:
            queryset = queryset.filter(subject__icontains=subject)
        
        if is_favorite:
            queryset = queryset.filter(is_favorite=is_favorite.lower() == 'true')
        
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(content__icontains=search)
            )
        
        return queryset.order_by('-updated_at')
    
    def perform_create(self, serializer):
        """Assign the current user to the note and track goal progress"""
        serializer.save(user=self.request.user)
        
        # Track goal progress for note creation
        try:
            from .feature_views import track_note_creation
            track_note_creation(self.request.user)
        except ImportError:
            pass  # Feature not available yet


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_user_stats(request):
    """
    Get comprehensive user statistics
    """
    user = request.user
    
    stats = {
        'profile': {
            'id': user.id,
            'full_name': user.get_full_name() or user.username,
            'email': user.email,
            'role': user.role,
            'profile_picture': user.profile_picture.url if user.profile_picture else None,
            'is_verified': user.is_verified,
            'created_at': user.created_at,
            'last_login': user.last_login,
        }
    }
    
    if user.role == 'student':
        # Student statistics
        try:
            from apps.progress.models import StudentProgress, QuizResult
            
            quiz_results = QuizResult.objects.filter(student=user)
            progress = StudentProgress.objects.filter(student=user)
            
            # Try to import CourseEnrollment safely
            enrollments_count = 0
            enrollments_completed = 0
            enrollments_in_progress = 0
            recent_activity = []
            
            # CourseEnrollment model doesn't exist, use progress data instead
            enrollments_count = progress.values('course').distinct().count() if progress.exists() else 0
            enrollments_completed = progress.filter(
                activity_type='course_complete', status='completed'
            ).values('course').distinct().count()
            enrollments_in_progress = max(0, enrollments_count - enrollments_completed)
            
            stats['academic'] = {
                'courses_enrolled': enrollments_count,
                'courses_completed': enrollments_completed,
                'courses_in_progress': enrollments_in_progress,
                'total_quizzes_taken': quiz_results.count(),
                'average_quiz_score': quiz_results.aggregate(avg=Avg('score'))['avg'] or 0,
                'total_study_time': progress.aggregate(
                    total_time=Sum('time_spent')
                )['total_time'] or 0,
                'lessons_completed': progress.filter(
                    activity_type='lesson_complete', status='completed'
                ).count(),
            }
            
            # Recent activity
            recent_progress = progress.order_by('-last_accessed')[:5]
            stats['recent_activity'] = [
                {
                    'course': getattr(p, 'course', {}).get('title', 'Unknown Course') if hasattr(p, 'course') else 'Unknown Course',
                    'activity': p.activity_type,
                    'status': p.status,
                    'last_accessed': p.last_accessed,
                    'score': p.score
                }
                for p in recent_progress
            ]
            
        except Exception as e:
            # If progress models don't exist, provide default stats
            stats['academic'] = {
                'courses_enrolled': 0,
                'courses_completed': 0,
                'courses_in_progress': 0,
                'total_quizzes_taken': 0,
                'average_quiz_score': 0,
                'total_study_time': 0,
                'lessons_completed': 0,
            }
            stats['recent_activity'] = []
        
    # Only students exist in AI system
    
    return Response(stats)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def upload_profile_picture(request):
    """
    Upload profile picture for current user
    """
    if 'profile_picture' not in request.FILES:
        return Response(
            {'error': 'No profile picture provided'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = request.user
    user.profile_picture = request.FILES['profile_picture']
    user.save()
    
    return Response({
        'message': 'Profile picture updated successfully',
        'profile_picture_url': user.profile_picture.url if user.profile_picture else None
    })


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def remove_profile_picture(request):
    """
    Remove profile picture for current user
    """
    user = request.user
    if user.profile_picture:
        user.profile_picture.delete()
        user.profile_picture = None
        user.save()
    
    return Response({'message': 'Profile picture removed successfully'})

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def student_notification_stats(request):
    """Get student notification statistics"""
    try:
        student = request.user
        
        # Get notification statistics
        total_notifications = Notification.objects.filter(recipient=student).count()
        unread_count = Notification.objects.filter(
            recipient=student,
            is_read=False
        ).exclude(expires_at__lt=timezone.now()).count()
        
        # Count by priority
        urgent_count = Notification.objects.filter(
            recipient=student,
            is_read=False,
            priority='urgent'
        ).exclude(expires_at__lt=timezone.now()).count()
        
        high_count = Notification.objects.filter(
            recipient=student,
            is_read=False,
            priority='high'
        ).exclude(expires_at__lt=timezone.now()).count()
        
        # Count by type
        type_counts = {}
        notification_types = ['enrollment_approved', 'assignment_created', 'assignment_due_soon', 'class_message', 'system_message']
        
        for notification_type in notification_types:
            type_counts[notification_type] = Notification.objects.filter(
                recipient=student,
                is_read=False,
                type=notification_type
            ).exclude(expires_at__lt=timezone.now()).count()
        
        # Recent notifications (last 5)
        recent_notifications = Notification.objects.filter(
            recipient=student
        ).exclude(
            expires_at__lt=timezone.now()
        ).order_by('-created_at')[:5]
        
        recent_serializer = NotificationSerializer(recent_notifications, many=True)
        
        return Response({
            'stats': {
                'total_notifications': total_notifications,
                'unread_count': unread_count,
                'urgent_count': urgent_count,
                'high_priority_count': high_count,
                'type_counts': type_counts
            },
            'recent_notifications': recent_serializer.data
        })
        
    except Exception as e:
        logger.error(f"Student notification stats error: {str(e)}")
        return Response(
            {'error': 'Failed to get notification stats', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def student_notification_detail(request, notification_id):
    """Get, update, or delete a specific notification"""
    try:
        student = request.user
        
        # Get the notification
        try:
            notification = Notification.objects.get(
                id=notification_id,
                recipient=student
            )
        except Notification.DoesNotExist:
            return Response(
                {'error': 'Notification not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if request.method == 'GET':
            # Get notification details
            serializer = NotificationSerializer(notification)
            return Response(serializer.data)
        
        elif request.method == 'PUT':
            # Update notification (mark as read/unread)
            is_read = request.data.get('is_read', True)
            
            notification.is_read = is_read
            if is_read and not notification.read_at:
                notification.read_at = timezone.now()
            elif not is_read:
                notification.read_at = None
            
            notification.save()
            
            serializer = NotificationSerializer(notification)
            return Response({
                'message': f'Notification marked as {"read" if is_read else "unread"}',
                'notification': serializer.data
            })
        
        elif request.method == 'DELETE':
            # Delete notification
            notification.delete()
            return Response({
                'message': 'Notification deleted successfully'
            })
        
    except Exception as e:
        logger.error(f"Student notification detail error: {str(e)}")
        return Response(
            {'error': 'Failed to process notification', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def user_goals(request):
    """Get or create user goals"""
    from .models import Goal
    
    if request.method == 'GET':
        goals = Goal.objects.filter(user=request.user).order_by('-created_at')
        goals_data = []
        
        for goal in goals:
            goals_data.append({
                'id': goal.id,
                'title': goal.title,
                'description': goal.description,
                'goal_type': goal.goal_type,
                'progress': goal.progress_percentage,
                'current_progress': goal.current_progress,
                'target_value': goal.target_value,
                'target_date': goal.target_date.strftime('%Y-%m-%d') if goal.target_date else None,
                'status': goal.status,
                'unit': goal.unit,
                'created_at': goal.created_at.strftime('%Y-%m-%d'),
                'completed_at': goal.completed_at.strftime('%Y-%m-%d') if goal.completed_at else None
            })
        
        return Response(goals_data)
    
    elif request.method == 'POST':
        # Create new goal
        data = request.data
        required_fields = ['title', 'goal_type', 'target_value', 'target_date', 'unit']
        
        for field in required_fields:
            if field not in data:
                return Response(
                    {'error': f'{field} is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        try:
            from datetime import datetime
            target_date = datetime.strptime(data['target_date'], '%Y-%m-%d')
            
            goal = Goal.objects.create(
                user=request.user,
                title=data['title'],
                description=data.get('description', ''),
                goal_type=data['goal_type'],
                target_value=int(data['target_value']),
                target_date=target_date,
                unit=data['unit'],
                subject_focus=data.get('subject_focus', ''),
                difficulty_level=data.get('difficulty_level', 'medium')
            )
            
            return Response({
                'id': goal.id,
                'title': goal.title,
                'message': 'Goal created successfully'
            }, status=status.HTTP_201_CREATED)
            
        except ValueError as e:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to create goal: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_achievements(request):
    """Get user achievements/rewards"""
    from .models import MilestoneReward
    
    achievements = MilestoneReward.objects.filter(
        user=request.user
    ).order_by('-created_at')
    
    achievements_data = []
    for achievement in achievements:
        achievements_data.append({
            'id': achievement.id,
            'title': achievement.title,
            'description': achievement.description,
            'reward_type': achievement.reward_type,
            'icon': achievement.icon,
            'color': achievement.color,
            'points_awarded': achievement.points_awarded,
            'is_claimed': achievement.is_claimed,
            'earned_date': achievement.created_at.strftime('%Y-%m-%d'),
            'claimed_at': achievement.claimed_at.strftime('%Y-%m-%d') if achievement.claimed_at else None,
            'badge': achievement.icon  # For frontend compatibility
        })
    
    return Response(achievements_data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def update_goal_progress(request, goal_id):
    """Update progress for a specific goal"""
    from .models import Goal
    
    try:
        goal = Goal.objects.get(id=goal_id, user=request.user)
    except Goal.DoesNotExist:
        return Response(
            {'error': 'Goal not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    increment = request.data.get('increment', 1)
    
    try:
        goal.update_progress(increment)
        return Response({
            'message': 'Goal progress updated successfully',
            'current_progress': goal.current_progress,
            'progress_percentage': goal.progress_percentage,
            'is_completed': goal.is_completed
        })
    except Exception as e:
        return Response(
            {'error': f'Failed to update progress: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
