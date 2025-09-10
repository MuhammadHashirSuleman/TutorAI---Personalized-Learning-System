import json
import random
from datetime import date, timedelta
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q, Count
from django.db import transaction
from rest_framework import status, permissions, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import AllowAny

from apps.chatbot.models import ChatSession
from .models import (
    Note, MotivationalQuote, DailyQuoteAssignment,
    SavedChatHistory, Goal, MilestoneReward, StudentProfile
)
from .feature_serializers import (
    NoteSummarySerializer, MotivationalQuoteSerializer, DailyQuoteSerializer,
    SavedChatHistorySerializer, CreateSavedChatSerializer, GoalSerializer,
    MilestoneRewardSerializer, ClaimRewardSerializer, UpdateGoalProgressSerializer
)


# ============ NOTE SUMMARIZER REMOVED ============
# The note summarizer has been replaced with a dedicated document summarizer
# that handles PDF and DOCX files. See document_views.py for the new implementation.


# ============ FEATURE 2: MOTIVATIONAL QUOTE OF THE DAY ============

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_daily_quote(request):
    """Get today's motivational quote for the user"""
    try:
        today = date.today()
        user = request.user
        
        # Check if user already has a quote for today
        try:
            daily_quote = DailyQuoteAssignment.objects.get(
                user=user,
                date_assigned=today
            )
        except DailyQuoteAssignment.DoesNotExist:
            # Generate new quote for today
            daily_quote = generate_daily_quote(user, today)
        
        if not daily_quote:
            # If no quotes available, create a fallback response
            return Response({
                'error': 'No quotes available today', 
                'fallback_message': 'Keep learning and growing! Your journey to knowledge is inspiring.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = DailyQuoteSerializer(daily_quote)
        return Response(serializer.data)
        
    except Exception as e:
        # Log the actual error for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Daily quote error: {str(e)}', exc_info=True)
        
        return Response({
            'error': f'Failed to get daily quote: {str(e)}',
            'fallback_message': 'Stay motivated and keep learning!'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_quote_viewed(request):
    """Mark today's quote as viewed"""
    try:
        today = date.today()
        daily_quote = get_object_or_404(
            DailyQuoteAssignment,
            user=request.user,
            date_assigned=today
        )
        
        if not daily_quote.viewed:
            daily_quote.viewed = True
            daily_quote.viewed_at = timezone.now()
            daily_quote.save()
        
        return Response({'message': 'Quote marked as viewed'})
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def like_daily_quote(request):
    """Like or unlike today's quote"""
    try:
        today = date.today()
        daily_quote = get_object_or_404(
            DailyQuoteAssignment,
            user=request.user,
            date_assigned=today
        )
        
        # Toggle like status
        daily_quote.liked = not daily_quote.liked
        daily_quote.save()
        
        return Response({
            'message': 'Quote liked' if daily_quote.liked else 'Quote unliked',
            'liked': daily_quote.liked
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def generate_daily_quote(user, target_date):
    """Generate a daily quote for user based on their progress and weak subjects"""
    
    # Get user's weak subjects from student profile
    weak_subjects = []
    try:
        if hasattr(user, 'student_profile'):
            student_profile = user.student_profile
            weak_subjects = student_profile.weaknesses or []
    except Exception:
        # StudentProfile doesn't exist or there's a database error
        pass
    
    try:
        # Build query to select appropriate quote
        quotes_query = MotivationalQuote.objects.filter(is_active=True)
        
        # Check if there are any quotes at all
        if not quotes_query.exists():
            # Create a default quote if none exist
            try:
                default_quote = MotivationalQuote.objects.create(
                    quote_text="Believe in yourself and all that you are. Know that there is something inside you that is greater than any obstacle.",
                    author="Christian D. Larson",
                    category="general",
                    is_active=True
                )
                quotes_query = MotivationalQuote.objects.filter(is_active=True)
            except Exception:
                # If we can't even create a quote, return None
                return None
        
        # Try to find quotes targeting weak subjects first
        targeted_quotes = None
        if weak_subjects:
            try:
                targeted_quotes = quotes_query.filter(
                    target_weak_subjects__overlap=weak_subjects
                )
            except Exception:
                # Database doesn't support JSON field operations, skip targeting
                targeted_quotes = None
        
        if targeted_quotes and targeted_quotes.exists():
            quote = targeted_quotes.order_by('?').first()  # Random selection
        else:
            # Fall back to general quotes
            quote = quotes_query.order_by('?').first()
        
        if quote:
            try:
                # Create assignment
                daily_quote = DailyQuoteAssignment.objects.create(
                    user=user,
                    quote=quote,
                    date_assigned=target_date
                )
                
                # Update quote usage
                quote.usage_count += 1
                quote.last_used = timezone.now()
                quote.save()
                
                return daily_quote
            except Exception:
                # If we can't create assignment, return None
                return None
    
    except Exception:
        # Any other database error
        return None
    
    return None


# ============ FEATURE 3: CHAT SAVING OPTION ============

class SavedChatHistoryListView(generics.ListAPIView):
    """List saved chat histories"""
    serializer_class = SavedChatHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return SavedChatHistory.objects.filter(
            user=self.request.user
        ).select_related('original_session')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def save_chat_session(request):
    """Save a chat session to history"""
    try:
        print(f"DEBUG: User authenticated: {request.user.is_authenticated}")
        print(f"DEBUG: Request data: {request.data}")
        
        serializer = CreateSavedChatSerializer(data=request.data)
        if not serializer.is_valid():
            print(f"DEBUG: Serializer errors: {serializer.errors}")
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        session_id = serializer.validated_data['session_id']
        title = serializer.validated_data['title']
        tags = serializer.validated_data.get('tags', [])
        notes = serializer.validated_data.get('notes', '')
        messages = serializer.validated_data.get('messages', [])
        
        # Try to get existing chat session, otherwise create a basic one
        chat_session = None
        try:
            chat_session = ChatSession.objects.get(
                session_id=session_id,
                user=request.user
            )
        except (ChatSession.DoesNotExist, ValueError):
            # Session doesn't exist in DB (frontend-only chat), create a temporary one
            # or work without it
            pass
        
        # If we have a chat session in DB, use its data
        if chat_session:
            # Serialize messages from DB
            messages_data = []
            for message in chat_session.messages.all().order_by('order'):
                messages_data.append({
                    'message_type': message.message_type,
                    'content': message.content,
                    'order': message.order,
                    'created_at': message.created_at.isoformat(),
                    'user_rating': message.user_rating,
                })
            
            message_count = len(messages_data)
            session_duration = chat_session.session_duration or 0
            topics_covered = chat_session.concepts_covered or []
            subject = chat_session.subject or ''
            
            if subject and subject not in topics_covered:
                topics_covered.insert(0, subject)
        else:
            # Frontend-only chat, use the messages from the request
            messages_data = messages or []
            message_count = len(messages_data)
            session_duration = 0
            topics_covered = []
            subject = 'AI Tutor Chat'  # Default subject
        
        # Create saved chat
        saved_chat = SavedChatHistory.objects.create(
            user=request.user,
            original_session=chat_session,  # Can be None
            title=title,
            messages_content=messages_data,
            subject=subject,
            topics_covered=topics_covered,
            message_count=message_count,
            session_duration=session_duration,
            tags=tags,
            notes=notes
        )
        
        serializer = SavedChatHistorySerializer(saved_chat)
        return Response({
            'message': 'Chat session saved successfully',
            'saved_chat': serializer.data
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to save chat session: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ============ DEBUG ENDPOINT ============

@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def debug_auth_test(request):
    """Debug endpoint to test authentication"""
    return Response({
        'message': 'Authentication successful!',
        'user': request.user.email,
        'method': request.method,
        'data': request.data if request.method == 'POST' else None
    })


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_saved_chat(request, chat_id):
    """Delete a saved chat"""
    try:
        saved_chat = get_object_or_404(
            SavedChatHistory,
            id=chat_id,
            user=request.user
        )
        saved_chat.delete()
        return Response({'message': 'Saved chat deleted successfully'})
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def update_saved_chat(request, chat_id):
    """Update saved chat metadata"""
    try:
        saved_chat = get_object_or_404(
            SavedChatHistory,
            id=chat_id,
            user=request.user
        )
        
        # Update allowed fields
        if 'title' in request.data:
            saved_chat.title = request.data['title']
        if 'tags' in request.data:
            saved_chat.tags = request.data['tags']
        if 'notes' in request.data:
            saved_chat.notes = request.data['notes']
        if 'is_favorite' in request.data:
            saved_chat.is_favorite = request.data['is_favorite']
        
        saved_chat.save()
        
        serializer = SavedChatHistorySerializer(saved_chat)
        return Response(serializer.data)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ============ FEATURE 4: GOAL SETTING AND MILESTONE REWARDS ============

class GoalListCreateView(generics.ListCreateAPIView):
    """List and create goals"""
    serializer_class = GoalSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Goal.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class GoalDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a goal"""
    serializer_class = GoalSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Goal.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def update_goal_progress(request):
    """Update progress for a specific goal"""
    try:
        serializer = UpdateGoalProgressSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        goal_id = serializer.validated_data['goal_id']
        increment = serializer.validated_data['increment']
        
        goal = get_object_or_404(Goal, id=goal_id, user=request.user)
        
        if goal.status != 'active':
            return Response(
                {'error': 'Can only update progress for active goals'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update progress
        goal.update_progress(increment)
        
        goal_serializer = GoalSerializer(goal)
        return Response({
            'message': 'Goal progress updated successfully',
            'goal': goal_serializer.data
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class MilestoneRewardListView(generics.ListAPIView):
    """List user's milestone rewards"""
    serializer_class = MilestoneRewardSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return MilestoneReward.objects.filter(
            user=self.request.user,
            is_visible=True
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def claim_reward(request):
    """Claim a milestone reward"""
    try:
        serializer = ClaimRewardSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reward_id = serializer.validated_data['reward_id']
        reward = get_object_or_404(
            MilestoneReward,
            id=reward_id,
            user=request.user
        )
        
        if reward.claim_reward():
            reward_serializer = MilestoneRewardSerializer(reward)
            return Response({
                'message': 'Reward claimed successfully!',
                'reward': reward_serializer.data
            })
        else:
            return Response(
                {'error': 'Reward has already been claimed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_goal_dashboard(request):
    """Get goal dashboard with statistics"""
    try:
        user = request.user
        
        # Get goal statistics
        goals = Goal.objects.filter(user=user)
        active_goals = goals.filter(status='active')
        completed_goals = goals.filter(status='completed')
        
        # Get recent rewards
        recent_rewards = MilestoneReward.objects.filter(
            user=user,
            is_visible=True
        ).order_by('-created_at')[:5]
        
        # Calculate statistics
        total_goals = goals.count()
        completion_rate = (completed_goals.count() / total_goals * 100) if total_goals > 0 else 0
        
        # Get active goals progress
        active_goals_data = []
        for goal in active_goals:
            active_goals_data.append({
                'id': goal.id,
                'title': goal.title,
                'progress_percentage': goal.progress_percentage,
                'current_progress': goal.current_progress,
                'target_value': goal.target_value,
                'unit': goal.unit,
                'days_remaining': (goal.target_date.date() - timezone.now().date()).days if goal.target_date else None
            })
        
        return Response({
            'statistics': {
                'total_goals': total_goals,
                'active_goals': active_goals.count(),
                'completed_goals': completed_goals.count(),
                'completion_rate': round(completion_rate, 1)
            },
            'active_goals': active_goals_data,
            'recent_rewards': MilestoneRewardSerializer(recent_rewards, many=True).data
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ============ AUTOMATED GOAL TRACKING ============

def track_note_creation(user):
    """Track note creation for relevant goals"""
    active_note_goals = Goal.objects.filter(
        user=user,
        goal_type='notes',
        status='active'
    )
    
    for goal in active_note_goals:
        goal.update_progress(1)


# ============ STUDENT NOTIFICATIONS ============

@api_view(['GET', 'POST', 'PUT'])
@permission_classes([permissions.IsAuthenticated])
def student_notifications(request):
    """Get, mark as read, or manage student notifications"""
    try:
        student = request.user
        
        if request.method == 'GET':
            # Get student's notifications
            
            # Query parameters
            is_read = request.query_params.get('is_read', None)
            notification_type = request.query_params.get('type', None)
            priority = request.query_params.get('priority', None)
            limit = int(request.query_params.get('limit', 50))
            
            # Get notifications
            notifications = Notification.objects.filter(
                recipient=student
            ).order_by('-created_at')
            
            # Apply filters
            if is_read is not None:
                is_read_bool = is_read.lower() == 'true'
                notifications = notifications.filter(is_read=is_read_bool)
            
            if notification_type:
                notifications = notifications.filter(type=notification_type)
            
            if priority:
                notifications = notifications.filter(priority=priority)
            
            # Remove expired notifications
            notifications = notifications.exclude(
                expires_at__lt=timezone.now()
            )
            
            # Limit results
            notifications = notifications[:limit]
            
            # Serialize notifications
            serializer = NotificationSerializer(notifications, many=True)
            
            # Get summary stats
            total_notifications = Notification.objects.filter(recipient=student).count()
            unread_count = Notification.objects.filter(
                recipient=student,
                is_read=False
            ).exclude(expires_at__lt=timezone.now()).count()
            
            high_priority_count = Notification.objects.filter(
                recipient=student,
                is_read=False,
                priority__in=['high', 'urgent']
            ).exclude(expires_at__lt=timezone.now()).count()
            
            return Response({
                'notifications': serializer.data,
                'summary': {
                    'total_notifications': total_notifications,
                    'unread_count': unread_count,
                    'high_priority_count': high_priority_count,
                    'notification_types': [
                        {'type': 'enrollment_approved', 'label': 'Enrollment Approved'},
                        {'type': 'assignment_created', 'label': 'New Assignment'},
                        {'type': 'assignment_due_soon', 'label': 'Assignment Due'},
                        {'type': 'class_message', 'label': 'Class Updates'},
                        {'type': 'system_message', 'label': 'System Messages'},
                    ]
                }
            })
        
        elif request.method == 'POST':
            # Mark notification(s) as read
            notification_ids = request.data.get('notification_ids', [])
            
            if not notification_ids:
                return Response(
                    {'error': 'notification_ids is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Mark notifications as read
            updated_count = Notification.objects.filter(
                id__in=notification_ids,
                recipient=student
            ).update(
                is_read=True,
                read_at=timezone.now()
            )
            
            return Response({
                'message': f'Marked {updated_count} notifications as read',
                'updated_count': updated_count
            })
        
        elif request.method == 'PUT':
            # Bulk actions (mark all as read, delete read notifications)
            action = request.data.get('action')
            
            if action == 'mark_all_read':
                updated_count = Notification.objects.filter(
                    recipient=student,
                    is_read=False
                ).update(
                    is_read=True,
                    read_at=timezone.now()
                )
                
                return Response({
                    'message': f'Marked {updated_count} notifications as read',
                    'updated_count': updated_count
                })
            
            elif action == 'delete_read':
                deleted_count = Notification.objects.filter(
                    recipient=student,
                    is_read=True
                ).count()
                
                Notification.objects.filter(
                    recipient=student,
                    is_read=True
                ).delete()
                
                return Response({
                    'message': f'Deleted {deleted_count} read notifications',
                    'deleted_count': deleted_count
                })
            
            else:
                return Response(
                    {'error': 'Invalid action. Use "mark_all_read" or "delete_read"'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Student notifications error: {str(e)}", exc_info=True)
        return Response(
            {'error': 'Failed to process notifications', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET', 'POST', 'PUT'])
@permission_classes([permissions.IsAuthenticated])
def student_notifications(request):
    """Get, mark as read, or manage student notifications"""
    try:
        student = request.user
        
        if request.method == 'GET':
            # Get student's notifications
            
            # Query parameters
            is_read = request.query_params.get('is_read', None)
            notification_type = request.query_params.get('type', None)
            priority = request.query_params.get('priority', None)
            limit = int(request.query_params.get('limit', 50))
            
            # Get notifications
            notifications = Notification.objects.filter(
                recipient=student
            ).order_by('-created_at')
            
            # Apply filters
            if is_read is not None:
                is_read_bool = is_read.lower() == 'true'
                notifications = notifications.filter(is_read=is_read_bool)
            
            if notification_type:
                notifications = notifications.filter(type=notification_type)
            
            if priority:
                notifications = notifications.filter(priority=priority)
            
            # Remove expired notifications
            notifications = notifications.exclude(
                expires_at__lt=timezone.now()
            )
            
            # Limit results
            notifications = notifications[:limit]
            
            # Serialize notifications
            serializer = NotificationSerializer(notifications, many=True)
            
            # Get summary stats
            total_notifications = Notification.objects.filter(recipient=student).count()
            unread_count = Notification.objects.filter(
                recipient=student,
                is_read=False
            ).exclude(expires_at__lt=timezone.now()).count()
            
            high_priority_count = Notification.objects.filter(
                recipient=student,
                is_read=False,
                priority__in=['high', 'urgent']
            ).exclude(expires_at__lt=timezone.now()).count()
            
            return Response({
                'notifications': serializer.data,
                'summary': {
                    'total_notifications': total_notifications,
                    'unread_count': unread_count,
                    'high_priority_count': high_priority_count,
                    'notification_types': [
                        {'type': 'enrollment_approved', 'label': 'Enrollment Approved'},
                        {'type': 'assignment_created', 'label': 'New Assignment'},
                        {'type': 'assignment_due_soon', 'label': 'Assignment Due'},
                        {'type': 'class_message', 'label': 'Class Updates'},
                        {'type': 'system_message', 'label': 'System Messages'},
                    ]
                }
            })
        
        elif request.method == 'POST':
            # Mark notification(s) as read
            notification_ids = request.data.get('notification_ids', [])
            
            if not notification_ids:
                return Response(
                    {'error': 'notification_ids is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Mark notifications as read
            updated_count = Notification.objects.filter(
                id__in=notification_ids,
                recipient=student
            ).update(
                is_read=True,
                read_at=timezone.now()
            )
            
            return Response({
                'message': f'Marked {updated_count} notifications as read',
                'updated_count': updated_count
            })
        
        elif request.method == 'PUT':
            # Bulk actions (mark all as read, delete read notifications)
            action = request.data.get('action')
            
            if action == 'mark_all_read':
                updated_count = Notification.objects.filter(
                    recipient=student,
                    is_read=False
                ).update(
                    is_read=True,
                    read_at=timezone.now()
                )
                
                return Response({
                    'message': f'Marked {updated_count} notifications as read',
                    'updated_count': updated_count
                })
            
            elif action == 'delete_read':
                deleted_count = Notification.objects.filter(
                    recipient=student,
                    is_read=True
                ).count()
                
                Notification.objects.filter(
                    recipient=student,
                    is_read=True
                ).delete()
                
                return Response({
                    'message': f'Deleted {deleted_count} read notifications',
                    'deleted_count': deleted_count
                })
            
            else:
                return Response(
                    {'error': 'Invalid action. Use "mark_all_read" or "delete_read"'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Student notifications error: {str(e)}", exc_info=True)
        return Response(
            {'error': 'Failed to process notifications', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_notification_stats(request):
    """
    Get student notification stats (unread count)
    """
    try:
        user = request.user
        unread_count = Notification.objects.filter(
            recipient=user,
            is_read=False
        ).count()
        
        return Response({
            'unread_count': unread_count
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
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
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Student notification detail error: {str(e)}", exc_info=True)
        return Response(
            {'error': 'Failed to process notification', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
