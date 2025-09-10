from django.urls import path
from . import views

app_name = 'progress'

urlpatterns = [
    # Student Progress (AI-only system)
    path(
        'student-progress/',
        views.StudentProgressListView.as_view(),
        name='student-progress-list'
    ),
    path(
        'student-progress/<int:pk>/',
        views.StudentProgressDetailView.as_view(),
        name='student-progress-detail'
    ),
    
    # Quiz Results
    path(
        'quiz-results/',
        views.QuizResultListView.as_view(),
        name='quiz-results-list'
    ),
    
    # AI Learning Goals
    path(
        'learning-goals/',
        views.LearningGoalListView.as_view(),
        name='learning-goals-list'
    ),
    path(
        'learning-goals/<int:pk>/',
        views.LearningGoalDetailView.as_view(),
        name='learning-goals-detail'
    ),
    
    # AI Recommendations
    path(
        'ai-recommended-courses/',
        views.ai_recommended_courses,
        name='ai-recommended-courses'
    ),
    
    # Student Analytics
    path(
        'student/analytics/',
        views.student_analytics,
        name='student-analytics'
    ),
    
    # Student Course Progress
    path(
        'student/progress/courses/',
        views.student_course_progress,
        name='student-course-progress'
    ),
]
