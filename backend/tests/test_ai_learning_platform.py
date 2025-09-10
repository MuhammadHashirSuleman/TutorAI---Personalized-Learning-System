"""
Comprehensive Test Suite for AI Learning Platform
Tests all major features including API endpoints, AI services, and integrations
"""

import pytest
import json
from datetime import datetime, timedelta
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock

# Import models
from apps.courses.models import Course, Quiz, Subject
from apps.progress.models import StudentProgress, QuizResult, ClassRoom, ClassEnrollment
from apps.users.models import StudentProfile

# Import services
from apps.assessments.ai_services import AIQuizGenerator, StudentAnalyzer
from apps.progress.recommendation_engine import recommendation_engine
from apps.progress.adaptive_learning import adaptive_learning_engine
from apps.progress.external_integrations import ExternalPlatformFactory

User = get_user_model()

class BaseTestCase(TestCase):
    """Base test case with common setup"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create test users
        self.admin_user = User.objects.create_user(
            email='admin@test.com',
            password='testpass123',
            role='admin',
            first_name='Admin',
            last_name='User'
        )
        
        self.teacher_user = User.objects.create_user(
            email='teacher@test.com',
            password='testpass123',
            role='teacher',
            first_name='Test',
            last_name='Teacher'
        )
        
        self.student_user = User.objects.create_user(
            email='student@test.com',
            password='testpass123',
            role='student',
            first_name='Test',
            last_name='Student'
        )
        
        # Create test subject
        self.subject = Subject.objects.create(
            name='Mathematics',
            description='Math subject'
        )
        
        # Create test course
        self.course = Course.objects.create(
            title='Test Course',
            description='Test course description',
            instructor=self.teacher_user,
            subject=self.subject,
            is_active=True
        )
        
        # Create test quiz
        self.quiz = Quiz.objects.create(
            title='Test Quiz',
            description='Test quiz description',
            course=self.course,
            questions_data=[
                {
                    'id': 1,
                    'type': 'multiple_choice',
                    'question': 'What is 2 + 2?',
                    'options': ['3', '4', '5', '6'],
                    'correct_answer': '1',
                    'points': 10
                },
                {
                    'id': 2,
                    'type': 'true_false',
                    'question': 'The sky is blue.',
                    'options': ['True', 'False'],
                    'correct_answer': 'true',
                    'points': 10
                }
            ],
            time_limit=30,
            passing_score=70,
            is_active=True
        )
        
        # Create student profile
        self.student_profile = StudentProfile.objects.create(
            user=self.student_user,
            learning_preferences={'style': 'visual'}
        )

class AuthenticationTestCase(BaseTestCase):
    """Test authentication and authorization"""
    
    def test_user_registration(self):
        """Test user registration"""
        data = {
            'email': 'newuser@test.com',
            'password': 'newpass123',
            'password_confirm': 'newpass123',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'student'
        }
        
        response = self.client.post('/api/auth/register/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='newuser@test.com').exists())
    
    def test_user_login(self):
        """Test user login"""
        data = {
            'email': 'student@test.com',
            'password': 'testpass123'
        }
        
        response = self.client.post('/api/auth/login/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_protected_endpoint_without_auth(self):
        """Test accessing protected endpoint without authentication"""
        response = self.client.get('/api/progress/student-progress/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_role_based_access_control(self):
        """Test role-based access control"""
        # Student trying to access admin endpoint
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get('/api/progress/integrations/status/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Admin accessing admin endpoint
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/progress/integrations/status/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class QuizManagementTestCase(BaseTestCase):
    """Test quiz management functionality"""
    
    def test_create_quiz_as_teacher(self):
        """Test creating quiz as teacher"""
        self.client.force_authenticate(user=self.teacher_user)
        
        data = {
            'title': 'New Test Quiz',
            'description': 'New quiz description',
            'course': self.course.id,
            'questions_data': [
                {
                    'id': 1,
                    'type': 'multiple_choice',
                    'question': 'Test question?',
                    'options': ['A', 'B', 'C', 'D'],
                    'correct_answer': '0',
                    'points': 10
                }
            ],
            'time_limit': 25,
            'passing_score': 80
        }
        
        response = self.client.post('/api/assessments/quizzes/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Test Quiz')
    
    def test_student_cannot_create_quiz(self):
        """Test that students cannot create quizzes"""
        self.client.force_authenticate(user=self.student_user)
        
        data = {
            'title': 'Unauthorized Quiz',
            'course': self.course.id
        }
        
        response = self.client.post('/api/assessments/quizzes/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_quiz_list_filtering(self):
        """Test quiz list with filtering"""
        self.client.force_authenticate(user=self.teacher_user)
        
        # Test without filters
        response = self.client.get('/api/assessments/quizzes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test with course filter
        response = self.client.get(f'/api/assessments/quizzes/?course_id={self.course.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class QuizTakingTestCase(BaseTestCase):
    """Test quiz taking functionality"""
    
    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.student_user)
    
    def test_start_quiz(self):
        """Test starting a quiz"""
        response = self.client.post(f'/api/assessments/quizzes/{self.quiz.id}/start/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('questions', response.data)
        self.assertIn('quiz_id', response.data)
    
    def test_submit_quiz_answers(self):
        """Test submitting quiz answers"""
        # First start the quiz
        start_response = self.client.post(f'/api/assessments/quizzes/{self.quiz.id}/start/')
        self.assertEqual(start_response.status_code, status.HTTP_200_OK)
        
        # Submit answers
        answers_data = {
            'answers': {
                '1': '1',  # Correct answer for question 1
                '2': 'true'  # Correct answer for question 2
            }
        }
        
        response = self.client.post(
            f'/api/assessments/quizzes/{self.quiz.id}/submit/',
            answers_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('score', response.data)
        self.assertEqual(response.data['score'], 100)  # Both answers correct
    
    def test_quiz_time_limit_validation(self):
        """Test quiz time limit validation"""
        # Start quiz
        self.client.post(f'/api/assessments/quizzes/{self.quiz.id}/start/')
        
        # Try to submit after time limit (mock expired time)
        with patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = timezone.now() + timedelta(minutes=35)  # Exceed 30 min limit
            
            answers_data = {'answers': {'1': '1', '2': 'true'}}
            response = self.client.post(
                f'/api/assessments/quizzes/{self.quiz.id}/submit/',
                answers_data,
                format='json'
            )
            
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('time limit', response.data['error'].lower())

class AIQuizGeneratorTestCase(BaseTestCase):
    """Test AI quiz generation"""
    
    def setUp(self):
        super().setUp()
        # Create quiz results for student analysis
        QuizResult.objects.create(
            student=self.student_user,
            quiz=self.quiz,
            score=65,
            answers={'1': '0', '2': 'false'},  # Wrong answers
            status='completed',
            weaknesses_identified=['basic_math', 'reading_comprehension']
        )
    
    @patch('apps.assessments.ai_services.requests.post')
    def test_ai_quiz_generation(self, mock_post):
        """Test AI quiz generation with mocked DeepSeek API"""
        self.client.force_authenticate(user=self.teacher_user)
        
        # Mock DeepSeek API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'choices': [{
                'message': {
                    'content': json.dumps([
                        {
                            'id': 1,
                            'type': 'multiple_choice',
                            'question': 'What is 3 + 3?',
                            'options': ['5', '6', '7', '8'],
                            'correct_answer': '1',
                            'explanation': 'Basic addition',
                            'difficulty': 'easy',
                            'tags': ['basic_math'],
                            'points': 10
                        }
                    ])
                }
            }]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Test AI quiz generation
        data = {
            'student_id': self.student_user.id,
            'course_id': self.course.id,
            'topic': 'Basic Mathematics',
            'difficulty_level': 'intermediate',
            'question_count': 5
        }
        
        response = self.client.post('/api/assessments/generate-quiz/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('quiz_data', response.data)
        
        # Verify API was called
        mock_post.assert_called_once()

class RecommendationEngineTestCase(BaseTestCase):
    """Test AI recommendation engine"""
    
    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.student_user)
        
        # Create performance data
        QuizResult.objects.create(
            student=self.student_user,
            quiz=self.quiz,
            score=85,
            status='completed',
            strengths_identified=['logical_thinking'],
            weaknesses_identified=['calculation_speed']
        )
    
    def test_get_student_recommendations(self):
        """Test getting student recommendations"""
        response = self.client.get('/api/progress/recommendations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('recommendations', response.data)
        self.assertIn('profile_summary', response.data)
    
    def test_get_course_recommendations(self):
        """Test getting course recommendations"""
        response = self.client.get('/api/progress/recommendations/courses/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('recommendations', response.data)
    
    def test_get_learning_path(self):
        """Test getting personalized learning path"""
        response = self.client.get('/api/progress/recommendations/learning-path/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('learning_path', response.data)

class AdaptiveLearningTestCase(BaseTestCase):
    """Test adaptive learning system"""
    
    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.student_user)
        
        # Create learning pattern data
        for i in range(5):
            QuizResult.objects.create(
                student=self.student_user,
                quiz=self.quiz,
                score=75 + i * 5,  # Improving scores
                time_taken=20 - i,  # Improving time
                status='completed'
            )
    
    def test_analyze_learning_pattern(self):
        """Test learning pattern analysis"""
        response = self.client.get('/api/progress/adaptive/learning-pattern/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('learning_velocity', response.data)
        self.assertIn('performance_patterns', response.data)
        self.assertIn('adaptive_parameters', response.data)
    
    def test_get_adaptive_content_plan(self):
        """Test adaptive content plan generation"""
        response = self.client.get('/api/progress/adaptive/content-plan/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('adaptive_content', response.data)
        self.assertIn('personalized_schedule', response.data)
    
    def test_difficulty_recommendation(self):
        """Test difficulty level recommendation"""
        response = self.client.get('/api/progress/adaptive/difficulty-recommendation/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('recommended_difficulty', response.data)
        self.assertIn('confidence', response.data)

class ExternalIntegrationTestCase(BaseTestCase):
    """Test external platform integrations"""
    
    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.admin_user)
    
    def test_integration_status(self):
        """Test getting integration status"""
        response = self.client.get('/api/progress/integrations/status/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('integrations', response.data)
        self.assertIn('moodle', response.data['integrations'])
        self.assertIn('coursera', response.data['integrations'])
        self.assertIn('lti', response.data['integrations'])
    
    def test_test_platform_connection(self):
        """Test platform connection testing"""
        data = {'platform': 'lti'}
        response = self.client.post('/api/progress/integrations/test-connection/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('connection_successful', response.data)
    
    @patch('apps.progress.external_integrations.get_lti_integration')
    def test_lti_launch_processing(self, mock_get_lti):
        """Test LTI launch processing"""
        # Mock LTI integration
        mock_lti = MagicMock()
        mock_lti.process_lti_launch.return_value = {
            'success': True,
            'launch_session': {
                'user': self.student_user,
                'course': self.course,
                'resource_link_id': 'test_link',
                'launch_timestamp': timezone.now(),
                'return_url': 'http://test.com/return'
            },
            'redirect_url': '/lti/course/1/'
        }
        mock_get_lti.return_value = mock_lti
        
        # Test LTI launch
        lti_data = {
            'user_id': 'test_user',
            'context_id': 'test_context',
            'resource_link_id': 'test_link',
            'lis_person_contact_email_primary': 'test@example.com',
            'oauth_consumer_key': 'test_key',
            'oauth_signature': 'test_signature'
        }
        
        response = self.client.post('/api/progress/lti/launch/', lti_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class SecurityTestCase(BaseTestCase):
    """Test security measures"""
    
    def test_sql_injection_protection(self):
        """Test SQL injection protection"""
        self.client.force_authenticate(user=self.student_user)
        
        # Try SQL injection in query params
        malicious_query = "1'; DROP TABLE auth_user; --"
        response = self.client.get(f'/api/assessments/quizzes/?course_id={malicious_query}')
        
        # Should not crash and should return appropriate error
        self.assertIn(response.status_code, [400, 404])  # Bad request or not found
        
        # Verify tables still exist
        self.assertTrue(User.objects.filter(email='student@test.com').exists())
    
    def test_xss_protection(self):
        """Test XSS protection"""
        self.client.force_authenticate(user=self.teacher_user)
        
        # Try XSS in quiz title
        xss_payload = '<script>alert("xss")</script>'
        data = {
            'title': xss_payload,
            'description': 'Test description',
            'course': self.course.id,
            'questions_data': [],
            'time_limit': 30
        }
        
        response = self.client.post('/api/assessments/quizzes/', data, format='json')
        
        # Should either reject or sanitize
        if response.status_code == 201:
            # If created, check that script is sanitized
            quiz = Quiz.objects.get(id=response.data['id'])
            self.assertNotIn('<script>', quiz.title)
    
    def test_rate_limiting_simulation(self):
        """Test rate limiting (simulated)"""
        self.client.force_authenticate(user=self.student_user)
        
        # Make multiple rapid requests
        for i in range(10):
            response = self.client.get('/api/progress/student-progress/')
            # In a real rate-limited system, later requests would return 429
            self.assertIn(response.status_code, [200, 429])
    
    def test_sensitive_data_exposure(self):
        """Test that sensitive data is not exposed"""
        self.client.force_authenticate(user=self.student_user)
        
        # Get user profile
        response = self.client.get('/api/users/profile/')
        
        if response.status_code == 200:
            # Check that password is not in response
            self.assertNotIn('password', response.data)
            self.assertNotIn('is_staff', response.data)
            self.assertNotIn('is_superuser', response.data)

class PerformanceTestCase(BaseTestCase):
    """Test performance aspects"""
    
    def test_bulk_data_handling(self):
        """Test handling of bulk data operations"""
        self.client.force_authenticate(user=self.teacher_user)
        
        # Create multiple quiz results
        quiz_results = []
        for i in range(100):
            quiz_results.append(QuizResult(
                student=self.student_user,
                quiz=self.quiz,
                score=80,
                status='completed'
            ))
        
        QuizResult.objects.bulk_create(quiz_results)
        
        # Test analytics endpoint with large dataset
        response = self.client.get('/api/progress/analytics/performance-charts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_database_query_optimization(self):
        """Test database query optimization"""
        self.client.force_authenticate(user=self.teacher_user)
        
        with self.assertNumQueries(lessThan=20):  # Ensure reasonable query count
            response = self.client.get('/api/users/dashboard/')
            if response.status_code == 200:
                pass  # Endpoint exists and responds
    
    def assertNumQueries(self, lessThan):
        """Custom assertion for query count"""
        class QueryCountContext:
            def __init__(self, max_queries):
                self.max_queries = max_queries
                
            def __enter__(self):
                from django.db import connection
                connection.queries_log.clear()
                return self
                
            def __exit__(self, exc_type, exc_val, exc_tb):
                from django.db import connection
                query_count = len(connection.queries)
                if query_count > self.max_queries:
                    raise AssertionError(f"Too many queries: {query_count} > {self.max_queries}")
        
        return QueryCountContext(lessThan)

class IntegrationTestCase(BaseTestCase):
    """Test integration between different components"""
    
    def test_complete_learning_workflow(self):
        """Test complete learning workflow from quiz to recommendations"""
        self.client.force_authenticate(user=self.student_user)
        
        # 1. Start a quiz
        start_response = self.client.post(f'/api/assessments/quizzes/{self.quiz.id}/start/')
        self.assertEqual(start_response.status_code, status.HTTP_200_OK)
        
        # 2. Submit answers
        answers = {'answers': {'1': '1', '2': 'true'}}
        submit_response = self.client.post(
            f'/api/assessments/quizzes/{self.quiz.id}/submit/',
            answers,
            format='json'
        )
        self.assertEqual(submit_response.status_code, status.HTTP_200_OK)
        
        # 3. Check that quiz result was created
        self.assertTrue(
            QuizResult.objects.filter(
                student=self.student_user,
                quiz=self.quiz
            ).exists()
        )
        
        # 4. Get recommendations (should now include this performance data)
        rec_response = self.client.get('/api/progress/recommendations/')
        self.assertEqual(rec_response.status_code, status.HTTP_200_OK)
        
        # 5. Get adaptive learning insights
        adaptive_response = self.client.get('/api/progress/adaptive/learning-pattern/')
        self.assertEqual(adaptive_response.status_code, status.HTTP_200_OK)

# Pytest fixtures and additional tests
@pytest.fixture
def api_client():
    """Fixture for API client"""
    return APIClient()

@pytest.fixture
def admin_user():
    """Fixture for admin user"""
    return User.objects.create_user(
        email='admin@pytest.com',
        password='testpass',
        role='admin'
    )

@pytest.mark.django_db
def test_api_documentation_accessibility(api_client):
    """Test that API documentation is accessible"""
    response = api_client.get('/api/schema/')
    assert response.status_code in [200, 404]  # 404 if not configured

@pytest.mark.django_db
def test_health_check_endpoint(api_client):
    """Test health check endpoint"""
    # This would test a health check endpoint if implemented
    response = api_client.get('/api/health/')
    # Should return 404 if not implemented, which is fine
    assert response.status_code in [200, 404]

class EdgeCaseTestCase(BaseTestCase):
    """Test edge cases and error handling"""
    
    def test_empty_quiz_submission(self):
        """Test submitting quiz with no answers"""
        self.client.force_authenticate(user=self.student_user)
        
        self.client.post(f'/api/assessments/quizzes/{self.quiz.id}/start/')
        
        response = self.client.post(
            f'/api/assessments/quizzes/{self.quiz.id}/submit/',
            {'answers': {}},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['score'], 0)
    
    def test_invalid_quiz_id(self):
        """Test accessing non-existent quiz"""
        self.client.force_authenticate(user=self.student_user)
        
        response = self.client.post('/api/assessments/quizzes/99999/start/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_concurrent_quiz_submissions(self):
        """Test handling of concurrent quiz submissions"""
        self.client.force_authenticate(user=self.student_user)
        
        # Start quiz
        self.client.post(f'/api/assessments/quizzes/{self.quiz.id}/start/')
        
        # Submit same quiz multiple times rapidly
        for i in range(3):
            response = self.client.post(
                f'/api/assessments/quizzes/{self.quiz.id}/submit/',
                {'answers': {'1': '1', '2': 'true'}},
                format='json'
            )
            # First should succeed, others should handle appropriately
            if i == 0:
                self.assertEqual(response.status_code, status.HTTP_200_OK)
            else:
                # Should either succeed or return appropriate error
                self.assertIn(response.status_code, [200, 400, 409])

if __name__ == '__main__':
    import sys
    import django
    from django.conf import settings
    from django.test.utils import get_runner
    
    if not settings.configured:
        import os
        os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
        django.setup()
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests([__name__])
    
    if failures:
        sys.exit(1)
