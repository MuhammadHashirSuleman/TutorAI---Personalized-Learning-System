from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, Q
from .models import (
    StudentProgress, QuizResult, 
    LearningGoal, PerformanceAnalytics, Notification
)
from apps.courses.models import Course, Lesson, Quiz, Subject

User = get_user_model()

class StudentProgressSerializer(serializers.ModelSerializer):
    """Serializer for detailed student progress tracking"""
    
    student_name = serializers.SerializerMethodField()
    course_title = serializers.SerializerMethodField()
    lesson_title = serializers.SerializerMethodField()
    duration_formatted = serializers.SerializerMethodField()
    grade_letter = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentProgress
        fields = [
            'id', 'student', 'student_name', 'course', 'course_title',
            'lesson', 'lesson_title', 'activity_type', 'status',
            'completion_percentage', 'time_spent', 'duration_formatted',
            'started_at', 'completed_at', 'last_accessed',
            'score', 'grade_letter', 'attempts', 'best_score',
            'difficulty_rating', 'engagement_level', 'notes',
            'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = ['student', 'created_at', 'updated_at', 'last_accessed']
    
    def get_student_name(self, obj):
        return obj.student.get_full_name() or obj.student.email
    
    def get_course_title(self, obj):
        return obj.course.title if obj.course else None
    
    def get_lesson_title(self, obj):
        return obj.lesson.title if obj.lesson else None
    
    def get_duration_formatted(self, obj):
        """Format time spent in human readable format"""
        if obj.time_spent == 0:
            return "0 min"
        
        hours = obj.time_spent // 60
        minutes = obj.time_spent % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"
    
    def get_grade_letter(self, obj):
        """Get letter grade based on score"""
        if obj.score is None:
            return None
        
        if obj.score >= 90:
            return 'A'
        elif obj.score >= 80:
            return 'B'
        elif obj.score >= 70:
            return 'C'
        elif obj.score >= 60:
            return 'D'
        else:
            return 'F'


class QuizResultSerializer(serializers.ModelSerializer):
    """Serializer for quiz results and analytics"""
    
    student_name = serializers.SerializerMethodField()
    quiz_title = serializers.SerializerMethodField()
    grade_letter = serializers.SerializerMethodField()
    time_taken_formatted = serializers.SerializerMethodField()
    accuracy_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = QuizResult
        fields = [
            'id', 'student', 'student_name', 'quiz', 'quiz_title',
            'attempt_number', 'status', 'score', 'grade_letter',
            'total_questions', 'correct_answers', 'incorrect_answers',
            'skipped_questions', 'accuracy_percentage',
            'time_started', 'time_completed', 'time_taken',
            'time_taken_formatted', 'average_time_per_question',
            'answers', 'question_analytics', 'strengths_identified',
            'weaknesses_identified', 'recommendations',
            'difficulty_progression', 'concept_mastery',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['student', 'created_at', 'updated_at', 'time_started']
    
    def get_student_name(self, obj):
        return obj.student.get_full_name() or obj.student.email
    
    def get_quiz_title(self, obj):
        return obj.quiz.title if obj.quiz else None
    
    def get_grade_letter(self, obj):
        return obj.calculate_grade()
    
    def get_time_taken_formatted(self, obj):
        """Format time taken in human readable format"""
        if obj.time_taken == 0:
            return "0 sec"
        
        minutes = obj.time_taken // 60
        seconds = obj.time_taken % 60
        
        if minutes > 0:
            return f"{minutes}m {seconds}s"
        return f"{seconds}s"
    
    def get_accuracy_percentage(self, obj):
        """Calculate accuracy percentage"""
        if obj.total_questions == 0:
            return 0.0
        return (obj.correct_answers / obj.total_questions) * 100




class LearningGoalSerializer(serializers.ModelSerializer):
    """Serializer for AI-driven learning goals and objectives"""
    
    student_name = serializers.SerializerMethodField()
    ai_tutor_name = serializers.SerializerMethodField()
    milestone_progress = serializers.SerializerMethodField()
    days_until_target = serializers.SerializerMethodField()
    related_courses_titles = serializers.SerializerMethodField()
    
    class Meta:
        model = LearningGoal
        fields = [
            'id', 'student', 'student_name', 'ai_tutor_name',
            'title', 'description', 'goal_type', 'status',
            'progress_percentage', 'target_score', 'target_completion_date',
            'days_until_target', 'related_courses', 'related_courses_titles',
            'related_subjects', 'milestones', 'completed_milestones',
            'milestone_progress', 'suggested_resources', 
            'adaptive_recommendations', 'created_at', 'updated_at', 'achieved_at'
        ]
        read_only_fields = ['student', 'created_at', 'updated_at', 'achieved_at']
    
    def get_student_name(self, obj):
        return obj.student.get_full_name() or obj.student.email
    
    def get_ai_tutor_name(self, obj):
        # In AI-only system, return AI tutor name from course or default
        if hasattr(obj, 'related_courses') and obj.related_courses.exists():
            return obj.related_courses.first().ai_tutor_name or "AI Learning Assistant"
        return "AI Learning Assistant"
    
    def get_milestone_progress(self, obj):
        """Get milestone completion summary"""
        total = len(obj.milestones) if obj.milestones else 0
        completed = len(obj.completed_milestones) if obj.completed_milestones else 0
        return {
            'total': total,
            'completed': completed,
            'remaining': total - completed
        }
    
    def get_days_until_target(self, obj):
        """Calculate days until target completion"""
        if not obj.target_completion_date:
            return None
        
        from django.utils import timezone
        today = timezone.now().date()
        delta = obj.target_completion_date - today
        return delta.days
    
    def get_related_courses_titles(self, obj):
        return [course.title for course in obj.related_courses.all()]


class PerformanceAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for AI-driven performance analytics and insights"""
    
    student_name = serializers.SerializerMethodField()
    ai_tutor_name = serializers.SerializerMethodField()
    course_title = serializers.SerializerMethodField()
    subject_name = serializers.SerializerMethodField()
    analysis_duration_days = serializers.SerializerMethodField()
    study_time_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = PerformanceAnalytics
        fields = [
            'id', 'student', 'student_name', 'ai_tutor_name',
            'analysis_type', 'course', 'course_title', 'subject', 'subject_name',
            'start_date', 'end_date', 'analysis_duration_days',
            'overall_score', 'improvement_rate', 'consistency_score',
            'strengths', 'weaknesses', 'recommendations', 'predicted_outcomes',
            'study_time_total', 'study_time_formatted', 'login_frequency',
            'resource_usage', 'ai_benchmark_average', 'percentile_rank',
            'learning_style_detected', 'difficulty_preferences',
            'optimal_study_times', 'created_at'
        ]
        read_only_fields = ['student', 'created_at']
    
    def get_student_name(self, obj):
        return obj.student.get_full_name() or obj.student.email
    
    def get_ai_tutor_name(self, obj):
        # Return AI tutor name from course or default
        if obj.course and hasattr(obj.course, 'ai_tutor_name'):
            return obj.course.ai_tutor_name or "AI Analytics Engine"
        return "AI Analytics Engine"
    
    def get_course_title(self, obj):
        return obj.course.title if obj.course else None
    
    def get_subject_name(self, obj):
        return obj.subject.name if obj.subject else None
    
    def get_analysis_duration_days(self, obj):
        """Calculate duration of analysis period"""
        delta = obj.end_date - obj.start_date
        return delta.days + 1
    
    def get_study_time_formatted(self, obj):
        """Format study time in human readable format"""
        if obj.study_time_total == 0:
            return "0 min"
        
        hours = obj.study_time_total // 60
        minutes = obj.study_time_total % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"


class StudentProgressSummarySerializer(serializers.Serializer):
    """Summary serializer for overall student progress"""
    
    student_id = serializers.IntegerField()
    student_name = serializers.CharField()
    student_email = serializers.CharField()
    
    # Course Progress
    total_courses = serializers.IntegerField()
    completed_courses = serializers.IntegerField()
    in_progress_courses = serializers.IntegerField()
    course_completion_rate = serializers.FloatField()
    
    # Activity Summary
    total_lessons = serializers.IntegerField()
    completed_lessons = serializers.IntegerField()
    lesson_completion_rate = serializers.FloatField()
    
    # Quiz Performance
    total_quizzes = serializers.IntegerField()
    completed_quizzes = serializers.IntegerField()
    average_quiz_score = serializers.FloatField()
    
    # Time Analytics
    total_study_time = serializers.IntegerField()  # in minutes
    study_time_formatted = serializers.CharField()
    average_daily_study = serializers.IntegerField()
    
    # Performance Metrics
    overall_grade = serializers.CharField()
    improvement_trend = serializers.CharField()  # 'improving', 'stable', 'declining'
    engagement_level = serializers.FloatField()
    
    # Recent Activity
    last_activity = serializers.DateTimeField()
    recent_achievements = serializers.ListField()
    
    # Goals and Recommendations
    active_goals = serializers.IntegerField()
    achieved_goals = serializers.IntegerField()
    ai_recommendations = serializers.ListField()






class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notifications"""
    
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)
    sender_email = serializers.CharField(source='sender.email', read_only=True)
    time_ago = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'type', 'title', 'message', 'priority', 'is_read', 'read_at',
            'sender', 'sender_name', 'sender_email', 'related_object_type',
            'related_object_id', 'metadata', 'action_url', 'action_label',
            'created_at', 'expires_at', 'time_ago', 'is_expired'
        ]
        read_only_fields = ['id', 'created_at', 'read_at']
    
    def get_time_ago(self, obj):
        """Get human-readable time since notification was created"""
        from django.utils import timezone
        from datetime import datetime, timedelta
        
        now = timezone.now()
        diff = now - obj.created_at
        
        if diff.days > 0:
            if diff.days == 1:
                return "1 day ago"
            elif diff.days < 7:
                return f"{diff.days} days ago"
            elif diff.days < 30:
                weeks = diff.days // 7
                return f"{weeks} week{'s' if weeks > 1 else ''} ago"
            else:
                months = diff.days // 30
                return f"{months} month{'s' if months > 1 else ''} ago"
        
        hours = diff.seconds // 3600
        if hours > 0:
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        
        minutes = diff.seconds // 60
        if minutes > 0:
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        
        return "Just now"
    
    def get_is_expired(self, obj):
        """Check if notification is expired"""
        return obj.is_expired()


class CreateNotificationSerializer(serializers.ModelSerializer):
    """Serializer for creating notifications (admin/system use)"""
    
    class Meta:
        model = Notification
        fields = [
            'recipient', 'sender', 'type', 'title', 'message', 'priority',
            'related_object_type', 'related_object_id', 'metadata',
            'action_url', 'action_label', 'expires_at'
        ]
    
    def validate_recipient(self, value):
        """Validate recipient exists and is active"""
        if not value.is_active:
            raise serializers.ValidationError("Cannot send notifications to inactive users.")
        return value
