from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Quiz Management URLs - Clean and Secure
urlpatterns = [
    # Quiz CRUD Operations
    path('quizzes/', views.QuizListCreateView.as_view(), name='quiz-list-create'),
    path('quizzes/<int:pk>/', views.QuizDetailView.as_view(), name='quiz-detail'),
    
    # Quiz Taking (Students)
    path('quizzes/<int:quiz_id>/take/', views.take_quiz, name='take-quiz'),
    path('quizzes/<int:quiz_id>/submit/', views.submit_quiz, name='submit-quiz'),
    
    # Quiz Results & Analytics
    path('quizzes/<int:quiz_id>/results/', views.quiz_results, name='quiz-results'),
    path('quizzes/<int:quiz_id>/analytics/', views.quiz_analytics, name='quiz-analytics'),
    
    # AI Quiz Generation Endpoints
    path('ai/generate-quiz/', views.generate_ai_quiz, name='generate-ai-quiz'),
    path('ai/student-analysis/<int:student_id>/<int:course_id>/', views.student_analysis, name='student-analysis'),
    path('ai/quiz-suggestions/', views.ai_quiz_suggestions, name='ai-quiz-suggestions'),
]
