from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import json
from datetime import timedelta

User = get_user_model()

class StudentProgress(models.Model):
    """Comprehensive student progress tracking"""
    
    ACTIVITY_TYPES = [
        ('lesson_start', 'Lesson Started'),
        ('lesson_complete', 'Lesson Completed'),
        ('quiz_attempt', 'Quiz Attempted'),
        ('quiz_complete', 'Quiz Completed'),
        ('assignment_submit', 'Assignment Submitted'),
        ('course_enroll', 'Course Enrolled'),
        ('course_complete', 'Course Completed'),
        ('video_watch', 'Video Watched'),
        ('resource_download', 'Resource Downloaded'),
        ('discussion_post', 'Discussion Post'),
        ('help_request', 'Help Requested')
    ]
    
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'), 
        ('completed', 'Completed'),
        ('review_needed', 'Needs Review'),
        ('failed', 'Failed - Needs Retry')
    ]
    
    # Core Relationships
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_progress')
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='student_progress')
    lesson = models.ForeignKey('courses.Lesson', on_delete=models.CASCADE, null=True, blank=True, related_name='student_progress')
    
    # Progress Details
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    completion_percentage = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Time Tracking
    time_spent = models.IntegerField(default=0, help_text="Time spent in minutes")
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_accessed = models.DateTimeField(auto_now=True)
    
    # Performance Metrics
    score = models.FloatField(null=True, blank=True, help_text="Score achieved (0-100)")
    attempts = models.IntegerField(default=0)
    best_score = models.FloatField(null=True, blank=True)
    
    # Learning Analytics
    difficulty_rating = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    engagement_level = models.FloatField(default=0.5, help_text="Engagement level 0-1")
    
    # Additional Data
    notes = models.TextField(blank=True, help_text="Student or teacher notes")
    metadata = models.JSONField(default=dict, help_text="Additional progress data")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'student_progress'
        indexes = [
            models.Index(fields=['student', 'course']),
            models.Index(fields=['activity_type', 'status']),
            models.Index(fields=['completion_percentage']),
            models.Index(fields=['last_accessed']),
        ]
        unique_together = ['student', 'course', 'lesson', 'activity_type']
    
    def calculate_duration(self):
        """Calculate time spent on activity"""
        if self.started_at and self.completed_at:
            duration = self.completed_at - self.started_at
            return int(duration.total_seconds() / 60)  # minutes
        return 0
    
    def mark_completed(self, score=None):
        """Mark activity as completed"""
        self.status = 'completed'
        self.completion_percentage = 100.0
        self.completed_at = timezone.now()
        
        if score is not None:
            self.score = score
            if self.best_score is None or score > self.best_score:
                self.best_score = score
        
        if self.started_at:
            self.time_spent = self.calculate_duration()
        
        self.save()
    
    def __str__(self):
        return f"{self.student.email} - {self.course.title} - {self.activity_type}"


class QuizResult(models.Model):
    """Detailed quiz/assessment results"""
    
    RESULT_STATUS = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('timed_out', 'Timed Out'),
        ('submitted', 'Submitted for Review')
    ]
    
    # Core Relationships
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_results')
    quiz = models.ForeignKey('courses.Quiz', on_delete=models.CASCADE, related_name='results')
    progress = models.ForeignKey(StudentProgress, on_delete=models.CASCADE, null=True, blank=True)
    
    # Result Details
    attempt_number = models.IntegerField(default=1)
    status = models.CharField(max_length=20, choices=RESULT_STATUS, default='in_progress')
    
    # Scoring
    score = models.FloatField(default=0.0, help_text="Score achieved (0-100)")
    total_questions = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    incorrect_answers = models.IntegerField(default=0)
    skipped_questions = models.IntegerField(default=0)
    
    # Time Tracking
    time_started = models.DateTimeField(auto_now_add=True)
    time_completed = models.DateTimeField(null=True, blank=True)
    time_taken = models.IntegerField(default=0, help_text="Time taken in seconds")
    
    # Detailed Results
    answers = models.JSONField(default=dict, help_text="Student's answers to each question")
    question_analytics = models.JSONField(default=dict, help_text="Per-question performance data")
    
    # AI Analysis
    strengths_identified = models.JSONField(default=list, help_text="Topics student performed well on")
    weaknesses_identified = models.JSONField(default=list, help_text="Topics student struggled with")
    recommendations = models.JSONField(default=list, help_text="AI-generated recommendations")
    
    # Performance Insights
    average_time_per_question = models.FloatField(default=0.0)
    difficulty_progression = models.JSONField(default=list, help_text="How performance changed with difficulty")
    concept_mastery = models.JSONField(default=dict, help_text="Mastery level for each concept tested")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'quiz_results'
        indexes = [
            models.Index(fields=['student', 'quiz']),
            models.Index(fields=['score']),
            models.Index(fields=['created_at']),
        ]
        unique_together = ['student', 'quiz', 'attempt_number']
    
    def calculate_grade(self):
        """Calculate letter grade based on score"""
        if self.score >= 90:
            return 'A'
        elif self.score >= 80:
            return 'B'
        elif self.score >= 70:
            return 'C'
        elif self.score >= 60:
            return 'D'
        else:
            return 'F'
    
    def finish_quiz(self):
        """Complete the quiz and calculate final metrics"""
        self.status = 'completed'
        self.time_completed = timezone.now()
        
        if self.time_started:
            duration = self.time_completed - self.time_started
            self.time_taken = int(duration.total_seconds())
            
            if self.total_questions > 0:
                self.average_time_per_question = self.time_taken / self.total_questions
        
        # Calculate accuracy
        if self.total_questions > 0:
            accuracy = (self.correct_answers / self.total_questions) * 100
            self.score = accuracy
        
        self.save()
        
        # Update related progress
        if self.progress:
            self.progress.mark_completed(score=self.score)
    
    def __str__(self):
        return f"{self.student.email} - {self.quiz.title} - Attempt {self.attempt_number} - {self.score}%"




class LearningGoal(models.Model):
    """Individual learning goals and objectives"""
    
    GOAL_TYPES = [
        ('skill_mastery', 'Skill Mastery'),
        ('course_completion', 'Course Completion'),
        ('grade_improvement', 'Grade Improvement'),
        ('time_management', 'Time Management'),
        ('concept_understanding', 'Concept Understanding')
    ]
    
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('achieved', 'Achieved'),
        ('overdue', 'Overdue'),
        ('modified', 'Modified')
    ]
    
    # Core Information
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_goals')
    # AI manages all learning goals - no teacher needed
    
    # Goal Details
    title = models.CharField(max_length=200)
    description = models.TextField()
    goal_type = models.CharField(max_length=25, choices=GOAL_TYPES)
    
    # Progress Tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    progress_percentage = models.FloatField(default=0.0)
    
    # Targets
    target_score = models.FloatField(null=True, blank=True)
    target_completion_date = models.DateField(null=True, blank=True)
    
    # Relationships
    related_courses = models.ManyToManyField('courses.Course', blank=True)
    related_subjects = models.ManyToManyField('courses.Subject', blank=True)
    
    # Milestones
    milestones = models.JSONField(default=list, help_text="Key milestones to achieve goal")
    completed_milestones = models.JSONField(default=list)
    
    # AI Recommendations
    suggested_resources = models.JSONField(default=list)
    adaptive_recommendations = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    achieved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'learning_goals'
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['target_completion_date']),
        ]
    
    def update_progress(self):
        """Update progress based on completed milestones"""
        if not self.milestones:
            return
        
        total_milestones = len(self.milestones)
        completed_count = len(self.completed_milestones)
        
        self.progress_percentage = (completed_count / total_milestones) * 100
        
        if self.progress_percentage >= 100:
            self.status = 'achieved'
            self.achieved_at = timezone.now()
        elif self.progress_percentage > 0:
            self.status = 'in_progress'
        
        self.save()
    
    def __str__(self):
        return f"{self.student.email} - {self.title}"


class PerformanceAnalytics(models.Model):
    """Comprehensive performance analytics and insights"""
    
    ANALYSIS_TYPES = [
        ('weekly', 'Weekly Analysis'),
        ('monthly', 'Monthly Analysis'),
        ('course', 'Course Analysis'),
        ('subject', 'Subject Analysis'),
        ('comparative', 'Comparative Analysis')
    ]
    
    # Target Information
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='performance_analytics')
    # AI generates all analytics - no teacher needed
    
    # Analysis Scope
    analysis_type = models.CharField(max_length=20, choices=ANALYSIS_TYPES)
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, null=True, blank=True)
    subject = models.ForeignKey('courses.Subject', on_delete=models.CASCADE, null=True, blank=True)
    
    # Time Period
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Performance Metrics
    overall_score = models.FloatField(default=0.0)
    improvement_rate = models.FloatField(default=0.0, help_text="Rate of improvement over time")
    consistency_score = models.FloatField(default=0.0, help_text="How consistent performance has been")
    
    # Detailed Analytics
    strengths = models.JSONField(default=list)
    weaknesses = models.JSONField(default=list)
    recommendations = models.JSONField(default=list)
    predicted_outcomes = models.JSONField(default=dict)
    
    # Engagement Metrics
    study_time_total = models.IntegerField(default=0, help_text="Total study time in minutes")
    login_frequency = models.IntegerField(default=0)
    resource_usage = models.JSONField(default=dict)
    
    # Comparative Data
    class_average = models.FloatField(null=True, blank=True)
    percentile_rank = models.IntegerField(null=True, blank=True)
    
    # AI Insights
    learning_style_detected = models.CharField(max_length=50, blank=True)
    difficulty_preferences = models.JSONField(default=dict)
    optimal_study_times = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'performance_analytics'
        indexes = [
            models.Index(fields=['student', 'analysis_type']),
            models.Index(fields=['start_date', 'end_date']),
        ]
    
    def __str__(self):
        return f"{self.student.email} - {self.analysis_type} - {self.start_date} to {self.end_date}"






class Notification(models.Model):
    """Comprehensive notification system for users"""
    
    NOTIFICATION_TYPES = [
        # Enrollment related
        ('enrollment_request', 'Enrollment Request'),
        ('enrollment_approved', 'Enrollment Approved'),
        ('enrollment_rejected', 'Enrollment Rejected'),
        
        # Assignment related
        ('assignment_created', 'New Assignment'),
        ('assignment_due_soon', 'Assignment Due Soon'),
        ('assignment_overdue', 'Assignment Overdue'),
        ('assignment_graded', 'Assignment Graded'),
        
        # Class related
        ('class_created', 'Class Created'),
        ('student_joined', 'Student Joined Class'),
        ('student_removed', 'Student Removed from Class'),
        
        # General
        ('system_message', 'System Message'),
        ('achievement', 'Achievement Unlocked'),
        ('reminder', 'Reminder'),
        ('announcement', 'Announcement')
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ]
    
    # Core Information
    recipient = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='notifications_received'
    )
    sender = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='notifications_sent',
        help_text="User who triggered this notification (can be null for system notifications)"
    )
    
    # Notification Details
    type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='normal')
    
    # Status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Related Objects (optional - for context)
    related_object_type = models.CharField(
        max_length=50, 
        blank=True,
        help_text="Type of related object (assignment, enrollment_request, etc.)"
    )
    related_object_id = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="ID of related object"
    )
    
    # Additional Data
    metadata = models.JSONField(
        default=dict, 
        help_text="Additional data for the notification (links, actions, etc.)"
    )
    
    # Action Information
    action_url = models.CharField(
        max_length=500, 
        blank=True,
        help_text="URL for primary action (e.g., view assignment, approve request)"
    )
    action_label = models.CharField(
        max_length=100, 
        blank=True,
        help_text="Label for primary action button"
    )
    
    # Timing
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="When this notification becomes irrelevant (optional)"
    )
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['type', 'priority']),
            models.Index(fields=['created_at']),
            models.Index(fields=['expires_at']),
        ]
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()
    
    def is_expired(self):
        """Check if notification is expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    @classmethod
    def create_notification(
        cls,
        recipient,
        notification_type,
        title,
        message,
        sender=None,
        priority='normal',
        related_object=None,
        action_url='',
        action_label='',
        metadata=None,
        expires_in_days=None
    ):
        """Helper method to create notifications"""
        
        notification_data = {
            'recipient': recipient,
            'sender': sender,
            'type': notification_type,
            'title': title,
            'message': message,
            'priority': priority,
            'action_url': action_url,
            'action_label': action_label,
            'metadata': metadata or {}
        }
        
        # Handle related object
        if related_object:
            notification_data['related_object_type'] = related_object.__class__.__name__.lower()
            notification_data['related_object_id'] = related_object.id
        
        # Handle expiration
        if expires_in_days:
            from django.utils import timezone
            from datetime import timedelta
            notification_data['expires_at'] = timezone.now() + timedelta(days=expires_in_days)
        
        return cls.objects.create(**notification_data)
    
    @classmethod
    def create_ai_progress_notification(cls, student, notification_type, course=None, quiz_result=None):
        """Create AI-powered learning notifications"""
        
        if notification_type == 'ai_recommendation':
            title = '🤖 AI Learning Recommendation'
            message = 'Your AI tutor has new personalized recommendations based on your learning progress.'
            action_url = '/dashboard'
            action_label = 'View Recommendations'
            priority = 'normal'
            
        elif notification_type == 'milestone_achieved':
            title = '🎆 Learning Milestone Achieved!'
            message = f'Congratulations! You\'ve reached a new milestone in your learning journey.'
            action_url = '/progress'
            action_label = 'View Progress'
            priority = 'high'
            
        elif notification_type == 'quiz_completed':
            grade_emoji = '🎉' if quiz_result and quiz_result.score >= 90 else '👍' if quiz_result and quiz_result.score >= 70 else '📈'
            title = f'Quiz Completed {grade_emoji}'
            message = f'You\'ve completed a quiz with a score of {quiz_result.score:.1f}%. Your AI tutor is analyzing your performance.'
            action_url = f'/courses/{course.id}' if course else '/progress'
            action_label = 'View Results'
            priority = 'normal'
            
        elif notification_type == 'ai_insight':
            title = '💡 AI Learning Insight'
            message = 'Your AI tutor has identified patterns in your learning and has insights to share.'
            action_url = '/chatbot'
            action_label = 'Chat with AI Tutor'
            priority = 'normal'
        
        return cls.create_notification(
            recipient=student,
            sender=None,  # System/AI generated
            notification_type=notification_type,
            title=title,
            message=message,
            priority=priority,
            related_object=course or quiz_result,
            action_url=action_url,
            action_label=action_label,
            expires_in_days=7
        )
    
    def __str__(self):
        return f"{self.title} -> {self.recipient.email} ({self.type})"
