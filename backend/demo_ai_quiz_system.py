#!/usr/bin/env python3
"""
AI Quiz Generation System Demo
Demonstrates the complete AI-powered personalized learning system
"""

import os
import sys
import django
import json
from django.utils import timezone
from datetime import datetime, timedelta

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.courses.models import Course, Subject, Quiz, CourseEnrollment
from apps.progress.models import QuizResult, StudentProgress
from apps.assessments.ai_services import quiz_generator_service, StudentAnalyzer

User = get_user_model()

class AIQuizDemoSystem:
    """Demonstration of the AI Quiz Generation System"""
    
    def __init__(self):
        self.demo_data = {}
        
    def setup_demo_data(self):
        """Create demo users, courses, and initial quiz data"""
        print("🚀 Setting up AI Quiz Demo System...")
        print("=" * 60)
        
        # Create demo teacher
        teacher, created = User.objects.get_or_create(
            email='ai_teacher@demo.com',
            defaults={
                'username': 'ai_teacher',
                'first_name': 'AI',
                'last_name': 'Teacher',
                'role': 'teacher'
            }
        )
        if created:
            teacher.set_password('demo123')
            teacher.save()
            print(f"✅ Created AI Teacher: {teacher.email}")
        
        # Create demo students with different performance levels
        students = []
        student_profiles = [
            {'email': 'struggling_student@demo.com', 'level': 'struggling'},
            {'email': 'average_student@demo.com', 'level': 'average'},
            {'email': 'excellent_student@demo.com', 'level': 'excellent'}
        ]
        
        for profile in student_profiles:
            student, created = User.objects.get_or_create(
                email=profile['email'],
                defaults={
                    'username': profile['email'].split('@')[0],
                    'first_name': profile['level'].capitalize(),
                    'last_name': 'Student',
                    'role': 'student'
                }
            )
            if created:
                student.set_password('demo123')
                student.save()
                print(f"✅ Created {profile['level']} student: {student.email}")
            students.append((student, profile['level']))
        
        # Create demo subject and course
        subject, created = Subject.objects.get_or_create(
            name="Artificial Intelligence",
            defaults={'description': 'AI and Machine Learning concepts'}
        )
        
        course, created = Course.objects.get_or_create(
            title="Introduction to Machine Learning",
            defaults={
                'description': 'Learn the fundamentals of machine learning and AI',
                'subject': subject,
                'instructor': teacher,
                'difficulty_level': 'intermediate'
            }
        )
        print(f"✅ Created course: {course.title}")
        
        # Enroll all students
        for student, level in students:
            enrollment, created = CourseEnrollment.objects.get_or_create(
                student=student,
                course=course,
                defaults={'is_active': True}
            )
            print(f"✅ Enrolled {level} student in course")
        
        # Create initial quiz with sample questions
        self._create_initial_quiz(course)
        
        # Generate sample performance data
        self._generate_sample_performance_data(course, students)
        
        self.demo_data = {
            'teacher': teacher,
            'students': students,
            'course': course,
            'subject': subject
        }
        
        print(f"\n🎯 Demo setup complete! Ready for AI Quiz Generation")
    
    def _create_initial_quiz(self, course):
        """Create an initial quiz to generate performance data"""
        sample_questions = [
            {
                'id': 1,
                'type': 'multiple_choice',
                'question': 'What is Machine Learning?',
                'options': [
                    'A subset of artificial intelligence',
                    'A programming language',
                    'A database system',
                    'A web framework'
                ],
                'correct_answer': '0',
                'explanation': 'Machine Learning is indeed a subset of AI',
                'difficulty': 'easy',
                'tags': ['machine-learning', 'ai-basics', 'definitions'],
                'points': 10
            },
            {
                'id': 2,
                'type': 'true_false',
                'question': 'Supervised learning requires labeled training data',
                'options': ['True', 'False'],
                'correct_answer': 'true',
                'explanation': 'Supervised learning algorithms need labeled examples to learn from',
                'difficulty': 'medium',
                'tags': ['supervised-learning', 'training-data', 'algorithms'],
                'points': 10
            },
            {
                'id': 3,
                'type': 'multiple_choice',
                'question': 'Which of these is NOT a common machine learning algorithm?',
                'options': [
                    'Linear Regression',
                    'Decision Trees',
                    'Neural Networks',
                    'HTML Parser'
                ],
                'correct_answer': '3',
                'explanation': 'HTML Parser is a web technology, not a machine learning algorithm',
                'difficulty': 'medium',
                'tags': ['algorithms', 'classification', 'regression'],
                'points': 15
            },
            {
                'id': 4,
                'type': 'short_answer',
                'question': 'What does "overfitting" mean in machine learning?',
                'correct_answer': 'when model performs well on training data but poorly on new data',
                'explanation': 'Overfitting occurs when a model learns the training data too specifically',
                'difficulty': 'hard',
                'tags': ['overfitting', 'model-evaluation', 'generalization'],
                'points': 20
            },
            {
                'id': 5,
                'type': 'multiple_choice',
                'question': 'What is the purpose of a validation dataset?',
                'options': [
                    'To train the model',
                    'To test final model performance',
                    'To tune hyperparameters and prevent overfitting',
                    'To store backup data'
                ],
                'correct_answer': '2',
                'explanation': 'Validation datasets help tune models and prevent overfitting',
                'difficulty': 'medium',
                'tags': ['validation', 'model-evaluation', 'hyperparameters'],
                'points': 15
            }
        ]
        
        quiz, created = Quiz.objects.get_or_create(
            title="ML Fundamentals Assessment",
            course=course,
            defaults={
                'description': 'Test your understanding of machine learning basics',
                'questions_data': sample_questions,
                'passing_score': 70.0,
                'time_limit': 30,
                'attempts_allowed': 3,
                'show_results_immediately': True
            }
        )
        
        if created:
            print(f"✅ Created initial quiz: {quiz.title}")
        
        return quiz
    
    def _generate_sample_performance_data(self, course, students):
        """Generate realistic performance data for different student types"""
        quiz = Quiz.objects.get(course=course, title="ML Fundamentals Assessment")
        
        # Performance patterns for different student levels
        performance_patterns = {
            'struggling': {
                'scores': [45, 52, 48, 58, 55],
                'weak_concepts': ['algorithms', 'overfitting', 'model-evaluation'],
                'strong_concepts': ['ai-basics']
            },
            'average': {
                'scores': [72, 68, 75, 78, 80],
                'weak_concepts': ['overfitting', 'hyperparameters'],
                'strong_concepts': ['ai-basics', 'definitions', 'supervised-learning']
            },
            'excellent': {
                'scores': [88, 92, 90, 95, 93],
                'weak_concepts': ['hyperparameters'],
                'strong_concepts': ['ai-basics', 'algorithms', 'supervised-learning', 'model-evaluation']
            }
        }
        
        for student, level in students:
            pattern = performance_patterns[level]
            
            # Create multiple quiz attempts to build performance history
            for i, score in enumerate(pattern['scores']):
                # Create quiz result
                quiz_result = QuizResult.objects.create(
                    student=student,
                    quiz=quiz,
                    attempt_number=i + 1,
                    status='completed',
                    score=score,
                    total_questions=len(quiz.questions_data),
                    correct_answers=int((score / 100) * len(quiz.questions_data)),
                    incorrect_answers=len(quiz.questions_data) - int((score / 100) * len(quiz.questions_data)),
                    time_taken=1200 + (i * 180),  # Varying time
                    strengths_identified=pattern['strong_concepts'],
                    weaknesses_identified=pattern['weak_concepts'],
                    time_started=timezone.now() - timedelta(days=30 - i * 5),
                    time_completed=timezone.now() - timedelta(days=30 - i * 5, minutes=-20)
                )
                
                # Create question-level analytics
                question_analytics = {}
                for j, question in enumerate(quiz.questions_data):
                    # Simulate realistic question performance
                    is_correct = (j / len(quiz.questions_data)) < (score / 100)
                    
                    question_analytics[str(question['id'])] = {
                        'correct': is_correct,
                        'student_answer': '0' if is_correct else '1',
                        'correct_answer': question['correct_answer'],
                        'points_earned': question['points'] if is_correct else 0,
                        'points_possible': question['points'],
                        'difficulty': question['difficulty'],
                        'tags': question['tags']
                    }
                
                quiz_result.question_analytics = question_analytics
                quiz_result.save()
                
                # Create progress record
                StudentProgress.objects.create(
                    student=student,
                    course=course,
                    activity_type='quiz_complete',
                    status='completed',
                    completion_percentage=100.0,
                    score=score,
                    time_spent=quiz_result.time_taken // 60,
                    started_at=quiz_result.time_started,
                    completed_at=quiz_result.time_completed,
                    attempts=1
                )
            
            print(f"✅ Generated performance data for {level} student ({len(pattern['scores'])} attempts)")
    
    def demonstrate_student_analysis(self):
        """Demonstrate the AI student analysis capabilities"""
        print("\n" + "=" * 60)
        print("🧠 AI STUDENT ANALYSIS DEMONSTRATION")
        print("=" * 60)
        
        for student, level in self.demo_data['students']:
            print(f"\n📊 Analyzing {level.upper()} Student: {student.email}")
            print("-" * 50)
            
            try:
                analyzer = StudentAnalyzer(student.id)
                
                # Get performance summary
                performance = analyzer.get_performance_summary(self.demo_data['course'].id)
                print(f"Overall Performance:")
                print(f"  • Total Quizzes: {performance['total_quizzes_taken']}")
                print(f"  • Average Score: {performance['overall_average_score']}%")
                print(f"  • Recent Score: {performance['recent_average_score']}%")
                print(f"  • Trend: {performance['performance_trend']}")
                print(f"  • Learning Velocity: {performance['learning_velocity']:.2f} quizzes/day")
                
                # Get weaknesses
                weaknesses = analyzer.identify_weaknesses(self.demo_data['course'].id)
                print(f"\n🔍 Identified Weaknesses:")
                for weakness in weaknesses[:3]:
                    print(f"  • {weakness['concept']}: {weakness['accuracy']:.1%} accuracy "
                          f"(Priority: {weakness['priority_score']:.2f})")
                
                # Get strengths
                strengths = analyzer.get_strengths(self.demo_data['course'].id)
                print(f"\n💪 Identified Strengths:")
                for strength in strengths[:3]:
                    print(f"  • {strength['concept']}: {strength['accuracy']:.1%} accuracy "
                          f"(Level: {strength['mastery_level']})")
                
            except Exception as e:
                print(f"❌ Analysis failed: {str(e)}")
    
    def demonstrate_ai_quiz_generation(self):
        """Demonstrate AI-powered quiz generation for different student types"""
        print("\n" + "=" * 60)
        print("🤖 AI QUIZ GENERATION DEMONSTRATION")
        print("=" * 60)
        
        for student, level in self.demo_data['students']:
            print(f"\n🎯 Generating Personalized Quiz for {level.upper()} Student")
            print(f"Student: {student.email}")
            print("-" * 50)
            
            try:
                # Generate AI quiz
                result = quiz_generator_service.create_personalized_quiz(
                    student_id=student.id,
                    course_id=self.demo_data['course'].id,
                    topic="Machine Learning Fundamentals",
                    difficulty_level='medium',
                    question_count=5,
                    save_to_db=False  # Don't save for demo
                )
                
                if result['success']:
                    quiz_data = result['quiz_data']
                    generation_info = result['generation_info']
                    analysis = result['student_analysis']
                    
                    print(f"✅ Quiz Generated Successfully!")
                    print(f"📝 Quiz Title: {quiz_data['title']}")
                    print(f"🎯 Target Concepts: {', '.join(quiz_data['target_concepts'][:3])}")
                    print(f"📊 Adaptive Passing Score: {quiz_data['passing_score']}%")
                    print(f"⏱️  Time Limit: {quiz_data['time_limit']} minutes")
                    
                    print(f"\n🧮 Generation Analytics:")
                    print(f"  • Weaknesses Targeted: {generation_info['weaknesses_targeted']}")
                    print(f"  • Strengths Reinforced: {generation_info['strengths_reinforced']}")
                    print(f"  • Performance Trend: {generation_info['performance_trend']}")
                    print(f"  • AI Model: {generation_info['ai_model_used']}")
                    
                    print(f"\n📋 Sample Questions Generated:")
                    for i, question in enumerate(quiz_data['questions_data'][:3], 1):
                        print(f"  {i}. [{question['type']}] {question['question'][:60]}...")
                        print(f"     Difficulty: {question['difficulty']} | Tags: {', '.join(question['tags'][:2])}")
                    
                    print(f"\n💡 Personalized Recommendations:")
                    for weakness in analysis['weaknesses'][:3]:
                        print(f"  • Focus on {weakness['concept']} (Current: {weakness['accuracy']:.1%})")
                
                else:
                    print(f"❌ Quiz generation failed: {result['error']}")
                    if result.get('fallback_available'):
                        print("🔄 Fallback system available")
                
            except Exception as e:
                print(f"❌ Generation error: {str(e)}")
    
    def demonstrate_adaptive_features(self):
        """Demonstrate adaptive learning features"""
        print("\n" + "=" * 60)
        print("🔄 ADAPTIVE LEARNING FEATURES")
        print("=" * 60)
        
        struggling_student = next(s for s, level in self.demo_data['students'] if level == 'struggling')
        excellent_student = next(s for s, level in self.demo_data['students'] if level == 'excellent')
        
        print("\n📈 Adaptive Passing Scores:")
        
        for student, description in [(struggling_student, "Struggling"), (excellent_student, "Excellent")]:
            analyzer = StudentAnalyzer(student.id)
            performance = analyzer.get_performance_summary(self.demo_data['course'].id)
            
            # Generate quiz to see adaptive score
            result = quiz_generator_service.create_personalized_quiz(
                student_id=student.id,
                course_id=self.demo_data['course'].id,
                topic="Advanced Topics",
                save_to_db=False
            )
            
            if result['success']:
                adaptive_score = result['quiz_data']['passing_score']
                print(f"  • {description} Student ({performance['overall_average_score']}% avg): "
                      f"Adaptive passing score = {adaptive_score}%")
        
        print("\n🎯 Question Difficulty Adaptation:")
        print("  • Struggling students: More basic questions, step-by-step explanations")
        print("  • Average students: Balanced mix of difficulties")
        print("  • Excellent students: More challenging questions, advanced concepts")
        
        print("\n⏱️  Time Limit Adaptation:")
        print("  • Based on question count and difficulty")
        print("  • Struggling students get more time per question")
        print("  • Advanced students get efficient time limits")
    
    def show_api_usage_examples(self):
        """Show how to use the AI quiz generation APIs"""
        print("\n" + "=" * 60)
        print("📡 API USAGE EXAMPLES")
        print("=" * 60)
        
        student_id = self.demo_data['students'][0][0].id
        course_id = self.demo_data['course'].id
        
        print("1️⃣  Generate AI Quiz (Teachers):")
        print(f"""
POST /api/assessments/ai/generate-quiz/
Authorization: Bearer <teacher_token>
Content-Type: application/json

{{
  "student_id": {student_id},
  "course_id": {course_id},
  "topic": "Machine Learning Algorithms",
  "difficulty_level": "medium",
  "question_count": 10,
  "question_types": ["multiple_choice", "short_answer"],
  "save_to_db": true
}}
        """)
        
        print("2️⃣  Get Student Analysis (Teachers):")
        print(f"""
GET /api/assessments/ai/student-analysis/{student_id}/{course_id}/
Authorization: Bearer <teacher_token>
        """)
        
        print("3️⃣  Get Quiz Suggestions (Students & Teachers):")
        print("""
GET /api/assessments/ai/quiz-suggestions/
Authorization: Bearer <token>
        """)
        
        print("\n📊 Example Response (AI Quiz Generation):")
        print("""
{
  "success": true,
  "message": "AI quiz generated successfully",
  "quiz_data": {
    "title": "AI-Generated Machine Learning Quiz",
    "questions_data": [...],
    "passing_score": 65.0,
    "time_limit": 25,
    "ai_generated": true
  },
  "generation_info": {
    "weaknesses_targeted": 3,
    "ai_model_used": "gpt-3.5-turbo"
  },
  "student_analysis": {
    "weaknesses": [...],
    "performance_summary": {...}
  }
}
        """)
    
    def run_complete_demo(self):
        """Run the complete AI quiz generation demo"""
        try:
            # Setup demo environment
            self.setup_demo_data()
            
            # Run demonstrations
            self.demonstrate_student_analysis()
            self.demonstrate_ai_quiz_generation()
            self.demonstrate_adaptive_features()
            self.show_api_usage_examples()
            
            print("\n" + "=" * 60)
            print("🎉 AI QUIZ GENERATION DEMO COMPLETED!")
            print("=" * 60)
            
            print("\n✨ Key Features Demonstrated:")
            print("  ✅ Intelligent Student Performance Analysis")
            print("  ✅ AI-Powered Personalized Quiz Generation")
            print("  ✅ Adaptive Difficulty & Passing Scores")
            print("  ✅ Weakness-Focused Question Selection")
            print("  ✅ Fallback System for Reliability")
            print("  ✅ RESTful API Integration")
            print("  ✅ Real-time Analytics & Insights")
            
            print("\n🚀 Next Steps:")
            print("  1. Add OpenAI API key to settings for full AI generation")
            print("  2. Customize question templates for your domain")
            print("  3. Integrate with frontend dashboard")
            print("  4. Add more sophisticated ML algorithms")
            print("  5. Implement real-time adaptive testing")
            
        except Exception as e:
            print(f"\n❌ Demo failed with error: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    print("🤖 AI Quiz Generation System Demo")
    print("Demonstrating personalized learning with AI-powered assessments")
    print()
    
    demo = AIQuizDemoSystem()
    demo.run_complete_demo()
