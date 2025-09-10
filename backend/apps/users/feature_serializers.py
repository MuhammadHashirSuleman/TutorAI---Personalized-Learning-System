from rest_framework import serializers
from django.utils import timezone
from .models import (
    Note, MotivationalQuote, DailyQuoteAssignment,
    SavedChatHistory, Goal, MilestoneReward, StudentProfile, DocumentSummary
)


class NoteSummarySerializer(serializers.ModelSerializer):
    """Serializer for note summaries"""
    
    class Meta:
        model = Note
        fields = ['id', 'title', 'summary', 'summary_generated_at']
        read_only_fields = ['id', 'summary_generated_at']


class MotivationalQuoteSerializer(serializers.ModelSerializer):
    """Serializer for motivational quotes"""
    
    class Meta:
        model = MotivationalQuote
        fields = [
            'id', 'quote_text', 'author', 'category', 
            'target_weak_subjects', 'target_low_motivation'
        ]


class DailyQuoteSerializer(serializers.ModelSerializer):
    """Serializer for daily quote assignments"""
    
    quote = MotivationalQuoteSerializer(read_only=True)
    
    class Meta:
        model = DailyQuoteAssignment
        fields = [
            'id', 'quote', 'date_assigned', 'viewed', 
            'viewed_at', 'liked'
        ]


class SavedChatHistorySerializer(serializers.ModelSerializer):
    """Serializer for saved chat history"""
    
    original_session_id = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = SavedChatHistory
        fields = [
            'id', 'title', 'messages_content', 'subject', 
            'topics_covered', 'message_count', 'session_duration',
            'tags', 'is_favorite', 'notes', 'original_session_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_original_session_id(self, obj):
        """Get original session ID, handle null sessions"""
        if obj.original_session:
            return str(obj.original_session.session_id)
        return None


class CreateSavedChatSerializer(serializers.Serializer):
    """Serializer for creating saved chats"""
    
    session_id = serializers.CharField()  # Accept string IDs from frontend
    title = serializers.CharField(max_length=200)
    tags = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        default=list
    )
    notes = serializers.CharField(required=False, allow_blank=True)
    messages = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list,
        help_text="Chat messages from frontend"
    )


class GoalSerializer(serializers.ModelSerializer):
    """Serializer for learning goals"""
    
    progress_percentage = serializers.ReadOnlyField()
    is_completed = serializers.ReadOnlyField()
    days_remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = Goal
        fields = [
            'id', 'title', 'description', 'goal_type', 'target_value',
            'current_progress', 'unit', 'start_date', 'target_date',
            'completed_at', 'status', 'reward_claimed', 'subject_focus',
            'difficulty_level', 'progress_percentage', 'is_completed',
            'days_remaining', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'start_date', 'current_progress', 'completed_at',
            'reward_claimed', 'created_at', 'updated_at'
        ]
    
    def get_days_remaining(self, obj):
        """Calculate days remaining until target date"""
        if obj.target_date:
            delta = obj.target_date.date() - timezone.now().date()
            return delta.days
        return None
    
    def validate_target_date(self, value):
        """Ensure target date is in the future"""
        if value <= timezone.now():
            raise serializers.ValidationError("Target date must be in the future.")
        return value


class MilestoneRewardSerializer(serializers.ModelSerializer):
    """Serializer for milestone rewards"""
    
    goal_title = serializers.CharField(source='goal.title', read_only=True)
    
    class Meta:
        model = MilestoneReward
        fields = [
            'id', 'reward_type', 'title', 'description', 'icon',
            'color', 'points_awarded', 'is_claimed', 'claimed_at',
            'is_visible', 'goal_title', 'created_at'
        ]
        read_only_fields = [
            'id', 'is_claimed', 'claimed_at', 'created_at'
        ]


class ClaimRewardSerializer(serializers.Serializer):
    """Serializer for claiming rewards"""
    
    reward_id = serializers.IntegerField()


class UpdateGoalProgressSerializer(serializers.Serializer):
    """Serializer for updating goal progress"""
    
    goal_id = serializers.IntegerField()
    increment = serializers.IntegerField(default=1)
    
    def validate_increment(self, value):
        if value <= 0:
            raise serializers.ValidationError("Increment must be positive.")
        return value


# ============ DOCUMENT SUMMARIZER SERIALIZERS ============

class DocumentSummarySerializer(serializers.ModelSerializer):
    """Serializer for document summaries"""
    
    word_count = serializers.ReadOnlyField()
    summary_word_count = serializers.ReadOnlyField()
    compression_ratio = serializers.ReadOnlyField()
    file_size_display = serializers.ReadOnlyField(source='get_file_size_display')
    
    class Meta:
        model = DocumentSummary
        fields = [
            'id', 'original_filename', 'file_type', 'file_size', 'file_size_display',
            'status', 'processing_error', 'extracted_text', 'summary', 'summary_metadata',
            'title', 'subject', 'tags', 'notes', 'is_favorite', 'view_count',
            'last_viewed', 'word_count', 'summary_word_count', 'compression_ratio',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'file_size', 'status', 'processing_error', 'extracted_text',
            'summary', 'summary_metadata', 'view_count', 'last_viewed',
            'created_at', 'updated_at'
        ]


class DocumentSummaryListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing document summaries"""
    
    word_count = serializers.ReadOnlyField()
    summary_word_count = serializers.ReadOnlyField()
    compression_ratio = serializers.ReadOnlyField()
    file_size_display = serializers.ReadOnlyField(source='get_file_size_display')
    
    class Meta:
        model = DocumentSummary
        fields = [
            'id', 'original_filename', 'file_type', 'file_size_display', 'status',
            'title', 'subject', 'tags', 'is_favorite', 'view_count',
            'word_count', 'summary_word_count', 'compression_ratio',
            'created_at', 'updated_at'
        ]


class DocumentUploadSerializer(serializers.Serializer):
    """Serializer for document upload"""
    
    file = serializers.FileField(
        help_text="PDF or DOCX file to process",
        required=True
    )
    title = serializers.CharField(
        max_length=200,
        required=False,
        allow_blank=True,
        help_text="Optional title for the document"
    )
    subject = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        help_text="Subject category"
    )
    tags = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        default=list,
        help_text="Tags for organization"
    )
    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="User notes about the document"
    )
    
    def validate_file(self, value):
        """Validate uploaded file"""
        # Check file extension
        filename = value.name.lower()
        if not (filename.endswith('.pdf') or filename.endswith('.docx')):
            raise serializers.ValidationError(
                "Only PDF and DOCX files are supported."
            )
        
        # Check file size (10MB limit)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError(
                "File size must be less than 10MB."
            )
        
        return value


class DocumentSummaryUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating document summary metadata"""
    
    class Meta:
        model = DocumentSummary
        fields = ['title', 'subject', 'tags', 'notes', 'is_favorite']


class DocumentSearchSerializer(serializers.Serializer):
    """Serializer for document search parameters"""
    
    query = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Search query for title, content, or tags"
    )
    file_type = serializers.ChoiceField(
        choices=[('all', 'All'), ('pdf', 'PDF'), ('docx', 'DOCX')],
        default='all',
        required=False
    )
    status = serializers.ChoiceField(
        choices=[('all', 'All'), ('completed', 'Completed'), ('processing', 'Processing'), ('failed', 'Failed')],
        default='all',
        required=False
    )
    subject = serializers.CharField(
        required=False,
        allow_blank=True
    )
    is_favorite = serializers.BooleanField(
        required=False
    )
    order_by = serializers.ChoiceField(
        choices=[
            ('-created_at', 'Newest First'),
            ('created_at', 'Oldest First'),
            ('title', 'Title A-Z'),
            ('-title', 'Title Z-A'),
            ('-view_count', 'Most Viewed')
        ],
        default='-created_at',
        required=False
    )
