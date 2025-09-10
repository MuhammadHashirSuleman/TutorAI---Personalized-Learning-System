from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.utils import timezone

User = get_user_model()

class Subject(models.Model):
    """Course subject categories"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'subjects'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Course(models.Model):
    """Main course model with essential features for AI learning system"""
    
    DIFFICULTY_LEVELS = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'), 
        ('advanced', 'Advanced')
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived')
    ]
    
    # Core Information
    title = models.CharField(max_length=200)
    description = models.TextField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='courses')
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_LEVELS, default='beginner')
    
    # Learning Data (for AI analysis)
    estimated_hours = models.FloatField(default=1.0)
    learning_objectives = models.JSONField(default=list)
    prerequisites = models.JSONField(default=list)
    tags = models.JSONField(default=list, help_text="For AI content matching")
    
    # AI-Powered Learning - No human instructors needed
    ai_tutor_name = models.CharField(max_length=100, default='AI Tutor', help_text="Name of AI tutor for this course")
    ai_tutor_avatar = models.CharField(max_length=10, default='AI', help_text="Avatar for AI tutor")
    
    # Status & Analytics (simplified)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='published')
    is_active = models.BooleanField(default=True)
    enrollment_count = models.IntegerField(default=0)
    average_rating = models.FloatField(default=0.0)
    
    # External Platform Integration
    external_platform = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        choices=[
            ('moodle', 'Moodle'),
            ('coursera', 'Coursera'),
            ('lti', 'LTI'),
        ],
        help_text="External platform this course is synced from"
    )
    external_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Course ID in the external platform"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'courses'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['subject', 'difficulty_level']),
            models.Index(fields=['status', 'is_active']),
        ]
    
    def __str__(self):
        return self.title

class Lesson(models.Model):
    """Course lessons - simplified but functional"""
    
    CONTENT_TYPES = [
        ('video', 'Video'),
        ('text', 'Text'),
        ('interactive', 'Interactive'),
        ('quiz', 'Quiz')
    ]
    
    # Basic Information
    title = models.CharField(max_length=200)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    order = models.IntegerField(default=0)
    
    # Content
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES, default='text')
    content = models.TextField()
    video_url = models.URLField(blank=True)
    
    # Learning Analytics Data
    estimated_duration = models.IntegerField(default=15, help_text="Minutes")
    key_concepts = models.JSONField(default=list, help_text="For AI learning analysis")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'lessons'
        ordering = ['course', 'order']
        unique_together = ['course', 'order']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"

# class CourseEnrollment(models.Model):
#     """Student enrollments - essential for progress tracking"""
#     student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
#     course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
#     enrolled_at = models.DateTimeField(auto_now_add=True)
#     completed_at = models.DateTimeField(null=True, blank=True)
#     progress_percentage = models.IntegerField(default=0)
#     is_active = models.BooleanField(default=True)
#     
#     class Meta:
#         db_table = 'course_enrollments'
#         unique_together = ['student', 'course']
#     
#     def __str__(self):
#         return f"{self.student.email} - {self.course.title}"

# CourseEnrollment model has been disabled to remove table dependency
# Use StudentProgress from apps.progress for enrollment tracking instead

class CourseRating(models.Model):
    """Course ratings - simplified for AI recommendations"""
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='ratings')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 stars
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'course_ratings'
        unique_together = ['student', 'course']
    
    def __str__(self):
        return f"{self.course.title} - {self.rating} stars"


class Quiz(models.Model):
    """Comprehensive quiz model with advanced features"""
    
    # Basic Information
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizzes')
    
    # Quiz Content
    questions_data = models.JSONField(default=list, help_text="Questions in JSON format")
    
    # Quiz Settings
    passing_score = models.FloatField(default=70.0, help_text="Minimum score to pass (0-100)")
    time_limit = models.IntegerField(default=0, help_text="Time limit in minutes (0 = unlimited)")
    attempts_allowed = models.IntegerField(default=1, help_text="Number of attempts allowed (0 = unlimited)")
    
    # Display Options
    show_results_immediately = models.BooleanField(default=True, help_text="Show results after submission")
    shuffle_questions = models.BooleanField(default=False, help_text="Randomize question order")
    shuffle_options = models.BooleanField(default=False, help_text="Randomize answer options")
    
    # Availability
    is_active = models.BooleanField(default=True)
    available_from = models.DateTimeField(null=True, blank=True, help_text="Quiz becomes available from this date")
    available_until = models.DateTimeField(null=True, blank=True, help_text="Quiz available until this date")
    
    # AI Integration
    ai_generated = models.BooleanField(default=False, help_text="Generated by AI based on student weaknesses")
    target_concepts = models.JSONField(default=list, help_text="Concepts this quiz targets")
    difficulty_level = models.CharField(
        max_length=10, 
        choices=[('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')],
        default='medium'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'quizzes'
        ordering = ['course', '-created_at']
        indexes = [
            models.Index(fields=['course', 'is_active']),
            models.Index(fields=['ai_generated', 'difficulty_level']),
            models.Index(fields=['available_from', 'available_until']),
        ]
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"
    
    @property
    def question_count(self):
        """Get total number of questions"""
        return len(self.questions_data) if isinstance(self.questions_data, list) else 0
    
    @property
    def total_points(self):
        """Calculate total possible points"""
        if isinstance(self.questions_data, list):
            return sum(q.get('points', 10) for q in self.questions_data)
        return 0
    
    def is_available(self):
        """Check if quiz is currently available"""
        if not self.is_active:
            return False
        
        now = timezone.now()
        
        if self.available_from and now < self.available_from:
            return False
        
        if self.available_until and now > self.available_until:
            return False
        
        return True
    
    def can_student_take(self, student):
        """Check if student can take this quiz"""
        if not self.is_available():
            return False, "Quiz is not currently available"
        
        # Check enrollment using StudentProgress instead of CourseEnrollment
        try:
            from apps.progress.models import StudentProgress
            if not StudentProgress.objects.filter(
                student=student,
                course=self.course.title  # Assuming course is stored as title in StudentProgress
            ).exists():
                return False, "You are not enrolled in this course"
        except Exception:
            # If StudentProgress doesn't exist or has different structure, allow access
            pass
        
        # Check attempts
        if self.attempts_allowed > 0:
            from apps.progress.models import QuizResult
            attempts = QuizResult.objects.filter(
                quiz=self, 
                student=student
            ).count()
            
            if attempts >= self.attempts_allowed:
                return False, f"Maximum attempts ({self.attempts_allowed}) reached"
        
        return True, "Can take quiz"
