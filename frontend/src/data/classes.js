// AI-powered classes data - No human teachers, only AI tutors
export const mockAIClasses = [
  {
    id: 1,
    name: 'AI-Powered JavaScript Mastery',
    ai_tutor: 'CodeBot AI',
    ai_avatar: '🤖',
    subject: 'computer-science',
    description: 'Learn advanced JavaScript with personalized AI tutoring and adaptive learning paths',
    status: 'active',
    enrolled_students: 127,
    max_students: 1000, // AI can handle unlimited students
    schedule: 'Available 24/7 - Learn at your own pace',
    duration: 'Self-paced (8-12 weeks recommended)',
    start_date: 'Anytime',
    level: 'Advanced',
    ai_rating: 4.9,
    price: 'Free', // AI education is accessible
    features: ['Personalized Learning Path', 'Instant Code Review', '24/7 AI Support', 'Adaptive Assessments']
  },
  {
    id: 2,
    name: 'AI Data Structures & Algorithms',
    ai_tutor: 'AlgoMaster AI',
    ai_avatar: '🧠',
    subject: 'computer-science',
    description: 'Master data structures and algorithms with AI-powered problem-solving guidance',
    status: 'active',
    enrolled_students: 89,
    max_students: 1000,
    schedule: 'Available 24/7 - Interactive problem solving',
    duration: 'Self-paced (10-14 weeks recommended)',
    start_date: 'Anytime',
    level: 'Intermediate',
    ai_rating: 4.8,
    price: 'Free',
    features: ['Visual Algorithm Explanations', 'Real-time Code Analysis', 'AI Debugging Help', 'Progress Tracking']
  },
  {
    id: 3,
    name: 'AI Calculus Tutor',
    ai_tutor: 'MathGenius AI',
    ai_avatar: '📊',
    subject: 'mathematics',
    description: 'Learn calculus with AI that adapts to your learning style and pace',
    status: 'active',
    enrolled_students: 156,
    max_students: 1000,
    schedule: 'Available 24/7 - Step-by-step guidance',
    duration: 'Self-paced (12-16 weeks recommended)',
    start_date: 'Anytime',
    level: 'Beginner',
    ai_rating: 4.9,
    price: 'Free',
    features: ['Interactive Problem Solving', 'Visual Graphing', 'Personalized Practice', 'Instant Feedback']
  },
  {
    id: 4,
    name: 'AI Physics Lab',
    ai_tutor: 'PhysicsBot AI',
    ai_avatar: '⚡',
    subject: 'physics',
    description: 'Explore physics concepts with AI-powered simulations and virtual experiments',
    status: 'active',
    enrolled_students: 203,
    max_students: 1000,
    schedule: 'Available 24/7 - Interactive simulations',
    duration: 'Self-paced (8-12 weeks recommended)',
    start_date: 'Anytime',
    level: 'Intermediate',
    ai_rating: 4.7,
    price: 'Free',
    features: ['Virtual Physics Lab', '3D Simulations', 'AI Experiment Guide', 'Concept Visualization']
  },
  {
    id: 5,
    name: 'AI Chemistry Explorer',
    ai_tutor: 'ChemBot AI',
    ai_avatar: '🧪',
    subject: 'chemistry',
    description: 'Master chemistry through AI-guided virtual lab experiments and molecular modeling',
    status: 'active',
    enrolled_students: 78,
    max_students: 1000,
    schedule: 'Available 24/7 - Virtual lab access',
    duration: 'Self-paced (10-14 weeks recommended)',
    start_date: 'Anytime',
    level: 'Advanced',
    ai_rating: 4.8,
    price: 'Free',
    features: ['Virtual Lab Equipment', 'Molecular Modeling', 'AI Safety Guide', 'Reaction Predictions']
  },
  {
    id: 6,
    name: 'AI Machine Learning Bootcamp',
    ai_tutor: 'MLMaster AI',
    ai_avatar: '🚀',
    subject: 'artificial-intelligence',
    description: 'Learn machine learning from AI itself - meta-learning experience',
    status: 'active',
    enrolled_students: 245,
    max_students: 1000,
    schedule: 'Available 24/7 - Hands-on projects',
    duration: 'Self-paced (6-10 weeks recommended)',
    start_date: 'Anytime',
    level: 'Advanced',
    ai_rating: 5.0,
    price: 'Free',
    features: ['Live Model Training', 'Real Dataset Projects', 'AI Code Generation', 'Performance Analytics']
  }
];

// AI Learning Progress Tracking - replaces teacher enrollment system
export const mockAIProgress = [
  {
    id: 1,
    class_id: 1,
    ai_tutor: 'CodeBot AI',
    subject: 'JavaScript Programming',
    status: 'in_progress',
    progress: 78,
    ai_recommendations: [
      'Focus on async/await concepts',
      'Practice more array methods',
      'Review closure examples'
    ],
    last_interaction: '2025-01-08T14:30:00Z',
    next_lesson: 'Advanced Promise Patterns'
  },
  {
    id: 2,
    class_id: 2,
    ai_tutor: 'AlgoMaster AI',
    subject: 'Data Structures',
    status: 'completed',
    progress: 100,
    ai_recommendations: [
      'Ready for advanced algorithms',
      'Consider graph theory next',
      'Practice coding interviews'
    ],
    last_interaction: '2025-01-05T16:45:00Z',
    completion_date: '2025-01-05'
  }
];

// AI-powered learning system - No enrollment needed, instant access
export const getUserSpecificProgress = (classId, userId) => {
  // AI tracks individual progress automatically
  const seed = (userId * classId) % 3;
  const statuses = ['not_started', 'in_progress', 'completed'];
  return statuses[seed];
};

export const getMyAIClasses = (userId, userRole) => {
  if (!userId || userRole !== 'student') return [];
  
  // Students see AI classes with their learning progress
  return mockAIClasses.map(cls => ({
    ...cls,
    learning_status: getUserSpecificProgress(cls.id, userId),
    progress: getUserSpecificProgress(cls.id, userId) === 'completed' ? 100 : 
              getUserSpecificProgress(cls.id, userId) === 'in_progress' ? 45 + (userId % 50) : 0
  }));
};

export const getAllAvailableAIClasses = (userId) => {
  if (!userId) return mockAIClasses;
  
  // All AI classes are available immediately - no enrollment process
  return mockAIClasses.map(cls => ({
    ...cls,
    learning_status: getUserSpecificProgress(cls.id, userId),
    progress: getUserSpecificProgress(cls.id, userId) === 'completed' ? 100 : 
              getUserSpecificProgress(cls.id, userId) === 'in_progress' ? 45 + (userId % 50) : 0
  }));
};

// AI Tutors are always available - no enrollment needed
export const getAvailableAITutors = () => {
  return [
    {
      id: 'codebot',
      name: 'CodeBot AI',
      avatar: '🤖',
      specialties: ['JavaScript', 'Python', 'Web Development'],
      availability: '24/7',
      response_time: 'Instant',
      rating: 4.9
    },
    {
      id: 'mathgenius',
      name: 'MathGenius AI',
      avatar: '📊',
      specialties: ['Calculus', 'Algebra', 'Statistics'],
      availability: '24/7',
      response_time: 'Instant',
      rating: 4.8
    },
    {
      id: 'physicsbot',
      name: 'PhysicsBot AI',
      avatar: '⚡',
      specialties: ['Mechanics', 'Thermodynamics', 'Quantum Physics'],
      availability: '24/7',
      response_time: 'Instant',
      rating: 4.7
    }
  ];
};

export const getAILearningProgress = (userId) => {
  if (!userId) return [];
  
  // Generate user-specific AI learning progress
  const userSeed = userId % mockAIProgress.length;
  return mockAIProgress.slice(0, userSeed + 1).map(progress => ({
    ...progress,
    id: progress.id + userId // Make IDs unique per user
  }));
};

// AI Analytics for platform insights (for admin use)
export const getAIAnalytics = () => {
  return {
    total_students: 1247,
    active_ai_tutors: 6,
    total_ai_classes: mockAIClasses.length,
    avg_completion_rate: 87,
    total_interactions: 45672,
    ai_response_time: '0.3s',
    student_satisfaction: 4.8,
    most_popular_subjects: ['Computer Science', 'Mathematics', 'Physics']
  };
};

export const getAIClassesBySubject = (subject, userId) => {
  const classes = getAllAvailableAIClasses(userId);
  if (subject === 'all') return classes;
  return classes.filter(cls => cls.subject === subject);
};

export const searchAIClasses = (query, userId) => {
  const classes = getAllAvailableAIClasses(userId);
  return classes.filter(cls => 
    cls.name.toLowerCase().includes(query.toLowerCase()) ||
    cls.ai_tutor.toLowerCase().includes(query.toLowerCase()) ||
    cls.description.toLowerCase().includes(query.toLowerCase())
  );
};
