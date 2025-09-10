from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import json
import uuid

User = get_user_model()

class ChatSession(models.Model):
    """Chat sessions between users and AI tutor"""
    
    SESSION_TYPES = [
        ('tutoring', 'Academic Tutoring'),
        ('homework_help', 'Homework Help'),
        ('concept_explanation', 'Concept Explanation'),
        ('quiz_assistance', 'Quiz Assistance'),
        ('general_support', 'General Learning Support'),
        ('career_guidance', 'Career Guidance')
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    session_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    
    # Session Details
    session_type = models.CharField(max_length=30, choices=SESSION_TYPES, default='tutoring')
    subject = models.CharField(max_length=100, blank=True, help_text="Subject area of discussion")
    topic = models.CharField(max_length=200, blank=True, help_text="Specific topic")
    difficulty_level = models.CharField(max_length=20, default='medium')
    
    # Session Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    is_anonymous = models.BooleanField(default=False)
    
    # Session Metadata
    title = models.CharField(max_length=200, blank=True, help_text="Auto-generated session title")
    summary = models.TextField(blank=True, help_text="AI-generated session summary")
    
    # Performance Metrics
    message_count = models.IntegerField(default=0)
    user_satisfaction = models.IntegerField(null=True, blank=True, choices=[(i, i) for i in range(1, 6)])
    session_duration = models.IntegerField(default=0, help_text="Duration in seconds")
    
    # Learning Analytics
    concepts_covered = models.JSONField(default=list, help_text="Concepts discussed in session")
    learning_objectives_met = models.JSONField(default=list)
    follow_up_actions = models.JSONField(default=list, help_text="Recommended follow-up actions")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    last_activity = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chat_sessions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['session_type', 'subject']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Chat Session - {self.user.email} ({self.session_type})"
    
    def end_session(self):
        """Mark session as completed and calculate duration"""
        self.status = 'completed'
        self.ended_at = timezone.now()
        if self.created_at:
            duration = self.ended_at - self.created_at
            self.session_duration = int(duration.total_seconds())
        self.save()


class ChatMessage(models.Model):
    """Individual messages in chat sessions"""
    
    MESSAGE_TYPES = [
        ('user', 'User Message'),
        ('ai_tutor', 'AI Tutor Response'),
        ('system', 'System Message'),
        ('suggestion', 'AI Suggestion'),
        ('resource', 'Resource Recommendation')
    ]
    
    CONTENT_TYPES = [
        ('text', 'Text'),
        ('code', 'Code'),
        ('math', 'Mathematical Expression'),
        ('image', 'Image'),
        ('link', 'Link/Resource'),
        ('quiz', 'Interactive Quiz'),
        ('explanation', 'Detailed Explanation')
    ]
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    
    # Message Details
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES, default='text')
    content = models.TextField()
    
    # Message Metadata
    order = models.IntegerField(default=0)
    is_edited = models.BooleanField(default=False)
    parent_message = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    
    # AI Response Metadata (for AI messages)
    model_used = models.CharField(max_length=50, blank=True, help_text="AI model used for response")
    response_time = models.FloatField(default=0.0, help_text="Time taken to generate response in seconds")
    confidence_score = models.FloatField(null=True, blank=True, help_text="AI confidence in response")
    tokens_used = models.IntegerField(default=0, help_text="Number of tokens used")
    
    # User Feedback
    user_rating = models.IntegerField(null=True, blank=True, choices=[(i, i) for i in range(1, 6)])
    is_helpful = models.BooleanField(null=True, blank=True)
    feedback_notes = models.TextField(blank=True)
    
    # Content Analysis
    concepts_mentioned = models.JSONField(default=list, help_text="Concepts referenced in message")
    difficulty_level = models.CharField(max_length=20, blank=True)
    educational_value = models.FloatField(default=0.0, help_text="Educational value score 0-1")
    
    # Additional Resources
    attachments = models.JSONField(default=list, help_text="File attachments or resources")
    external_links = models.JSONField(default=list, help_text="External resources mentioned")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chat_messages'
        ordering = ['session', 'order']
        indexes = [
            models.Index(fields=['session', 'order']),
            models.Index(fields=['message_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Message {self.order} in {self.session.title or 'Session'} ({self.message_type})"


class TutorPersonality(models.Model):
    """AI Tutor personality configurations"""
    
    PERSONALITY_TYPES = [
        ('friendly', 'Friendly & Encouraging'),
        ('professional', 'Professional & Formal'),
        ('patient', 'Patient & Supportive'),
        ('energetic', 'Energetic & Motivating'),
        ('analytical', 'Analytical & Detailed'),
        ('creative', 'Creative & Inspiring')
    ]
    
    TEACHING_STYLES = [
        ('socratic', 'Socratic Method (Question-based)'),
        ('explanatory', 'Direct Explanation'),
        ('example_driven', 'Example-driven Learning'),
        ('step_by_step', 'Step-by-step Guidance'),
        ('discovery', 'Guided Discovery'),
        ('adaptive', 'Adaptive to Student Needs')
    ]
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    
    # Personality Configuration
    personality_type = models.CharField(max_length=20, choices=PERSONALITY_TYPES)
    teaching_style = models.CharField(max_length=20, choices=TEACHING_STYLES)
    
    # Behavior Settings
    formality_level = models.IntegerField(default=3, help_text="Formality level 1-5")
    patience_level = models.IntegerField(default=4, help_text="Patience level 1-5")
    encouragement_frequency = models.IntegerField(default=3, help_text="How often to encourage 1-5")
    
    # Language and Communication
    vocabulary_level = models.CharField(max_length=20, default='adaptive', help_text="Vocabulary complexity")
    use_examples = models.BooleanField(default=True)
    use_analogies = models.BooleanField(default=True)
    use_humor = models.BooleanField(default=False)
    
    # Subject Specialization
    specialized_subjects = models.JSONField(default=list, help_text="Subjects this personality excels in")
    
    # Response Patterns
    greeting_templates = models.JSONField(default=list, help_text="Greeting message templates")
    explanation_templates = models.JSONField(default=list, help_text="Explanation templates")
    encouragement_phrases = models.JSONField(default=list, help_text="Phrases to encourage students")
    
    # Advanced Settings
    max_response_length = models.IntegerField(default=500, help_text="Maximum response length in words")
    question_asking_tendency = models.IntegerField(default=3, help_text="Tendency to ask questions 1-5")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tutor_personalities'
    
    def __str__(self):
        return f"{self.name} ({self.personality_type})"


class ConversationAnalytics(models.Model):
    """Analytics and insights from chat conversations"""
    
    session = models.OneToOneField(ChatSession, on_delete=models.CASCADE, related_name='analytics')
    
    # Conversation Quality Metrics
    coherence_score = models.FloatField(default=0.0, help_text="Conversation coherence 0-1")
    engagement_score = models.FloatField(default=0.0, help_text="Student engagement level 0-1")
    learning_progress = models.FloatField(default=0.0, help_text="Estimated learning progress 0-1")
    
    # Language Analysis
    sentiment_scores = models.JSONField(default=dict, help_text="Sentiment analysis over time")
    complexity_progression = models.JSONField(default=list, help_text="Language complexity progression")
    key_phrases = models.JSONField(default=list, help_text="Important phrases extracted")
    
    # Learning Analytics
    concepts_mastered = models.JSONField(default=list)
    concepts_struggling = models.JSONField(default=list)
    misconceptions_identified = models.JSONField(default=list)
    learning_style_indicators = models.JSONField(default=dict)
    
    # Tutor Performance
    response_quality_avg = models.FloatField(default=0.0)
    response_time_avg = models.FloatField(default=0.0)
    helpfulness_rating = models.FloatField(default=0.0)
    
    # Recommendations
    next_topics = models.JSONField(default=list, help_text="Recommended topics for next session")
    resource_suggestions = models.JSONField(default=list)
    improvement_areas = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'conversation_analytics'
    
    def __str__(self):
        return f"Analytics for {self.session}"


class KnowledgeBase(models.Model):
    """Knowledge base for AI tutor responses"""
    
    CONTENT_CATEGORIES = [
        ('concept', 'Concept Explanation'),
        ('example', 'Example/Case Study'),
        ('formula', 'Formula/Equation'),
        ('procedure', 'Step-by-step Procedure'),
        ('tip', 'Learning Tip'),
        ('common_mistake', 'Common Mistake'),
        ('analogy', 'Analogy/Metaphor'),
        ('resource', 'Learning Resource')
    ]
    
    title = models.CharField(max_length=200)
    content_category = models.CharField(max_length=20, choices=CONTENT_CATEGORIES)
    
    # Content
    content = models.TextField()
    keywords = models.JSONField(default=list, help_text="Keywords for matching")
    subjects = models.JSONField(default=list, help_text="Subject areas this applies to")
    
    # Metadata
    difficulty_level = models.CharField(max_length=20, default='medium')
    prerequisites = models.JSONField(default=list)
    related_concepts = models.JSONField(default=list)
    
    # Usage Statistics
    usage_count = models.IntegerField(default=0)
    success_rate = models.FloatField(default=0.0, help_text="Success rate when used")
    average_rating = models.FloatField(default=0.0)
    
    # Quality Control
    is_verified = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'knowledge_base'
        indexes = [
            models.Index(fields=['content_category']),
            models.Index(fields=['difficulty_level']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.content_category})"


class StudentQuestionPattern(models.Model):
    """Track common question patterns from students"""
    
    question_text = models.TextField()
    normalized_question = models.TextField(help_text="Normalized version for matching")
    
    # Classification
    question_type = models.CharField(max_length=50)
    subject_area = models.CharField(max_length=100)
    difficulty_level = models.CharField(max_length=20)
    
    # Pattern Analysis
    keywords = models.JSONField(default=list)
    concepts_involved = models.JSONField(default=list)
    common_followups = models.JSONField(default=list)
    
    # Statistics
    frequency = models.IntegerField(default=1)
    success_rate = models.FloatField(default=0.0, help_text="Rate of successful answers")
    
    # Response Templates
    effective_responses = models.JSONField(default=list)
    response_strategies = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'student_question_patterns'
        indexes = [
            models.Index(fields=['question_type', 'subject_area']),
            models.Index(fields=['frequency']),
        ]
    
    def __str__(self):
        return f"Pattern: {self.normalized_question[:50]}..."

