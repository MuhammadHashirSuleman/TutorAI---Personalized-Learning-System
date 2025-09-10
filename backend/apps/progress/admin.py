from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Avg, Count
from .models import (
    StudentProgress, QuizResult, LearningGoal, PerformanceAnalytics
)


@admin.register(StudentProgress)
class StudentProgressAdmin(admin.ModelAdmin):
    list_display = [
        'student_name', 'course_title', 'activity_type', 'status',
        'completion_percentage', 'score_display', 'time_spent_formatted',
        'last_accessed'
    ]
    list_filter = [
        'activity_type', 'status', 'course__subject', 'difficulty_rating',
        'created_at'
    ]
    search_fields = [
        'student__email', 'student__first_name', 'student__last_name',
        'course__title', 'lesson__title'
    ]
    readonly_fields = ['created_at', 'updated_at', 'last_accessed']
    fieldsets = [
        ('Basic Information', {
            'fields': [
                'student', 'course', 'lesson', 'activity_type', 'status'
            ]
        }),
        ('Progress Details', {
            'fields': [
                'completion_percentage', 'time_spent', 'started_at',
                'completed_at', 'score', 'attempts', 'best_score'
            ]
        }),
        ('Learning Analytics', {
            'fields': [
                'difficulty_rating', 'engagement_level', 'notes', 'metadata'
            ]
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at', 'last_accessed'],
            'classes': ['collapse']
        })
    ]
    
    def student_name(self, obj):
        return obj.student.get_full_name() or obj.student.email
    student_name.short_description = 'Student'
    
    def course_title(self, obj):
        return obj.course.title if obj.course else '-'
    course_title.short_description = 'Course'
    
    def score_display(self, obj):
        if obj.score is not None:
            color = 'green' if obj.score >= 80 else 'orange' if obj.score >= 60 else 'red'
            return format_html(
                '<span style="color: {};">{:.1f}%</span>',
                color, obj.score
            )
        return '-'
    score_display.short_description = 'Score'
    
    def time_spent_formatted(self, obj):
        if obj.time_spent:
            hours = obj.time_spent // 60
            minutes = obj.time_spent % 60
            return f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
        return '0m'
    time_spent_formatted.short_description = 'Time Spent'


@admin.register(QuizResult)
class QuizResultAdmin(admin.ModelAdmin):
    list_display = [
        'student_name', 'quiz_title', 'attempt_number', 'status',
        'score_display', 'accuracy', 'time_taken_display', 'created_at'
    ]
    list_filter = [
        'status', 'quiz__course__subject', 'attempt_number', 'created_at'
    ]
    search_fields = [
        'student__email', 'student__first_name', 'student__last_name',
        'quiz__title', 'quiz__course__title'
    ]
    readonly_fields = ['created_at', 'updated_at', 'time_started']
    fieldsets = [
        ('Basic Information', {
            'fields': [
                'student', 'quiz', 'attempt_number', 'status'
            ]
        }),
        ('Results', {
            'fields': [
                'score', 'total_questions', 'correct_answers',
                'incorrect_answers', 'skipped_questions'
            ]
        }),
        ('Time Tracking', {
            'fields': [
                'time_started', 'time_completed', 'time_taken',
                'average_time_per_question'
            ]
        }),
        ('Analytics', {
            'fields': [
                'answers', 'question_analytics', 'strengths_identified',
                'weaknesses_identified', 'recommendations',
                'difficulty_progression', 'concept_mastery'
            ],
            'classes': ['collapse']
        })
    ]
    
    def student_name(self, obj):
        return obj.student.get_full_name() or obj.student.email
    student_name.short_description = 'Student'
    
    def quiz_title(self, obj):
        return obj.quiz.title if obj.quiz else '-'
    quiz_title.short_description = 'Quiz'
    
    def score_display(self, obj):
        color = 'green' if obj.score >= 80 else 'orange' if obj.score >= 60 else 'red'
        return format_html(
            '<span style="color: {};">{:.1f}%</span>',
            color, obj.score
        )
    score_display.short_description = 'Score'
    
    def accuracy(self, obj):
        if obj.total_questions > 0:
            acc = (obj.correct_answers / obj.total_questions) * 100
            return f"{acc:.1f}%"
        return '0%'
    accuracy.short_description = 'Accuracy'
    
    def time_taken_display(self, obj):
        if obj.time_taken:
            minutes = obj.time_taken // 60
            seconds = obj.time_taken % 60
            return f"{minutes}m {seconds}s" if minutes > 0 else f"{seconds}s"
        return '0s'
    time_taken_display.short_description = 'Time Taken'




@admin.register(LearningGoal)
class LearningGoalAdmin(admin.ModelAdmin):
    list_display = [
        'student_name', 'title', 'goal_type', 'status',
        'progress_percentage', 'target_completion_date',
        'days_remaining'
    ]
    list_filter = [
        'goal_type', 'status', 'created_at', 'target_completion_date'
    ]
    search_fields = [
        'student__email', 'student__first_name', 'student__last_name',
        'title', 'description'
    ]
    readonly_fields = ['created_at', 'updated_at', 'achieved_at']
    filter_horizontal = ['related_courses', 'related_subjects']
    fieldsets = [
        ('Basic Information', {
            'fields': [
                'student', 'title', 'description', 'goal_type'
            ]
        }),
        ('Progress Tracking', {
            'fields': [
                'status', 'progress_percentage', 'target_score',
                'target_completion_date'
            ]
        }),
        ('Relationships', {
            'fields': [
                'related_courses', 'related_subjects'
            ]
        }),
        ('Milestones & Recommendations', {
            'fields': [
                'milestones', 'completed_milestones',
                'suggested_resources', 'adaptive_recommendations'
            ],
            'classes': ['collapse']
        })
    ]
    
    def student_name(self, obj):
        return obj.student.get_full_name() or obj.student.email
    student_name.short_description = 'Student'
    
    def days_remaining(self, obj):
        if obj.target_completion_date and obj.status != 'achieved':
            from django.utils import timezone
            today = timezone.now().date()
            delta = obj.target_completion_date - today
            days = delta.days
            
            if days < 0:
                return format_html('<span style="color: red;">Overdue by {} days</span>', abs(days))
            elif days == 0:
                return format_html('<span style="color: orange;">Due today</span>')
            elif days <= 7:
                return format_html('<span style="color: orange;">{} days left</span>', days)
            else:
                return f"{days} days left"
        return '-'
    days_remaining.short_description = 'Time Remaining'


@admin.register(PerformanceAnalytics)
class PerformanceAnalyticsAdmin(admin.ModelAdmin):
    list_display = [
        'student_name', 'analysis_type', 'overall_score',
        'improvement_rate', 'start_date', 'end_date', 'created_at'
    ]
    list_filter = [
        'analysis_type', 'course__subject', 'subject',
        'start_date', 'created_at'
    ]
    search_fields = [
        'student__email', 'student__first_name', 'student__last_name',
        'course__title', 'subject__name'
    ]
    readonly_fields = ['created_at']
    fieldsets = [
        ('Basic Information', {
            'fields': [
                'student', 'analysis_type',
                'course', 'subject', 'start_date', 'end_date'
            ]
        }),
        ('Performance Metrics', {
            'fields': [
                'overall_score', 'improvement_rate', 'consistency_score',
                'class_average', 'percentile_rank'
            ]
        }),
        ('Analytics', {
            'fields': [
                'strengths', 'weaknesses', 'recommendations',
                'predicted_outcomes'
            ]
        }),
        ('Engagement Data', {
            'fields': [
                'study_time_total', 'login_frequency', 'resource_usage'
            ]
        }),
        ('AI Insights', {
            'fields': [
                'learning_style_detected', 'difficulty_preferences',
                'optimal_study_times'
            ],
            'classes': ['collapse']
        })
    ]
    
    def student_name(self, obj):
        return obj.student.get_full_name() or obj.student.email
    student_name.short_description = 'Student'
