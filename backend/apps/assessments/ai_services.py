"""
AI Quiz Generation Services
Automatically generate quizzes based on student performance and weaknesses
"""

import json
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

import requests
import json
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Avg, Count, Q

from apps.courses.models import Course, Subject, Quiz
from apps.progress.models import QuizResult, StudentProgress
from apps.users.models import StudentProfile

User = get_user_model()
logger = logging.getLogger(__name__)

@dataclass
class QuizGenerationRequest:
    """Data class for quiz generation requests"""
    student_id: int
    course_id: int
    topic: str
    difficulty_level: str = 'medium'
    question_count: int = 10
    question_types: List[str] = None
    target_concepts: List[str] = None
    focus_on_weaknesses: bool = True

class StudentAnalyzer:
    """Analyze student performance to identify learning patterns and weaknesses"""
    
    def __init__(self, student_id: int):
        self.student_id = student_id
        try:
            self.student = User.objects.get(id=student_id)
        except User.DoesNotExist:
            raise ValueError(f"Student with ID {student_id} not found")
        
    def get_performance_summary(self, course_id: Optional[int] = None) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        queryset = QuizResult.objects.filter(student=self.student, status='completed')
        
        if course_id:
            queryset = queryset.filter(quiz__course_id=course_id)
        
        # Recent performance (last 30 days)
        recent_date = timezone.now() - timedelta(days=30)
        recent_results = queryset.filter(created_at__gte=recent_date)
        
        # Calculate metrics
        total_quizzes = queryset.count()
        recent_quizzes = recent_results.count()
        avg_score = queryset.aggregate(Avg('score'))['score__avg'] or 0
        recent_avg_score = recent_results.aggregate(Avg('score'))['score__avg'] or 0
        
        return {
            'total_quizzes_taken': total_quizzes,
            'recent_quizzes_taken': recent_quizzes,
            'overall_average_score': round(avg_score, 2),
            'recent_average_score': round(recent_avg_score, 2),
            'performance_trend': self._calculate_trend(queryset),
            'learning_velocity': recent_quizzes / 30.0 if recent_quizzes > 0 else 0
        }
    
    def identify_weaknesses(self, course_id: Optional[int] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Identify student's weak areas based on quiz performance"""
        queryset = QuizResult.objects.filter(
            student=self.student, 
            status='completed'
        )
        
        if course_id:
            queryset = queryset.filter(quiz__course_id=course_id)
        
        # Aggregate weaknesses from all quiz results
        weakness_stats = {}
        
        for result in queryset:
            for weakness in result.weaknesses_identified:
                if weakness not in weakness_stats:
                    weakness_stats[weakness] = {
                        'concept': weakness,
                        'occurrence_count': 0,
                        'total_questions': 0,
                        'correct_answers': 0,
                        'recent_performance': []
                    }
                
                weakness_stats[weakness]['occurrence_count'] += 1
                
                # Analyze question-level performance for this concept
                for q_id, analytics in result.question_analytics.items():
                    if weakness in analytics.get('tags', []):
                        weakness_stats[weakness]['total_questions'] += 1
                        if analytics.get('correct', False):
                            weakness_stats[weakness]['correct_answers'] += 1
                        
                        # Track recent performance
                        weakness_stats[weakness]['recent_performance'].append({
                            'correct': analytics.get('correct', False),
                            'date': result.created_at,
                            'difficulty': analytics.get('difficulty', 'medium')
                        })
        
        # Calculate accuracy and priority for each weakness
        weaknesses = []
        for concept, stats in weakness_stats.items():
            if stats['total_questions'] > 0:
                accuracy = stats['correct_answers'] / stats['total_questions']
                
                # Recent performance trend (last 5 attempts)
                recent_attempts = sorted(
                    stats['recent_performance'], 
                    key=lambda x: x['date'], 
                    reverse=True
                )[:5]
                
                recent_accuracy = sum(1 for attempt in recent_attempts if attempt['correct']) / len(recent_attempts) if recent_attempts else 0
                
                # Priority score (lower accuracy = higher priority)
                priority_score = (1 - accuracy) * stats['occurrence_count']
                
                weaknesses.append({
                    'concept': concept,
                    'accuracy': round(accuracy, 3),
                    'recent_accuracy': round(recent_accuracy, 3),
                    'occurrence_count': stats['occurrence_count'],
                    'total_questions': stats['total_questions'],
                    'priority_score': round(priority_score, 3),
                    'improvement_needed': accuracy < 0.7,
                    'recent_attempts': len(recent_attempts)
                })
        
        # Sort by priority score (highest first)
        weaknesses.sort(key=lambda x: x['priority_score'], reverse=True)
        
        return weaknesses[:limit]
    
    def get_strengths(self, course_id: Optional[int] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Identify student's strong areas"""
        queryset = QuizResult.objects.filter(
            student=self.student, 
            status='completed'
        )
        
        if course_id:
            queryset = queryset.filter(quiz__course_id=course_id)
        
        # Aggregate strengths
        strength_stats = {}
        
        for result in queryset:
            for strength in result.strengths_identified:
                if strength not in strength_stats:
                    strength_stats[strength] = {
                        'concept': strength,
                        'occurrence_count': 0,
                        'total_questions': 0,
                        'correct_answers': 0
                    }
                
                strength_stats[strength]['occurrence_count'] += 1
                
                # Analyze question-level performance
                for q_id, analytics in result.question_analytics.items():
                    if strength in analytics.get('tags', []):
                        strength_stats[strength]['total_questions'] += 1
                        if analytics.get('correct', False):
                            strength_stats[strength]['correct_answers'] += 1
        
        # Calculate accuracy for strengths
        strengths = []
        for concept, stats in strength_stats.items():
            if stats['total_questions'] > 0:
                accuracy = stats['correct_answers'] / stats['total_questions']
                
                strengths.append({
                    'concept': concept,
                    'accuracy': round(accuracy, 3),
                    'occurrence_count': stats['occurrence_count'],
                    'total_questions': stats['total_questions'],
                    'mastery_level': 'high' if accuracy >= 0.9 else 'medium' if accuracy >= 0.8 else 'developing'
                })
        
        # Sort by accuracy (highest first)
        strengths.sort(key=lambda x: x['accuracy'], reverse=True)
        
        return strengths[:limit]
    
    def _calculate_trend(self, queryset) -> str:
        """Calculate performance trend"""
        recent_results = queryset.order_by('-created_at')[:10]
        
        if len(recent_results) < 3:
            return 'insufficient_data'
        
        scores = [result.score for result in recent_results]
        
        # Simple trend analysis
        first_half_avg = sum(scores[:len(scores)//2]) / (len(scores)//2)
        second_half_avg = sum(scores[len(scores)//2:]) / (len(scores) - len(scores)//2)
        
        if second_half_avg > first_half_avg + 5:
            return 'improving'
        elif second_half_avg < first_half_avg - 5:
            return 'declining'
        else:
            return 'stable'

class AIQuizGenerator:
    """Generate quizzes using DeepSeek API based on student analysis"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'DEEPSEEK_API_KEY', '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')
        self.api_url = "https://api.deepseek.com/chat/completions"
        
    def generate_quiz(self, request: QuizGenerationRequest) -> Dict[str, Any]:
        """Generate a complete quiz based on student weaknesses"""
        try:
            # Analyze student performance
            analyzer = StudentAnalyzer(request.student_id)
            weaknesses = analyzer.identify_weaknesses(request.course_id)
            strengths = analyzer.get_strengths(request.course_id)
            performance = analyzer.get_performance_summary(request.course_id)
            
            # Get course context
            course = Course.objects.get(id=request.course_id)
            
            # Generate questions using AI or fallback
            questions = self._generate_questions_with_ai(
                course=course,
                topic=request.topic,
                weaknesses=weaknesses,
                strengths=strengths,
                performance=performance,
                difficulty_level=request.difficulty_level,
                question_count=request.question_count,
                question_types=request.question_types or ['multiple_choice', 'true_false', 'short_answer']
            )
            
            # Create quiz data structure
            quiz_data = {
                'title': f"AI-Generated {request.topic} Quiz",
                'description': f"Personalized quiz focusing on {request.topic} concepts, targeting identified weak areas.",
                'course': request.course_id,
                'questions_data': questions,
                'difficulty_level': request.difficulty_level,
                'ai_generated': True,
                'target_concepts': request.target_concepts or [w['concept'] for w in weaknesses[:5]],
                'passing_score': self._calculate_adaptive_passing_score(performance),
                'time_limit': max(len(questions) * 1.5, 15),  # 1.5 min per question, min 15 min
                'attempts_allowed': 2,
                'show_results_immediately': True,
                'shuffle_questions': True
            }
            
            return {
                'success': True,
                'quiz_data': quiz_data,
                'generation_info': {
                    'weaknesses_targeted': len(weaknesses),
                    'strengths_reinforced': len(strengths),
                    'performance_trend': performance['performance_trend'],
                    'difficulty_level': request.difficulty_level,
                    'ai_model_used': 'deepseek-chat' if self.api_key else 'fallback'
                },
                'student_analysis': {
                    'weaknesses': weaknesses[:5],
                    'strengths': strengths[:3],
                    'performance_summary': performance
                }
            }
            
        except Exception as e:
            logger.error(f"AI Quiz generation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'fallback_available': True
            }
    
    def _generate_questions_with_ai(self, course, topic, weaknesses, strengths, performance, 
                                  difficulty_level, question_count, question_types) -> List[Dict]:
        """Use OpenAI to generate questions or fallback to templates"""
        
        # Try AI generation if API key is available
        if self.api_key:
            try:
                return self._generate_with_deepseek(
                    course, topic, weaknesses, strengths, performance, 
                    difficulty_level, question_count, question_types
                )
            except Exception as e:
                logger.warning(f"DeepSeek generation failed, using fallback: {str(e)}")
        
        # Fallback to template-based generation
        return self._generate_fallback_questions(topic, weaknesses, question_count)
    
    def _generate_with_deepseek(self, course, topic, weaknesses, strengths, performance,
                             difficulty_level, question_count, question_types) -> List[Dict]:
        """Generate questions using DeepSeek API"""
        
        # Prepare context for AI
        context = {
            'course_title': course.title,
            'course_description': course.description,
            'topic': topic,
            'difficulty_level': difficulty_level,
            'student_weaknesses': [w['concept'] for w in weaknesses[:5]],
            'student_strengths': [s['concept'] for s in strengths[:3]],
            'performance_trend': performance['performance_trend'],
            'average_score': performance['overall_average_score']
        }
        
        # Create AI prompt
        prompt = self._create_ai_prompt(context, question_count, question_types)
        
        # Call DeepSeek API
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "You are an expert educational content creator specializing in adaptive learning and personalized assessments."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 3000,
            "temperature": 0.7
        }
        
        response = requests.post(self.api_url, headers=headers, json=data)
        response.raise_for_status()
        
        # Parse AI response
        response_data = response.json()
        ai_response = response_data['choices'][0]['message']['content']
        questions = self._parse_ai_response(ai_response)
        
        # Validate and enhance questions
        return self._validate_and_enhance_questions(questions, weaknesses)
    
    def _create_ai_prompt(self, context, question_count, question_types) -> str:
        """Create detailed prompt for AI question generation"""
        
        prompt = f"""
Generate {question_count} educational quiz questions for the course "{context['course_title']}" on the topic "{context['topic']}".

**Course Context:**
- Course: {context['course_title']}
- Description: {context['course_description']}
- Topic Focus: {context['topic']}
- Difficulty Level: {context['difficulty_level']}

**Student Analysis:**
- Weak Areas: {', '.join(context['student_weaknesses'])}
- Strong Areas: {', '.join(context['student_strengths'])}
- Performance Trend: {context['performance_trend']}
- Average Score: {context['average_score']}%

**Requirements:**
1. Focus 70% of questions on weak areas to help student improve
2. Include 30% questions on strong areas for confidence building
3. Use difficulty level: {context['difficulty_level']}
4. Question types to use: {', '.join(question_types)}
5. Include educational explanations for each answer
6. Tag each question with relevant concepts for analytics

**Output Format (JSON):**
```json
[
  {{
    "id": 1,
    "type": "multiple_choice",
    "question": "Your question here",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": "0",
    "explanation": "Detailed explanation of why this is correct",
    "difficulty": "easy|medium|hard",
    "tags": ["concept1", "concept2"],
    "points": 10
  }}
]
```

**Question Type Guidelines:**
- multiple_choice: 4 options, correct_answer is index (0-3)
- true_false: 2 options ["True", "False"], correct_answer is "true" or "false"
- short_answer: correct_answer is the expected answer string
- fill_blank: question has _____ blank, correct_answer fills the blank

Generate exactly {question_count} questions focusing on student improvement:
"""
        
        return prompt
    
    def _parse_ai_response(self, ai_response: str) -> List[Dict]:
        """Parse AI response to extract questions"""
        try:
            # Extract JSON from response
            start_idx = ai_response.find('[')  
            end_idx = ai_response.rfind(']') + 1
            
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON array found in AI response")
            
            json_str = ai_response[start_idx:end_idx]
            questions = json.loads(json_str)
            
            return questions
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse AI response: {str(e)}")
            logger.error(f"AI Response: {ai_response}")
            
            # Return empty list, will trigger fallback
            return []
    
    def _validate_and_enhance_questions(self, questions: List[Dict], weaknesses: List[Dict]) -> List[Dict]:
        """Validate and enhance generated questions"""
        validated_questions = []
        
        for i, question in enumerate(questions):
            try:
                # Ensure required fields
                enhanced_question = {
                    'id': i + 1,
                    'type': question.get('type', 'multiple_choice'),
                    'question': question.get('question', ''),
                    'options': question.get('options', []),
                    'correct_answer': str(question.get('correct_answer', '')),
                    'explanation': question.get('explanation', ''),
                    'difficulty': question.get('difficulty', 'medium'),
                    'tags': question.get('tags', []),
                    'points': question.get('points', 10)
                }
                
                # Validate based on question type
                if self._is_valid_question(enhanced_question):
                    validated_questions.append(enhanced_question)
                    
            except Exception as e:
                logger.warning(f"Skipping invalid question {i}: {str(e)}")
                continue
        
        # If no valid questions, generate fallback
        if not validated_questions:
            logger.warning("No valid questions from AI, using fallback")
            return self._generate_fallback_questions("General Topic", weaknesses, 5)
        
        return validated_questions
    
    def _is_valid_question(self, question: Dict) -> bool:
        """Validate individual question structure"""
        required_fields = ['question', 'type', 'correct_answer']
        
        # Check required fields
        for field in required_fields:
            if not question.get(field):
                return False
        
        # Type-specific validation
        if question['type'] == 'multiple_choice':
            options = question.get('options', [])
            if len(options) < 2:
                return False
            try:
                correct_idx = int(question['correct_answer'])
                if correct_idx < 0 or correct_idx >= len(options):
                    return False
            except ValueError:
                return False
        
        elif question['type'] == 'true_false':
            if question['correct_answer'].lower() not in ['true', 'false']:
                return False
        
        return True
    
    def _generate_fallback_questions(self, topic: str, weaknesses: List[Dict], 
                                   question_count: int) -> List[Dict]:
        """Generate basic questions as fallback when AI fails"""
        fallback_questions = []
        
        # If no weaknesses identified, create general questions
        if not weaknesses:
            weaknesses = [{'concept': topic.lower()}] * question_count
        
        # Create simple template questions focused on weaknesses
        for i, weakness in enumerate(weaknesses[:question_count]):
            concept = weakness['concept']
            
            fallback_question = {
                'id': i + 1,
                'type': 'multiple_choice',
                'question': f"Which statement about {concept} is most accurate?",
                'options': [
                    f"{concept} is fundamental to understanding {topic}",
                    f"{concept} is not related to {topic}",
                    f"{concept} is optional when learning {topic}",
                    f"{concept} is deprecated in modern {topic}"
                ],
                'correct_answer': '0',
                'explanation': f"Understanding {concept} is crucial for mastering {topic}.",
                'difficulty': 'medium',
                'tags': [concept, topic.lower()],
                'points': 10
            }
            
            fallback_questions.append(fallback_question)
        
        return fallback_questions
    
    def _calculate_adaptive_passing_score(self, performance: Dict) -> float:
        """Calculate adaptive passing score based on student performance"""
        avg_score = performance['overall_average_score']
        trend = performance['performance_trend']
        
        # Base passing score
        base_score = 70.0
        
        # Adjust based on performance
        if avg_score < 60:
            # Lower passing score for struggling students
            adapted_score = max(50.0, avg_score * 0.8)
        elif avg_score > 90:
            # Higher passing score for high performers
            adapted_score = min(85.0, base_score + 10)
        else:
            # Standard passing score with slight adjustment
            adapted_score = base_score
        
        # Adjust based on trend
        if trend == 'improving':
            adapted_score = min(adapted_score + 5, 80.0)
        elif trend == 'declining':
            adapted_score = max(adapted_score - 5, 60.0)
        
        return round(adapted_score, 1)

class QuizGenerationService:
    """Main service for AI-powered quiz generation"""
    
    def __init__(self):
        self.ai_generator = AIQuizGenerator()
    
    def create_personalized_quiz(self, student_id: int, course_id: int, 
                                topic: str, **kwargs) -> Dict[str, Any]:
        """Create a personalized quiz for a student"""
        
        # Validate inputs
        try:
            student = User.objects.get(id=student_id, role='student')
            course = Course.objects.get(id=course_id)
        except User.DoesNotExist:
            return {'success': False, 'error': 'Student not found'}
        except Course.DoesNotExist:
            return {'success': False, 'error': 'Course not found'}
        
        # Skip enrollment check since CourseEnrollment model is disabled
        # You can implement alternative enrollment checking logic here if needed
        # For now, allow all students to access quizzes
        
        # Create generation request
        request = QuizGenerationRequest(
            student_id=student_id,
            course_id=course_id,
            topic=topic,
            difficulty_level=kwargs.get('difficulty_level', 'medium'),
            question_count=kwargs.get('question_count', 10),
            question_types=kwargs.get('question_types'),
            target_concepts=kwargs.get('target_concepts'),
            focus_on_weaknesses=kwargs.get('focus_on_weaknesses', True)
        )
        
        # Generate quiz
        result = self.ai_generator.generate_quiz(request)
        
        if result['success']:
            # Optionally save the quiz to database
            if kwargs.get('save_to_db', False):
                quiz = self._save_quiz_to_db(result['quiz_data'], course.instructor)
                result['quiz_id'] = quiz.id
        
        return result
    
    def _save_quiz_to_db(self, quiz_data: Dict, instructor: User) -> Quiz:
        """Save generated quiz to database"""
        quiz = Quiz.objects.create(
            title=quiz_data['title'],
            description=quiz_data['description'],
            course_id=quiz_data['course'],
            questions_data=quiz_data['questions_data'],
            difficulty_level=quiz_data['difficulty_level'],
            ai_generated=quiz_data['ai_generated'],
            target_concepts=quiz_data['target_concepts'],
            passing_score=quiz_data['passing_score'],
            time_limit=quiz_data['time_limit'],
            attempts_allowed=quiz_data['attempts_allowed'],
            show_results_immediately=quiz_data['show_results_immediately'],
            shuffle_questions=quiz_data['shuffle_questions']
        )
        
        logger.info(f"AI-generated quiz saved: {quiz.title} (ID: {quiz.id})")
        return quiz

# Service instance
quiz_generator_service = QuizGenerationService()
