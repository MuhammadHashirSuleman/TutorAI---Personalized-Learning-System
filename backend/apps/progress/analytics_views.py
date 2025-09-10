"""
Student Performance Analytics Views
Detailed student performance tracking with charts data and insights
Provides data in format ready for frontend visualization libraries
"""

from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Q, Avg, Count, Sum, Max, Min, F
from django.utils import timezone
from datetime import datetime, timedelta
import logging
import json

from apps.courses.models import Course, CourseEnrollment, Quiz
from .models import (
    StudentProgress, QuizResult, ClassRoom, ClassEnrollment,
    LearningGoal, PerformanceAnalytics
)
from apps.assessments.ai_services import StudentAnalyzer

User = get_user_model()
logger = logging.getLogger(__name__)

# Custom permissions
class IsTeacherOrStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(request.user, 'role', None) in ['teacher', 'student']

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsTeacherOrStudent])
def student_performance_charts(request, student_id=None):
    """
    Get comprehensive chart data for student performance visualization
    Students can only view their own data, teachers can view their students' data
    """
    user = request.user
    
    # Determine target student
    if student_id and user.role == 'teacher':
        try:
            target_student = User.objects.get(id=student_id, role='student')
            # Verify teacher has access to this student
            if not CourseEnrollment.objects.filter(
                student=target_student,
                course__instructor=user,
                is_active=True
            ).exists():
                return Response(
                    {'error': 'Access denied to this student'},
                    status=status.HTTP_403_FORBIDDEN
                )
        except User.DoesNotExist:
            return Response(
                {'error': 'Student not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    elif user.role == 'student':
        target_student = user
    else:
        return Response(
            {'error': 'Invalid request'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Optional course filter
    course_id = request.query_params.get('course_id')
    time_range = request.query_params.get('time_range', '30')  # days
    
    try:
        # Time range setup
        end_date = timezone.now()
        start_date = end_date - timedelta(days=int(time_range))
        
        # Base queryset
        quiz_results = QuizResult.objects.filter(
            student=target_student,
            status='completed',
            created_at__gte=start_date
        ).select_related('quiz', 'quiz__course')
        
        if course_id:
            quiz_results = quiz_results.filter(quiz__course_id=course_id)
        
        # 1. Performance Over Time Chart
        performance_timeline = _generate_performance_timeline(quiz_results, start_date, end_date)
        
        # 2. Score Distribution Chart
        score_distribution = _generate_score_distribution(quiz_results)
        
        # 3. Subject/Course Performance Chart
        subject_performance = _generate_subject_performance(quiz_results)
        
        # 4. Difficulty Level Performance Chart
        difficulty_performance = _generate_difficulty_performance(quiz_results)
        
        # 5. Concept Mastery Radar Chart
        concept_mastery = _generate_concept_mastery_chart(target_student, course_id)
        
        # 6. Time Analysis Chart
        time_analysis = _generate_time_analysis_chart(quiz_results)
        
        # 7. Progress Streak Chart
        progress_streak = _generate_progress_streak(target_student, course_id, start_date, end_date)
        
        # 8. Comparison with Class Average
        class_comparison = _generate_class_comparison(target_student, quiz_results, course_id)
        
        # Summary statistics
        summary_stats = _generate_summary_statistics(quiz_results, target_student, course_id)
        
        chart_data = {
            'student_info': {
                'id': target_student.id,
                'email': target_student.email,
                'name': f"{target_student.first_name or ''} {target_student.last_name or ''}".strip()
            },
            'time_range': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': int(time_range)
            },
            'charts': {
                'performance_timeline': performance_timeline,
                'score_distribution': score_distribution,
                'subject_performance': subject_performance,
                'difficulty_performance': difficulty_performance,
                'concept_mastery': concept_mastery,
                'time_analysis': time_analysis,
                'progress_streak': progress_streak,
                'class_comparison': class_comparison
            },
            'summary_stats': summary_stats,
            'insights': _generate_performance_insights(
                quiz_results, target_student, course_id
            )
        }
        
        return Response(chart_data)
        
    except Exception as e:
        logger.error(f"Performance charts error: {str(e)}")
        return Response(
            {'error': 'Failed to generate performance charts', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def _generate_performance_timeline(quiz_results, start_date, end_date):
    """Generate line chart data for performance over time"""
    timeline_data = []
    
    # Group results by day
    daily_scores = {}
    for result in quiz_results:
        date_str = result.created_at.date().isoformat()
        if date_str not in daily_scores:
            daily_scores[date_str] = []
        daily_scores[date_str].append(result.score)
    
    # Calculate daily averages
    for date_str, scores in daily_scores.items():
        timeline_data.append({
            'date': date_str,
            'average_score': round(sum(scores) / len(scores), 1),
            'quiz_count': len(scores),
            'best_score': max(scores),
            'worst_score': min(scores)
        })
    
    # Sort by date
    timeline_data.sort(key=lambda x: x['date'])
    
    # Calculate trend line
    if len(timeline_data) >= 2:
        scores = [point['average_score'] for point in timeline_data]
        trend = _calculate_trend(scores)
        
        return {
            'type': 'line',
            'title': 'Performance Over Time',
            'data': timeline_data,
            'trend': trend,
            'x_axis': 'date',
            'y_axis': 'average_score',
            'description': f'Daily average quiz scores over {len(timeline_data)} days'
        }
    
    return {
        'type': 'line',
        'title': 'Performance Over Time',
        'data': timeline_data,
        'trend': 'insufficient_data',
        'x_axis': 'date',
        'y_axis': 'average_score',
        'description': 'Insufficient data for trend analysis'
    }

def _generate_score_distribution(quiz_results):
    """Generate histogram data for score distribution"""
    score_ranges = {
        'A (90-100)': {'min': 90, 'max': 100, 'count': 0, 'color': '#4CAF50'},
        'B (80-89)': {'min': 80, 'max': 89, 'count': 0, 'color': '#8BC34A'},
        'C (70-79)': {'min': 70, 'max': 79, 'count': 0, 'color': '#FFC107'},
        'D (60-69)': {'min': 60, 'max': 69, 'count': 0, 'color': '#FF9800'},
        'F (0-59)': {'min': 0, 'max': 59, 'count': 0, 'color': '#F44336'}
    }
    
    # Count scores in each range
    for result in quiz_results:
        score = result.score
        for grade, range_info in score_ranges.items():
            if range_info['min'] <= score <= range_info['max']:
                range_info['count'] += 1
                break
    
    # Convert to chart format
    distribution_data = [
        {
            'grade': grade,
            'count': info['count'],
            'percentage': round((info['count'] / len(quiz_results) * 100), 1) if quiz_results else 0,
            'color': info['color']
        }
        for grade, info in score_ranges.items()
    ]
    
    return {
        'type': 'bar',
        'title': 'Score Distribution',
        'data': distribution_data,
        'x_axis': 'grade',
        'y_axis': 'count',
        'total_quizzes': len(quiz_results),
        'description': f'Distribution of {len(quiz_results)} quiz scores by grade'
    }

def _generate_subject_performance(quiz_results):
    """Generate chart data for performance by subject/course"""
    subject_stats = {}
    
    for result in quiz_results:
        course = result.quiz.course
        subject_name = course.subject.name
        
        if subject_name not in subject_stats:
            subject_stats[subject_name] = {
                'scores': [],
                'course_titles': set()
            }
        
        subject_stats[subject_name]['scores'].append(result.score)
        subject_stats[subject_name]['course_titles'].add(course.title)
    
    # Calculate averages
    performance_data = []
    for subject, stats in subject_stats.items():
        performance_data.append({
            'subject': subject,
            'average_score': round(sum(stats['scores']) / len(stats['scores']), 1),
            'quiz_count': len(stats['scores']),
            'course_count': len(stats['course_titles']),
            'best_score': max(stats['scores']),
            'worst_score': min(stats['scores'])
        })
    
    # Sort by average score
    performance_data.sort(key=lambda x: x['average_score'], reverse=True)
    
    return {
        'type': 'bar',
        'title': 'Performance by Subject',
        'data': performance_data,
        'x_axis': 'subject',
        'y_axis': 'average_score',
        'description': f'Average performance across {len(performance_data)} subjects'
    }

def _generate_difficulty_performance(quiz_results):
    """Generate chart data for performance by difficulty level"""
    difficulty_stats = {'easy': [], 'medium': [], 'hard': []}
    
    for result in quiz_results:
        difficulty = result.quiz.difficulty_level
        if difficulty in difficulty_stats:
            difficulty_stats[difficulty].append(result.score)
    
    difficulty_data = []
    for difficulty, scores in difficulty_stats.items():
        if scores:  # Only include difficulties with data
            difficulty_data.append({
                'difficulty': difficulty.capitalize(),
                'average_score': round(sum(scores) / len(scores), 1),
                'quiz_count': len(scores),
                'best_score': max(scores),
                'worst_score': min(scores),
                'std_dev': round(_calculate_standard_deviation(scores), 1)
            })
    
    return {
        'type': 'radar',
        'title': 'Performance by Difficulty Level',
        'data': difficulty_data,
        'description': f'Performance comparison across difficulty levels'
    }

def _generate_concept_mastery_chart(student, course_id):
    """Generate radar chart for concept mastery levels"""
    try:
        analyzer = StudentAnalyzer(student.id)
        
        # Get weaknesses and strengths
        weaknesses = analyzer.identify_weaknesses(course_id, limit=10)
        strengths = analyzer.get_strengths(course_id, limit=10)
        
        # Combine all concepts
        all_concepts = {}
        
        # Add weaknesses (low mastery)
        for weakness in weaknesses:
            all_concepts[weakness['concept']] = {
                'mastery_level': weakness['accuracy'] * 100,
                'question_count': weakness['total_questions'],
                'category': 'weakness'
            }
        
        # Add strengths (high mastery)
        for strength in strengths:
            all_concepts[strength['concept']] = {
                'mastery_level': strength['accuracy'] * 100,
                'question_count': strength['total_questions'],
                'category': 'strength'
            }
        
        # Convert to chart format
        concept_data = [
            {
                'concept': concept,
                'mastery_level': info['mastery_level'],
                'question_count': info['question_count'],
                'category': info['category']
            }
            for concept, info in all_concepts.items()
        ]
        
        return {
            'type': 'radar',
            'title': 'Concept Mastery Levels',
            'data': concept_data[:12],  # Limit to 12 concepts for readability
            'description': f'Mastery levels for key concepts based on quiz performance'
        }
        
    except Exception as e:
        logger.warning(f"Concept mastery chart error: {str(e)}")
        return {
            'type': 'radar',
            'title': 'Concept Mastery Levels',
            'data': [],
            'description': 'Insufficient data for concept analysis'
        }

def _generate_time_analysis_chart(quiz_results):
    """Generate chart for time-based performance analysis"""
    time_data = []
    
    for result in quiz_results:
        if result.time_taken > 0:  # Only include results with time data
            time_per_question = result.time_taken / result.total_questions if result.total_questions > 0 else 0
            
            time_data.append({
                'quiz_title': result.quiz.title[:30] + '...' if len(result.quiz.title) > 30 else result.quiz.title,
                'total_time': result.time_taken,
                'time_per_question': round(time_per_question, 1),
                'score': result.score,
                'efficiency': round(result.score / (time_per_question + 1), 2)  # Score per minute
            })
    
    # Sort by efficiency
    time_data.sort(key=lambda x: x['efficiency'], reverse=True)
    
    return {
        'type': 'scatter',
        'title': 'Time vs Performance Analysis',
        'data': time_data,
        'x_axis': 'time_per_question',
        'y_axis': 'score',
        'description': f'Relationship between time spent and performance for {len(time_data)} quizzes'
    }

def _generate_progress_streak(student, course_id, start_date, end_date):
    """Generate streak data for consistent progress"""
    progress_records = StudentProgress.objects.filter(
        student=student,
        last_accessed__gte=start_date,
        last_accessed__lte=end_date
    )
    
    if course_id:
        progress_records = progress_records.filter(course_id=course_id)
    
    # Group by date
    daily_activity = {}
    for record in progress_records:
        date_str = record.last_accessed.date().isoformat()
        if date_str not in daily_activity:
            daily_activity[date_str] = 0
        daily_activity[date_str] += 1
    
    # Calculate streak
    streak_data = []
    current_streak = 0
    max_streak = 0
    
    current_date = start_date.date()
    while current_date <= end_date.date():
        date_str = current_date.isoformat()
        active = daily_activity.get(date_str, 0) > 0
        
        if active:
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 0
        
        streak_data.append({
            'date': date_str,
            'active': active,
            'activity_count': daily_activity.get(date_str, 0),
            'streak': current_streak
        })
        
        current_date += timedelta(days=1)
    
    return {
        'type': 'calendar',
        'title': 'Learning Activity Streak',
        'data': streak_data,
        'max_streak': max_streak,
        'total_active_days': sum(1 for day in streak_data if day['active']),
        'description': f'Daily learning activity over {len(streak_data)} days'
    }

def _generate_class_comparison(student, quiz_results, course_id):
    """Generate comparison with class average"""
    if not quiz_results:
        return {
            'type': 'comparison',
            'title': 'Class Performance Comparison',
            'data': [],
            'description': 'No quiz data available for comparison'
        }
    
    # Get student's average
    student_avg = sum(r.score for r in quiz_results) / len(quiz_results)
    
    # Get class averages for same quizzes
    quiz_ids = [r.quiz.id for r in quiz_results]
    
    class_results = QuizResult.objects.filter(
        quiz_id__in=quiz_ids,
        status='completed'
    ).exclude(student=student)
    
    if course_id:
        class_results = class_results.filter(quiz__course_id=course_id)
    
    # Calculate class average per quiz
    comparison_data = []
    for result in quiz_results:
        quiz_class_results = class_results.filter(quiz=result.quiz)
        
        if quiz_class_results.exists():
            class_avg = quiz_class_results.aggregate(Avg('score'))['score__avg']
            class_count = quiz_class_results.count()
        else:
            class_avg = 0
            class_count = 0
        
        comparison_data.append({
            'quiz_title': result.quiz.title,
            'student_score': result.score,
            'class_average': round(class_avg, 1),
            'difference': round(result.score - class_avg, 1),
            'percentile': _calculate_percentile(result.score, quiz_class_results),
            'class_size': class_count + 1  # +1 for the student
        })
    
    return {
        'type': 'comparison',
        'title': 'Class Performance Comparison',
        'data': comparison_data,
        'student_overall_avg': round(student_avg, 1),
        'description': f'Performance comparison with classmates for {len(comparison_data)} quizzes'
    }

def _generate_summary_statistics(quiz_results, student, course_id):
    """Generate comprehensive summary statistics"""
    if not quiz_results:
        return {
            'total_quizzes': 0,
            'overall_average': 0,
            'best_score': 0,
            'improvement_trend': 'no_data'
        }
    
    scores = [r.score for r in quiz_results]
    
    # Basic stats
    summary = {
        'total_quizzes': len(quiz_results),
        'overall_average': round(sum(scores) / len(scores), 1),
        'best_score': max(scores),
        'worst_score': min(scores),
        'median_score': round(_calculate_median(scores), 1),
        'standard_deviation': round(_calculate_standard_deviation(scores), 1),
        'improvement_trend': _calculate_trend(scores),
        'passing_rate': round(
            sum(1 for r in quiz_results if r.score >= r.quiz.passing_score) / len(quiz_results) * 100, 1
        )
    }
    
    # Time-based analysis
    if all(r.time_taken > 0 for r in quiz_results):
        total_time = sum(r.time_taken for r in quiz_results)
        summary['total_time_minutes'] = total_time
        summary['average_time_per_quiz'] = round(total_time / len(quiz_results), 1)
    
    # Recent performance (last 5 quizzes)
    recent_results = sorted(quiz_results, key=lambda x: x.created_at)[-5:]
    if recent_results:
        recent_avg = sum(r.score for r in recent_results) / len(recent_results)
        summary['recent_average'] = round(recent_avg, 1)
        summary['recent_improvement'] = summary['recent_average'] - summary['overall_average']
    
    return summary

def _generate_performance_insights(quiz_results, student, course_id):
    """Generate AI-powered insights from performance data"""
    insights = []
    
    if not quiz_results:
        return insights
    
    scores = [r.score for r in quiz_results]
    
    # Performance level insight
    avg_score = sum(scores) / len(scores)
    if avg_score >= 90:
        insights.append({
            'type': 'success',
            'title': 'Excellent Performance',
            'message': f'Outstanding average score of {avg_score:.1f}% across all quizzes',
            'icon': '🏆'
        })
    elif avg_score < 60:
        insights.append({
            'type': 'warning',
            'title': 'Performance Needs Attention',
            'message': f'Current average of {avg_score:.1f}% indicates need for additional support',
            'icon': '⚠️'
        })
    
    # Consistency insight
    std_dev = _calculate_standard_deviation(scores)
    if std_dev < 10:
        insights.append({
            'type': 'info',
            'title': 'Consistent Performance',
            'message': f'Low variability ({std_dev:.1f}%) shows consistent learning approach',
            'icon': '📈'
        })
    elif std_dev > 25:
        insights.append({
            'type': 'tip',
            'title': 'Variable Performance',
            'message': f'High variability ({std_dev:.1f}%) suggests reviewing study strategies',
            'icon': '💡'
        })
    
    # Trend insight
    trend = _calculate_trend(scores)
    if trend == 'improving':
        insights.append({
            'type': 'success',
            'title': 'Positive Trend',
            'message': 'Performance is improving over time - keep up the great work!',
            'icon': '📊'
        })
    elif trend == 'declining':
        insights.append({
            'type': 'warning',
            'title': 'Declining Trend',
            'message': 'Recent performance shows decline - consider reviewing weak areas',
            'icon': '📉'
        })
    
    return insights

# Helper functions
def _calculate_trend(scores):
    """Calculate trend direction from a list of scores"""
    if len(scores) < 3:
        return 'insufficient_data'
    
    # Simple linear trend calculation
    n = len(scores)
    x_avg = (n - 1) / 2
    y_avg = sum(scores) / n
    
    numerator = sum((i - x_avg) * (scores[i] - y_avg) for i in range(n))
    denominator = sum((i - x_avg) ** 2 for i in range(n))
    
    if denominator == 0:
        return 'stable'
    
    slope = numerator / denominator
    
    if slope > 2:
        return 'improving'
    elif slope < -2:
        return 'declining'
    else:
        return 'stable'

def _calculate_median(scores):
    """Calculate median of scores"""
    sorted_scores = sorted(scores)
    n = len(sorted_scores)
    
    if n % 2 == 0:
        return (sorted_scores[n//2 - 1] + sorted_scores[n//2]) / 2
    else:
        return sorted_scores[n//2]

def _calculate_standard_deviation(scores):
    """Calculate standard deviation"""
    if len(scores) <= 1:
        return 0
    
    mean = sum(scores) / len(scores)
    variance = sum((x - mean) ** 2 for x in scores) / (len(scores) - 1)
    return variance ** 0.5

def _calculate_percentile(score, class_results):
    """Calculate what percentile the student's score falls into"""
    if not class_results.exists():
        return None
    
    class_scores = list(class_results.values_list('score', flat=True))
    class_scores.append(score)
    class_scores.sort()
    
    position = class_scores.index(score)
    percentile = (position / (len(class_scores) - 1)) * 100
    
    return round(percentile, 1)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def learning_velocity_analysis(request, student_id=None):
    """
    Analyze learning velocity - how fast a student is improving
    """
    user = request.user
    
    # Determine target student (same logic as performance charts)
    if student_id and user.role == 'teacher':
        try:
            target_student = User.objects.get(id=student_id, role='student')
            if not CourseEnrollment.objects.filter(
                student=target_student,
                course__instructor=user,
                is_active=True
            ).exists():
                return Response(
                    {'error': 'Access denied to this student'},
                    status=status.HTTP_403_FORBIDDEN
                )
        except User.DoesNotExist:
            return Response(
                {'error': 'Student not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    elif user.role == 'student':
        target_student = user
    else:
        return Response(
            {'error': 'Invalid request'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Analyze learning velocity using StudentAnalyzer
        analyzer = StudentAnalyzer(target_student.id)
        
        # Get all courses for the student
        enrolled_courses = CourseEnrollment.objects.filter(
            student=target_student,
            is_active=True
        ).values_list('course_id', flat=True)
        
        velocity_analysis = {}
        
        for course_id in enrolled_courses:
            course = Course.objects.get(id=course_id)
            performance_summary = analyzer.get_performance_summary(course_id)
            
            # Calculate learning velocity metrics
            velocity_metrics = {
                'course_title': course.title,
                'learning_velocity': performance_summary['learning_velocity'],
                'total_quizzes': performance_summary['total_quizzes_taken'],
                'recent_quizzes': performance_summary['recent_quizzes_taken'],
                'performance_trend': performance_summary['performance_trend'],
                'overall_score': performance_summary['overall_average_score'],
                'recent_score': performance_summary['recent_average_score'],
                'improvement_rate': performance_summary['recent_average_score'] - performance_summary['overall_average_score']
            }
            
            velocity_analysis[course_id] = velocity_metrics
        
        # Overall velocity summary
        total_velocity = sum(course['learning_velocity'] for course in velocity_analysis.values())
        avg_improvement = sum(course['improvement_rate'] for course in velocity_analysis.values()) / len(velocity_analysis) if velocity_analysis else 0
        
        return Response({
            'student_info': {
                'id': target_student.id,
                'email': target_student.email
            },
            'velocity_analysis': velocity_analysis,
            'summary': {
                'total_learning_velocity': round(total_velocity, 3),
                'average_improvement_rate': round(avg_improvement, 1),
                'active_courses': len(velocity_analysis),
                'velocity_category': _categorize_velocity(total_velocity)
            }
        })
        
    except Exception as e:
        logger.error(f"Learning velocity analysis error: {str(e)}")
        return Response(
            {'error': 'Failed to analyze learning velocity', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def _categorize_velocity(velocity):
    """Categorize learning velocity"""
    if velocity >= 0.5:
        return 'high'
    elif velocity >= 0.2:
        return 'moderate'
    elif velocity >= 0.1:
        return 'low'
    else:
        return 'minimal'
