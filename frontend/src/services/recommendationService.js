import apiService from './apiService';

class RecommendationService {
  constructor() {
    this.userInteractions = this.loadUserInteractions();
    this.learningPatterns = {};
  }

  // Load user interactions from localStorage
  loadUserInteractions() {
    try {
      const stored = localStorage.getItem('userInteractions');
      return stored ? JSON.parse(stored) : {
        courseViews: {},
        timeSpent: {},
        subjects: {},
        difficulty: {},
        completedCourses: [],
        bookmarkedCourses: [],
        searchQueries: [],
        clickedCourses: [],
      };
    } catch (error) {
      console.error('Error loading user interactions:', error);
      return {
        courseViews: {},
        timeSpent: {},
        subjects: {},
        difficulty: {},
        completedCourses: [],
        bookmarkedCourses: [],
        searchQueries: [],
        clickedCourses: [],
      };
    }
  }

  // Save user interactions to localStorage
  saveUserInteractions() {
    try {
      localStorage.setItem('userInteractions', JSON.stringify(this.userInteractions));
    } catch (error) {
      console.error('Error saving user interactions:', error);
    }
  }

  // Track user course view
  trackCourseView(courseId, courseData = {}) {
    if (!courseId) return;

    // Track view count
    this.userInteractions.courseViews[courseId] = 
      (this.userInteractions.courseViews[courseId] || 0) + 1;

    // Track subject interest
    if (courseData.subject) {
      this.userInteractions.subjects[courseData.subject] = 
        (this.userInteractions.subjects[courseData.subject] || 0) + 1;
    }

    // Track difficulty preference
    if (courseData.difficulty) {
      this.userInteractions.difficulty[courseData.difficulty] = 
        (this.userInteractions.difficulty[courseData.difficulty] || 0) + 1;
    }

    this.saveUserInteractions();
  }

  // Track time spent on course/class
  trackTimeSpent(courseId, duration) {
    if (!courseId || !duration) return;

    this.userInteractions.timeSpent[courseId] = 
      (this.userInteractions.timeSpent[courseId] || 0) + duration;

    this.saveUserInteractions();
  }

  // Track course completion
  trackCourseCompletion(courseId, rating = null) {
    if (!courseId) return;

    if (!this.userInteractions.completedCourses.includes(courseId)) {
      this.userInteractions.completedCourses.push(courseId);
    }

    this.saveUserInteractions();
  }

  // Track bookmark action
  trackBookmark(courseId, bookmarked) {
    if (!courseId) return;

    if (bookmarked) {
      if (!this.userInteractions.bookmarkedCourses.includes(courseId)) {
        this.userInteractions.bookmarkedCourses.push(courseId);
      }
    } else {
      this.userInteractions.bookmarkedCourses = 
        this.userInteractions.bookmarkedCourses.filter(id => id !== courseId);
    }

    this.saveUserInteractions();
  }

  // Track search queries
  trackSearchQuery(query) {
    if (!query || query.trim().length < 2) return;

    const normalizedQuery = query.toLowerCase().trim();
    
    // Add to recent searches (keep last 50)
    this.userInteractions.searchQueries = [
      normalizedQuery,
      ...this.userInteractions.searchQueries.filter(q => q !== normalizedQuery)
    ].slice(0, 50);

    this.saveUserInteractions();
  }

  // Track course clicks
  trackCourseClick(courseId) {
    if (!courseId) return;

    this.userInteractions.clickedCourses = [
      courseId,
      ...this.userInteractions.clickedCourses.filter(id => id !== courseId)
    ].slice(0, 100);

    this.saveUserInteractions();
  }

  // Get user's preferred subjects
  getPreferredSubjects() {
    const subjects = this.userInteractions.subjects;
    return Object.entries(subjects)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 5)
      .map(([subject]) => subject);
  }

  // Get user's preferred difficulty
  getPreferredDifficulty() {
    const difficulty = this.userInteractions.difficulty;
    if (Object.keys(difficulty).length === 0) return 'beginner';

    return Object.entries(difficulty)
      .sort(([,a], [,b]) => b - a)[0]?.[0] || 'beginner';
  }

  // Get learning style based on interactions
  getLearningStyle() {
    const totalViews = Object.values(this.userInteractions.courseViews)
      .reduce((sum, views) => sum + views, 0);
    const totalTime = Object.values(this.userInteractions.timeSpent)
      .reduce((sum, time) => sum + time, 0);
    
    const averageTimePerView = totalViews > 0 ? totalTime / totalViews : 0;

    if (averageTimePerView > 30) return 'deep_learner'; // Spends more time per course
    if (totalViews > 50) return 'explorer'; // Views many courses
    if (this.userInteractions.completedCourses.length > 10) return 'completer'; // Completes courses
    return 'beginner';
  }

  // Generate course recommendations
  async getCourseRecommendations(courses = [], limit = 6) {
    try {
      const preferredSubjects = this.getPreferredSubjects();
      const preferredDifficulty = this.getPreferredDifficulty();
      const learningStyle = this.getLearningStyle();
      const completedCourses = this.userInteractions.completedCourses;
      const clickedCourses = this.userInteractions.clickedCourses;

      // Score courses based on user preferences
      const scoredCourses = courses
        .filter(course => !completedCourses.includes(course.id))
        .map(course => {
          let score = 0;

          // Subject preference (highest weight)
          if (preferredSubjects.includes(course.category || course.subject)) {
            const subjectRank = preferredSubjects.indexOf(course.category || course.subject);
            score += (5 - subjectRank) * 10;
          }

          // Difficulty preference
          if (course.level === preferredDifficulty) {
            score += 8;
          } else if (
            (preferredDifficulty === 'beginner' && course.level === 'intermediate') ||
            (preferredDifficulty === 'intermediate' && ['beginner', 'advanced'].includes(course.level))
          ) {
            score += 5;
          }

          // High-rated courses
          if (course.rating >= 4.5) score += 7;
          else if (course.rating >= 4.0) score += 5;

          // Popular courses (more students)
          if (course.students > 50000) score += 4;
          else if (course.students > 10000) score += 2;

          // Recently clicked courses (but not too recent to avoid repetition)
          const clickIndex = clickedCourses.indexOf(course.id);
          if (clickIndex >= 10 && clickIndex < 20) score += 3;

          // Learning style adjustments
          if (learningStyle === 'deep_learner' && course.duration && course.duration.includes('week')) {
            score += 5; // Prefer longer courses
          }
          if (learningStyle === 'explorer') {
            score += Math.random() * 3; // Add some randomness for variety
          }

          // Trending courses (newer courses get slight boost)
          const courseDate = new Date(course.created_at || Date.now());
          const monthsOld = (Date.now() - courseDate) / (1000 * 60 * 60 * 24 * 30);
          if (monthsOld < 6) score += 2;

          return { ...course, recommendationScore: score };
        })
        .sort((a, b) => b.recommendationScore - a.recommendationScore)
        .slice(0, limit);

      return scoredCourses;
    } catch (error) {
      console.error('Error generating course recommendations:', error);
      return courses.slice(0, limit);
    }
  }

  // Generate class recommendations (for teacher-led classes)
  async getClassRecommendations(teachers = [], limit = 6) {
    try {
      const preferredSubjects = this.getPreferredSubjects();
      const learningStyle = this.getLearningStyle();

      const scoredTeachers = teachers
        .filter(teacher => teacher.available_for_new_students)
        .map(teacher => {
          let score = 0;

          // Subject match
          const teacherSubjects = teacher.subjects_taught?.map(s => s.name.toLowerCase()) || [];
          preferredSubjects.forEach((subject, index) => {
            if (teacherSubjects.some(ts => ts.includes(subject.toLowerCase()))) {
              score += (5 - index) * 8;
            }
          });

          // High-rated teachers
          if (teacher.average_rating >= 4.5) score += 10;
          else if (teacher.average_rating >= 4.0) score += 7;

          // Experience
          if (teacher.experience_years >= 5) score += 6;
          else if (teacher.experience_years >= 2) score += 3;

          // Active classes
          if (teacher.active_classes > 2) score += 4;

          // Learning style match
          if (learningStyle === 'deep_learner' && teacher.teaching_approach?.includes('intensive')) {
            score += 5;
          }

          return { ...teacher, recommendationScore: score };
        })
        .sort((a, b) => b.recommendationScore - a.recommendationScore)
        .slice(0, limit);

      return scoredTeachers;
    } catch (error) {
      console.error('Error generating class recommendations:', error);
      return teachers.slice(0, limit);
    }
  }

  // Generate AI insights for dashboard
  getAIInsights() {
    const insights = [];
    const preferredSubjects = this.getPreferredSubjects();
    const learningStyle = this.getLearningStyle();
    const totalCourses = this.userInteractions.completedCourses.length;
    const mostViewedSubject = preferredSubjects[0];

    // Learning style insights
    switch (learningStyle) {
      case 'deep_learner':
        insights.push({
          type: 'learning_style',
          title: 'Deep Learning Pattern Detected',
          message: 'You tend to spend quality time on courses. Consider advanced courses in your favorite subjects.',
          action: 'Explore Advanced Courses',
          priority: 'medium'
        });
        break;
      case 'explorer':
        insights.push({
          type: 'learning_style',
          title: 'Explorer Learning Style',
          message: 'You love exploring new topics! Try focusing on completing a few courses to build expertise.',
          action: 'View In-Progress Courses',
          priority: 'medium'
        });
        break;
      case 'completer':
        insights.push({
          type: 'achievement',
          title: 'Course Completion Champion',
          message: `Congratulations on completing ${totalCourses} courses! You're building solid expertise.`,
          action: 'Discover New Challenges',
          priority: 'high'
        });
        break;
    }

    // Subject-based insights
    if (mostViewedSubject) {
      insights.push({
        type: 'subject_interest',
        title: `Strong Interest in ${mostViewedSubject}`,
        message: `You show consistent engagement with ${mostViewedSubject}. Consider advanced topics or related fields.`,
        action: `Explore ${mostViewedSubject} Courses`,
        priority: 'high'
      });
    }

    // Engagement insights
    const recentActivity = this.userInteractions.clickedCourses.length;
    if (recentActivity > 20) {
      insights.push({
        type: 'engagement',
        title: 'High Learning Activity',
        message: 'Your learning activity is excellent! Consider joining a teacher-led class for guided learning.',
        action: 'Browse Classes',
        priority: 'medium'
      });
    }

    return insights.slice(0, 3); // Return top 3 insights
  }

  // Get study recommendations based on time patterns
  getStudyTimeRecommendations() {
    // This could be enhanced with actual time tracking data
    const currentHour = new Date().getHours();
    
    if (currentHour >= 9 && currentHour <= 11) {
      return {
        message: "Perfect timing! Research shows you're most focused in the morning.",
        recommendation: "Tackle challenging topics now",
        optimal: true
      };
    } else if (currentHour >= 14 && currentHour <= 16) {
      return {
        message: "Good afternoon study time! Your brain is ready for practice and review.",
        recommendation: "Try quizzes or practice exercises",
        optimal: true
      };
    } else if (currentHour >= 19 && currentHour <= 21) {
      return {
        message: "Evening learning detected. Perfect for reviewing today's material.",
        recommendation: "Review notes or watch educational videos",
        optimal: false
      };
    }
    
    return {
      message: "Every moment is a learning opportunity!",
      recommendation: "Light reading or quick tutorials work well now",
      optimal: false
    };
  }

  // Reset user data (for privacy/testing)
  resetUserData() {
    this.userInteractions = {
      courseViews: {},
      timeSpent: {},
      subjects: {},
      difficulty: {},
      completedCourses: [],
      bookmarkedCourses: [],
      searchQueries: [],
      clickedCourses: [],
    };
    this.saveUserInteractions();
  }

  // Export user data (for data portability)
  exportUserData() {
    return {
      interactions: this.userInteractions,
      learningStyle: this.getLearningStyle(),
      preferredSubjects: this.getPreferredSubjects(),
      preferredDifficulty: this.getPreferredDifficulty(),
      insights: this.getAIInsights(),
      exportDate: new Date().toISOString()
    };
  }
}

// Create singleton instance
const recommendationService = new RecommendationService();
export default recommendationService;
