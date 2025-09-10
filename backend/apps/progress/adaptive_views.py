"""
Adaptive Learning System API Views
Provides endpoints for adaptive content delivery and personalized learning
"""

from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Avg, Count, Q
from datetime import timedelta
import logging

from .adaptive_learning import adaptive_learning_engine
from .models import StudentProgress, QuizResult
from apps.courses.models import Course

User = get_user_model()
logger = logging.getLogger(__name__)

# Custom permissions
class IsStudentOrTeacher(permissions.BasePermission):
    """Allow access to students (for their own data) and teachers"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role in ['student', 'teacher']

class IsStudent(permissions.BasePermission):
    """Allow access only to students"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'student'

class IsTeacher(permissions.BasePermission):
    """Allow access only to teachers"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'teacher'

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsStudentOrTeacher])
def analyze_learning_pattern(request, student_id=None):
    """
    Analyze student's learning patterns for adaptive content delivery
    Students can only access their own patterns, teachers can access their students'
    """
    try:
        # Determine target student
        if student_id is None:
            if request.user.role != 'student':
                return Response(
                    {'error': 'student_id is required for teachers'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            target_student_id = request.user.id
        else:
            # Access by ID (teachers or self-access)
            if request.user.role == 'student' and request.user.id != student_id:
                return Response(
                    {'error': 'Students can only access their own learning patterns'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            if request.user.role == 'teacher':
                # Verify teacher has access to this student
                student = get_object_or_404(User, id=student_id, role='student')
                student_courses = student.enrollments.values_list('course_id', flat=True)
                teacher_courses = Course.objects.filter(instructor=request.user).values_list('id', flat=True)
                
                if not set(student_courses).intersection(set(teacher_courses)):
                    return Response(
                        {'error': 'Access denied - student not in your courses'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            
            target_student_id = student_id
        
        # Analyze learning pattern
        learning_pattern = adaptive_learning_engine.analyze_student_learning_pattern(target_student_id)
        
        if 'error' in learning_pattern:
            return Response(
                {'error': 'Failed to analyze learning pattern', 'details': learning_pattern['error']},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Add metadata
        learning_pattern['metadata'] = {
            'requested_by': request.user.id,
            'requester_role': request.user.role,
            'analysis_timestamp': timezone.now().isoformat()
        }
        
        return Response(learning_pattern)
        
    except Exception as e:
        logger.error(f"Learning pattern analysis error: {str(e)}")
        return Response(
            {'error': 'Failed to analyze learning pattern', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsStudent])
def get_adaptive_content_plan(request):
    """
    Get personalized adaptive content plan for authenticated student
    """
    try:
        student = request.user
        course_id = request.query_params.get('course_id')
        
        if course_id:
            # Verify student is enrolled in the course
            try:
                course_id = int(course_id)
                if not student.enrollments.filter(course_id=course_id).exists():
                    return Response(
                        {'error': 'You are not enrolled in this course'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except ValueError:
                return Response(
                    {'error': 'Invalid course_id'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Generate adaptive content plan
        content_plan = adaptive_learning_engine.generate_adaptive_content_plan(student.id, course_id)
        
        if 'error' in content_plan:
            return Response(
                {'error': 'Failed to generate adaptive content plan', 'details': content_plan['error']},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response(content_plan)
        
    except Exception as e:
        logger.error(f"Adaptive content plan error: {str(e)}")
        return Response(
            {'error': 'Failed to generate adaptive content plan', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsStudent])
def update_adaptive_parameters(request):
    """
    Update adaptive parameters based on recent performance
    """
    try:
        student = request.user
        recent_performance = request.data.get('recent_performance', {})
        
        # Validate recent performance data
        required_fields = ['average_score', 'trend', 'consistency']
        missing_fields = [field for field in required_fields if field not in recent_performance]
        
        if missing_fields:
            return Response(
                {'error': f'Missing required fields: {", ".join(missing_fields)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update adaptive parameters
        update_result = adaptive_learning_engine.update_adaptive_parameters_based_on_performance(
            student.id, 
            recent_performance
        )
        
        if 'error' in update_result:
            return Response(
                {'error': 'Failed to update adaptive parameters', 'details': update_result['error']},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response({
            'success': True,
            'update_result': update_result,
            'message': 'Adaptive parameters updated successfully'
        })
        
    except Exception as e:
        logger.error(f"Adaptive parameters update error: {str(e)}")
        return Response(
            {'error': 'Failed to update adaptive parameters', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsStudent])
def get_personalized_schedule(request):
    """
    Get personalized study schedule based on learning patterns
    """
    try:
        student = request.user
        course_id = request.query_params.get('course_id')
        
        # First get learning pattern
        learning_pattern = adaptive_learning_engine.analyze_student_learning_pattern(student.id)
        
        if 'error' in learning_pattern:
            return Response(
                {'error': 'Failed to analyze learning pattern for schedule generation'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Generate content plan to get adaptive content
        content_plan = adaptive_learning_engine.generate_adaptive_content_plan(student.id, course_id)
        
        if 'error' in content_plan:
            return Response(
                {'error': 'Failed to generate content for schedule'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Extract schedule from content plan
        personalized_schedule = content_plan.get('personalized_schedule', {})
        
        # Add additional schedule insights
        schedule_insights = {
            'schedule': personalized_schedule,
            'optimization_tips': _generate_schedule_optimization_tips(learning_pattern),
            'productivity_insights': _generate_productivity_insights(learning_pattern),
            'recommended_breaks': _calculate_break_schedule(learning_pattern),
            'generated_at': timezone.now().isoformat()
        }
        
        return Response(schedule_insights)
        
    except Exception as e:
        logger.error(f"Personalized schedule error: {str(e)}")
        return Response(
            {'error': 'Failed to generate personalized schedule', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsStudent])
def get_difficulty_recommendation(request):
    """
    Get recommended difficulty level for next content
    """
    try:
        student = request.user
        subject = request.query_params.get('subject', '')
        
        # Analyze learning pattern
        learning_pattern = adaptive_learning_engine.analyze_student_learning_pattern(student.id)
        
        if 'error' in learning_pattern:
            return Response(
                {'error': 'Failed to analyze learning pattern'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        adaptive_params = learning_pattern.get('adaptive_parameters')
        difficulty_preferences = learning_pattern.get('difficulty_preferences', {})
        
        if not adaptive_params:
            return Response(
                {'error': 'No adaptive parameters available'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get subject-specific performance if available
        subject_performance = None
        if subject:
            performance_patterns = learning_pattern.get('performance_patterns', {})
            subject_perf_data = performance_patterns.get('subject_performance', {})
            subject_performance = subject_perf_data.get(subject)
        
        # Calculate recommended difficulty
        recommended_difficulty = _calculate_recommended_difficulty(
            adaptive_params, 
            difficulty_preferences, 
            subject_performance
        )
        
        recommendation = {
            'recommended_difficulty': recommended_difficulty['level'],
            'confidence': recommended_difficulty['confidence'],
            'reasoning': recommended_difficulty['reasoning'],
            'subject': subject or 'General',
            'current_performance_level': _get_performance_level(learning_pattern),
            'suggested_progression': _get_difficulty_progression(learning_pattern),
            'generated_at': timezone.now().isoformat()
        }
        
        return Response(recommendation)
        
    except Exception as e:
        logger.error(f"Difficulty recommendation error: {str(e)}")
        return Response(
            {'error': 'Failed to generate difficulty recommendation', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsStudent])
def get_learning_velocity_insights(request):
    """
    Get insights about student's learning velocity and suggestions for improvement
    """
    try:
        student = request.user
        
        # Analyze learning pattern
        learning_pattern = adaptive_learning_engine.analyze_student_learning_pattern(student.id)
        
        if 'error' in learning_pattern:
            return Response(
                {'error': 'Failed to analyze learning pattern'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        learning_velocity = learning_pattern.get('learning_velocity', {})
        adaptive_params = learning_pattern.get('adaptive_parameters')
        
        velocity_insights = {
            'current_velocity': learning_velocity,
            'velocity_analysis': _analyze_velocity_factors(learning_pattern),
            'improvement_suggestions': _generate_velocity_improvement_suggestions(learning_velocity),
            'optimal_content_pace': adaptive_params.content_pace if adaptive_params else 1.0,
            'predicted_completion_times': _calculate_predicted_completion_times(learning_pattern),
            'velocity_comparison': _compare_velocity_with_peers(learning_velocity),
            'generated_at': timezone.now().isoformat()
        }
        
        return Response(velocity_insights)
        
    except Exception as e:
        logger.error(f"Learning velocity insights error: {str(e)}")
        return Response(
            {'error': 'Failed to generate learning velocity insights', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsTeacher])
def get_class_adaptive_summary(request):
    """
    Get adaptive learning summary for all students in teacher's classes
    """
    try:
        teacher = request.user
        
        # Get all students in teacher's courses
        teacher_courses = Course.objects.filter(instructor=teacher)
        student_ids = teacher_courses.values_list('enrollments__student_id', flat=True).distinct()
        
        # Analyze patterns for each student (limit for performance)
        class_adaptive_summary = {
            'total_students': len(student_ids),
            'students_analyzed': 0,
            'velocity_distribution': {
                'very_slow': 0,
                'slow': 0,
                'normal': 0,
                'fast': 0,
                'very_fast': 0
            },
            'difficulty_preferences': {
                'beginner': 0,
                'intermediate': 0,
                'advanced': 0
            },
            'common_patterns': [],
            'recommendations': [],
            'generated_at': timezone.now().isoformat()
        }
        
        pattern_data = []
        
        for student_id in student_ids[:20]:  # Limit for performance
            try:
                student = User.objects.get(id=student_id, role='student')
                learning_pattern = adaptive_learning_engine.analyze_student_learning_pattern(student_id)
                
                if 'error' not in learning_pattern:
                    class_adaptive_summary['students_analyzed'] += 1
                    pattern_data.append(learning_pattern)
                    
                    # Update velocity distribution
                    velocity = learning_pattern.get('learning_velocity', {}).get('velocity', 'normal')
                    class_adaptive_summary['velocity_distribution'][velocity] += 1
                    
                    # Update difficulty preferences
                    optimal_diff = learning_pattern.get('difficulty_preferences', {}).get('optimal_difficulty', 'intermediate')
                    class_adaptive_summary['difficulty_preferences'][optimal_diff] += 1
                    
            except Exception as e:
                logger.warning(f"Error analyzing student {student_id}: {str(e)}")
                continue
        
        # Generate class-level insights
        if pattern_data:
            class_adaptive_summary['common_patterns'] = _identify_common_patterns(pattern_data)
            class_adaptive_summary['recommendations'] = _generate_class_recommendations(pattern_data)
        
        return Response(class_adaptive_summary)
        
    except Exception as e:
        logger.error(f"Class adaptive summary error: {str(e)}")
        return Response(
            {'error': 'Failed to generate class adaptive summary', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsStudent])
def submit_learning_feedback(request):
    """
    Allow students to provide feedback on adaptive content effectiveness
    """
    try:
        student = request.user
        feedback_data = request.data
        
        # Validate feedback data
        required_fields = ['content_effectiveness', 'difficulty_appropriateness', 'schedule_suitability']
        missing_fields = [field for field in required_fields if field not in feedback_data]
        
        if missing_fields:
            return Response(
                {'error': f'Missing required feedback fields: {", ".join(missing_fields)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Process feedback and adjust parameters
        feedback_analysis = {
            'student_id': student.id,
            'feedback_received': feedback_data,
            'adjustments_made': [],
            'submitted_at': timezone.now().isoformat()
        }
        
        # Analyze feedback and suggest parameter adjustments
        if feedback_data.get('difficulty_appropriateness', 3) < 2:  # Too hard
            feedback_analysis['adjustments_made'].append('Reduce difficulty adjustment')
            
        elif feedback_data.get('difficulty_appropriateness', 3) > 4:  # Too easy
            feedback_analysis['adjustments_made'].append('Increase difficulty adjustment')
        
        if feedback_data.get('schedule_suitability', 3) < 2:  # Schedule too aggressive
            feedback_analysis['adjustments_made'].append('Reduce content pace')
            
        elif feedback_data.get('content_effectiveness', 3) < 2:  # Content not effective
            feedback_analysis['adjustments_made'].append('Increase repetition factor')
        
        # In a real implementation, you would store this feedback and use it to improve the system
        
        return Response({
            'success': True,
            'feedback_analysis': feedback_analysis,
            'message': 'Feedback received and will be used to improve your learning experience'
        })
        
    except Exception as e:
        logger.error(f"Learning feedback submission error: {str(e)}")
        return Response(
            {'error': 'Failed to process learning feedback', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# Helper functions
def _generate_schedule_optimization_tips(learning_pattern):
    """Generate schedule optimization tips"""
    tips = []
    time_patterns = learning_pattern.get('time_patterns', {})
    
    best_hour = time_patterns.get('best_performance_hour')
    if best_hour:
        tips.append(f"Schedule important study sessions around {best_hour}:00 for optimal performance")
    
    time_efficiency = time_patterns.get('time_efficiency', 'moderate')
    if time_efficiency == 'slow':
        tips.append("Consider breaking study sessions into smaller chunks with more frequent breaks")
    elif time_efficiency == 'fast':
        tips.append("You can handle longer study sessions - consider consolidating related topics")
    
    return tips

def _generate_productivity_insights(learning_pattern):
    """Generate productivity insights"""
    insights = {}
    performance_patterns = learning_pattern.get('performance_patterns', {})
    
    consistency = performance_patterns.get('consistency_level', 'medium')
    insights['consistency_feedback'] = {
        'high': "Your performance is very consistent - maintain this steady approach",
        'medium': "Your performance shows moderate variation - focus on consistent study habits",
        'low': "Your performance varies significantly - consider establishing a regular routine"
    }.get(consistency, "Continue monitoring your consistency")
    
    trend = performance_patterns.get('performance_trend', 'stable')
    insights['trend_feedback'] = {
        'improving': "Great! Your performance is improving - keep up the momentum",
        'declining': "Your recent performance shows decline - consider reviewing study strategies",
        'stable': "Your performance is stable - look for opportunities to challenge yourself more"
    }.get(trend, "Continue monitoring your progress")
    
    return insights

def _calculate_break_schedule(learning_pattern):
    """Calculate optimal break schedule"""
    adaptive_params = learning_pattern.get('adaptive_parameters')
    if not adaptive_params:
        return {'break_interval': 25, 'break_duration': 5}
    
    session_time = adaptive_params.estimated_completion_time
    break_interval = max(15, min(45, session_time // 2))
    break_duration = max(5, min(15, break_interval // 5))
    
    return {
        'break_interval': break_interval,
        'break_duration': break_duration,
        'technique': 'Pomodoro-style' if break_interval <= 25 else 'Extended focus'
    }

def _calculate_recommended_difficulty(adaptive_params, difficulty_preferences, subject_performance):
    """Calculate recommended difficulty level"""
    base_difficulty = difficulty_preferences.get('optimal_difficulty', 'intermediate')
    adjustment = adaptive_params.difficulty_adjustment
    
    difficulty_levels = ['beginner', 'intermediate', 'advanced']
    current_index = difficulty_levels.index(base_difficulty) if base_difficulty in difficulty_levels else 1
    
    # Adjust based on subject performance
    if subject_performance:
        subject_avg = subject_performance.get('mean', 70)
        if subject_avg >= 85:
            adjustment += 0.2
        elif subject_avg < 60:
            adjustment -= 0.3
    
    # Calculate final difficulty
    if adjustment > 0.3:
        recommended_index = min(len(difficulty_levels) - 1, current_index + 1)
        confidence = 'high'
        reasoning = 'Strong performance indicates readiness for increased difficulty'
    elif adjustment < -0.3:
        recommended_index = max(0, current_index - 1)
        confidence = 'high'
        reasoning = 'Performance suggests need for easier content to build confidence'
    else:
        recommended_index = current_index
        confidence = 'medium'
        reasoning = 'Current difficulty level appears appropriate'
    
    return {
        'level': difficulty_levels[recommended_index],
        'confidence': confidence,
        'reasoning': reasoning
    }

def _get_performance_level(learning_pattern):
    """Get student's current performance level"""
    avg_score = learning_pattern.get('performance_patterns', {}).get('overall_average', 70)
    
    if avg_score >= 90:
        return 'excellent'
    elif avg_score >= 80:
        return 'proficient'
    elif avg_score >= 70:
        return 'developing'
    else:
        return 'needs_improvement'

def _get_difficulty_progression(learning_pattern):
    """Get suggested difficulty progression"""
    current_level = learning_pattern.get('difficulty_preferences', {}).get('optimal_difficulty', 'intermediate')
    performance_trend = learning_pattern.get('performance_patterns', {}).get('performance_trend', 'stable')
    
    progressions = {
        'beginner': ['beginner', 'intermediate', 'advanced'],
        'intermediate': ['intermediate', 'advanced', 'expert'],
        'advanced': ['advanced', 'expert']
    }
    
    current_progression = progressions.get(current_level, ['intermediate', 'advanced'])
    
    if performance_trend == 'improving':
        return current_progression
    elif performance_trend == 'declining':
        return current_progression[:2] if len(current_progression) > 1 else current_progression
    else:
        return current_progression[:2] if len(current_progression) > 2 else current_progression

def _analyze_velocity_factors(learning_pattern):
    """Analyze factors affecting learning velocity"""
    factors = {}
    
    consistency = learning_pattern.get('performance_patterns', {}).get('consistency_level', 'medium')
    factors['consistency_impact'] = {
        'high': 'High consistency supports steady learning velocity',
        'medium': 'Moderate consistency allows for steady progress with room for improvement',
        'low': 'Low consistency may be limiting learning velocity'
    }.get(consistency)
    
    time_efficiency = learning_pattern.get('time_patterns', {}).get('time_efficiency', 'moderate')
    factors['time_efficiency_impact'] = {
        'fast': 'Efficient time use enables faster learning velocity',
        'moderate': 'Good time efficiency supports normal learning velocity',
        'slow': 'Time efficiency could be improved to increase learning velocity'
    }.get(time_efficiency)
    
    return factors

def _generate_velocity_improvement_suggestions(learning_velocity):
    """Generate suggestions for improving learning velocity"""
    suggestions = []
    velocity = learning_velocity.get('velocity', 'normal')
    
    if velocity in ['very_slow', 'slow']:
        suggestions.extend([
            'Break down complex topics into smaller, manageable chunks',
            'Use active learning techniques like summarization and self-testing',
            'Establish a consistent daily study routine',
            'Identify and address specific knowledge gaps'
        ])
    elif velocity == 'normal':
        suggestions.extend([
            'Consider challenging yourself with slightly more difficult content',
            'Use spaced repetition to reinforce learning',
            'Try teaching concepts to others to deepen understanding'
        ])
    elif velocity in ['fast', 'very_fast']:
        suggestions.extend([
            'Take on more challenging projects or advanced topics',
            'Help slower learners to reinforce your own knowledge',
            'Explore connections between different subjects'
        ])
    
    return suggestions

def _calculate_predicted_completion_times(learning_pattern):
    """Calculate predicted completion times for different content types"""
    adaptive_params = learning_pattern.get('adaptive_parameters')
    if not adaptive_params:
        return {}
    
    base_time = adaptive_params.estimated_completion_time
    pace = adaptive_params.content_pace
    
    return {
        'quiz_10_questions': int(base_time * 0.6 / pace),
        'lesson_reading': int(base_time * 0.8 / pace),
        'practice_exercise': int(base_time * 0.4 / pace),
        'comprehensive_review': int(base_time * 1.5 / pace)
    }

def _compare_velocity_with_peers(learning_velocity):
    """Compare student's velocity with typical ranges"""
    velocity = learning_velocity.get('velocity', 'normal')
    
    comparisons = {
        'very_slow': 'Slower than 90% of learners - focus on fundamental skills',
        'slow': 'Slower than 70% of learners - consider additional support',
        'normal': 'Similar to 60% of learners - typical learning pace',
        'fast': 'Faster than 70% of learners - consider advanced challenges',
        'very_fast': 'Faster than 90% of learners - excellent learning capacity'
    }
    
    return {
        'comparison': comparisons.get(velocity, 'Typical learning pace'),
        'percentile': {
            'very_slow': 10,
            'slow': 30,
            'normal': 50,
            'fast': 75,
            'very_fast': 95
        }.get(velocity, 50)
    }

def _identify_common_patterns(pattern_data):
    """Identify common learning patterns across students"""
    patterns = []
    
    # Analyze velocity distribution
    velocities = [p.get('learning_velocity', {}).get('velocity', 'normal') for p in pattern_data]
    most_common_velocity = max(set(velocities), key=velocities.count)
    patterns.append(f"Most common learning velocity: {most_common_velocity}")
    
    # Analyze performance consistency
    consistencies = [p.get('performance_patterns', {}).get('consistency_level', 'medium') for p in pattern_data]
    most_common_consistency = max(set(consistencies), key=consistencies.count)
    patterns.append(f"Most common consistency level: {most_common_consistency}")
    
    return patterns

def _generate_class_recommendations(pattern_data):
    """Generate recommendations for the entire class"""
    recommendations = []
    
    # Analyze overall performance
    avg_scores = [p.get('performance_patterns', {}).get('overall_average', 70) for p in pattern_data if p.get('performance_patterns', {}).get('overall_average')]
    
    if avg_scores:
        class_avg = sum(avg_scores) / len(avg_scores)
        
        if class_avg < 65:
            recommendations.append({
                'type': 'performance_support',
                'priority': 'high',
                'suggestion': 'Consider additional support materials or tutoring for the class'
            })
        elif class_avg > 85:
            recommendations.append({
                'type': 'advanced_challenge',
                'priority': 'medium',
                'suggestion': 'Class is performing well - consider introducing more challenging content'
            })
    
    return recommendations
