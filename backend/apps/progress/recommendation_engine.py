"""
AI Recommendation Engine
Personalized learning recommendation system using machine learning algorithms
Provides intelligent content suggestions and learning paths based on student behavior
"""

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from django.db.models import Avg, Count, Q, F, Max, Min
from django.utils import timezone
from datetime import timedelta
import logging
import json
from typing import List, Dict, Tuple, Optional
import requests
from django.conf import settings

from apps.courses.models import Course, Quiz
from apps.progress.models import StudentProgress, QuizResult, LearningGoal
from apps.assessments.ai_services import StudentAnalyzer
from django.contrib.auth import get_user_model

User = get_user_model()
logger = logging.getLogger(__name__)

class RecommendationEngine:
    """
    AI-powered recommendation engine for personalized learning
    """
    
    def __init__(self):
        self.api_key = getattr(settings, 'DEEPSEEK_API_KEY', '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')
        self.api_url = "https://api.deepseek.com/chat/completions"
        self.scaler = StandardScaler()
        
    def get_student_recommendations(self, student_id: int, recommendation_type: str = 'all') -> Dict:
        """
        Generate comprehensive recommendations for a student
        
        Args:
            student_id: ID of the student
            recommendation_type: Type of recommendations ('courses', 'quizzes', 'topics', 'all')
        
        Returns:
            Dict containing various types of recommendations
        """
        try:
            student = User.objects.get(id=student_id, role='student')
            
            # Get student profile and performance data
            student_profile = self._build_student_profile(student)
            
            recommendations = {
                'student_id': student_id,
                'timestamp': timezone.now().isoformat(),
                'profile_summary': student_profile['summary'],
                'recommendations': {}
            }
            
            if recommendation_type in ['courses', 'all']:
                recommendations['recommendations']['courses'] = self._recommend_courses(student, student_profile)
                
            if recommendation_type in ['quizzes', 'all']:
                recommendations['recommendations']['quizzes'] = self._recommend_quizzes(student, student_profile)
                
            if recommendation_type in ['topics', 'all']:
                recommendations['recommendations']['study_topics'] = self._recommend_study_topics(student, student_profile)
                
            if recommendation_type in ['learning_path', 'all']:
                recommendations['recommendations']['learning_path'] = self._generate_learning_path(student, student_profile)
                
            # Add peer-based recommendations
            recommendations['recommendations']['peer_suggestions'] = self._get_peer_based_recommendations(student, student_profile)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Recommendation generation error: {str(e)}")
            return {'error': str(e)}
    
    def _build_student_profile(self, student) -> Dict:
        """Build comprehensive student learning profile"""
        try:
            # Get performance data
            quiz_results = QuizResult.objects.filter(student=student, status='completed')
            
            if not quiz_results.exists():
                return {
                    'summary': 'New student - no performance data available',
                    'performance_metrics': {},
                    'learning_patterns': {},
                    'strengths': [],
                    'weaknesses': []
                }
            
            # Performance metrics
            avg_score = quiz_results.aggregate(Avg('score'))['score__avg']
            total_quizzes = quiz_results.count()
            recent_performance = quiz_results.filter(
                created_at__gte=timezone.now() - timedelta(days=30)
            ).aggregate(Avg('score'))['score__avg'] or 0
            
            # Subject-wise performance
            subject_performance = {}
            courses_taken = quiz_results.values('quiz__course').distinct()
            
            for course_data in courses_taken:
                course = Course.objects.get(id=course_data['quiz__course'])
                course_results = quiz_results.filter(quiz__course=course)
                subject_performance[course.subject.name if course.subject else 'General'] = {
                    'avg_score': course_results.aggregate(Avg('score'))['score__avg'],
                    'quiz_count': course_results.count(),
                    'improvement_trend': self._calculate_improvement_trend(course_results)
                }
            
            # Learning patterns
            learning_patterns = self._analyze_learning_patterns(quiz_results)
            
            # Strengths and weaknesses
            strengths = []
            weaknesses = []
            
            for subject, data in subject_performance.items():
                if data['avg_score'] >= 85:
                    strengths.append({
                        'subject': subject,
                        'score': data['avg_score'],
                        'confidence': 'high'
                    })
                elif data['avg_score'] < 65:
                    weaknesses.append({
                        'subject': subject,
                        'score': data['avg_score'],
                        'priority': 'high' if data['avg_score'] < 50 else 'medium'
                    })
            
            return {
                'summary': f"Student with {total_quizzes} quizzes completed, {avg_score:.1f}% average",
                'performance_metrics': {
                    'overall_average': round(avg_score, 1),
                    'recent_average': round(recent_performance, 1),
                    'total_quizzes': total_quizzes,
                    'performance_trend': 'improving' if recent_performance > avg_score else 'declining'
                },
                'subject_performance': subject_performance,
                'learning_patterns': learning_patterns,
                'strengths': strengths,
                'weaknesses': weaknesses
            }
            
        except Exception as e:
            logger.error(f"Student profile building error: {str(e)}")
            return {'summary': 'Error building profile', 'error': str(e)}
    
    def _analyze_learning_patterns(self, quiz_results) -> Dict:
        """Analyze student learning patterns from quiz data"""
        try:
            # Time-based patterns
            results_df = pd.DataFrame(list(quiz_results.values(
                'created_at', 'score', 'time_taken', 'quiz__difficulty_level'
            )))
            
            if results_df.empty:
                return {}
            
            # Convert datetime
            results_df['created_at'] = pd.to_datetime(results_df['created_at'])
            results_df['hour'] = results_df['created_at'].dt.hour
            results_df['day_of_week'] = results_df['created_at'].dt.day_name()
            
            # Analyze patterns
            patterns = {
                'best_performance_time': results_df.groupby('hour')['score'].mean().idxmax(),
                'most_active_day': results_df['day_of_week'].value_counts().index[0],
                'difficulty_preference': results_df.groupby('quiz__difficulty_level')['score'].mean().to_dict(),
                'time_management': {
                    'avg_time_taken': results_df['time_taken'].mean(),
                    'time_vs_performance_correlation': results_df[['time_taken', 'score']].corr().iloc[0,1]
                }
            }
            
            return patterns
            
        except Exception as e:
            logger.error(f"Learning pattern analysis error: {str(e)}")
            return {}
    
    def _calculate_improvement_trend(self, quiz_results) -> str:
        """Calculate if student is improving in a subject"""
        try:
            recent_results = list(quiz_results.order_by('created_at').values_list('score', flat=True))
            
            if len(recent_results) < 3:
                return 'insufficient_data'
            
            # Simple trend analysis
            early_avg = np.mean(recent_results[:len(recent_results)//2])
            late_avg = np.mean(recent_results[len(recent_results)//2:])
            
            if late_avg > early_avg + 5:
                return 'improving'
            elif late_avg < early_avg - 5:
                return 'declining'
            else:
                return 'stable'
                
        except Exception as e:
            logger.error(f"Trend calculation error: {str(e)}")
            return 'unknown'
    
    def _recommend_courses(self, student, student_profile: Dict) -> List[Dict]:
        """Recommend courses based on student profile"""
        try:
            # Get courses student is not enrolled in
            enrolled_courses = student.enrollments.values_list('course_id', flat=True)
            available_courses = Course.objects.exclude(id__in=enrolled_courses).filter(is_active=True)
            
            recommendations = []
            
            # Content-based filtering
            for course in available_courses[:10]:  # Limit to top 10
                compatibility_score = self._calculate_course_compatibility(course, student_profile)
                
                if compatibility_score > 0.6:  # Threshold for recommendation
                    recommendations.append({
                        'course_id': course.id,
                        'title': course.title,
                        'description': course.description,
                        'instructor': course.instructor.first_name + ' ' + course.instructor.last_name,
                        'compatibility_score': round(compatibility_score, 2),
                        'reason': self._generate_course_recommendation_reason(course, student_profile, compatibility_score),
                        'estimated_difficulty': course.difficulty_level,
                        'estimated_duration': course.estimated_duration,
                        'prerequisites_met': self._check_prerequisites(student, course)
                    })
            
            # Sort by compatibility score
            recommendations.sort(key=lambda x: x['compatibility_score'], reverse=True)
            
            return recommendations[:5]  # Top 5 recommendations
            
        except Exception as e:
            logger.error(f"Course recommendation error: {str(e)}")
            return []
    
    def _calculate_course_compatibility(self, course, student_profile: Dict) -> float:
        """Calculate how compatible a course is with student's profile"""
        try:
            compatibility_score = 0.5  # Base score
            
            # Subject alignment
            if course.subject:
                subject_name = course.subject.name
                
                # Check if student has strengths in this subject
                for strength in student_profile.get('strengths', []):
                    if strength['subject'] == subject_name:
                        compatibility_score += 0.3
                        break
                
                # Check if this addresses weaknesses
                for weakness in student_profile.get('weaknesses', []):
                    if weakness['subject'] == subject_name:
                        if weakness['priority'] == 'high':
                            compatibility_score += 0.4
                        else:
                            compatibility_score += 0.2
                        break
            
            # Difficulty alignment
            overall_avg = student_profile.get('performance_metrics', {}).get('overall_average', 0)
            if overall_avg >= 80 and course.difficulty_level == 'advanced':
                compatibility_score += 0.2
            elif 60 <= overall_avg < 80 and course.difficulty_level == 'intermediate':
                compatibility_score += 0.2
            elif overall_avg < 60 and course.difficulty_level == 'beginner':
                compatibility_score += 0.2
            
            return min(compatibility_score, 1.0)  # Cap at 1.0
            
        except Exception as e:
            logger.error(f"Compatibility calculation error: {str(e)}")
            return 0.5
    
    def _generate_course_recommendation_reason(self, course, student_profile: Dict, compatibility_score: float) -> str:
        """Generate human-readable reason for course recommendation"""
        try:
            reasons = []
            
            if course.subject:
                subject_name = course.subject.name
                
                # Check strengths
                for strength in student_profile.get('strengths', []):
                    if strength['subject'] == subject_name:
                        reasons.append(f"Builds on your strength in {subject_name}")
                        break
                
                # Check weaknesses
                for weakness in student_profile.get('weaknesses', []):
                    if weakness['subject'] == subject_name:
                        reasons.append(f"Helps improve your {subject_name} skills")
                        break
            
            # Difficulty alignment
            overall_avg = student_profile.get('performance_metrics', {}).get('overall_average', 0)
            if overall_avg >= 80 and course.difficulty_level == 'advanced':
                reasons.append("Suitable challenge level for your performance")
            elif overall_avg < 60 and course.difficulty_level == 'beginner':
                reasons.append("Good foundation building course")
            
            if not reasons:
                reasons.append("Good match based on your learning profile")
            
            return "; ".join(reasons)
            
        except Exception as e:
            logger.error(f"Reason generation error: {str(e)}")
            return "Recommended based on your profile"
    
    def _check_prerequisites(self, student, course) -> bool:
        """Check if student meets course prerequisites"""
        # Simplified prerequisite check
        # In a real system, this would check actual prerequisite courses
        try:
            if course.difficulty_level == 'beginner':
                return True
            
            # For intermediate and advanced, check if student has completed related beginner courses
            student_courses = student.enrollments.filter(status='completed').values_list('course__subject', flat=True)
            
            if course.subject_id in student_courses:
                return True
            
            return course.difficulty_level != 'advanced'  # Allow intermediate for most students
            
        except Exception as e:
            logger.error(f"Prerequisites check error: {str(e)}")
            return True
    
    def _recommend_quizzes(self, student, student_profile: Dict) -> List[Dict]:
        """Recommend quizzes for practice based on student weaknesses"""
        try:
            recommendations = []
            
            # Get courses student is enrolled in
            enrolled_courses = student.enrollments.values_list('course_id', flat=True)
            available_quizzes = Quiz.objects.filter(course_id__in=enrolled_courses, is_active=True)
            
            # Find quizzes in weak subjects
            for weakness in student_profile.get('weaknesses', []):
                subject_name = weakness['subject']
                
                subject_quizzes = available_quizzes.filter(
                    course__subject__name=subject_name
                ).exclude(
                    results__student=student,
                    results__score__gte=80  # Exclude quizzes already mastered
                )
                
                for quiz in subject_quizzes[:3]:  # Top 3 per weakness
                    recommendations.append({
                        'quiz_id': quiz.id,
                        'title': quiz.title,
                        'description': quiz.description,
                        'subject': subject_name,
                        'difficulty': quiz.difficulty_level,
                        'estimated_time': quiz.time_limit,
                        'reason': f"Practice for {subject_name} improvement",
                        'priority': weakness['priority'],
                        'expected_improvement': self._estimate_quiz_improvement(quiz, weakness)
                    })
            
            # Add general practice quizzes
            general_quizzes = available_quizzes.filter(
                difficulty_level='intermediate'
            ).exclude(
                id__in=[r['quiz_id'] for r in recommendations]
            )[:2]
            
            for quiz in general_quizzes:
                recommendations.append({
                    'quiz_id': quiz.id,
                    'title': quiz.title,
                    'description': quiz.description,
                    'subject': quiz.course.subject.name if quiz.course.subject else 'General',
                    'difficulty': quiz.difficulty_level,
                    'estimated_time': quiz.time_limit,
                    'reason': "General skill maintenance",
                    'priority': 'low',
                    'expected_improvement': "Skill maintenance"
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Quiz recommendation error: {str(e)}")
            return []
    
    def _estimate_quiz_improvement(self, quiz, weakness) -> str:
        """Estimate improvement potential from taking a quiz"""
        try:
            if weakness['priority'] == 'high':
                return "High improvement potential"
            elif quiz.difficulty_level == 'beginner':
                return "Foundation building"
            else:
                return "Moderate improvement expected"
        except:
            return "Skill development"
    
    def _recommend_study_topics(self, student, student_profile: Dict) -> List[Dict]:
        """Recommend specific topics for study based on AI analysis"""
        try:
            # Use AI to analyze student's weak areas and recommend topics
            analyzer = StudentAnalyzer()
            weaknesses_analysis = analyzer.analyze_student_weaknesses(student.id)
            
            topics_recommendations = []
            
            for weakness in weaknesses_analysis.get('detailed_weaknesses', []):
                topic_suggestion = self._generate_topic_recommendation(weakness, student_profile)
                if topic_suggestion:
                    topics_recommendations.append(topic_suggestion)
            
            # Use OpenAI for additional topic suggestions
            ai_topics = self._get_ai_topic_recommendations(student_profile)
            topics_recommendations.extend(ai_topics[:3])  # Add top 3 AI suggestions
            
            return topics_recommendations[:8]  # Limit to 8 topics
            
        except Exception as e:
            logger.error(f"Study topics recommendation error: {str(e)}")
            return []
    
    def _generate_topic_recommendation(self, weakness, student_profile: Dict) -> Optional[Dict]:
        """Generate topic recommendation based on weakness analysis"""
        try:
            return {
                'topic': weakness.get('concept', 'Unknown Topic'),
                'subject': weakness.get('subject', 'General'),
                'priority': weakness.get('severity', 'medium'),
                'study_time_estimate': f"{weakness.get('difficulty_score', 5) * 10} minutes",
                'resources': [
                    f"Review {weakness.get('concept', 'topic')} fundamentals",
                    f"Practice {weakness.get('concept', 'topic')} exercises",
                    f"Take quiz on {weakness.get('concept', 'topic')}"
                ],
                'reason': f"Identified as {weakness.get('severity', 'medium')} priority weakness"
            }
        except Exception as e:
            logger.error(f"Topic recommendation generation error: {str(e)}")
            return None
    
    def _get_ai_topic_recommendations(self, student_profile: Dict) -> List[Dict]:
        """Use DeepSeek to suggest study topics based on student profile"""
        try:
            prompt = f"""
            Based on this student profile, recommend 3 specific study topics:
            
            Performance: {student_profile.get('performance_metrics', {})}
            Strengths: {student_profile.get('strengths', [])}
            Weaknesses: {student_profile.get('weaknesses', [])}
            
            For each topic, provide:
            1. Topic name
            2. Subject area
            3. Priority level (high/medium/low)
            4. Estimated study time
            5. Brief reason for recommendation
            
            Format as JSON array.
            """
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            response_data = response.json()
            
            ai_suggestions = json.loads(response_data['choices'][0]['message']['content'])
            
            return [
                {
                    'topic': suggestion.get('topic', 'AI Suggested Topic'),
                    'subject': suggestion.get('subject', 'General'),
                    'priority': suggestion.get('priority', 'medium'),
                    'study_time_estimate': suggestion.get('study_time', '30 minutes'),
                    'reason': suggestion.get('reason', 'AI recommendation'),
                    'source': 'ai_generated'
                }
                for suggestion in ai_suggestions
            ]
            
        except Exception as e:
            logger.error(f"AI topic recommendation error: {str(e)}")
            return []
    
    def _generate_learning_path(self, student, student_profile: Dict) -> Dict:
        """Generate personalized learning path"""
        try:
            learning_path = {
                'path_id': f"path_{student.id}_{int(timezone.now().timestamp())}",
                'title': f"Personalized Learning Path for {student.first_name}",
                'description': "AI-generated learning path based on your performance and goals",
                'estimated_duration': "4-6 weeks",
                'phases': []
            }
            
            # Phase 1: Address critical weaknesses
            if student_profile.get('weaknesses'):
                high_priority_weaknesses = [w for w in student_profile['weaknesses'] if w['priority'] == 'high']
                if high_priority_weaknesses:
                    learning_path['phases'].append({
                        'phase_number': 1,
                        'title': "Foundation Building",
                        'duration': "1-2 weeks",
                        'focus': "Address critical knowledge gaps",
                        'activities': [
                            f"Review {w['subject']} fundamentals" for w in high_priority_weaknesses[:3]
                        ]
                    })
            
            # Phase 2: Skill development
            learning_path['phases'].append({
                'phase_number': 2,
                'title': "Skill Development",
                'duration': "2-3 weeks",
                'focus': "Build on strengths and improve weak areas",
                'activities': [
                    "Practice intermediate level quizzes",
                    "Focus on time management",
                    "Regular progress assessment"
                ]
            })
            
            # Phase 3: Advanced learning
            if student_profile.get('performance_metrics', {}).get('overall_average', 0) > 70:
                learning_path['phases'].append({
                    'phase_number': 3,
                    'title': "Advanced Mastery",
                    'duration': "1-2 weeks",
                    'focus': "Challenge yourself with advanced topics",
                    'activities': [
                        "Take advanced level quizzes",
                        "Explore supplementary topics",
                        "Peer collaboration activities"
                    ]
                })
            
            return learning_path
            
        except Exception as e:
            logger.error(f"Learning path generation error: {str(e)}")
            return {'error': str(e)}
    
    def _get_peer_based_recommendations(self, student, student_profile: Dict) -> List[Dict]:
        """Get recommendations based on similar students' success"""
        try:
            # Find similar students using collaborative filtering
            similar_students = self._find_similar_students(student, student_profile)
            
            peer_recommendations = []
            
            for similar_student_data in similar_students[:3]:  # Top 3 similar students
                similar_student = User.objects.get(id=similar_student_data['student_id'])
                
                # Find courses/quizzes that worked well for similar student
                successful_activities = self._get_successful_activities(similar_student)
                
                for activity in successful_activities[:2]:  # Top 2 per similar student
                    peer_recommendations.append({
                        'type': activity['type'],
                        'item_id': activity['id'],
                        'title': activity['title'],
                        'reason': f"Students with similar profiles found this helpful",
                        'peer_success_rate': activity['success_rate'],
                        'similarity_score': similar_student_data['similarity_score']
                    })
            
            return peer_recommendations
            
        except Exception as e:
            logger.error(f"Peer recommendation error: {str(e)}")
            return []
    
    def _find_similar_students(self, student, student_profile: Dict) -> List[Dict]:
        """Find students with similar learning profiles"""
        try:
            # Get other students with performance data
            other_students = User.objects.filter(
                role='student',
                quiz_results__isnull=False
            ).exclude(id=student.id).distinct()
            
            similarities = []
            
            for other_student in other_students:
                other_profile = self._build_student_profile(other_student)
                similarity_score = self._calculate_profile_similarity(student_profile, other_profile)
                
                if similarity_score > 0.7:  # Similarity threshold
                    similarities.append({
                        'student_id': other_student.id,
                        'similarity_score': similarity_score
                    })
            
            return sorted(similarities, key=lambda x: x['similarity_score'], reverse=True)
            
        except Exception as e:
            logger.error(f"Similar students finding error: {str(e)}")
            return []
    
    def _calculate_profile_similarity(self, profile1: Dict, profile2: Dict) -> float:
        """Calculate similarity between two student profiles"""
        try:
            similarity_score = 0.0
            
            # Performance similarity
            perf1 = profile1.get('performance_metrics', {})
            perf2 = profile2.get('performance_metrics', {})
            
            if perf1.get('overall_average') and perf2.get('overall_average'):
                perf_diff = abs(perf1['overall_average'] - perf2['overall_average'])
                perf_similarity = max(0, 1 - perf_diff / 100)  # Normalize to 0-1
                similarity_score += perf_similarity * 0.4
            
            # Subject strength/weakness similarity
            strengths1 = {s['subject'] for s in profile1.get('strengths', [])}
            strengths2 = {s['subject'] for s in profile2.get('strengths', [])}
            
            weaknesses1 = {w['subject'] for w in profile1.get('weaknesses', [])}
            weaknesses2 = {w['subject'] for w in profile2.get('weaknesses', [])}
            
            # Jaccard similarity for strengths and weaknesses
            if strengths1 or strengths2:
                strength_similarity = len(strengths1.intersection(strengths2)) / len(strengths1.union(strengths2))
                similarity_score += strength_similarity * 0.3
            
            if weaknesses1 or weaknesses2:
                weakness_similarity = len(weaknesses1.intersection(weaknesses2)) / len(weaknesses1.union(weaknesses2))
                similarity_score += weakness_similarity * 0.3
            
            return min(similarity_score, 1.0)
            
        except Exception as e:
            logger.error(f"Profile similarity calculation error: {str(e)}")
            return 0.0
    
    def _get_successful_activities(self, student) -> List[Dict]:
        """Get activities where student was successful"""
        try:
            successful_activities = []
            
            # Find quizzes with high scores
            high_scoring_quizzes = QuizResult.objects.filter(
                student=student,
                score__gte=80,
                status='completed'
            ).select_related('quiz')
            
            for result in high_scoring_quizzes:
                successful_activities.append({
                    'type': 'quiz',
                    'id': result.quiz.id,
                    'title': result.quiz.title,
                    'success_rate': result.score,
                    'subject': result.quiz.course.subject.name if result.quiz.course.subject else 'General'
                })
            
            return successful_activities
            
        except Exception as e:
            logger.error(f"Successful activities retrieval error: {str(e)}")
            return []

# Singleton instance
recommendation_engine = RecommendationEngine()
