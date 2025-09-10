from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import datetime, timedelta
import logging

from apps.courses.models import Quiz, Course
from apps.progress.models import QuizResult, StudentProgress
from .serializers import (
    QuizSerializer, QuizListSerializer, StudentQuizSerializer,
    QuestionSerializer
)
from .ai_services import quiz_generator_service

# Custom permissions
from rest_framework.permissions import BasePermission

class IsTeacher(BasePermission):
    """Permission class for teacher-only access"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(request.user, 'role', None) == 'teacher'

class IsStudent(BasePermission):
    """Permission class for student-only access"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(request.user, 'role', None) == 'student'

class IsTeacherOrStudent(BasePermission):
    """Permission class for teacher or student access"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(request.user, 'role', None) in ['teacher', 'student']

class IsQuizOwner(BasePermission):
    """Permission class to ensure teacher can only modify their own quizzes"""
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'teacher':
            return obj.course.instructor == request.user
        return False

logger = logging.getLogger(__name__)
User = get_user_model()


class QuizListCreateView(generics.ListCreateAPIView):
    """
    List quizzes and create new quizzes
    Teachers: See their own course quizzes
    Students: See quizzes from enrolled courses
    """
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrStudent]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return QuizSerializer
        elif self.request.user.role == 'student':
            return QuizListSerializer
        return QuizListSerializer
    
    def get_queryset(self):
        user = self.request.user
        queryset = Quiz.objects.select_related('course', 'course__instructor')
        
        if user.role == 'teacher':
            # Teachers see quizzes from their courses
            queryset = queryset.filter(course__instructor=user)
        elif user.role == 'student':
            # Students see all active quizzes (since CourseEnrollment is disabled)
            # You can modify this logic based on your enrollment tracking method
            queryset = queryset.filter(is_active=True)
        
        # Filters
        course_id = self.request.query_params.get('course_id')
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        
        difficulty = self.request.query_params.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty_level=difficulty)
        
        ai_generated = self.request.query_params.get('ai_generated')
        if ai_generated is not None:
            queryset = queryset.filter(ai_generated=ai_generated.lower() == 'true')
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """Auto-assign course validation for teachers"""
        if self.request.user.role == 'teacher':
            # Additional validation happens in serializer
            serializer.save()
        else:
            return Response(
                {'error': 'Only teachers can create quizzes'},
                status=status.HTTP_403_FORBIDDEN
            )


class QuizDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete quiz
    Teachers: Full access to their quizzes
    Students: Read-only access without answers
    """
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrStudent]
    
    def get_serializer_class(self):
        if self.request.user.role == 'teacher':
            return QuizSerializer
        else:
            return StudentQuizSerializer
    
    def get_queryset(self):
        user = self.request.user
        queryset = Quiz.objects.select_related('course', 'course__instructor')
        
        if user.role == 'teacher':
            return queryset.filter(course__instructor=user)
        elif user.role == 'student':
            # Students see all active quizzes (since CourseEnrollment is disabled)
            # You can modify this logic based on your enrollment tracking method
            return queryset.filter(is_active=True)
        
        return queryset.none()
    
    def update(self, request, *args, **kwargs):
        """Only teachers can update quizzes"""
        if request.user.role != 'teacher':
            return Response(
                {'error': 'Only teachers can update quizzes'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """Only teachers can delete quizzes"""
        if request.user.role != 'teacher':
            return Response(
                {'error': 'Only teachers can delete quizzes'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        quiz = self.get_object()
        # Check if quiz has been taken
        if QuizResult.objects.filter(quiz=quiz).exists():
            return Response(
                {'error': 'Cannot delete quiz that has been taken by students'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return super().destroy(request, *args, **kwargs)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsStudent])
def take_quiz(request, quiz_id):
    """
    Start taking a quiz - returns quiz with questions but no answers
    Creates a new QuizResult record to track the attempt
    """
    try:
        quiz = Quiz.objects.select_related('course').get(id=quiz_id)
    except Quiz.DoesNotExist:
        return Response(
            {'error': 'Quiz not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check if student can take this quiz
    can_take, message = quiz.can_student_take(request.user)
    if not can_take:
        return Response(
            {'error': message},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Check for ongoing attempt
    ongoing_attempt = QuizResult.objects.filter(
        quiz=quiz,
        student=request.user,
        status='in_progress'
    ).first()
    
    if ongoing_attempt:
        # Return existing attempt
        serializer = StudentQuizSerializer(quiz, context={'request': request})
        return Response({
            'quiz': serializer.data,
            'attempt_id': ongoing_attempt.id,
            'time_started': ongoing_attempt.time_started,
            'message': 'Resuming existing attempt'
        })
    
    # Create new attempt
    attempt_number = QuizResult.objects.filter(
        quiz=quiz,
        student=request.user
    ).count() + 1
    
    quiz_result = QuizResult.objects.create(
        student=request.user,
        quiz=quiz,
        attempt_number=attempt_number,
        total_questions=quiz.question_count,
        status='in_progress'
    )
    
    # Create progress record
    progress, created = StudentProgress.objects.get_or_create(
        student=request.user,
        course=quiz.course,
        activity_type='quiz_attempt',
        defaults={
            'status': 'in_progress',
            'started_at': timezone.now()
        }
    )
    
    if not created:
        progress.status = 'in_progress'
        progress.started_at = timezone.now()
        progress.attempts += 1
        progress.save()
    
    quiz_result.progress = progress
    quiz_result.save()
    
    # Return quiz data without answers
    serializer = StudentQuizSerializer(quiz, context={'request': request})
    
    return Response({
        'quiz': serializer.data,
        'attempt_id': quiz_result.id,
        'time_started': quiz_result.time_started,
        'message': 'Quiz started successfully'
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsStudent])
def submit_quiz(request, quiz_id):
    """
    Submit quiz answers and calculate score
    Expects: {'attempt_id': int, 'answers': {question_id: answer}}
    """
    try:
        quiz = Quiz.objects.get(id=quiz_id)
    except Quiz.DoesNotExist:
        return Response(
            {'error': 'Quiz not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    attempt_id = request.data.get('attempt_id')
    answers = request.data.get('answers', {})
    
    if not attempt_id:
        return Response(
            {'error': 'attempt_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get the quiz result
    try:
        quiz_result = QuizResult.objects.get(
            id=attempt_id,
            quiz=quiz,
            student=request.user,
            status='in_progress'
        )
    except QuizResult.DoesNotExist:
        return Response(
            {'error': 'Invalid attempt or quiz already submitted'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Validate and grade answers
    correct_answers = 0
    incorrect_answers = 0
    question_analytics = {}
    
    for question in quiz.questions_data:
        question_id = str(question.get('id'))
        student_answer = answers.get(question_id)
        correct_answer = question.get('correct_answer')
        question_type = question.get('type')
        
        is_correct = False
        
        if question_type == 'multiple_choice':
            try:
                correct_index = int(correct_answer)
                student_index = int(student_answer) if student_answer is not None else -1
                is_correct = correct_index == student_index
            except (ValueError, TypeError):
                is_correct = False
        
        elif question_type == 'true_false':
            correct_bool = str(correct_answer).lower() in ['true', '1']
            student_bool = str(student_answer).lower() in ['true', '1'] if student_answer is not None else None
            is_correct = correct_bool == student_bool
        
        elif question_type in ['short_answer', 'fill_blank']:
            # Simple string comparison (case-insensitive)
            if student_answer and correct_answer:
                is_correct = str(student_answer).strip().lower() == str(correct_answer).strip().lower()
        
        # Record analytics
        question_analytics[question_id] = {
            'correct': is_correct,
            'student_answer': student_answer,
            'correct_answer': correct_answer,
            'points_earned': question.get('points', 10) if is_correct else 0,
            'points_possible': question.get('points', 10),
            'difficulty': question.get('difficulty', 'medium'),
            'tags': question.get('tags', [])
        }
        
        if is_correct:
            correct_answers += 1
        else:
            incorrect_answers += 1
    
    # Calculate final score
    total_questions = len(quiz.questions_data)
    score = (correct_answers / total_questions * 100) if total_questions > 0 else 0
    
    # Update quiz result
    quiz_result.correct_answers = correct_answers
    quiz_result.incorrect_answers = incorrect_answers
    quiz_result.score = score
    quiz_result.answers = answers
    quiz_result.question_analytics = question_analytics
    quiz_result.finish_quiz()
    
    # Determine pass/fail
    passed = score >= quiz.passing_score
    grade = quiz_result.calculate_grade()
    
    # AI Analysis for personalized feedback
    strengths = []
    weaknesses = []
    
    # Analyze performance by tags/concepts
    concept_performance = {}
    for q_id, analytics in question_analytics.items():
        for tag in analytics.get('tags', []):
            if tag not in concept_performance:
                concept_performance[tag] = {'correct': 0, 'total': 0}
            
            concept_performance[tag]['total'] += 1
            if analytics['correct']:
                concept_performance[tag]['correct'] += 1
    
    # Identify strengths and weaknesses
    for concept, performance in concept_performance.items():
        accuracy = performance['correct'] / performance['total']
        if accuracy >= 0.8:
            strengths.append(concept)
        elif accuracy < 0.6:
            weaknesses.append(concept)
    
    quiz_result.strengths_identified = strengths
    quiz_result.weaknesses_identified = weaknesses
    quiz_result.save()
    
    # Prepare response
    response_data = {
        'success': True,
        'score': score,
        'grade': grade,
        'passed': passed,
        'correct_answers': correct_answers,
        'incorrect_answers': incorrect_answers,
        'total_questions': total_questions,
        'strengths': strengths,
        'weaknesses': weaknesses,
        'time_taken': quiz_result.time_taken,
        'attempt_number': quiz_result.attempt_number
    }
    
    # Add detailed results if quiz allows
    if quiz.show_results_immediately:
        response_data['detailed_results'] = question_analytics
    
    return Response(response_data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def quiz_results(request, quiz_id):
    """
    Get quiz results for a specific quiz
    Teachers: All results for their quiz
    Students: Their own results only
    """
    try:
        quiz = Quiz.objects.get(id=quiz_id)
    except Quiz.DoesNotExist:
        return Response(
            {'error': 'Quiz not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Permission check
    user = request.user
    if user.role == 'teacher':
        if quiz.course.instructor != user:
            return Response(
                {'error': 'Access denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        # Teacher sees all results
        results = QuizResult.objects.filter(quiz=quiz).select_related('student')
    elif user.role == 'student':
        # Skip enrollment check since CourseEnrollment is disabled
        # Allow all students to view quiz results
        # Student sees only their results
        results = QuizResult.objects.filter(quiz=quiz, student=user)
    else:
        return Response(
            {'error': 'Access denied'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Serialize results
    results_data = []
    for result in results:
        result_data = {
            'id': result.id,
            'student': result.student.email if user.role == 'teacher' else 'You',
            'attempt_number': result.attempt_number,
            'score': result.score,
            'grade': result.calculate_grade(),
            'passed': result.score >= quiz.passing_score,
            'time_taken': result.time_taken,
            'status': result.status,
            'created_at': result.time_started,
            'completed_at': result.time_completed,
            'strengths': result.strengths_identified,
            'weaknesses': result.weaknesses_identified
        }
        
        # Add detailed analytics for teachers or if student quiz shows results
        if user.role == 'teacher' or quiz.show_results_immediately:
            result_data['question_analytics'] = result.question_analytics
        
        results_data.append(result_data)
    
    return Response({
        'quiz_title': quiz.title,
        'results': results_data,
        'total_results': len(results_data)
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsTeacher])
def quiz_analytics(request, quiz_id):
    """
    Detailed analytics for quiz (teachers only)
    """
    try:
        quiz = Quiz.objects.get(id=quiz_id, course__instructor=request.user)
    except Quiz.DoesNotExist:
        return Response(
            {'error': 'Quiz not found or access denied'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Get all results
    results = QuizResult.objects.filter(quiz=quiz, status='completed')
    
    if not results.exists():
        return Response({
            'message': 'No completed attempts yet',
            'quiz_title': quiz.title,
            'analytics': {}
        })
    
    # Calculate analytics
    analytics = {
        'total_attempts': results.count(),
        'unique_students': results.values('student').distinct().count(),
        'average_score': results.aggregate(Avg('score'))['score__avg'],
        'pass_rate': (results.filter(score__gte=quiz.passing_score).count() / results.count() * 100),
        'score_distribution': {
            'A (90-100)': results.filter(score__gte=90).count(),
            'B (80-89)': results.filter(score__gte=80, score__lt=90).count(),
            'C (70-79)': results.filter(score__gte=70, score__lt=80).count(),
            'D (60-69)': results.filter(score__gte=60, score__lt=70).count(),
            'F (0-59)': results.filter(score__lt=60).count(),
        },
        'average_time': results.aggregate(Avg('time_taken'))['time_taken__avg'],
        'difficulty_analysis': {},
        'concept_analysis': {}
    }
    
    # Question-level analysis
    question_stats = {}
    for result in results:
        for q_id, q_analytics in result.question_analytics.items():
            if q_id not in question_stats:
                question_stats[q_id] = {
                    'correct_count': 0,
                    'total_count': 0,
                    'difficulty': q_analytics.get('difficulty', 'medium'),
                    'tags': q_analytics.get('tags', [])
                }
            
            question_stats[q_id]['total_count'] += 1
            if q_analytics.get('correct', False):
                question_stats[q_id]['correct_count'] += 1
    
    # Process question stats
    question_analytics = {}
    for q_id, stats in question_stats.items():
        accuracy = stats['correct_count'] / stats['total_count']
        question_analytics[q_id] = {
            'accuracy': accuracy,
            'difficulty': stats['difficulty'],
            'tags': stats['tags'],
            'performance_level': 'Easy' if accuracy >= 0.8 else 'Medium' if accuracy >= 0.6 else 'Hard'
        }
    
    analytics['question_analytics'] = question_analytics
    
    return Response({
        'quiz_title': quiz.title,
        'analytics': analytics
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsTeacher])
def generate_ai_quiz(request):
    """
    Generate AI-powered personalized quiz for a student
    Teachers can create adaptive quizzes based on student weaknesses
    """
    
    # Extract request data
    student_id = request.data.get('student_id')
    course_id = request.data.get('course_id')
    topic = request.data.get('topic')
    
    # Validate required fields
    if not all([student_id, course_id, topic]):
        return Response(
            {'error': 'student_id, course_id, and topic are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Verify teacher has access to the course
    try:
        course = Course.objects.get(id=course_id, instructor=request.user)
    except Course.DoesNotExist:
        return Response(
            {'error': 'Course not found or access denied'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Verify student exists (skip enrollment check since CourseEnrollment is disabled)
    try:
        student = User.objects.get(id=student_id, role='student')
    except User.DoesNotExist:
        return Response(
            {'error': 'Student not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Optional parameters
    difficulty_level = request.data.get('difficulty_level', 'medium')
    question_count = request.data.get('question_count', 10)
    question_types = request.data.get('question_types')
    save_to_db = request.data.get('save_to_db', True)
    
    # Validate parameters
    if question_count < 1 or question_count > 50:
        return Response(
            {'error': 'question_count must be between 1 and 50'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if difficulty_level not in ['easy', 'medium', 'hard']:
        return Response(
            {'error': 'difficulty_level must be easy, medium, or hard'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Generate personalized quiz
    try:
        result = quiz_generator_service.create_personalized_quiz(
            student_id=student_id,
            course_id=course_id,
            topic=topic,
            difficulty_level=difficulty_level,
            question_count=question_count,
            question_types=question_types,
            save_to_db=save_to_db
        )
        
        if result['success']:
            return Response({
                'success': True,
                'message': 'AI quiz generated successfully',
                'quiz_data': result['quiz_data'],
                'generation_info': result['generation_info'],
                'student_analysis': result['student_analysis'],
                'quiz_id': result.get('quiz_id'),
                'recommendations': {
                    'focus_areas': [w['concept'] for w in result['student_analysis']['weaknesses']],
                    'adaptive_score': result['quiz_data']['passing_score'],
                    'estimated_time': result['quiz_data']['time_limit']
                }
            })
        else:
            return Response({
                'success': False,
                'error': result['error'],
                'fallback_available': result.get('fallback_available', False)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    except Exception as e:
        logger.error(f"AI quiz generation error: {str(e)}")
        return Response(
            {'error': 'Failed to generate AI quiz', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsTeacher])
def student_analysis(request, student_id, course_id):
    """
    Get detailed analysis of a student's performance for AI quiz generation
    Helps teachers understand student's learning patterns
    """
    
    # Verify teacher has access to the course
    try:
        course = Course.objects.get(id=course_id, instructor=request.user)
    except Course.DoesNotExist:
        return Response(
            {'error': 'Course not found or access denied'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Verify student exists (skip enrollment check since CourseEnrollment is disabled)
    try:
        student = User.objects.get(id=student_id, role='student')
    except User.DoesNotExist:
        return Response(
            {'error': 'Student not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    try:
        # Analyze student performance
        from .ai_services import StudentAnalyzer
        analyzer = StudentAnalyzer(student_id)
        
        performance_summary = analyzer.get_performance_summary(course_id)
        weaknesses = analyzer.identify_weaknesses(course_id)
        strengths = analyzer.get_strengths(course_id)
        
        return Response({
            'student_email': student.email,
            'course_title': course.title,
            'performance_summary': performance_summary,
            'weaknesses': weaknesses,
            'strengths': strengths,
            'recommendations': {
                'suggested_topics': [w['concept'] for w in weaknesses[:5]],
                'difficulty_recommendation': (
                    'easy' if performance_summary['overall_average_score'] < 60 
                    else 'hard' if performance_summary['overall_average_score'] > 85 
                    else 'medium'
                ),
                'question_count_suggestion': (
                    min(15, max(5, len(weaknesses) * 2))
                ),
                'focus_strategy': (
                    'remedial' if performance_summary['overall_average_score'] < 70
                    else 'advanced' if performance_summary['overall_average_score'] > 90
                    else 'balanced'
                )
            }
        })
        
    except Exception as e:
        logger.error(f"Student analysis error: {str(e)}")
        return Response(
            {'error': 'Failed to analyze student performance', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def ai_quiz_suggestions(request):
    """
    Get AI-powered quiz suggestions for the current user
    Students: Get suggestions based on their performance
    Teachers: Get suggestions for their students
    """
    
    user = request.user
    
    if user.role == 'student':
        # Get suggestions for the student
        try:
            from .ai_services import StudentAnalyzer
            analyzer = StudentAnalyzer(user.id)
            
            # Since CourseEnrollment is disabled, show suggestions for all available courses
            # You can modify this logic based on your enrollment tracking method
            courses = Course.objects.filter(status='published', is_active=True)
            
            suggestions = []
            
            for course in courses:
                performance = analyzer.get_performance_summary(course.id)
                weaknesses = analyzer.identify_weaknesses(course.id, limit=3)
                
                if weaknesses:  # Only suggest if there are identified weaknesses
                    suggestions.append({
                        'course_id': course.id,
                        'course_title': course.title,
                        'suggested_topics': [w['concept'] for w in weaknesses],
                        'priority_level': (
                            'high' if performance['overall_average_score'] < 70
                            else 'medium' if performance['overall_average_score'] < 85
                            else 'low'
                        ),
                        'performance_trend': performance['performance_trend'],
                        'last_quiz_score': performance['recent_average_score']
                    })
            
            return Response({
                'suggestions': suggestions,
                'message': 'Personalized quiz suggestions based on your performance'
            })
            
        except Exception as e:
            return Response(
                {'error': 'Failed to get suggestions', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    elif user.role == 'teacher':
        # Get suggestions for teacher's students
        try:
            # Get teacher's courses
            courses = Course.objects.filter(instructor=user)
            
            suggestions = []
            
            for course in courses:
                # Since CourseEnrollment is disabled, get all students for now
                # You can modify this logic based on your enrollment tracking method
                students = User.objects.filter(role='student', is_active=True)
                
                for student in students:
                    
                    try:
                        from .ai_services import StudentAnalyzer
                        analyzer = StudentAnalyzer(student.id)
                        performance = analyzer.get_performance_summary(course.id)
                        
                        # Only suggest for students who have taken quizzes
                        if performance['total_quizzes_taken'] > 0:
                            weaknesses = analyzer.identify_weaknesses(course.id, limit=3)
                            
                            if weaknesses:  # Student has identifiable weaknesses
                                suggestions.append({
                                    'student_id': student.id,
                                    'student_email': student.email,
                                    'course_id': course.id,
                                    'course_title': course.title,
                                    'suggested_topics': [w['concept'] for w in weaknesses],
                                    'urgency_level': (
                                        'urgent' if performance['overall_average_score'] < 60
                                        else 'moderate' if performance['overall_average_score'] < 75
                                        else 'low'
                                    ),
                                    'performance_trend': performance['performance_trend'],
                                    'avg_score': performance['overall_average_score'],
                                    'quizzes_taken': performance['total_quizzes_taken']
                                })
                    except Exception as e:
                        logger.warning(f"Failed to analyze student {student.id}: {str(e)}")
                        continue
            
            # Sort by urgency
            suggestions.sort(key=lambda x: {
                'urgent': 0, 'moderate': 1, 'low': 2
            }[x['urgency_level']])
            
            return Response({
                'suggestions': suggestions,
                'message': 'Students who would benefit from personalized AI quizzes'
            })
            
        except Exception as e:
            return Response(
                {'error': 'Failed to get teacher suggestions', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    else:
        return Response(
            {'error': 'Access denied'},
            status=status.HTTP_403_FORBIDDEN
        )
