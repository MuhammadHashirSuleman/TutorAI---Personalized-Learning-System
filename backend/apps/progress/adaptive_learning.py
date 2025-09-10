"""
Adaptive Learning System
Dynamic content delivery based on student performance patterns and learning behavior
Implements adaptive algorithms for personalized education experience
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Avg, Count, Max, Min, Q, F
from django.contrib.auth import get_user_model
import logging
import json
from dataclasses import dataclass
from enum import Enum

from .models import StudentProgress, QuizResult, LearningGoal, PerformanceAnalytics
from .recommendation_engine import recommendation_engine
from apps.courses.models import Course, Quiz
from apps.assessments.ai_services import StudentAnalyzer

User = get_user_model()
logger = logging.getLogger(__name__)

class LearningVelocity(Enum):
    VERY_SLOW = "very_slow"
    SLOW = "slow"
    NORMAL = "normal"
    FAST = "fast"
    VERY_FAST = "very_fast"

class DifficultyLevel(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class LearningStyle(Enum):
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    READING_WRITING = "reading_writing"

@dataclass
class AdaptiveParameters:
    """Parameters for adaptive content delivery"""
    difficulty_adjustment: float  # -1.0 to 1.0
    content_pace: float  # 0.5 to 2.0
    repetition_factor: float  # 1.0 to 3.0
    challenge_level: float  # 0.0 to 1.0
    support_level: float  # 0.0 to 1.0
    preferred_learning_style: LearningStyle
    estimated_completion_time: int  # in minutes

class AdaptiveLearningEngine:
    """
    Core adaptive learning engine that personalizes content delivery
    """
    
    def __init__(self):
        self.performance_thresholds = {
            'mastery': 0.85,
            'proficiency': 0.75,
            'developing': 0.65,
            'struggling': 0.50
        }
        
        self.velocity_thresholds = {
            'very_slow': 0.3,
            'slow': 0.6,
            'normal': 1.0,
            'fast': 1.5,
            'very_fast': 2.0
        }
    
    def analyze_student_learning_pattern(self, student_id: int) -> Dict:
        """
        Comprehensive analysis of student's learning patterns
        """
        try:
            student = User.objects.get(id=student_id, role='student')
            
            # Get performance history
            quiz_results = QuizResult.objects.filter(
                student=student,
                status='completed'
            ).order_by('-created_at')
            
            if not quiz_results.exists():
                return self._create_default_pattern()
            
            # Analyze different aspects
            performance_analysis = self._analyze_performance_patterns(quiz_results)
            time_analysis = self._analyze_time_patterns(quiz_results)
            difficulty_analysis = self._analyze_difficulty_preferences(quiz_results)
            content_analysis = self._analyze_content_preferences(student)
            learning_velocity = self._calculate_learning_velocity(quiz_results)
            
            return {
                'student_id': student_id,
                'learning_velocity': learning_velocity,
                'performance_patterns': performance_analysis,
                'time_patterns': time_analysis,
                'difficulty_preferences': difficulty_analysis,
                'content_preferences': content_analysis,
                'adaptive_parameters': self._calculate_adaptive_parameters(
                    performance_analysis, time_analysis, difficulty_analysis, learning_velocity
                ),
                'last_updated': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Learning pattern analysis error: {str(e)}")
            return {'error': str(e)}
    
    def _analyze_performance_patterns(self, quiz_results) -> Dict:
        """Analyze student's performance patterns over time"""
        try:
            results_data = []
            
            for result in quiz_results[:50]:  # Last 50 attempts
                results_data.append({
                    'score': result.score,
                    'date': result.created_at,
                    'difficulty': result.quiz.difficulty_level,
                    'time_taken': result.time_taken,
                    'subject': result.quiz.course.subject.name if result.quiz.course.subject else 'General'
                })
            
            if not results_data:
                return {}
            
            df = pd.DataFrame(results_data)
            df['date'] = pd.to_datetime(df['date'])
            
            # Performance trends
            recent_scores = df.head(10)['score'].tolist()
            older_scores = df.tail(10)['score'].tolist()
            
            trend = 'improving' if np.mean(recent_scores) > np.mean(older_scores) else 'declining' if np.mean(recent_scores) < np.mean(older_scores) else 'stable'
            
            # Consistency analysis
            score_std = df['score'].std()
            consistency = 'high' if score_std < 10 else 'medium' if score_std < 20 else 'low'
            
            # Subject-wise performance
            subject_performance = df.groupby('subject')['score'].agg(['mean', 'count', 'std']).to_dict('index')
            
            return {
                'overall_average': df['score'].mean(),
                'recent_average': recent_scores[:5] and np.mean(recent_scores[:5]) or 0,
                'performance_trend': trend,
                'consistency_level': consistency,
                'score_variability': score_std,
                'subject_performance': subject_performance,
                'best_subject': max(subject_performance.keys(), key=lambda x: subject_performance[x]['mean']) if subject_performance else None,
                'weakest_subject': min(subject_performance.keys(), key=lambda x: subject_performance[x]['mean']) if subject_performance else None
            }
            
        except Exception as e:
            logger.error(f"Performance pattern analysis error: {str(e)}")
            return {}
    
    def _analyze_time_patterns(self, quiz_results) -> Dict:
        """Analyze student's time-based learning patterns"""
        try:
            time_data = []
            
            for result in quiz_results[:30]:
                time_data.append({
                    'hour': result.created_at.hour,
                    'day_of_week': result.created_at.strftime('%A'),
                    'score': result.score,
                    'time_taken': result.time_taken
                })
            
            if not time_data:
                return {}
            
            df = pd.DataFrame(time_data)
            
            # Best performance times
            hourly_performance = df.groupby('hour')['score'].mean()
            best_hour = hourly_performance.idxmax()
            
            daily_performance = df.groupby('day_of_week')['score'].mean()
            best_day = daily_performance.idxmax()
            
            # Time efficiency
            avg_time_per_question = df['time_taken'].mean()
            time_efficiency = 'fast' if avg_time_per_question < 2 else 'moderate' if avg_time_per_question < 4 else 'slow'
            
            return {
                'best_performance_hour': int(best_hour),
                'best_performance_day': best_day,
                'average_session_time': df['time_taken'].mean(),
                'time_efficiency': time_efficiency,
                'peak_performance_period': f"{best_day} at {best_hour}:00",
                'recommended_study_times': [
                    int(hour) for hour, score in hourly_performance.items() 
                    if score >= hourly_performance.mean() + hourly_performance.std() * 0.5
                ]
            }
            
        except Exception as e:
            logger.error(f"Time pattern analysis error: {str(e)}")
            return {}
    
    def _analyze_difficulty_preferences(self, quiz_results) -> Dict:
        """Analyze student's performance across different difficulty levels"""
        try:
            difficulty_data = []
            
            for result in quiz_results:
                difficulty_data.append({
                    'difficulty': result.quiz.difficulty_level,
                    'score': result.score
                })
            
            if not difficulty_data:
                return {}
            
            df = pd.DataFrame(difficulty_data)
            difficulty_stats = df.groupby('difficulty')['score'].agg(['mean', 'count', 'std']).to_dict('index')
            
            # Determine optimal difficulty
            optimal_difficulty = 'intermediate'  # default
            
            for diff, stats in difficulty_stats.items():
                if stats['mean'] >= 75 and stats['count'] >= 3:  # Good performance with sufficient data
                    if diff == 'advanced':
                        optimal_difficulty = 'advanced'
                    elif diff == 'intermediate' and optimal_difficulty != 'advanced':
                        optimal_difficulty = 'intermediate'
            
            return {
                'difficulty_performance': difficulty_stats,
                'optimal_difficulty': optimal_difficulty,
                'comfort_zone': max(difficulty_stats.keys(), key=lambda x: difficulty_stats[x]['mean']) if difficulty_stats else 'intermediate',
                'growth_zone': self._determine_growth_zone(difficulty_stats),
                'difficulty_adaptability': self._calculate_difficulty_adaptability(difficulty_stats)
            }
            
        except Exception as e:
            logger.error(f"Difficulty preference analysis error: {str(e)}")
            return {}
    
    def _analyze_content_preferences(self, student) -> Dict:
        """Analyze student's content interaction preferences"""
        try:
            # Get course enrollments and progress
            progress_data = StudentProgress.objects.filter(student=student)
            
            content_preferences = {
                'preferred_subjects': [],
                'engagement_patterns': {},
                'content_consumption_rate': 'moderate',
                'interaction_style': 'balanced'
            }
            
            if progress_data.exists():
                # Subject preferences based on time spent and performance
                subject_data = {}
                for progress in progress_data:
                    subject = progress.course.subject.name if progress.course.subject else 'General'
                    if subject not in subject_data:
                        subject_data[subject] = {
                            'time_spent': 0,
                            'courses_count': 0,
                            'avg_progress': 0
                        }
                    
                    subject_data[subject]['time_spent'] += progress.time_spent_minutes
                    subject_data[subject]['courses_count'] += 1
                    subject_data[subject]['avg_progress'] += progress.completion_percentage
                
                # Calculate preferences
                for subject, data in subject_data.items():
                    data['avg_progress'] /= data['courses_count']
                    data['engagement_score'] = (data['time_spent'] / 60) * data['avg_progress'] / 100
                
                # Sort by engagement score
                sorted_subjects = sorted(subject_data.items(), key=lambda x: x[1]['engagement_score'], reverse=True)
                content_preferences['preferred_subjects'] = [subject for subject, _ in sorted_subjects[:3]]
                content_preferences['engagement_patterns'] = subject_data
            
            return content_preferences
            
        except Exception as e:
            logger.error(f"Content preference analysis error: {str(e)}")
            return {}
    
    def _calculate_learning_velocity(self, quiz_results) -> Dict:
        """Calculate student's learning velocity"""
        try:
            if len(quiz_results) < 5:
                return {'velocity': 'normal', 'confidence': 'low'}
            
            # Calculate improvement rate over time
            recent_results = list(quiz_results[:20])  # Last 20 attempts
            scores = [r.score for r in recent_results]
            
            # Time-based improvement
            time_deltas = []
            score_improvements = []
            
            for i in range(1, len(recent_results)):
                time_delta = (recent_results[i-1].created_at - recent_results[i].created_at).days
                score_improvement = recent_results[i-1].score - recent_results[i].score
                
                if time_delta > 0:
                    time_deltas.append(time_delta)
                    score_improvements.append(score_improvement)
            
            if not time_deltas:
                return {'velocity': 'normal', 'confidence': 'low'}
            
            # Average improvement per day
            avg_improvement_per_day = np.mean(score_improvements) / np.mean(time_deltas) if np.mean(time_deltas) > 0 else 0
            
            # Classify velocity
            if avg_improvement_per_day > 2:
                velocity = LearningVelocity.VERY_FAST
            elif avg_improvement_per_day > 1:
                velocity = LearningVelocity.FAST
            elif avg_improvement_per_day > -0.5:
                velocity = LearningVelocity.NORMAL
            elif avg_improvement_per_day > -2:
                velocity = LearningVelocity.SLOW
            else:
                velocity = LearningVelocity.VERY_SLOW
            
            confidence = 'high' if len(recent_results) >= 15 else 'medium' if len(recent_results) >= 10 else 'low'
            
            return {
                'velocity': velocity.value,
                'improvement_rate': avg_improvement_per_day,
                'confidence': confidence,
                'data_points': len(recent_results)
            }
            
        except Exception as e:
            logger.error(f"Learning velocity calculation error: {str(e)}")
            return {'velocity': 'normal', 'confidence': 'low'}
    
    def _calculate_adaptive_parameters(self, performance_analysis, time_analysis, difficulty_analysis, learning_velocity) -> AdaptiveParameters:
        """Calculate adaptive parameters based on analysis"""
        try:
            # Difficulty adjustment (-1 to 1)
            avg_score = performance_analysis.get('overall_average', 70)
            if avg_score >= 85:
                difficulty_adjustment = 0.3  # Increase difficulty
            elif avg_score >= 75:
                difficulty_adjustment = 0.1
            elif avg_score >= 65:
                difficulty_adjustment = 0.0  # Keep same
            elif avg_score >= 55:
                difficulty_adjustment = -0.2  # Decrease difficulty
            else:
                difficulty_adjustment = -0.5
            
            # Content pace (0.5 to 2.0)
            velocity_value = learning_velocity.get('velocity', 'normal')
            pace_mapping = {
                'very_fast': 1.8,
                'fast': 1.4,
                'normal': 1.0,
                'slow': 0.7,
                'very_slow': 0.5
            }
            content_pace = pace_mapping.get(velocity_value, 1.0)
            
            # Repetition factor (1.0 to 3.0)
            consistency = performance_analysis.get('consistency_level', 'medium')
            repetition_mapping = {
                'high': 1.0,
                'medium': 1.5,
                'low': 2.5
            }
            repetition_factor = repetition_mapping.get(consistency, 1.5)
            
            # Challenge level (0.0 to 1.0)
            if avg_score >= 80:
                challenge_level = 0.8
            elif avg_score >= 70:
                challenge_level = 0.6
            elif avg_score >= 60:
                challenge_level = 0.4
            else:
                challenge_level = 0.2
            
            # Support level (0.0 to 1.0) - inverse of performance
            support_level = max(0.1, min(1.0, 1.0 - (avg_score / 100)))
            
            # Estimated completion time
            time_efficiency = time_analysis.get('time_efficiency', 'moderate')
            base_time = 30  # base minutes
            time_mapping = {
                'fast': 0.8,
                'moderate': 1.0,
                'slow': 1.5
            }
            estimated_time = int(base_time * time_mapping.get(time_efficiency, 1.0) * repetition_factor)
            
            return AdaptiveParameters(
                difficulty_adjustment=difficulty_adjustment,
                content_pace=content_pace,
                repetition_factor=repetition_factor,
                challenge_level=challenge_level,
                support_level=support_level,
                preferred_learning_style=LearningStyle.VISUAL,  # Default, could be determined from interactions
                estimated_completion_time=estimated_time
            )
            
        except Exception as e:
            logger.error(f"Adaptive parameters calculation error: {str(e)}")
            return self._create_default_adaptive_parameters()
    
    def generate_adaptive_content_plan(self, student_id: int, course_id: Optional[int] = None) -> Dict:
        """
        Generate personalized content delivery plan
        """
        try:
            # Get learning pattern analysis
            learning_pattern = self.analyze_student_learning_pattern(student_id)
            
            if 'error' in learning_pattern:
                return learning_pattern
            
            student = User.objects.get(id=student_id)
            
            # Get student's current progress
            current_progress = self._get_current_progress(student, course_id)
            
            # Generate adaptive content recommendations
            content_plan = {
                'student_id': student_id,
                'course_id': course_id,
                'learning_pattern_summary': learning_pattern,
                'adaptive_content': {},
                'personalized_schedule': {},
                'success_metrics': {},
                'generated_at': timezone.now().isoformat()
            }
            
            # Content adaptation
            content_plan['adaptive_content'] = self._generate_adaptive_content(
                student, learning_pattern, current_progress, course_id
            )
            
            # Schedule adaptation
            content_plan['personalized_schedule'] = self._generate_personalized_schedule(
                learning_pattern, content_plan['adaptive_content']
            )
            
            # Success metrics
            content_plan['success_metrics'] = self._define_success_metrics(
                learning_pattern, current_progress
            )
            
            return content_plan
            
        except Exception as e:
            logger.error(f"Adaptive content plan generation error: {str(e)}")
            return {'error': str(e)}
    
    def _generate_adaptive_content(self, student, learning_pattern, current_progress, course_id) -> Dict:
        """Generate adaptive content recommendations"""
        try:
            adaptive_params = learning_pattern.get('adaptive_parameters')
            
            if not adaptive_params:
                return {}
            
            content_recommendations = {
                'difficulty_level': self._determine_optimal_difficulty(adaptive_params),
                'content_sequence': [],
                'practice_exercises': [],
                'review_materials': [],
                'challenge_activities': [],
                'support_resources': []
            }
            
            # Get available content based on course
            if course_id:
                available_quizzes = Quiz.objects.filter(
                    course_id=course_id,
                    is_active=True
                ).exclude(
                    results__student=student,
                    results__score__gte=adaptive_params.challenge_level * 100
                )
            else:
                # Get quizzes from enrolled courses
                enrolled_courses = student.enrollments.values_list('course_id', flat=True)
                available_quizzes = Quiz.objects.filter(
                    course_id__in=enrolled_courses,
                    is_active=True
                ).exclude(
                    results__student=student,
                    results__score__gte=adaptive_params.challenge_level * 100
                )
            
            # Sequence content based on adaptive parameters
            for quiz in available_quizzes[:10]:  # Limit for performance
                content_item = {
                    'quiz_id': quiz.id,
                    'title': quiz.title,
                    'adapted_difficulty': self._adapt_quiz_difficulty(quiz, adaptive_params),
                    'estimated_time': int(quiz.time_limit * adaptive_params.content_pace),
                    'repetition_count': int(adaptive_params.repetition_factor),
                    'support_level': adaptive_params.support_level,
                    'sequence_order': len(content_recommendations['content_sequence']) + 1
                }
                
                content_recommendations['content_sequence'].append(content_item)
            
            # Practice exercises (based on weaknesses)
            performance_patterns = learning_pattern.get('performance_patterns', {})
            weakest_subject = performance_patterns.get('weakest_subject')
            
            if weakest_subject and course_id:
                practice_quizzes = Quiz.objects.filter(
                    course__subject__name=weakest_subject,
                    difficulty_level='intermediate',
                    is_active=True
                )[:3]
                
                for quiz in practice_quizzes:
                    content_recommendations['practice_exercises'].append({
                        'quiz_id': quiz.id,
                        'title': f"Practice: {quiz.title}",
                        'focus_area': weakest_subject,
                        'priority': 'high'
                    })
            
            # Challenge activities (if performing well)
            if adaptive_params.challenge_level > 0.6:
                challenge_quizzes = Quiz.objects.filter(
                    difficulty_level='advanced',
                    is_active=True
                )[:2]
                
                for quiz in challenge_quizzes:
                    content_recommendations['challenge_activities'].append({
                        'quiz_id': quiz.id,
                        'title': f"Challenge: {quiz.title}",
                        'unlock_condition': 'Complete 3 intermediate quizzes with 80%+ score'
                    })
            
            return content_recommendations
            
        except Exception as e:
            logger.error(f"Adaptive content generation error: {str(e)}")
            return {}
    
    def _generate_personalized_schedule(self, learning_pattern, adaptive_content) -> Dict:
        """Generate personalized study schedule"""
        try:
            time_patterns = learning_pattern.get('time_patterns', {})
            adaptive_params = learning_pattern.get('adaptive_parameters')
            
            if not adaptive_params:
                return {}
            
            # Get optimal study times
            best_hour = time_patterns.get('best_performance_hour', 14)  # Default 2 PM
            recommended_times = time_patterns.get('recommended_study_times', [10, 14, 19])
            
            schedule = {
                'optimal_study_times': recommended_times,
                'session_duration': adaptive_params.estimated_completion_time,
                'frequency': 'daily' if adaptive_params.content_pace > 1.0 else 'every_other_day',
                'weekly_schedule': {},
                'break_intervals': max(5, int(adaptive_params.estimated_completion_time / 6)),
                'review_schedule': []
            }
            
            # Generate weekly schedule
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            content_sequence = adaptive_content.get('content_sequence', [])
            
            for i, day in enumerate(days):
                if i < len(content_sequence):
                    schedule['weekly_schedule'][day] = {
                        'study_time': f"{best_hour}:00",
                        'content': content_sequence[i]['title'],
                        'duration': content_sequence[i]['estimated_time'],
                        'type': 'main_content'
                    }
                elif i % 2 == 0:  # Practice days
                    schedule['weekly_schedule'][day] = {
                        'study_time': f"{best_hour}:00",
                        'content': 'Practice and Review',
                        'duration': adaptive_params.estimated_completion_time // 2,
                        'type': 'practice'
                    }
            
            # Review schedule based on repetition factor
            if adaptive_params.repetition_factor > 1.5:
                schedule['review_schedule'] = [
                    {'day': 1, 'type': 'immediate_review'},
                    {'day': 3, 'type': 'spaced_review'},
                    {'day': 7, 'type': 'weekly_review'}
                ]
            
            return schedule
            
        except Exception as e:
            logger.error(f"Personalized schedule generation error: {str(e)}")
            return {}
    
    def update_adaptive_parameters_based_on_performance(self, student_id: int, recent_performance: Dict) -> Dict:
        """
        Update adaptive parameters based on recent performance
        """
        try:
            # Get current learning pattern
            current_pattern = self.analyze_student_learning_pattern(student_id)
            
            if 'error' in current_pattern:
                return current_pattern
            
            current_params = current_pattern.get('adaptive_parameters')
            
            if not current_params:
                return {'error': 'No adaptive parameters found'}
            
            # Analyze recent performance
            recent_score = recent_performance.get('average_score', 70)
            score_trend = recent_performance.get('trend', 'stable')
            consistency = recent_performance.get('consistency', 'medium')
            
            # Adjust parameters
            updated_params = {
                'difficulty_adjustment': current_params.difficulty_adjustment,
                'content_pace': current_params.content_pace,
                'repetition_factor': current_params.repetition_factor,
                'challenge_level': current_params.challenge_level,
                'support_level': current_params.support_level
            }
            
            # Dynamic adjustments based on performance
            if score_trend == 'improving' and recent_score > 80:
                updated_params['difficulty_adjustment'] = min(1.0, current_params.difficulty_adjustment + 0.1)
                updated_params['challenge_level'] = min(1.0, current_params.challenge_level + 0.1)
                updated_params['content_pace'] = min(2.0, current_params.content_pace + 0.1)
                
            elif score_trend == 'declining' or recent_score < 60:
                updated_params['difficulty_adjustment'] = max(-1.0, current_params.difficulty_adjustment - 0.2)
                updated_params['support_level'] = min(1.0, current_params.support_level + 0.2)
                updated_params['repetition_factor'] = min(3.0, current_params.repetition_factor + 0.3)
                updated_params['content_pace'] = max(0.5, current_params.content_pace - 0.1)
            
            return {
                'student_id': student_id,
                'updated_parameters': updated_params,
                'changes_made': self._identify_parameter_changes(current_params, updated_params),
                'reason': f"Performance trend: {score_trend}, Recent score: {recent_score}%",
                'updated_at': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Adaptive parameters update error: {str(e)}")
            return {'error': str(e)}
    
    # Helper methods
    def _create_default_pattern(self) -> Dict:
        """Create default learning pattern for new students"""
        return {
            'learning_velocity': {'velocity': 'normal', 'confidence': 'low'},
            'performance_patterns': {'overall_average': 70, 'consistency_level': 'medium'},
            'time_patterns': {'best_performance_hour': 14, 'time_efficiency': 'moderate'},
            'difficulty_preferences': {'optimal_difficulty': 'intermediate'},
            'content_preferences': {'preferred_subjects': []},
            'adaptive_parameters': self._create_default_adaptive_parameters()
        }
    
    def _create_default_adaptive_parameters(self) -> AdaptiveParameters:
        """Create default adaptive parameters"""
        return AdaptiveParameters(
            difficulty_adjustment=0.0,
            content_pace=1.0,
            repetition_factor=1.5,
            challenge_level=0.5,
            support_level=0.5,
            preferred_learning_style=LearningStyle.VISUAL,
            estimated_completion_time=30
        )
    
    def _determine_growth_zone(self, difficulty_stats: Dict) -> str:
        """Determine the growth zone for the student"""
        if not difficulty_stats:
            return 'intermediate'
        
        # Find the highest difficulty level where student scores above 60%
        growth_zones = ['beginner', 'intermediate', 'advanced']
        
        for zone in reversed(growth_zones):
            if zone in difficulty_stats and difficulty_stats[zone]['mean'] >= 60:
                # Return next level as growth zone
                current_index = growth_zones.index(zone)
                if current_index < len(growth_zones) - 1:
                    return growth_zones[current_index + 1]
                else:
                    return zone
        
        return 'beginner'
    
    def _calculate_difficulty_adaptability(self, difficulty_stats: Dict) -> float:
        """Calculate how well student adapts to different difficulty levels"""
        if len(difficulty_stats) < 2:
            return 0.5
        
        scores = [stats['mean'] for stats in difficulty_stats.values()]
        # Lower standard deviation means better adaptability
        adaptability = 1.0 - (np.std(scores) / 100)
        return max(0.0, min(1.0, adaptability))
    
    def _get_current_progress(self, student, course_id) -> Dict:
        """Get student's current progress"""
        if course_id:
            progress = StudentProgress.objects.filter(
                student=student,
                course_id=course_id
            ).first()
        else:
            progress = StudentProgress.objects.filter(student=student)
        
        if not progress:
            return {'completion_percentage': 0, 'topics_covered': [], 'current_level': 'beginner'}
        
        if course_id:
            return {
                'completion_percentage': progress.completion_percentage,
                'topics_covered': progress.topics_covered or [],
                'current_level': progress.current_level or 'intermediate'
            }
        else:
            avg_completion = progress.aggregate(Avg('completion_percentage'))['completion_percentage__avg'] or 0
            return {
                'completion_percentage': avg_completion,
                'topics_covered': [],
                'current_level': 'intermediate'
            }
    
    def _determine_optimal_difficulty(self, adaptive_params) -> str:
        """Determine optimal difficulty level based on adaptive parameters"""
        difficulty_score = adaptive_params.challenge_level + adaptive_params.difficulty_adjustment
        
        if difficulty_score >= 0.8:
            return 'advanced'
        elif difficulty_score >= 0.5:
            return 'intermediate'
        else:
            return 'beginner'
    
    def _adapt_quiz_difficulty(self, quiz, adaptive_params) -> str:
        """Adapt quiz difficulty based on parameters"""
        base_difficulty = quiz.difficulty_level
        adjustment = adaptive_params.difficulty_adjustment
        
        difficulty_levels = ['beginner', 'intermediate', 'advanced']
        current_index = difficulty_levels.index(base_difficulty) if base_difficulty in difficulty_levels else 1
        
        if adjustment > 0.3:
            new_index = min(len(difficulty_levels) - 1, current_index + 1)
        elif adjustment < -0.3:
            new_index = max(0, current_index - 1)
        else:
            new_index = current_index
        
        return difficulty_levels[new_index]
    
    def _define_success_metrics(self, learning_pattern, current_progress) -> Dict:
        """Define success metrics based on student's pattern"""
        adaptive_params = learning_pattern.get('adaptive_parameters')
        
        if not adaptive_params:
            return {}
        
        return {
            'target_completion_rate': min(100, current_progress.get('completion_percentage', 0) + 20),
            'target_average_score': min(100, learning_pattern.get('performance_patterns', {}).get('overall_average', 70) + 10),
            'consistency_goal': 'Maintain score variation within 15 points',
            'velocity_goal': f"Complete content at {adaptive_params.content_pace}x pace",
            'mastery_threshold': 85,
            'review_frequency': f"Every {int(1/adaptive_params.repetition_factor * 7)} days"
        }
    
    def _identify_parameter_changes(self, old_params, new_params) -> List[str]:
        """Identify what parameters changed"""
        changes = []
        
        for key in new_params:
            if hasattr(old_params, key):
                old_value = getattr(old_params, key)
                new_value = new_params[key]
                
                if abs(old_value - new_value) > 0.05:  # Significant change threshold
                    if new_value > old_value:
                        changes.append(f"Increased {key.replace('_', ' ')}")
                    else:
                        changes.append(f"Decreased {key.replace('_', ' ')}")
        
        return changes

# Singleton instance
adaptive_learning_engine = AdaptiveLearningEngine()
