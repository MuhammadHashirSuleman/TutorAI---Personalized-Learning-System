from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class User(AbstractUser):
    """User model with role-based authentication - matches frontend form"""
    
    class UserRole(models.TextChoices):
        STUDENT = 'student', _('Student')
        ADMIN = 'admin', _('Admin')
    
    # Core fields - matching frontend form exactly
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.STUDENT)
    email = models.EmailField(_('email address'), unique=True)
    phone_number = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'users'
        verbose_name = _('User')
        verbose_name_plural = _('Users')
    
    def __str__(self):
        return f"{self.email} ({self.role})"

class StudentProfile(models.Model):
    """Student profile for AI personalization - essential fields only"""
    
    class LearningStyle(models.TextChoices):
        VISUAL = 'visual', _('Visual')
        AUDITORY = 'auditory', _('Auditory')
        KINESTHETIC = 'kinesthetic', _('Kinesthetic')
        READING = 'reading', _('Reading/Writing')
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    
    # Learning preferences for AI
    learning_style = models.CharField(max_length=20, choices=LearningStyle.choices, blank=True)
    learning_goals = models.TextField(blank=True)
    
    # AI analysis data - these are crucial for personalization
    strengths = models.JSONField(default=list, help_text="Strong subject areas")
    weaknesses = models.JSONField(default=list, help_text="Areas needing improvement") 
    preferences = models.JSONField(default=dict, help_text="Learning preferences")
    
    class Meta:
        db_table = 'student_profiles'
        verbose_name = _('Student Profile')
        verbose_name_plural = _('Student Profiles')
    
    def __str__(self):
        return f"Student Profile - {self.user.email}"


class Note(models.Model):
    """Student notes - simplified but functional"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
    title = models.CharField(max_length=200)
    content = models.TextField()
    subject = models.CharField(max_length=100, blank=True)
    tags = models.JSONField(default=list, help_text="For organization and AI analysis")
    summary = models.TextField(blank=True, help_text="AI-generated summary")
    summary_generated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notes'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.email}"


class MotivationalQuote(models.Model):
    """Daily motivational quotes for students"""
    
    CATEGORY_CHOICES = [
        ('general', 'General Motivation'),
        ('study', 'Study & Learning'),
        ('perseverance', 'Perseverance'),
        ('success', 'Success & Achievement'),
        ('growth', 'Growth Mindset'),
        ('confidence', 'Confidence Building'),
        ('focus', 'Focus & Concentration'),
        ('goals', 'Goal Achievement'),
    ]
    
    quote_text = models.TextField()
    author = models.CharField(max_length=100, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    
    # Targeting based on student progress
    target_weak_subjects = models.JSONField(default=list, help_text="Show when student is weak in these subjects")
    target_low_motivation = models.BooleanField(default=True, help_text="Show when student engagement is low")
    
    # Usage tracking
    usage_count = models.IntegerField(default=0)
    last_used = models.DateTimeField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'motivational_quotes'
    
    def __str__(self):
        return f"{self.quote_text[:50]}... - {self.author}"


class DailyQuoteAssignment(models.Model):
    """Track daily quote assignments to users"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_quotes')
    quote = models.ForeignKey(MotivationalQuote, on_delete=models.CASCADE)
    date_assigned = models.DateField(auto_now_add=True)
    viewed = models.BooleanField(default=False)
    viewed_at = models.DateTimeField(null=True, blank=True)
    liked = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'daily_quote_assignments'
        unique_together = ['user', 'date_assigned']
    
    def __str__(self):
        return f"Daily quote for {self.user.email} on {self.date_assigned}"


class SavedChatHistory(models.Model):
    """Saved chat sessions with AI tutor"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_chats')
    original_session = models.ForeignKey('chatbot.ChatSession', on_delete=models.CASCADE, related_name='saved_versions', null=True, blank=True)
    
    # Saved content
    title = models.CharField(max_length=200, help_text="User-defined title for saved chat")
    messages_content = models.JSONField(help_text="Serialized messages from the chat session")
    
    # Metadata
    subject = models.CharField(max_length=100, blank=True)
    topics_covered = models.JSONField(default=list)
    message_count = models.IntegerField(default=0)
    session_duration = models.IntegerField(default=0, help_text="Duration in seconds")
    
    # Organization
    tags = models.JSONField(default=list, help_text="User tags for organization")
    is_favorite = models.BooleanField(default=False)
    notes = models.TextField(blank=True, help_text="User notes about this chat")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'saved_chat_history'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Saved Chat: {self.title} - {self.user.email}"


class Goal(models.Model):
    """Student learning goals"""
    
    GOAL_TYPES = [
        ('notes', 'Notes Creation'),
        ('courses', 'Course Completion'),
        ('quizzes', 'Quiz Performance'),
        ('study_time', 'Study Time'),
        ('streak', 'Learning Streak'),
        ('skills', 'Skill Development'),
        ('custom', 'Custom Goal'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('paused', 'Paused'),
        ('abandoned', 'Abandoned'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals')
    
    # Goal Details
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    goal_type = models.CharField(max_length=20, choices=GOAL_TYPES)
    
    # Progress Tracking
    target_value = models.IntegerField(help_text="Target value to achieve")
    current_progress = models.IntegerField(default=0)
    unit = models.CharField(max_length=50, help_text="Unit of measurement (notes, hours, points, etc.)")
    
    # Timeline
    start_date = models.DateTimeField(auto_now_add=True)
    target_date = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Rewards
    reward_claimed = models.BooleanField(default=False)
    
    # Metadata
    subject_focus = models.CharField(max_length=100, blank=True)
    difficulty_level = models.CharField(max_length=20, default='medium')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'goals'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.email}"
    
    @property
    def progress_percentage(self):
        if self.target_value == 0:
            return 0
        return min(100, (self.current_progress / self.target_value) * 100)
    
    @property
    def is_completed(self):
        return self.current_progress >= self.target_value
    
    def update_progress(self, increment=1):
        """Update goal progress and check completion"""
        self.current_progress += increment
        if self.is_completed and self.status == 'active':
            self.status = 'completed'
            self.completed_at = timezone.now()
            # Trigger reward
            MilestoneReward.objects.create(
                user=self.user,
                goal=self,
                reward_type='goal_completion',
                title=f"Goal Achieved: {self.title}",
                description=f"Congratulations! You've completed your goal: {self.title}"
            )
        self.save()


class MilestoneReward(models.Model):
    """Virtual rewards and badges for achieving goals"""
    
    REWARD_TYPES = [
        ('badge', 'Badge'),
        ('points', 'Points'),
        ('certificate', 'Certificate'),
        ('goal_completion', 'Goal Completion'),
        ('streak_milestone', 'Streak Milestone'),
        ('special_achievement', 'Special Achievement'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rewards')
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='rewards', null=True, blank=True)
    
    # Reward Details
    reward_type = models.CharField(max_length=20, choices=REWARD_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Visual
    icon = models.CharField(max_length=50, default='🏆', help_text="Emoji or icon class")
    color = models.CharField(max_length=7, default='#FFD700', help_text="Hex color code")
    
    # Points and Value
    points_awarded = models.IntegerField(default=0)
    
    # Status
    is_claimed = models.BooleanField(default=False)
    claimed_at = models.DateTimeField(null=True, blank=True)
    is_visible = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'milestone_rewards'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.email}"
    
    def claim_reward(self):
        """Mark reward as claimed"""
        if not self.is_claimed:
            self.is_claimed = True
            self.claimed_at = timezone.now()
            self.save()
            return True
        return False


class DocumentSummary(models.Model):
    """AI-generated summaries from uploaded PDF/DOCX documents"""
    
    FILE_TYPES = [
        ('pdf', 'PDF Document'),
        ('docx', 'Word Document'),
    ]
    
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='document_summaries')
    
    # File Information
    original_filename = models.CharField(max_length=255)
    file_type = models.CharField(max_length=10, choices=FILE_TYPES)
    file_size = models.IntegerField(help_text="File size in bytes")
    uploaded_file = models.FileField(upload_to='documents/%Y/%m/', null=True, blank=True)
    
    # Processing Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    processing_error = models.TextField(blank=True, help_text="Error message if processing failed")
    
    # Extracted Content
    extracted_text = models.TextField(blank=True, help_text="Full text extracted from document")
    
    # AI Summary
    summary = models.TextField(blank=True, help_text="AI-generated summary")
    summary_metadata = models.JSONField(default=dict, help_text="Metadata about summary generation")
    
    # User Metadata
    title = models.CharField(max_length=200, blank=True, help_text="User-defined title")
    subject = models.CharField(max_length=100, blank=True)
    tags = models.JSONField(default=list, help_text="User-defined tags")
    notes = models.TextField(blank=True, help_text="User notes about the document")
    
    # Tracking
    is_favorite = models.BooleanField(default=False)
    view_count = models.IntegerField(default=0)
    last_viewed = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'document_summaries'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['file_type']),
        ]
    
    def __str__(self):
        display_title = self.title or self.original_filename
        return f"{display_title} - {self.user.email}"
    
    def update_view_count(self):
        """Update view count and last viewed timestamp"""
        self.view_count += 1
        self.last_viewed = timezone.now()
        self.save(update_fields=['view_count', 'last_viewed'])
    
    @property
    def word_count(self):
        """Get approximate word count of extracted text"""
        if self.extracted_text:
            return len(self.extracted_text.split())
        return 0
    
    @property
    def summary_word_count(self):
        """Get word count of summary"""
        if self.summary:
            return len(self.summary.split())
        return 0
    
    @property
    def compression_ratio(self):
        """Calculate compression ratio (summary length / original length)"""
        if self.word_count > 0 and self.summary_word_count > 0:
            return round(self.summary_word_count / self.word_count * 100, 1)
        return 0
    
    def get_file_size_display(self):
        """Get human readable file size"""
        size = self.file_size
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size // 1024} KB"
        else:
            return f"{size // (1024 * 1024)} MB"
